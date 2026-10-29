import asyncio
import json

import pytest

from app.agent import answer as ans
from app.agent.answer import Evidence, Plan, format_citations, unverified_numbers
from app.providers.chat import ChatResult
from tests.helpers import make_settings

EV = [
    Evidence(1, "budget-2026-approved", "Sokoto State FY 2026 Budget", 2026, 40, "text",
             "[Table: Total Expenditure by Programme]\n05 Education | 2026 Approved Budget: 128,495,868,362.13"),
    Evidence(2, "smart-agenda", "Sokoto State 9-Point SMART Agenda", None, 3, "ocr", "Security 01 Education 03"),
]


def test_unverified_numbers_ignores_citation_markers_and_formatting() -> None:
    assert unverified_numbers("An ware 128,495,868,362.13 ga ilimi [1].", EV) == []
    assert unverified_numbers("An ware 128495868362.13 [1]", EV) == []                 # commas don't matter
    assert unverified_numbers("An ware 130,000,000,000.00 [1]", EV) == ["130,000,000,000.00"]
    assert unverified_numbers("Kashi 12% ne [1]", EV) == ["12"]                      # a computed % isn't in the evidence


def test_citations_show_page_word_in_user_language_and_ocr_flag() -> None:
    assert format_citations(EV, "ha") == ("[1] Sokoto State FY 2026 Budget, shafi 40\n"
                                          "[2] Sokoto State 9-Point SMART Agenda, shafi 3 (OCR)")
    assert "page 40" in format_citations(EV[:1], "en")


def test_assumption_shown_in_user_language() -> None:
    p = Plan("q", ["x"], [], "used the latest budget, 2026", "Na yi amfani da kasafin 2026 mafi sabo.")
    assert p.assumption_for("ha") == "Na yi amfani da kasafin 2026 mafi sabo."
    assert p.assumption_for("en") == "Assumption: used the latest budget, 2026."
    assert Plan("q", [], []).assumption_for("ha") == ""


# --- answer_question with a fake model and fake retrieval ------------------------------------

class FakeClient:
    """Replies to the planner, then to each compose call, from a queue."""

    def __init__(self, replies: list[dict]) -> None:
        self.replies, self.calls = list(replies), []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


PLAN = {"english_question": "How much for education?", "search_queries": ["education total"],
        "doc_ids": ["budget-2026-approved"], "assumption": "used the latest budget, 2026",
        "assumption_ha": "Na yi amfani da kasafin 2026 mafi sabo."}


def run(monkeypatch, replies: list[dict], evidence=EV, gaps: list | None = None, **kw):
    fake = FakeClient(replies)
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "budget-2026-approved", "title": "t"}])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: evidence)
    monkeypatch.setattr(ans, "log_gap", lambda conn, q, doc, reason, detail=None: (gaps if gaps is not None else []
                                                                                    ).append((q, doc, reason)))
    a = asyncio.run(ans.answer_question("Nawa aka ware wa ilimi?", "ha", conn=None, settings=make_settings(),
                                        client_factory=lambda s: fake, **kw))
    return a, fake


def test_grounded_answer_with_assumption_and_citation(monkeypatch) -> None:
    a, fake = run(monkeypatch, [PLAN, {"answer": "An ware 128,495,868,362.13 ga ilimi [1].", "found": "full", "cited": [1]}])
    assert a.found and a.verified and not a.partial
    assert a.text.startswith("_Na yi amfani da kasafin 2026 mafi sabo._")
    assert "₦128.50 biliyan" in a.text and "128,495,868,362.13" in a.exact      # readable for users, exact for checks
    assert "[1] Sokoto State FY 2026 Budget, shafi 40" in a.text
    evidence_msg = fake.calls[1][1]["content"]
    assert "EVIDENCE:" in evidence_msg and "Reply in Hausa" in evidence_msg


def test_unverified_figure_is_retried_then_replaced_by_sources(monkeypatch) -> None:
    bad = {"answer": "An ware 130,000,000,000.00 [1].", "found": "full", "cited": [1]}
    a, fake = run(monkeypatch, [PLAN, bad, bad])
    assert len(fake.calls) == 3 and "CORRECTION NEEDED" in fake.calls[2][1]["content"]
    assert a.found and not a.verified and "130,000,000,000.00" not in a.text
    assert a.text.startswith(ans.UNVERIFIED["ha"]) and "shafi 40" in a.text


def test_retry_that_fixes_the_figure_is_accepted(monkeypatch) -> None:
    bad = {"answer": "An ware 130,000,000,000.00 [1].", "found": "full", "cited": [1]}
    good = {"answer": "An ware 128,495,868,362.13 [1].", "found": "full", "cited": [1]}
    a, _ = run(monkeypatch, [PLAN, bad, good])
    assert a.verified and "128,495,868,362.13" in a.exact and "₦128.50 biliyan" in a.text


def test_partial_answer_is_sent(monkeypatch) -> None:
    a, _ = run(monkeypatch, [PLAN, {"answer": "Rahoton bai bayar da jimillar ba [1].", "found": "partial", "cited": [1]}])
    assert a.found and a.partial and "Rahoton bai bayar" in a.text


@pytest.mark.parametrize("reply", [{"answer": "Ban samu ba.", "found": "none", "cited": []},
                                   {"answer": "x", "found": "full", "cited": [99]},          # cites nothing real
                                   {"answer": "", "found": "full", "cited": [1]}])
def test_not_found_cases(monkeypatch, reply: dict) -> None:
    a, _ = run(monkeypatch, [PLAN, reply])
    assert not a.found and a.text == ans.NOT_FOUND["ha"]


def test_no_evidence_skips_the_answer_call(monkeypatch) -> None:
    a, fake = run(monkeypatch, [PLAN], evidence=[])
    assert not a.found and len(fake.calls) == 1


def test_planner_drops_unknown_doc_ids_and_caps_lists(monkeypatch) -> None:
    plan = {**PLAN, "doc_ids": ["nope", "budget-2026-approved", "x", "y"], "search_queries": ["a", "b", "c", "d"]}
    a, _ = run(monkeypatch, [plan, {"answer": "An ware 128,495,868,362.13 [1].", "found": "full", "cited": [1]}])
    assert a.plan.doc_ids == ["budget-2026-approved"] and len(a.plan.search_queries) == 3


# --- WhatsApp format: summary, bullets, readable amounts -------------------------------------

from app.agent.answer import readable_amounts, render_answer  # noqa: E402


@pytest.mark.parametrize("raw, ha, en", [
    ("118,827,792,994.59", "₦118.83 biliyan", "₦118.83 billion"),
    ("N52,179,252,082.91", "₦52.18 biliyan", "₦52.18 billion"),
    ("2,500,000,000,000.00", "₦2.50 tiriliyan", "₦2.50 trillion"),
    ("1,200,000.00", "₦1.20 miliyan", "₦1.20 million"),
    ("₦640,000.00", "₦640,000.00", "₦640,000.00"),
    ("N104,450 million", "₦104,450 million", "₦104,450 million"),   # already in units
])
def test_readable_amounts(raw: str, ha: str, en: str) -> None:
    assert readable_amounts(raw, "ha") == ha and readable_amounts(raw, "en") == en


@pytest.mark.parametrize("text", ["a 2025", "87.76 da 200%", "code 052100000000", "page 40", "0.489"])
def test_non_money_numbers_are_untouched(text: str) -> None:
    assert readable_amounts(text, "ha") == text


def test_render_summary_then_bullets() -> None:
    d = {"summary": "An ware wa Ma'aikatar Lafiya kuɗi a 2025 [1][2].",
         "items": ["2025 (approved): 52,179,252,082.91 [1]", "Spent (Q1–Q4 2025): 17,506,884,680.90 [2]"]}
    assert render_answer(d, "ha") == ("An ware wa Ma'aikatar Lafiya kuɗi a 2025 [1][2].\n\n"
                                      "• 2025 (approved): ₦52.18 biliyan [1]\n"
                                      "• Spent (Q1–Q4 2025): ₦17.51 biliyan [2]")
    assert render_answer({"summary": "Kawai layi ɗaya [1].", "items": []}, "ha") == "Kawai layi ɗaya [1]."
    assert render_answer({"answer": "Tsohon tsari [1]."}, "ha") == "Tsohon tsari [1]."   # older reply shape


def test_figure_check_covers_summary_and_items(monkeypatch) -> None:
    bad = {"summary": "Total [1].", "items": ["2025: 999,999,999.00 [1]"], "found": "full", "cited": [1]}
    a, fake = run(monkeypatch, [PLAN, bad, bad])
    assert not a.verified and len(fake.calls) == 3


def test_word_ending_in_n_is_not_a_naira_sign() -> None:
    assert readable_amounts("kasafin 52,179,252,082.91", "ha") == "kasafin ₦52.18 biliyan"
    assert readable_amounts("N52,179,252,082.91", "ha") == "₦52.18 biliyan"
    assert readable_amounts("NGN 1,200,000.00", "en") == "₦1.20 million"


def test_over_hooked_hausa_is_fixed_but_correct_hooks_stay() -> None:
    d = {"summary": "Ƙasafin 2025 ya ware, kuma an ƙashe kuɗi a ƙaramar hukuma [1].", "items": []}
    assert render_answer(d, "ha") == "Kasafin 2025 ya ware, kuma an kashe kuɗi a ƙaramar hukuma [1]."
    assert render_answer({"summary": "ƙasafi", "items": []}, "en") == "ƙasafi"     # only for Hausa replies


@pytest.mark.parametrize("raw, out", [
    ("2,345,000 IDPs", "2,345,000 IDPs"),                       # a count of people: no naira sign
    ("₦1,234,567.00 displaced people", "1,234,567.00 displaced people"),
    ("mutane 1,120,000 'yan gudun hijira", "mutane 1,120,000 'yan gudun hijira"),
    ("1,250,000 individuals in 210,000 households", "1,250,000 individuals in 210,000 households"),
    ("total of 45,012 [1]", "total of 45,012 [1]"),             # no ₦, no kobo: not assumed to be money
])
def test_counts_never_get_a_naira_sign(raw: str, out: str) -> None:
    assert readable_amounts(raw, "en") == out and readable_amounts(raw, "ha") == out


def test_naira_word_before_an_amount_is_replaced_by_the_sign() -> None:
    assert readable_amounts("An ware Naira 9,076,557,198.38 [1]", "ha") == "An ware ₦9.08 biliyan [1]"
    assert readable_amounts("naira ₦9,076,557,198.38", "ha") == "₦9.08 biliyan"
    assert readable_amounts("Naira nawa aka ware?", "ha") == "Naira nawa aka ware?"


# --- self-growing library: a missing document is fetched, or the gap is logged ---------------

from app.acquisition.library import Acquired  # noqa: E402

MISSING = {**PLAN, "missing_document": "Sokoto State Budget Implementation Report Q3 2025"}
GOOD = {"summary": "An ware 128,495,868,362.13 [1].", "items": [], "found": "full", "cited": [1]}


def test_missing_document_is_fetched_announced_and_searched_first(monkeypatch) -> None:
    sent, asked = [], []

    async def notify(text):
        sent.append(text)

    async def acquire(conn, description, *, settings, client):
        asked.append(description)
        return Acquired("indexed", "bir-2025-q3", "Budget Implementation Report Q3 2025",
                        "https://mof.sk.gov.ng/q3.pdf")

    a, _ = run(monkeypatch, [MISSING, GOOD], notify=notify, acquire_fn=acquire)
    assert a.plan.doc_ids == ["bir-2025-q3", "budget-2026-approved"]          # the new document is searched first
    assert asked == ["Sokoto State Budget Implementation Report Q3 2025"]
    assert sent and "Ina neman takardar" in sent[0] and "Q3 2025" in sent[0]
    assert a.found and a.text.startswith("📥 Na samo kuma na ƙara sabuwar takarda")
    assert "mof.sk.gov.ng" in a.text and a.acquired.doc_id == "bir-2025-q3"


def test_document_not_found_is_logged_and_said(monkeypatch) -> None:
    gaps = []

    async def acquire(conn, description, *, settings, client):
        return Acquired("not_found", detail="3 candidates, none matched")

    a, _ = run(monkeypatch, [MISSING], evidence=[], gaps=gaps, acquire_fn=acquire)
    assert not a.found and "Ban samo takardar" in a.text and "Q3 2025" in a.text
    assert gaps == [("How much for education?", "Sokoto State Budget Implementation Report Q3 2025", "not_found")]


def test_no_missing_document_means_no_fetch(monkeypatch) -> None:
    async def acquire(*a, **k):
        raise AssertionError("should not fetch")

    a, _ = run(monkeypatch, [PLAN, GOOD], acquire_fn=acquire)
    assert a.found and a.acquired is None and "📥" not in a.text


def test_unanswered_question_goes_to_the_review_queue(monkeypatch) -> None:
    gaps = []
    run(monkeypatch, [PLAN, {"summary": "", "items": [], "found": "none", "cited": []}], gaps=gaps)
    assert gaps and gaps[0][2] == "no_answer"


def test_model_calls_get_excerpts_not_whole_documents() -> None:
    """README "Data sources and use" promises these limits (some sites say ai-train=no). Update both together."""
    from app.acquisition import library
    assert ans.MAX_EVIDENCE <= 6 and ans.EVIDENCE_CHARS <= 4500 and library.CONFIRM_CHARS <= 4000

    class Spy:
        async def chat(self, messages, **kw):
            self.sent = messages[1]["content"]
            return ChatResult(content='{"match": false}', model="m", finish_reason="stop")

    spy = Spy()
    asyncio.run(library.confirm_document("d", ["x" * 5000] * 50, [], spy, make_settings()))
    assert len(spy.sent) < library.CONFIRM_CHARS + 200          # 3 pages at most, cut to the limit


# --- "latest" questions: newest edition, named, older edition flagged -------------------------

from datetime import date  # noqa: E402

from app.acquisition.editions import SERIES, Latest  # noqa: E402

LATEST_PLAN = {**PLAN, "latest": {"series": "nbs_cpi", "name": "NBS CPI", "frequency": "monthly"}}
CPI_GOOD = {"summary": "128,495,868,362.13 [1].", "items": [], "found": "full", "cited": [1]}


def run_latest(monkeypatch, result: Latest, replies, gaps=None, lang="en"):
    seen = {}

    async def latest_fn(conn, series, today, *, newer_than=None, notify=None, notify_text=""):
        seen.update(series=series.key, today=today, notify_text=notify_text)
        return result

    monkeypatch.setattr(ans, "series_doc_ids", lambda conn, s: {"cpi-2025-06"})
    fake = FakeClient(replies)
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "cpi-2025-06", "title": "t"}])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: EV)
    monkeypatch.setattr(ans, "log_gap", lambda conn, q, doc, reason, detail=None: (gaps if gaps is not None else []
                                                                                    ).append((doc, reason)))
    a = asyncio.run(ans.answer_question("latest CPI?", lang, conn=None, settings=make_settings(),
                                        client_factory=lambda s: fake, latest_fn=latest_fn, today=date(2026, 10, 28)))
    return a, seen, fake


def test_planner_gets_todays_date(monkeypatch) -> None:
    _, _, fake = run_latest(monkeypatch, Latest(SERIES["nbs_cpi"], "2026-09", "cpi-2026-09", "2026-09", "newest"),
                            [{**LATEST_PLAN, "doc_ids": ["cpi-2025-06"]}, CPI_GOOD])
    assert "TODAY: 2026-10-28" in fake.calls[0][1]["content"]


def test_latest_question_names_the_newest_edition(monkeypatch) -> None:
    a, seen, fake = run_latest(monkeypatch, Latest(SERIES["nbs_cpi"], "2026-09", "cpi-2026-09", "2026-09", "newest"),
                               [{**LATEST_PLAN, "doc_ids": ["cpi-2025-06"]}, CPI_GOOD])
    assert seen["series"] == "nbs_cpi" and "September 2026" in seen["notify_text"]
    assert a.text.startswith("📅 NBS CPI and Inflation Report, September 2026: the newest edition "
                             "(released around October 2026).")
    assert a.plan.doc_ids == ["cpi-2026-09"]                       # the older June 2025 edition is out of the plan
    assert "September 2026" in fake.calls[1][1]["content"]         # the composer is told which edition


def test_older_edition_is_said_plainly_and_logged(monkeypatch) -> None:
    gaps = []
    a, _, _ = run_latest(monkeypatch, Latest(SERIES["nbs_cpi"], "2026-09", "cpi-2025-06", "2025-06", "older",
                                             tried=["2026-09"]), [LATEST_PLAN, CPI_GOOD], gaps=gaps)
    assert a.text.startswith("📅 The newest I could get is NBS CPI and Inflation Report, June 2025; "
                             "a newer one (up to September 2026) may exist.")
    assert gaps == [("NBS Nigeria Consumer Price Index (CPI) and Inflation Report September 2026", "older_edition")]


def test_no_edition_at_all(monkeypatch) -> None:
    a, _, fake = run_latest(monkeypatch, Latest(SERIES["nbs_cpi"], "2026-09", tried=["2026-09", "2026-08"]),
                            [LATEST_PLAN], lang="ha")
    assert not a.found and "Satumba 2026, Agusta 2026" in a.text and len(fake.calls) == 1


def test_L17_edition_year_from_the_title_is_not_an_unverified_figure() -> None:
    ev = [Evidence(1, "cpi", "Consumer Price Index September 2026", 2026, 19, "ocr",
                   "Sokoto | Sep 2026 All Items: 135.1 | Year-on-Year All Items: 8.0")]
    assert unverified_numbers("In September 2026 Sokoto's rate was 8.0 [1].", ev) == []
    assert unverified_numbers("In September 2027 it was 8.0 [1].", ev) == ["2027"]


def test_page_references_and_asked_years_are_not_figures() -> None:
    ev = [Evidence(1, "d", "Budget Implementation Report Q2 2026", 2026, 18, "text", "Ministry of Health | x: 10.6%")]
    assert unverified_numbers("Release rate 10.6%, page 18 [1].", ev) == []
    assert unverified_numbers("Kashi 10.6%, shafi na 18 [1].", ev) == []
    assert unverified_numbers("Release rate 10.6%, page 44 [1].", ev) == ["44"]          # not a cited page
    years = ans.question_years("What is the 2026 target compared with 2025?")
    assert unverified_numbers("No 2026 target was found [1].", ev, years) == []
    assert unverified_numbers("A difference of 6,309,344,300.00 [1].", ev, years) == ["6,309,344,300.00"]


def test_invalid_json_is_retried_then_the_user_is_asked_to_rephrase(monkeypatch) -> None:
    class Garbled:
        def __init__(self, replies):
            self.replies, self.calls = list(replies), 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def chat(self, messages, **kw):
            self.calls += 1
            return ChatResult(content=self.replies.pop(0), model="m", finish_reason="stop")

    monkeypatch.setattr(ans, "load_catalog", lambda conn: [])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: [])
    monkeypatch.setattr(ans, "log_gap", lambda *a, **k: None)
    g = Garbled(["{not json", "still not json"])
    a = asyncio.run(ans.answer_question("q", "ha", conn=None, settings=make_settings(), client_factory=lambda s: g))
    assert not a.found and a.text == ans.REPHRASE["ha"] and g.calls == 2
    g = Garbled(["{not json", json.dumps(PLAN)])                    # the retry works: carry on
    a = asyncio.run(ans.answer_question("q", "en", conn=None, settings=make_settings(), client_factory=lambda s: g))
    assert a.text == ans.NOT_FOUND["en"] and g.calls == 2
