"""Wide search over budget lines (app/retrieval/line_search.py)."""

from decimal import Decimal

import pytest

from app.retrieval import tables
from app.retrieval.line_search import Line, groups, ministry_of, search_lines

TITLE = "Capital Expenditure by Project"


def test_one_id_per_printed_line_in_reading_order() -> None:
    a = tables.rows_from_page(67, "Counterpart Funds for BHCBF | 2025 Revised Budget: 70,000,000.00 | 2026 Approved Budget: 70,000,000.00", TITLE)
    b = tables.rows_from_page(67, "Learn to Read Project | 2026 Approved Budget: 100.00", TITLE)
    ids = tables.line_ids("budget-2026-approved", a + b)
    assert [v[0] for v in ids.values()] == ["budget-2026-approved:67:1", "budget-2026-approved:67:2"]


def test_fragment_named_lines_that_differ_only_in_their_place_are_all_kept(conn) -> None:
    """Project rows printed without their title differ only in the LGA at the end of the name; the per-document
    copy limit must not treat them as copies (m05: the Wamakko NGN 10 bn line was dropped)."""
    hits = search_lines(conn, ["medical equipment", "Ministry of Health"], years=[2026], spend="expenditure")[:40]
    places = {x.name.rsplit(" - ", 1)[-1] for x in hits
              if x.doc_id == "budget-2026-approved" and x.name.startswith("Ministry of Health 23010122")}
    assert {"WAMAKKO", "BINJI", "TAMBUWAL", "SABON BIRNI"} <= places


def test_meaning_search_finds_a_line_by_what_it_is(conn) -> None:
    from app.retrieval.line_search import nearest
    if not conn.execute("SELECT 1 FROM budget_lines WHERE embedding IS NOT NULL LIMIT 1").fetchone():
        pytest.skip("line vectors not built")
    (near,) = nearest(conn, ["persons with disabilities"], years=[2026], docs=["budget-2026-approved"])
    names = list(dict.fromkeys(x.name.lower() for x in near))[:5]
    assert any("disabilit" in n for n in names)
    (ict,) = nearest(conn, ["ICT"], years=[2026], docs=["budget-2026-approved"])
    assert "information communication and technology" in [" ".join(x.name.lower().split()) for x in ict][:40]


def test_ministry_of_a_project_line() -> None:
    line = Line("x", "t", "d", 67, TITLE, "Counterpart Funds", "Counterpart Funds for BHCBF- EMT 052100100100 - Ministry "
                "of Health 23050103 - MONITORING | 2026 Approved Budget: 70,000,000.00", "project", "", "", 1.0)
    assert ministry_of(line) == "Ministry of Health"
    assert groups([line, line]) == [("Ministry of Health", 2)]


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT to_regclass('budget_lines')").fetchone()[0] or \
                not c.execute("SELECT 1 FROM budget_lines LIMIT 1").fetchone():
            pytest.skip("budget_lines not indexed")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_m06_bhcpf_counterpart_is_the_top_hit_despite_the_spelling(conn) -> None:
    hits = search_lines(conn, ["BHCPF", "Basic Health Care Provision Fund", "counterpart funds", "routine immunization"],
                        year=2026)
    top = hits[0]
    assert (top.doc_id, top.page) == ("budget-2026-approved", 67) and "BHCBF" in top.name
    assert top.cell("2026 Approved Budget").amount == Decimal("70000000.00")


def test_year_filter_and_empty_terms(conn) -> None:
    assert search_lines(conn, ["", "x"]) == []                  # too short to search
    hits = search_lines(conn, ["tertiary education"], year=2026, limit=20)
    assert hits and all(any(c.year == 2026 for c in h.cells) for h in hits)


def test_page_search_gets_the_printed_rows_its_key_terms_name(conn) -> None:
    # m37: page search took p16; the ministry's 2026 total is on p17. m16: the 2026 IGR target row (p1).
    from app.agent.answer import Plan, line_evidence
    ict = line_evidence(conn, Plan("ICT and Innovation totals in 2025 and 2026", [], ["budget-2025-approved",
                                   "budget-2026-approved"], key_terms=["ICT", "Innovation", "Total Expenditure"]), [])
    assert ("budget-2026-approved", 17) in {(e.doc_id, e.page) for e in ict}
    igr = line_evidence(conn, Plan("IGR target for 2026", [], ["budget-2026-approved"],
                                   key_terms=["Independent Revenue"]), [])
    assert igr and igr[0].doc_id == "budget-2026-approved" and "INDEPENDENT REVENUE" in igr[0].text


def test_an_acronym_gets_the_budgets_own_expansion_last(monkeypatch) -> None:
    from app.retrieval import line_search as ls
    assert ls.initials("Information Communication and Technology - General") == "ICT"
    monkeypatch.setattr(ls, "_initials_cache", {"ICT": ["Information Communication and Technology"],
                                                 "LGA": ["Local Government Audit"]})
    terms = ["ICT and Innovation", "Total Expenditure"]
    assert ls.expand_acronyms(None, terms) == terms + ["Information Communication and Technology"]
    full = [f"term {i}" for i in range(ls.MAX_TERMS - 1)] + ["LGA projects"]
    assert ls.expand_acronyms(None, full) == full                  # no room: the planner's terms stay
    assert ls.expand_acronyms(None, ["LGA projects"])[-1] == "Local Government Audit"     # room: added last
