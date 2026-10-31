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


# --- 3. projects named: found by fuzzy name before 'not found' ------------------------------------------------

@pytest.mark.parametrize("q,want", [
    ("How much is budgeted for Construction of Offa Road in Sokoto Metropolis in 2026?",
     "Construction of Offa Road in Sokoto Metropolis"),
    ("How much was spent on constraction of water supply at Rugar Liman by Q2 2026?",
     "constraction of water supply at Rugar Liman"),
    ("What about the Rehabilitation and Upgrading of Specialist Hospital?",
     "Rehabilitation and Upgrading of Specialist Hospital"),
    ("How much for health in 2026?", None)])
def test_the_project_a_question_names(q, want) -> None:
    from app.retrieval.line_search import project_phrases
    got = project_phrases(q)
    assert (got[0] if got else None) == want


def test_misspelt_project_names_are_found_in_the_project_lists() -> None:
    import psycopg

    from app.config import get_settings
    from app.retrieval.line_search import project_lines
    try:
        conn = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except Exception:
        pytest.skip("no database")
    with conn:
        if not conn.execute("SELECT 1 FROM budget_lines WHERE doc_id = 'budget-2026-approved' LIMIT 1").fetchone():
            pytest.skip("no 2026 budget lines")
        got = project_lines(conn, "constraction of water supply at rugar liman", years=[2026])
        assert any("Rugar Liman" in x.name and x.cells for x in got)


# --- 4. narrative questions read the narrative ------------------------------------------------------------------

@pytest.mark.parametrize("q,want", [
    ("What did the Q2 2026 report say was corrected in the revenue figures?", True),
    ("What reasons does the BIR give for the low capital performance?", True),
    ("What explanation was noted for the variance in personnel costs?", True),
    ("Me ya sa aka samu ƙarancin kashe kuɗi a manyan ayyuka?", True),
    ("How much was allocated to health in 2026?", False),
    ("What is the percentage change in education between 2025 and 2026?", False)])
def test_narrative_questions(q, want) -> None:
    assert ag.narrative_asked(_plan(q, original=q)) is want


def test_prose_search_leaves_out_table_rows() -> None:
    import psycopg

    from app.config import get_settings
    from app.retrieval.search import search
    try:
        conn = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except Exception:
        pytest.skip("no database")
    with conn:
        hits = search(conn, "capital expenditure performance reasons", k=6, prose=True)
        if not hits:
            pytest.skip("no indexed narrative")
        assert all(not h.text.startswith("[Table:") and " | " not in h.text for h in hits)


# --- 8. names: no footnote digits, no internal labels in the reply ------------------------------------------------

@pytest.mark.parametrize("raw,want", [("Normadic Education1", "Normadic Education"), ("Height-for-age1", "Height-for-age"),
                                      ("Q4 Performance", "Q4 Performance"), ("COVID19 Response", "COVID19 Response"),
                                      ("SDG4 Unit", "SDG4 Unit")])
def test_footnote_digits_are_stripped_from_names(raw, want) -> None:
    from app.agent.line_answer import clean_name
    assert clean_name(raw) == want


def test_the_reply_shows_plain_names_and_the_working_keeps_the_labels() -> None:
    from app.agent.line_answer import plain_label
    from app.retrieval.line_search import Line
    x = Line(1, "Budget 2026", "budget-2026-approved", 16, "Total Expenditure by Administrative Classification",
             "Agency for Normadic Education1", "Agency for Normadic Education1 | 2026: 5", "administrative", "", "", 0.0,
             code="051700300100")
    assert plain_label(x) == "Agency for Normadic Education"
    assert "one agency or unit" not in plain_label(x) and "code" not in plain_label(x)
    cap = Line(2, "Budget 2026", "budget-2026-approved", 30, "Capital Expenditure by Administrative Classification",
               "Ministry of Health", "Ministry of Health | 2026: 9", "administrative", "", "", 0.0, code="052100000000",
               spend_kind="capital")
    assert plain_label(cap) == "Ministry of Health (capital)" and plain_label(cap, "ha").endswith("(manyan ayyuka)")


# --- 5. not published: the nearest figure that is -------------------------------------------------------------

def test_a_headcount_question_also_searches_the_agencys_personnel_rows() -> None:
    q = "How many staff does the Ministry of Health employ?"
    plan = _plan(q)
    lines = ag.with_nearest_terms(plan, q, {"terms": ["Ministry of Health"], "years": [2026]})
    assert {"Personnel", "Salaries and Wages"} <= set(lines["terms"]) and lines["terms"][0] == "Ministry of Health"
    assert any(s.startswith("Personnel Expenditure") for s in plan.search_queries)
    other = ag.with_nearest_terms(_plan("Health budget 2026"), "Health budget 2026", {"terms": ["Health"]})
    assert other == {"terms": ["Health"]}


def test_both_prompts_say_not_published_and_give_the_nearest() -> None:
    from app.agent.line_answer import SELECT_SYSTEM
    assert "isn't published in these documents" in ag.ANSWER_SYSTEM
    assert "don't publish it" in SELECT_SYSTEM and "personnel (salaries) line" in SELECT_SYSTEM
