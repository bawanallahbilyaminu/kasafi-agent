"""A deep answer never ends in 'took too long' (5 Nov 2026: a deep turn reached 232 s of its 240 s). A revise round that
won't fit in the time left gives the checked partial answer, with 'not read in time'; a slow writer gives a brief written
in code; a turn that outruns its limit is sent when ready."""

import asyncio
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from app.agent import answer as A
from app.agent import answer_check as ck
from app.agent import deep as D
from app.whatsapp import conversation as C
from tests.helpers import make_settings


def _claim(statement, value, dim="funding", doc="fs", page=147, **kw):
    return D.Claim(dim, statement, value, "", "2024", "Sokoto", doc, doc.upper(), page, **kw)


CLAIMS = [_claim("Computers budget was fully released", "₦40 million"),
          _claim("Office buildings variance", "₦55 million", dim="assets"),
          _claim("Digital hubs planned", "9", dim="assets", doc="mbp", page=175)]


def _result(**kw):
    base = dict(summary="The computers budget was ₦40 million (AFS, p. 147).",
                sections=[("funding", "The computers budget was ₦40 million (AFS, p. 147)."),
                          ("assets", "The variance was ₦55 million (AFS, p. 147), and ₦777 million went elsewhere.")],
                differ="", missing="staffing", claims=CLAIMS, documents=["fs"], cost=0.1, seconds=100.0,
                unread=["Financial Statements 2025"], pool=CLAIMS)
    return D.DeepResult(**{**base, **kw})


def _deep_answer():
    return A.deep_as_answer(_result(), None, {}, "en")


class _Fake:
    def __init__(self, settings=None, **kw):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None


@asynccontextmanager
async def _client(settings, factory):
    yield object()


def _run(a, monkeypatch, verdicts, elapsed: float, rewrite=None):
    """checked_answer with `elapsed` seconds of the turn already gone."""
    calls: list = []
    it = iter(verdicts)

    async def fake_check(message, a_, u, history, conn, settings, client, *, round_=1, model=None, **kw):
        calls.append({"round": round_, "timeout": settings.kasafi_check_timeout_s, **kw})
        return next(it)
    monkeypatch.setattr(A.answer_check, "check", fake_check)
    monkeypatch.setattr(A, "check_client", _client)
    if rewrite is not None:
        monkeypatch.setattr(A, "deep_rewritten", rewrite)

    async def no_second_round(*a, **k):
        raise AssertionError("a deep turn never runs the whole analysis again")
    monkeypatch.setattr(A, "_answer_finished", no_second_round)
    s = make_settings(kasafi_answer_check=True)
    out = asyncio.run(A.checked_answer(a, "the ministry", "en", object(), {"settings": s, "client_factory": _Fake},
                                       time.perf_counter() - elapsed))
    return out, calls


def test_a_revise_that_wont_fit_gives_the_checked_partial_with_the_not_read_note(monkeypatch) -> None:
    async def rewrite(*a, **k):
        raise AssertionError("no time for a rewrite")
    # 285 s is the deep turn's clock inside the answer; 230 s gone leaves 55 s, under what a rewrite and its check need
    out, calls = _run(_deep_answer(), monkeypatch, [ck.Verdict("revise", feedback="x", unsupported=["₦777 million"])],
                      230.0, rewrite)
    assert [c["round"] for c in calls] == [1]
    assert out.found and out.partial and out.deep is None and out.parts == []
    assert "₦40 million" in out.text and "₦55 million" not in out.text.split("⏳")[1]
    assert "777" not in out.text                                   # the flagged figure is out
    assert "Not read in time (ask again for these): Financial Statements 2025" in out.text
    assert "Not found in the documents read: staffing" in out.text
    assert "full brief" not in out.text and "took too long" not in out.text
    assert any(c.get("verdict") == "no time for a rewrite" for c in out.checks)


def test_with_time_left_the_rewrite_still_runs(monkeypatch) -> None:
    rewritten = A.deep_as_answer(_result(summary="The computers budget was ₦40 million (AFS, p. 147).", sections=[]), None, {}, "en")
    seen: dict = {}

    async def rewrite(a, feedback, question, lang, settings, factory, limit=45.0):
        seen["limit"], seen["feedback"] = limit, feedback
        return rewritten
    out, calls = _run(_deep_answer(), monkeypatch, [ck.Verdict("revise", feedback="fix it"), ck.Verdict("pass", round=2)],
                      100.0, rewrite)
    assert [c["round"] for c in calls] == [1, 2] and out is rewritten and seen == {"limit": 45.0, "feedback": "fix it"}


def test_the_check_of_a_rewrite_only_gets_what_is_left(monkeypatch) -> None:
    from types import SimpleNamespace
    real, gone = time.perf_counter, [0.0]
    monkeypatch.setattr(A, "time", SimpleNamespace(perf_counter=lambda: real() + gone[0]))

    async def rewrite(a, feedback, question, lang, settings, factory, limit=45.0):
        assert limit == 45.0
        gone[0] = 45.0                                            # the rewrite took all of it
        return _deep_answer()
    # 285 - 215 = 70 s left before the rewrite, 25 s after it
    out, calls = _run(_deep_answer(), monkeypatch, [ck.Verdict("revise"), ck.Verdict("skipped", round=2)], 215.0, rewrite)
    assert calls[0]["timeout"] == 30.0 and calls[1]["timeout"] <= 25.0
    assert out.deep is not None                                   # its check couldn't run: the claims are verified


def test_with_almost_nothing_left_the_brief_goes_out_with_its_figures_already_verified(monkeypatch) -> None:
    a = _deep_answer()
    out, calls = _run(a, monkeypatch, [], 280.0)
    assert calls == [] and out is a and out.checks[0]["verdict"] == "skipped"


def test_a_slow_or_failed_writer_gives_a_brief_written_in_code(monkeypatch) -> None:
    d = D.plain_brief(CLAIMS, "en")
    summary, sections, differ, used, cov = D.written(d, CLAIMS, [])
    assert "₦40 million" in summary and summary.startswith("These are the checked figures")
    assert dict(sections).keys() == {"funding", "assets"} and "₦55 million" in dict(sections)["assets"]
    assert "(" in dict(sections)["assets"] and "[C" not in dict(sections)["assets"]     # the [C<n>] became source tags
    assert D.plain_brief(CLAIMS, "ha")["summary"].startswith("Ga alƙaluman")
    assert D.WRITE_LIMIT_S + D.READ_DEADLINE_S <= D.TIME_BUDGET_S


def test_a_turn_past_its_limit_goes_on_and_is_sent_when_ready() -> None:
    async def run():
        job = asyncio.ensure_future(asyncio.sleep(0.3, "done"))
        with pytest.raises(C.FetchStillRunning) as e:
            await C._await_answer(job, 0.02, [], "en", _notify, carry_on=True)
        assert e.value.job is job and not job.cancelled()
        assert await e.value.job == "done"
        other = asyncio.ensure_future(asyncio.sleep(5))
        with pytest.raises(asyncio.TimeoutError):              # any other answer keeps its limit and its apology
            await C._await_answer(other, 0.02, [], "en", _notify)
        await asyncio.sleep(0)
        assert other.cancelled()

    async def _notify(out):
        return None
    asyncio.run(run())
    assert "took too long" not in C.FETCH_WORDS["en"]["deep_later"]
    assert D.DEEP_TURN_S == 300.0 and C_typing_covers_it()


def C_typing_covers_it() -> bool:
    from app.whatsapp.webhook import TYPING_MOST_S
    return TYPING_MOST_S > D.DEEP_TURN_S


def test_a_late_deep_answer_brings_its_section_messages(monkeypatch) -> None:
    from app.users import UserStore
    from app.whatsapp import client as client_module
    from types import SimpleNamespace
    sent: list = []

    class Client:
        async def send_text(self, to, body):
            sent.append(body)

        async def aclose(self):
            return None
    monkeypatch.setattr(client_module, "WhatsAppClient", Client)

    async def job():
        return SimpleNamespace(text="The brief.", parts=["*Funding*\nOne line."], sources=[], working="", quotes="")
    store = UserStore(":memory:")
    store.create("k", "en")

    async def run():
        await C._deliver_later(asyncio.ensure_future(job()), "234", "k", "en", "q", store, make_settings())
    asyncio.run(run())
    assert sent == ["The brief.", "*Funding*\nOne line."]


def test_an_analysis_stopped_by_its_budget_never_says_took_too_long(monkeypatch) -> None:
    async def slow(*a, box=None, **k):
        box["deep_profile"] = profile
        raise asyncio.TimeoutError
    profile = A.Answer("In 2026 the ministry has ₦3.59 billion.", True, True)
    monkeypatch.setattr(A, "_answer_question", slow)
    from types import SimpleNamespace
    q = "Tell me about the ministry including its budget and spending"
    out = asyncio.run(A._answer_finished(q, "en", None, understanding=SimpleNamespace(capability="deep")))
    assert out is profile

    async def slower(*a, box=None, **k):
        raise asyncio.TimeoutError
    monkeypatch.setattr(A, "_answer_question", slower)
    for lang in ("en", "ha"):
        out = asyncio.run(A._answer_finished(q, lang, None, understanding=SimpleNamespace(capability="deep")))
        assert out.text == A.DEEP_UNFINISHED[lang] and not out.found and "too long" not in out.text
    out = asyncio.run(A._answer_finished(q, "en", None, understanding=SimpleNamespace(capability="budget")))
    assert out.text == A.TIMED_OUT["en"]                       # other answers as before


def test_empty_section_headings_go_from_a_partial_answer() -> None:
    text = "Summary line.\n\n*Staffing*\n\n*Funding*\nA line.\n\n*Plans*\n\nℹ️ Not found: x"
    assert ck.no_empty_headings(text) == "Summary line.\n\n*Funding*\nA line.\n\nℹ️ Not found: x"
    assert ck.no_empty_headings("*Staffing*\n\nℹ️ Not found: x\n⏳ Not read: y") == ""


def test_registry_counts_are_evidence_for_the_check() -> None:
    claims = [D.Claim("facilities", "primary-level facilities in the registry", "894", "", "", "Sokoto",
                      "registry:grid3", "Registry", 0), _claim("Computers budget", "₦40 million")]
    a = A.deep_as_answer(_result(claims=claims, summary="There are 894 facilities and ₦40 million.", sections=[]), None, {}, "en")
    assert [e.doc_id for e in a.cited] == ["fs"] and "894" in a.working
    assert ck.found_count(a)[0] == ck.found_count(a)[1]        # both found: the page's and the registry's
    assert "894" in ck.evidence_text(None, a)


def test_a_sentence_never_names_its_source() -> None:
    """Live: 'MFS 2025-2027 p.37 prints its share of total sector personnel allocation in 2025 as 0.16%'."""
    rules = " ".join(D.SYNTH_SYSTEM.split())
    assert "A sentence says the fact, never where it was read" in rules and "Never name a document or a page" in rules
    seen: dict = {}

    async def chat_json(client, messages, **kw):
        seen["user"] = messages[1]["content"]
        return {"summary": "x"}
    from app.agent import answer as answer_module
    real = answer_module.chat_json
    answer_module.chat_json = chat_json
    try:
        asyncio.run(D.synthesise(object(), "q", "en", CLAIMS, [], make_settings(), feedback="cite MFS p.37 as the source"))
    finally:
        answer_module.chat_json = real
    assert "its [C<n>] tag alone even when the review mentions a document or a page" in seen["user"]


def test_the_deletion_page_promises_only_what_exists() -> None:
    page = " ".join(Path("docs/site/data-deletion.md").read_text(encoding="utf-8").split())
    assert "your phone number and WhatsApp name from our records" not in page
    assert "never stores your WhatsApp profile name" in page and "a name you told Kasafi" in page
    assert not re.search(r"(?i)baseten|azure", page)
