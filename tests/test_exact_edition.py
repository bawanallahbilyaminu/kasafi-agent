"""A missing document named with an exact period (4 Nov 2026 live-fetch demo): "Sokoto State Budget Implementation
Report Q4 2025" had come back as 'known' = the 2026 Q3 report, because the download wasn't tied to the edition
wanted and the library's newer edition of the series won. Now the series AND the exact period are read from the
description; only that edition counts as held; a download must be that edition; and when it really isn't
available the answer says so plainly and uses the latest earlier edition, named."""

import asyncio
from types import SimpleNamespace

import pytest

from app.acquisition import editions as E
from app.acquisition import library as L
from app.acquisition.library import Acquired
from tests.helpers import make_settings


@pytest.mark.parametrize("description, want", [
    ("Sokoto State Budget Implementation Report Q4 2025", ("sokoto_bir", "2025-Q4")),
    ("Sokoto State 2026 Q3 Budget Performance Report", ("sokoto_bir", "2026-Q3")),
    ("Budget implementation report for the fourth quarter of 2025", ("sokoto_bir", "2025-Q4")),
    ("Sokoto State 2024 Approved Budget", ("sokoto_budget", "2024")),
    ("NBS CPI and Inflation Report September 2026", ("nbs_cpi", "2026-09")),
    ("Sokoto State Budget Implementation Report", None),          # the series, no period: the newest answers
    ("Sokoto State Health Sector Annual Operational Plan 2025", None),
])
def test_the_series_and_exact_period_are_read_from_a_description(description, want) -> None:
    assert E.wanted_edition(description) == want


def test_q4_2025_is_fetched_when_the_library_holds_the_other_quarters(monkeypatch) -> None:
    """Library: 2025 Q1-Q3 and 2026 Q1-Q3 of the series. Asked for Q4 2025: fetched, tied to that edition; the
    fuzzy title match (which would give 2026 Q3) is never consulted."""
    held = {("sokoto_bir", e) for e in ("2025-Q1", "2025-Q2", "2025-Q3", "2026-Q1", "2026-Q2", "2026-Q3")}
    seen: dict = {}
    monkeypatch.setattr(L, "local_edition", lambda conn, s, e: f"bir-{e.lower()}" if (s, e) in held else None)
    monkeypatch.setattr(L, "find_local", lambda conn, d: seen.setdefault("find_local", True) and "bir-2026-q3")
    monkeypatch.setattr(L, "fetches_today", lambda conn: 0)
    monkeypatch.setattr(L, "registry_urls", lambda d: ["https://mof.sk.gov.ng/bir-2025-q4.pdf"])

    async def allowed(self, url):
        return True, ""
    monkeypatch.setattr(L.Robots, "allowed", allowed)

    async def fetch_and_index(conn, url, description, *, settings, client, http, robots, series, edition, allowed):
        seen["fetch"] = (url, series, edition)
        return Acquired("fetched", "bir-2025-q4-fetched", url=url)
    monkeypatch.setattr(L, "fetch_and_index", fetch_and_index)
    s = make_settings(kasafi_fetch_enabled=True)
    got = asyncio.run(L.find_and_fetch(object(), "Sokoto State Budget Implementation Report Q4 2025", settings=s,
                                       client=None))
    assert got.status == "fetched" and got.doc_id == "bir-2025-q4-fetched"
    assert seen["fetch"] == ("https://mof.sk.gov.ng/bir-2025-q4.pdf", "sokoto_bir", "2025-Q4")
    assert "find_local" not in seen                                 # another edition never stands in
    # the exact edition held: no fetch at all
    got = asyncio.run(L.find_and_fetch(object(), "Sokoto State Budget Implementation Report Q3 2026", settings=s,
                                       client=None))
    assert got.status == "local" and got.doc_id == "bir-2026-q3"


def test_the_librarys_other_documents_never_answer_in_place_of_a_missing_exact_edition(monkeypatch) -> None:
    """4 Nov live (18:13): 'library first' answered Q4 2025 social protection from the UN social-protection report
    and the citizens' budget, and logged 'no fetch'. An exact edition the library doesn't hold is fetched."""
    from app.agent import answer as A
    monkeypatch.setattr(A, "local_edition", lambda conn, s, e: "bir-2026-q2" if e == "2026-Q2" else None)
    conn = object()
    assert A.exact_edition_missing(conn, "Sokoto State Budget Implementation Report Q4 2025")
    assert not A.exact_edition_missing(conn, "Sokoto State Budget Implementation Report Q2 2026")   # held
    assert not A.exact_edition_missing(conn, "UN Joint Programme on Social Protection report")        # no edition
    assert not A.exact_edition_missing(None, "Sokoto State Budget Implementation Report Q4 2025")


def test_a_typed_whole_question_is_new_even_with_a_read_back_pending(monkeypatch) -> None:
    """4 Nov live (18:17): the typed 'How much did Sokoto spend on social protection in Q3 2026?' after an unclear
    voice note was resolved as a correction and answered with 'Corrected: …'."""
    from types import SimpleNamespace
    from app.users import UserStore, user_key
    from app.whatsapp import conversation as C
    from app.guardrails.scope import Verdict
    s = make_settings(kasafi_understanding=False)
    store, sender = UserStore(":memory:"), "2348000000081"
    key = user_key(sender, s)
    store.create(key, "en")
    store.give_consent(key)
    store.set_pending(key, "Nawa aka ware wa ilimi?", "How much for education?")
    seen: dict = {}

    async def resolve_fn(pending, reply, *, settings):
        seen["resolved"] = True
        from app.whatsapp.corrections import Resolution
        return Resolution("correction", reply)

    async def answer(question, lang, **kw):
        seen["question"] = question
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")

    async def ok(*a, **k):
        return Verdict("ok", "none")

    async def none(*a, **k):
        return None
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    q = "How much did Sokoto spend on social protection in Q3 2026?"
    outs = asyncio.run(C.handle({"from": sender, "id": "w-typed", "type": "text", "text": {"body": q}}, None, store=store,
                                settings=s, answer_fn=answer, guard_fn=ok, place_fn=none, resolve_fn=resolve_fn,
                                emergency_fn=none, classify_fn=none))
    assert "resolved" not in seen and seen["question"] == q and outs[0].text.startswith("ANSWER")
    assert store.get_pending(key, 60) is None                      # the old read-back lapsed


def test_a_period_that_isnt_available_is_said_plainly_and_the_latest_earlier_edition_answers(monkeypatch) -> None:
    from app.agent import answer as A
    plan = A.Plan(english_question="How much was spent on health in Q4 2025?", search_queries=[],
                  doc_ids=["bir-2026-q3"], missing_document="Sokoto State Budget Implementation Report Q4 2025")
    monkeypatch.setattr(A, "log_gap", lambda *a, **k: None)
    monkeypatch.setattr(A, "newest_local", lambda conn, s, before=None: ("bir-2025-q3", "2025-Q3"))

    async def acquire_fn(conn, description, *, settings, client):
        return Acquired("not_found", detail="0 candidates")
    acq = asyncio.run(A.acquire_missing(object(), plan, "en", None, make_settings(), None, acquire_fn=acquire_fn))
    assert acq.status == "not_found"
    assert plan.edition_note == "I don't have the Q4 2025 report; the latest I have before it is Q3 2025, used below."
    assert plan.doc_ids[0] == "bir-2025-q3"                          # the earlier edition answers, named
    ha = A.Plan(english_question="q", search_queries=[], doc_ids=[],
                missing_document="Sokoto State Budget Implementation Report Q4 2025")
    asyncio.run(A.acquire_missing(object(), ha, "ha", None, make_settings(), None, acquire_fn=acquire_fn))
    assert ha.edition_note.startswith("Ba ni da rahoton")
    # the note goes first in the answer text
    a = SimpleNamespace(text="Health spent ₦3.43 billion by September 2025 (Q3 2025 report, p. 26).", plan=plan,
                        clarify=None)

    async def finished(question, lang, conn, **kw):
        return a

    async def checked(a_, *args):
        return a_
    monkeypatch.setattr(A, "_answer_finished", finished)
    monkeypatch.setattr(A, "checked_answer", checked)
    out = asyncio.run(A.answer_question("q", "en", object(), settings=make_settings()))
    assert out.text.startswith("I don't have the Q4 2025 report; the latest I have before it is Q3 2025, used below.\n\n"
                               "Health spent")
