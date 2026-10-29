"""Structured budget core: entities built from the extraction, and their reconciliation (app/retrieval/entities.py)."""

from decimal import Decimal

import pytest

from app.retrieval import entities as ent

HEADER = ("Sokoto State Government 2026 Approved Budget - Capital Expenditure by Project Project Name Administrative "
          "Code and Description Economic Code and Description Function Code and Description Location Code and "
          "Description 2024 Full Year Actuals 2025 Revised Budget 2025 Performance January to September 2026 "
          "Approved Budget 2027 Out-Year Estimate 2028 Out-Year Estimate 2026 Nutrition Tagging Total Capital "
          "Expenditure 0.00 400,000,000.00 0.00 1,000,000,000.00 0.00 0.00 0.00\n")
# real row shapes from the 2026 budget: a wrapped name, and a function name glued to the location code (p65)
ROWS = ("Completion of 2 Storey building of 6 Classrooms\nat GDSS Tambuwal 051700100100 - Ministry for Basic Education "
        "23020107 - CONSTRUCTION / PROVISION OF PUBLIC SCHOOLS 70922 - UPPER-SECONDARY EDUCATION33331800 - TAMBUWAL "
        "- 300,000,000.00 - 750,000,000.00 - - -\n"
        "Rehabilitation of GDSS Mabera 051700100100 - Ministry for Basic Education 23030106 - REHABILITATION / "
        "REPAIRS - PUBLIC SCHOOLS 70922 - UPPER-SECONDARY EDUCATION 33342400 - State Wide - 100,000,000.00 - "
        "250,000,000.00 - - -\n")


def test_columns_are_named_by_year_and_measure_as_printed() -> None:
    assert ent.column_of(2025, "actual", "jan_sep") == "jan_sep_2025"
    assert ent.column_of(2024, "actual", "full_year") == "actual_2024"
    assert ent.column_of(2026, "approved", "full_year") == "approved_2026"
    assert ent.column_of(2026, "actual", "q1") is None             # a report's quarter: perf_items, not here


def test_projects_are_parsed_by_their_code_anchors() -> None:
    projects, info = ent.parse_projects([(49, HEADER + ROWS)])
    assert [p.name for p in projects] == ["Completion of 2 Storey building of 6 Classrooms at GDSS Tambuwal",
                                          "Rehabilitation of GDSS Mabera"]
    a = projects[0]
    assert (a.mda_code, a.econ_code, a.function_code, a.location_code, a.location_name) == \
        ("051700100100", "23020107", "70922", "33331800", "TAMBUWAL")
    assert a.amounts["revised_2025"] == Decimal("300000000.00") and a.amounts["approved_2026"] == Decimal("750000000.00")
    assert a.amounts["jan_sep_2025"] == 0
    assert info["printed"]["approved_2026"] == "1000000000.00" and info["unparsed"] == 0


def test_the_list_ends_at_the_next_table_and_sector_lists_are_not_read_twice() -> None:
    sector = ("Sokoto State Government 2026 Approved Budget - Basic Education Capital Expenditure by Project " + ROWS)
    nxt = "Sokoto State Government 2026 Approved Budget - Basic Education Expenditure by Economic Classification " + ROWS
    projects, info = ent.parse_projects([(48, sector), (49, HEADER + ROWS), (50, ROWS), (76, nxt)])
    assert len(projects) == 4 and info["pages"] == [49, 50]


class FakePositions:
    """Right edges of numbers as printed: columns end at 100, 200, ..., 700 points."""
    def __init__(self, where: dict[str, list[float]]):
        self.where = where

    def x(self, flat, token, at):
        k = flat[:at].split().count(token)
        xs = self.where.get(token, [])
        return xs[k] if k < len(xs) else None


def test_a_row_with_blank_cells_is_placed_by_where_its_number_is_printed() -> None:
    # 2026 budget p51: "... 33312100 - WAMAKKO - - 7,300,000,000.00 -": 4 tokens for 7 columns
    flat = ("A 016100100100 - SSG'S Office 23020101 - CONSTRUCTION 70111 - EXECUTIVE 33312100 - WAMAKKO "
            "- 1.00 2.00 3.00 4.00 5.00 - "
            "B 016100100100 - SSG'S Office 23020101 - CONSTRUCTION 70111 - EXECUTIVE 33312100 - WAMAKKO "
            "- - 7,300,000,000.00 -")
    pos = FakePositions({"1.00": [200], "2.00": [300], "3.00": [400], "4.00": [500], "5.00": [600],
                         "7,300,000,000.00": [401]})
    full, short = list(ent.PROJECT.finditer(flat))
    placed = ent.place_by_position(pos, flat, [full], [short], 7)
    assert placed == {short.start(): {3: "7,300,000,000.00"}}          # the 2026 approved column


def test_administrative_parents_are_fixed_levels_not_trailing_zeros() -> None:
    codes = {"010000000000", "017000000000", "017200000000", "017000100100", "017200100100"}
    assert ent.parent_code("017200100100", codes) == "017200000000"
    assert ent.parent_code("017000100100", codes) == "017000000000"
    assert ent.parent_code("017200000000", codes) == "010000000000"     # not "0170...", a ministry, not a sector
    assert ent.parent_code("70631", {"7063", "706", "70631"}) == "7063"


def item(code, name, kind="total", cls="administrative", title="T", **amounts) -> ent.Item:
    return ent.Item(f"d:1:{code or name}", 1, 0, title, cls, kind, code, name,
                    {k: Decimal(v) for k, v in amounts.items()})


def test_children_must_add_up_to_their_parent() -> None:
    rows = [item(None, "Total Expenditure", approved_2026="30"), item("010000000000", "Administration Sector",
            approved_2026="30"), item("011100000000", "Government House", approved_2026="30"),
            item("011100100100", "Government House", approved_2026="10"),
            item("011103300100", "SOSACAT", approved_2026="20")]
    checks = ent.Checks()
    ent.check_hierarchy(rows, ("approved_2026",), checks)
    assert checks.results["hierarchy:administrative"] == {"passed": 2, "failed": 0, "examples": []}
    rows[-1].amounts["approved_2026"] = Decimal("25")          # more than the ₦1 rounding tolerance
    checks = ent.Checks()
    ent.check_hierarchy(rows, ("approved_2026",), checks)
    assert checks.results["hierarchy:administrative"]["failed"] == 1


def test_a_table_starting_at_its_total_row_takes_the_classification_of_its_title() -> None:
    cont = item("016100100100", "SSG'S Office", kind="capital", cls="other",
                title="Capital Expenditure (table starting at its Total row)")
    full = item("016700100100", "Ministry for Special Duties", kind="capital",
                title="Sokoto State Government 2026 Approved Budget - Capital Expenditure by Administrative Classification")
    loc = item("33331800", "TAMBUWAL", kind="capital", cls="function", title="Capital Expenditure by Functional")
    ent.classify([cont, full, loc])
    assert (cont.classification, loc.classification) == ("administrative", "location")


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT to_regclass('projects') IS NOT NULL AND EXISTS "
                         "(SELECT 1 FROM projects WHERE doc_id = 'budget-2026-approved')").fetchone()[0]:
            pytest.skip("structured core not built")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_2026_projects_reconcile_with_the_printed_capital_total(conn) -> None:
    """2026 budget p49: Total Capital Expenditure 553,343,592,103.46. One row (₦200 m) can't be placed."""
    total, n = conn.execute("SELECT sum(approved_2026), count(*) FROM projects WHERE doc_id = 'budget-2026-approved'"
                            ).fetchone()
    assert n > 1650 and Decimal("553143592103.46") <= total <= Decimal("553343592103.46")
    checks = conn.execute("SELECT checks FROM entity_builds WHERE doc_id = 'budget-2026-approved'").fetchone()[0]
    assert checks["kinds"]["failed"] == 0 and checks["projects:mda_capital"]["passed"] > 600


def test_ministry_of_health_projects_add_up_to_its_capital(conn) -> None:
    projects, capital = conn.execute(
        "SELECT (SELECT sum(approved_2026) FROM projects WHERE doc_id = 'budget-2026-approved' AND mda_code = "
        "'052100100100'), (SELECT approved_2026 FROM budget_items WHERE doc_id = 'budget-2026-approved' AND code = "
        "'052100100100' AND classification = 'administrative' AND spend_kind = 'capital' ORDER BY seq LIMIT 1)"
    ).fetchone()
    assert projects == capital == Decimal("92523418285.85")


def test_per_agency_economic_rows_belong_to_their_agency(conn) -> None:
    """The drugs line of the Ministry of Health's own economic table (the m05 category answer uses these)."""
    n = conn.execute("SELECT count(*) FROM budget_items WHERE doc_id = 'budget-2026-approved' AND code = '22020307' "
                     "AND mda_code LIKE '0521%%'").fetchone()[0]
    assert n >= 5
