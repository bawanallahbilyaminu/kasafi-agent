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
