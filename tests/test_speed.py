"""The speed round (Nov 1): searches off the event loop on pooled connections, the keyword and vector searches
side by side, crops rendered during the checks, the code-written entity/level/period check on every answer and
the model-based parts check only for multi-part questions, and a redo that re-reads or searches for the missing
part only. Nothing here may change an answer: only when work happens."""

import asyncio
import pytest
import threading

from app.retrieval import pool
from tests.helpers import make_settings


def test_without_a_database_the_pool_runs_in_the_calling_thread() -> None:
    s = make_settings()                                   # no database_url: has_database is False
    here = threading.current_thread().name
    got = asyncio.run(pool.run(s, lambda conn, x: (conn, x, threading.current_thread().name), "CONN", 7))
    assert got == ("CONN", 7, here)
    assert pool.run_sync(s, lambda conn, x: x * 2, None, 4).result() == 8


def test_a_pool_that_cannot_open_turns_itself_off_and_stays_off(monkeypatch) -> None:
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")      # nothing listens there
    monkeypatch.setattr(pool, "_pool", None)
    monkeypatch.setattr(pool, "_off", False)
    monkeypatch.setattr(pool, "POOL_MAX", 1)
    monkeypatch.setattr(pool, "POOL_TIMEOUT", 1.0)
    assert asyncio.run(pool.run(s, lambda conn: conn, "C")) == "C"           # falls back to the caller's conn
    assert pool._off and not pool.available(s)                               # and stays off
    pool.close()


def test_the_pool_passes_a_settings_keyword_through_to_the_search() -> None:
    """search_lines takes settings= for its own parallel vector search: the pool's own first parameter must not
    swallow it (positional-only), with or without a pool."""
    s = make_settings()
    got = asyncio.run(pool.run(s, lambda conn, terms, settings=None: (terms, settings is s), "C", ["x"], settings=s))
    assert got == (["x"], True)
    assert pool.run_sync(s, lambda conn, settings=None: settings is s, "C", settings=s).result() is True


# --- the entity / level / period check in code, on every answer ------------------------------------------------

from decimal import Decimal

from app.agent import answer as ag
from app.agent import consistency
from app.agent.line_answer import LineResult, Selection
from app.agent.need import Entity, Need
from app.agent.periods import Period
from app.retrieval.line_search import Cell, Line


def _line(code, doc, year, period="full_year", measure="approved"):
    x = Line(1, "t", doc, 5, "Total Expenditure by Administrative Classification", "Agency", "Agency | 2026: 1",
             "administrative", "", "", 0.0, code=code, spend_kind="total")
    cell = Cell("col", year, measure, period, Decimal("1"))
    x.cells.append(cell)
    return Selection(x, cell)


def _answer_with(sels):
    return ag.Answer("t", True, True, lines=LineResult(selections=sels, found="full"))


def _plan_asking(entity_type, code):
    need = Need("q", entities=[Entity(entity_type, "Govt House", "Government House", code)])
    return ag.Plan("q", [], [], need=need)


def test_rows_for_another_agency_or_the_parent_total_are_mismatches() -> None:
    plan = _plan_asking("sub_agency", "011100100100")
    assert consistency.check(plan, "q", _answer_with([_line("011100100100", "budget-2026-approved", 2026)])) == []
    other = consistency.check(plan, "q", _answer_with([_line("052100000000", "budget-2026-approved", 2026)]))
    assert [m.kind for m in other] == ["entity"]
    parent = consistency.check(plan, "q", _answer_with([_line("011100000000", "budget-2026-approved", 2026)]))
    assert [m.kind for m in parent] == ["level"] and "ministry total" in parent[0].got


def test_a_figure_for_another_period_is_a_mismatch() -> None:
    plan = _plan_asking("mda", "052100000000")
    q2 = _answer_with([_line("052100000000", "bir-2026-q2", 2026, "q1_q2", "actual")])
    assert [m.kind for m in consistency.check(plan, "q", q2, Period(2026, 1))] == ["period"]
    assert consistency.check(plan, "q", q2, Period(2026, 2)) == []
    y25 = _answer_with([_line("052100000000", "budget-2025-approved", 2025)])
    assert [m.kind for m in consistency.check(plan, "q", y25, None, [2026])] == ["period"]
    assert consistency.check(plan, "q", y25, None, [2025]) == []
    assert consistency.check(plan, "q", ag.Answer("t", True, True)) == []    # nothing used: nothing to compare


def test_focus_terms_and_notes() -> None:
    m = [consistency.Mismatch("level", "Government House (011100100100)", "the ministry total (011100000000)")]
    assert consistency.focus_terms(m, None) == ["Government House", "011100100100"]
    assert consistency.note(m, "en") == "The row found is the ministry total (011100000000), not Government House " \
                                        "(011100100100) on its own."
    assert "Use exactly level: Government House" in consistency.redo_hint(m)


@pytest.mark.parametrize("q,want", [
    ("How much was allocated to the Ministry of Health in 2026?", False),
    ("How much was allocated to the Ministry of Health in 2026, and how much had it spent by Q2?", True),
    ("Compare the 2025 and 2026 education budgets", True),
    ("Nawa aka ware wa lafiya a 2026, kuma nawa aka kashe?", True)])
def test_single_part_questions_skip_the_model_check(q, want) -> None:
    assert ag.is_multi_part(ag.Plan(q, [], []), q) is want


def test_a_mismatch_is_redone_with_the_missing_part_and_a_leftover_is_said() -> None:
    plan = _plan_asking("sub_agency", "011100100100")
    first = _answer_with([_line("011100000000", "budget-2026-approved", 2026)])
    first.text = "parent figure\n\n📄 *Sources:* x"
    fixed = _answer_with([_line("011100100100", "budget-2026-approved", 2026)])
    fixed.text = "own figure\n\n📄 *Sources:* x"
    calls = []

    async def redo(focus=None):
        calls.append(focus)
        return fixed
    a = asyncio.run(ag.completed(first, "q", plan, "en", None, make_settings(), redo))
    assert calls == [["Government House", "011100100100"]] and a is fixed and "not Government House" not in a.text

    async def still(focus=None):
        return first
    a = asyncio.run(ag.completed(first, "q", plan, "en", None, make_settings(), still))
    assert "The row found is the ministry total (011100000000), not Government House (011100100100) on its own." \
           in a.text and a.partial
    assert a.text.index("The row found") < a.text.index("📄")


def test_the_redo_reads_the_same_hits_when_the_missing_part_is_already_among_them(monkeypatch) -> None:
    hits = [_line("011100100100", "budget-2026-approved", 2026).line]
    monkeypatch.setattr(ag, "search_lines", lambda conn, terms, **kw: list(hits))     # nothing new
    plan = ag.Plan("q", [], [], line_search={"terms": ["x"], "years": [2026]})
    same = asyncio.run(ag._focused_lines(None, plan, make_settings(), hits, ["Government House"], None))
    assert same is hits
    new = _line("011100200100", "budget-2026-approved", 2026).line
    new.id = 2
    monkeypatch.setattr(ag, "search_lines", lambda conn, terms, **kw: [new])
    merged = asyncio.run(ag._focused_lines(None, plan, make_settings(), hits, ["Government House"], None))
    assert [x.id for x in merged] == [2, 1]                                   # the missing part's rows first


def test_crops_render_once_and_are_sent_only_if_still_cited(monkeypatch) -> None:
    from app.evidence import crops
    crops._cache.clear()
    made = []

    async def fake(req, settings):
        made.append(req.figure)
        return b"jpeg"
    monkeypatch.setattr(crops, "_make_crop", fake)
    req = crops.CropRequest(1, "budget-2026-approved", "t", 16, "460,480,000.00")
    s = make_settings()
    assert asyncio.run(crops.make_crop(req, s)) == b"jpeg" and asyncio.run(crops.make_crop(req, s)) == b"jpeg"
    assert made == ["460,480,000.00"]                                        # rendered once
    # the final answer no longer cites that row: plan_crops on it plans nothing, so nothing cached is sent
    assert crops.plan_crops(ag.Answer("no figures", True, True), 2) == []


def test_the_period_parsed_in_code_pins_the_need_quarter() -> None:
    plan = _plan_asking("mda", "025300000000")
    plan.need.time = {"kind": "year", "year": 2025}            # the planner read 'January to September' as the year
    ag.pin_quarter(plan, 3, 2025)
    assert plan.need.time == {"kind": "quarter", "year": 2025, "quarter": 3}
    plan.need.time = {"kind": "quarter", "year": 2025, "quarter": 2}    # the planner's own quarter stays
    ag.pin_quarter(plan, 3, 2025)
    assert plan.need.time["quarter"] == 2
    plan.need.time = {"kind": "range", "from": 2024, "to": 2025}        # so does a range of years
    ag.pin_quarter(plan, 3, 2025)
    assert plan.need.time["kind"] == "range"


def test_a_structured_answer_for_another_period_is_dropped() -> None:
    q = "How much did the Ministry of Lands and Housing spend from January to September 2025?"
    plan = _plan_asking("mda", "025300000000")
    plan.english_question = q

    def from_report(doc):
        return ag.Answer("t", True, True, cited=[ag.Evidence(1, doc, "BIR", 2025, 18, "text",
                                                             "025300000000 Min of Lands and Housing | 51,920")])
    assert [m.kind for m in ag.structured_mismatch(from_report("bir-2025-q4"), plan, q)] == ["period"]
    assert ag.structured_mismatch(from_report("bir-2025-q3"), plan, q) == []


def test_a_revenue_narrative_question_reads_the_rows_and_pages_not_the_fixed_summary() -> None:
    q = "What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?"
    assert ag.revenue_rows_needed(q, ag.Plan(q, [], []))
    q2 = "What was the state's total revenue in 2025?"
    assert not ag.revenue_rows_needed(q2, ag.Plan(q2, [], []))


def test_a_narrative_question_reads_the_whole_page_else_the_hits_and_their_neighbours() -> None:
    assert ag.page_chunks_wanted([0], whole=False) == [0, 1]
    assert ag.page_chunks_wanted([2, 5], whole=False) == [1, 2, 3, 4, 5, 6]
    assert ag.page_chunks_wanted([0], whole=True) is None


def test_the_reader_level_labels_echoed_in_a_summary_become_plain_words() -> None:
    s = "It expects ₦100.00 million in 2026. This is the ministry total including its agencies."
    assert ag.plain_level_words(s, "en") == "It expects ₦100.00 million in 2026. This is the ministry's total, " \
                                            "its agencies included."
    assert "one agency or unit" not in ag.plain_level_words("the 'one agency or unit' line", "en")
    assert "all spending (total)" not in ag.plain_level_words("Wannan all spending (total) ne", "ha")
    assert ag.plain_level_words("No label here: ₦5.00 billion", "en") == "No label here: ₦5.00 billion"


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT 1 FROM budget_lines WHERE doc_id = 'budget-2026-approved' LIMIT 1").fetchone():
            pytest.skip("budget_lines not indexed")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_a_named_project_is_its_own_line_but_a_kind_of_spending_is_not(conn) -> None:
    from app.retrieval.line_search import project_named
    assert "Peugout 406" in project_named(conn, "Procurment of 5n0 peugout 406 saloon for members and secretary")
    assert project_named(conn, "purchase of motor vehicles") is None       # also an economic line: a kind
    assert project_named(conn, "construction of roads") is None            # a third of any road's name
    assert project_named(conn, "provision of drugs") is None
