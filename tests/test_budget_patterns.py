"""General answer patterns from the Oct 31 phone test (budget questions): revenue questions reach the rows they
name, a named period beats the newest report, projects are found by fuzzy names, narrative questions read the
narrative, not-found names the nearest published figure, every part is answered, Hausa letters stay Latin, table
names lose footnote digits, long replies split instead of being cut, duplicates are dropped, and budget answers
lead with one plain sentence."""

from datetime import date

import pytest

from app.agent import answer as ag
from app.agent.periods import Period, asked_period, report_for


def _plan(q: str, **kw) -> ag.Plan:
    return ag.Plan(english_question=q, search_queries=[q], doc_ids=kw.pop("doc_ids", []), **kw)


# --- 1. revenue: the statewide summary only for the statewide picture -----------------------------------------

@pytest.mark.parametrize("q", ["How much revenue does Sokoto State expect in 2026?",
                               "What is the state's IGR in 2026?", "Nawa jiha ke sa ran samu a 2026?"])
def test_the_statewide_revenue_picture_keeps_the_summary(q) -> None:
    assert ag.statewide_revenue(q, _plan(q))


@pytest.mark.parametrize("q", ["How much revenue does the Ministry of Lands expect to collect in 2026?",
                               "How much does the 2026 budget expect from the World Bank for ACRESAL?",
                               "What grants from UNICEF are in the 2025 budget?",
                               "What share of total revenue in 2026 comes from FAAC?",
                               "Which MDA generates the most independent revenue?",
                               "How much is expected from land use charges in 2026?",
                               "Nawa hukumar tara haraji ta samu a 2025?"])
def test_a_named_agency_donor_line_or_calculation_searches_the_rows(q) -> None:
    assert not ag.statewide_revenue(q, _plan(q))


def test_the_revenue_rows_search_reads_revenue_rows_with_their_tables() -> None:
    plan = _plan("World Bank grant for ACRESAL in 2026", key_terms=["ACRESAL", "World Bank"])
    ls = ag.revenue_rows_search(plan, "World Bank grant for ACRESAL in 2026")
    assert ls["spend"] == "revenue" and ls["terms"][:2] == ["ACRESAL", "World Bank"]
    assert {"Capital Receipts", "Aid and Grants", "Independent Revenue"} <= set(ls["terms"])
    assert ls["years"] == [2026]


# --- 2. the period asked beats the newest report ---------------------------------------------------------------

@pytest.mark.parametrize("q,want", [
    ("How much had the Ministry of Health spent in Q1-Q2 2026?", Period(2026, 2)),
    ("Capital spending in the first half of 2026", Period(2026, 2)),
    ("What was released by the end of Q2?", Period(None, 2)),
    ("Spending from January to September 2025", Period(2025, 3)),
    ("By the end of the third quarter of 2025, how much was spent?", Period(2025, 3)),
    ("Q1 2026 performance of the Ministry of Water Resources", Period(2026, 1)),
    ("Nawa aka kashe a rabin shekara na farko na 2026?", Period(2026, 2)),
    ("How much has been spent so far this year?", None),
    ("What is the latest spending on education?", None)])
def test_the_period_a_question_names(q, want) -> None:
    assert asked_period(q) == want


class Conn:
    """perf_items: (doc_id, year, max quarter)."""
    def __init__(self):
        self.reports = [("bir-2026-q2", 2026, 2), ("bir-2026-q1", 2026, 1), ("bir-2025-q4", 2025, 4),
                        ("bir-2025-q3", 2025, 3)]

    def execute(self, sql, args=()):
        rows = []
        if "HAVING max(quarter)" in sql:
            rows = [(d, y) for d, y, q in self.reports if q == args[0]]
        elif "doc_id <> %s" in sql:
            rows = [(d,) for d, y, q in self.reports if y == args[0] and d != args[1]]

        class R:
            def fetchall(self):
                return rows
        return R()

    def rollback(self):
        pass


def test_a_named_period_reads_its_report_and_leaves_the_newer_one_out() -> None:
    conn = Conn()
    assert report_for(conn, Period(2026, 1)) == ("bir-2026-q1", 2026)
    assert report_for(conn, Period(None, 3)) == ("bir-2025-q3", 2025)          # the latest year with a Q3 report
    plan = _plan("How much had the Ministry of Health spent by the end of Q1 2026?",
                 doc_ids=["bir-2026-q2", "budget-2026-approved"], latest={"series": "sokoto_bir"},
                 analysis={"tool": "revenue"})
    ag.apply_period(conn, plan, plan.english_question, date(2026, 10, 31))
    assert plan.period_doc == "bir-2026-q1" and plan.skip_docs == ["bir-2026-q2"]
    assert plan.doc_ids == ["bir-2026-q1", "budget-2026-approved"] and plan.latest == {}
    assert plan.analysis["report"] == "bir-2026-q1"


def test_latest_or_no_period_changes_nothing() -> None:
    plan = _plan("What is the latest capital spending?", doc_ids=["bir-2026-q2"], latest={"series": "sokoto_bir"})
    ag.apply_period(Conn(), plan, plan.english_question, date(2026, 10, 31))
    assert plan.period_doc == "" and plan.latest and plan.doc_ids == ["bir-2026-q2"]
