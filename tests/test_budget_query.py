"""query_budget: document choice, hierarchy, arithmetic; and the real rows when the dev database is up."""

from decimal import Decimal

import pytest

from app.agent import budget_query as bq
from app.agent.budget_query import Item, ItemResult, Picked, _contains, _doc_rank, run_budget_query


def test_document_choice_follows_where_each_figure_is_authoritative() -> None:
    approved = Item("x", year=2025, measure="approved")
    docs = [("sokoto_budget", "2026"), ("sokoto_budget", "2025"), ("sokoto_bir", "2025-Q4")]
    assert min(docs, key=lambda d: _doc_rank(approved, *d)) == ("sokoto_budget", "2025")
    revised = Item("x", year=2025, measure="revised")
    assert min(docs, key=lambda d: _doc_rank(revised, *d)) == ("sokoto_budget", "2026")
    final = Item("x", year=2025, measure="final")
    docs += [("sokoto_bir", "2025-Q2")]
    assert min(docs, key=lambda d: _doc_rank(final, *d)) == ("sokoto_bir", "2025-Q4")


def test_hierarchy_of_administrative_codes() -> None:
    assert _contains("056900000000", "056900400100")            # a university inside its ministry
    assert not _contains("056900400100", "056900000000")
    assert not _contains("052100000000", "056900400100")


def P(amount: str, code: str = "7094", page: int = 1) -> Picked:
    return Picked("d", "Doc", page, "t", code, "n", "2026 Approved Budget", Decimal(amount), "row")


def run_ops(monkeypatch, op: str, totals: list[str]):
    results = iter([ItemResult(Item(f"i{i}"), [P(t, code=f"70{i}")]) for i, t in enumerate(totals)])
    monkeypatch.setattr(bq, "run_item", lambda conn, it: next(results))
    return run_budget_query(None, {"operation": op, "items": [{"label": f"i{i}"} for i in range(len(totals))]})


def test_compare_total_share_are_exact(monkeypatch) -> None:
    q = run_ops(monkeypatch, "compare", ["20666975000.00", "7824339750.89"])
    assert q.difference == Decimal("12842635249.11") and q.change_pct == Decimal("164.1")
    assert "12,842,635,249.11" in q.computed_numbers() and "164.10" in q.computed_numbers()
    assert run_ops(monkeypatch, "total", ["1.10", "2.20"]).total == Decimal("3.30")
    assert run_ops(monkeypatch, "share", ["25", "200"]).share_pct == Decimal("12.5")


def test_bad_spec_is_safe() -> None:
    it = Item.from_dict({"label": "x", "year": "20x6", "codes": ["7094", "DROP TABLE"], "units": ["a"] * 50})
    assert it.year is None and it.codes == ["7094"] and len(it.units) == bq.MAX_UNITS


# --- the real rows (dev database with the indexed budgets) -----------------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT to_regclass('budget_rows')").fetchone()[0] or \
                not c.execute("SELECT 1 FROM budget_rows WHERE doc_id = 'budget-2026-approved' LIMIT 1").fetchone():
            pytest.skip("budget_rows not indexed")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_tertiary_capital_2026_vs_2025(conn) -> None:
    q = run_budget_query(conn, {"operation": "compare", "items": [
        {"label": "2026", "classification": "function", "spend_kind": "capital", "year": 2026, "names": ["tertiary education"]},
        {"label": "2025", "classification": "function", "spend_kind": "capital", "year": 2025, "names": ["tertiary education"],
         "alt_measure": "revised"}]})
    a, b = q.items
    assert (a.rows[0].doc_id, a.rows[0].page, a.rows[0].code, a.rows[0].amount) == \
        ("budget-2026-approved", 38, "7094", Decimal("20666975000.00"))            # 7094, not 70941/70942
    assert (b.rows[0].doc_id, b.rows[0].page, b.rows[0].amount) == ("budget-2025-approved", 22, Decimal("7824339750.89"))
    assert (b.alt.doc_id, b.alt.amount) == ("budget-2026-approved", Decimal("6707032782.20"))
    assert q.difference == Decimal("12842635249.11") and q.change_pct == Decimal("164.1")


def test_ranking_lists_ministries_not_sectors(conn) -> None:
    q = run_budget_query(conn, {"operation": "rank", "top": 3, "items": [
        {"label": "x", "classification": "administrative", "spend_kind": "capital", "year": 2026}]})
    assert q.ranking[0].name == "Ministry of Health" and all(not p.code.endswith("0" * 10) for p in q.ranking)


def test_units_inside_a_picked_ministry_are_not_counted_twice(conn) -> None:
    q = run_budget_query(conn, {"operation": "total", "items": [{
        "label": "x", "classification": "administrative", "spend_kind": "total", "year": 2026,
        "units": ["Ministry for Higher Education", "Sokoto State University", "No Such Agency"]}]})
    r = q.items[0]
    assert [p.code for p in r.rows] == ["056900000000"] and r.included == {"Sokoto State University": "Ministry for Higher Education"}
    assert r.missing == ["No Such Agency"] and not q.complete


def test_unit_names_match_by_meaningful_words() -> None:
    m = bq._unit_matches
    assert m("State Polytechnic", "Umaru Ali Shinkafi Polytechnic Sokoto")
    assert m("Colleges of Education", "Shehu Shagari Collage of Education Sokoto")      # plural and misprint
    assert m("Ministry for Higher Education", "Ministry for Higher Education")
    assert not m("Ministry headquarters", "Ministry for Higher Education")
    assert not m("Sokoto State", "Ministry of Health")                                   # only filler words


def test_every_college_counts_once(conn) -> None:
    q = run_budget_query(conn, {"operation": "total", "items": [{
        "label": "x", "classification": "administrative", "spend_kind": "total", "year": 2026,
        "units": ["State Polytechnic", "Colleges of Education"]}]})
    r = q.items[0]
    names = [p.name for p in r.rows]
    assert any("Polytechnic" in n for n in names) and any("Coll" in n for n in names) and not r.missing
    assert len({p.code for p in r.rows}) == len(r.rows)


# --- fix 1: no substitution, no double counting, LGAs are not institutions located in them --------------

def MoW(page: int = 26) -> Picked:
    return Picked("budget-2026-approved", "Budget", page, "t", "023400000000", "Ministry of Works", "2026 Approved Budget",
                  Decimal("58129741319.77"), "row")


def test_same_row_found_by_three_items_is_added_once(monkeypatch) -> None:
    results = iter([ItemResult(Item(f"i{i}"), [MoW()]) for i in range(3)])
    monkeypatch.setattr(bq, "_run_item", lambda conn, it: next(results))
    q = run_budget_query(None, {"operation": "total", "items": [{"label": "flyovers"}, {"label": "dualisation"},
                                                                {"label": "feeder roads"}]})
    assert q.total == Decimal("58129741319.77")                    # m12 had added it three times (174.39 bn)
    text = bq.render_working(q, {("budget-2026-approved", 26): 1}, "en")
    assert text.count("same row as above, counted once") == 2


def test_ministry_total_for_a_specific_item_is_a_container(monkeypatch) -> None:
    moh = Picked("budget-2026-approved", "Budget", 27, "t", "052100000000", "Ministry of Health", "2026 Approved Budget",
                 Decimal("104644218330.85"), "row")
    monkeypatch.setattr(bq, "_run_item", lambda conn, it: ItemResult(it, [moh]))
    q = run_budget_query(None, {"operation": "lookup", "items": [{"label": "drugs", "topic": "drugs and hospital equipment",
                                                                 "classification": "administrative"}]})
    assert q.items[0].container and not q.complete
    text = bq.render_working(q, {("budget-2026-approved", 27): 1}, "en")
    assert "the budget doesn't show drugs and hospital equipment separately" in text and "Ministry of Health" in text
    # a topic the row really is stays a normal answer
    tert = Picked("d", "B", 38, "t", "7094", "TERTIARY EDUCATION", "2026 Approved Budget", Decimal("1"), "row")
    monkeypatch.setattr(bq, "_run_item", lambda conn, it: ItemResult(it, [tert]))
    q = run_budget_query(None, {"operation": "lookup", "items": [{"label": "x", "topic": "tertiary education"}]})
    assert not q.items[0].container and q.complete


def test_containers_are_never_compared_or_added(monkeypatch) -> None:
    monkeypatch.setattr(bq, "_run_item", lambda conn, it: ItemResult(it, [MoW()]))
    q = run_budget_query(None, {"operation": "compare", "items": [
        {"label": "a", "topic": "flyovers", "container": True}, {"label": "b", "topic": "feeder roads", "container": True}]})
    assert q.difference is None and q.total is None


def test_an_institution_in_an_lga_is_not_the_lga_allocation(monkeypatch) -> None:
    hosp = Picked("d", "B", 18, "t", "052104100100", "Orthopedic Hospital Wamakko", "2026 Approved Budget", Decimal("1.00"), "row")
    monkeypatch.setattr(bq, "_run_item", lambda conn, it: ItemResult(it, [hosp]))
    q = run_budget_query(None, {"operation": "lookup", "items": [{"label": "Wamakko LGA", "names": ["Wamakko"],
                                                                 "classification": "administrative"}]})
    r = q.items[0]
    assert r.rows == [] and r.located_in == ["Wamakko"] and not q.complete
    text = bq.render_working(q, {}, "en")
    assert "not an allocation to Wamakko LGA" in text and "Orthopedic" not in text
