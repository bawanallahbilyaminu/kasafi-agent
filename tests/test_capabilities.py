"""The capability catalog (data/catalog.yaml), cells from an information need, and the structured tools."""

from decimal import Decimal

from app.agent import answer as ans
from app.agent.capabilities import Cell, catalog, cover, match, required_cells
from app.agent.need import Entity, Need

ALL = {c.id for c in catalog()}
SBS = Entity("sub_agency", "State Bureau of Statistics", "State Bureau of Statistics", "023800400100")


def test_the_catalog_parses_and_structured_tools_come_first() -> None:
    ids = [c.id for c in catalog()]
    assert {"budget_core", "dtm_api", "topic_sweep", "page_search", "open_web_search"} <= set(ids)
    cell = Cell("idp_count", Entity("lga", "Sabon Birni", "Sabon Birni"), "lga")
    assert [c.id for c in match(cell, "rank", available=ALL)][0] == "dtm_api"
    assert "dtm_api" not in [c.id for c in match(cell, "rank", available=ALL - {"dtm_api"})]   # no key: not run


def test_a_sub_agency_split_with_quarter_spending_is_all_budget_core_cells() -> None:
    """h2-01's shape: personnel / overhead / capital of a sub-agency, revised and spent to Q2 2026."""
    need = Need("q", measures=["revised", "quarter_spent", "actual_ytd"], entities=[SBS],
                splits=["personnel", "overhead", "capital"], time={"kind": "quarter", "year": 2026, "quarter": 2},
                operation="breakdown")
    cov = cover(need, available=ALL)
    assert len(cov.cells) == 9 and cov.all_by("budget_core") and not cov.gaps


def test_lgas_ranked_by_idps_are_dtm_cells_and_a_town_level_measure_is_a_gap() -> None:
    need = Need("q", measures=["idp_count"], entities=[Entity("state", "Sokoto", "Sokoto")], geo_level="lga",
                operation="rank", top_n=5)
    assert cover(need, available=ALL).all_by("dtm_api")
    town = Need("q", measures=["idp_count"], entities=[Entity("state", "Sokoto")], geo_level="town")
    assert cover(town, available={"budget_core", "dtm_api"}).gaps          # no structured source has town figures
    assert cover(town, available=ALL).best() == "topic_sweep"              # the town survey (SBS/JIPS) may


def test_cells_cover_every_measure_split_and_year() -> None:
    need = Need("q", measures=["approved"], entities=[SBS], splits=["overhead"], time={"kind": "range", "from": 2025,
                                                                                       "to": 2026})
    need.operation = "compare"
    assert [(c.measure, c.split, c.year) for c in required_cells(need)] == [("approved", "overhead", 2025),
                                                                            ("approved", "overhead", 2026)]


def test_a_part_is_read_against_its_whole() -> None:
    need = Need("How much of its 2026 budget is capital?", measures=["approved"], entities=[SBS], splits=["capital"],
                time={"kind": "year", "year": 2026}, operation="lookup")
    assert [c.split for c in required_cells(need)] == ["capital", "total"]
    cells = [Cell("approved", SBS, "state", "capital", 2026, value=Decimal("30000000.00"), source="p. 25"),
             Cell("approved", SBS, "state", "total", 2026, value=Decimal("150000000.00"), source="p. 17")]
    text, exact = ans.write_budget_cells(need, cells, "en")
    assert "20.0% of its total (Kasafi's calculation)" in text and "share of total: 20.0%" in exact


def test_a_quarter_not_over_yet_is_answered_with_what_exists() -> None:
    from datetime import date
    q4 = Cell("actual_ytd", SBS, "state", "", 2026, 4)
    assert ans.not_yet_published(q4, date(2026, 10, 30))
    assert not ans.not_yet_published(Cell("actual_ytd", SBS, "state", "", 2026, 3), date(2026, 10, 30))  # may be out
    assert not ans.not_yet_published(Cell("approved", SBS, "state", "", 2027), date(2026, 10, 30))
    text, _ = ans.write_budget_cells(Need("q"), [q4], "en", _Conn())
    assert "the latest implementation report is Q2 2026" in text


def test_budget_cells_are_written_by_code_with_the_change_computed() -> None:
    gh = Entity("sub_agency", "Government House", "Government House", "011100100100")
    cells = [Cell("approved", gh, "state", "overhead", 2025, value=Decimal("4201809645.00"), source="2025 budget, p. 14"),
             Cell("approved", gh, "state", "overhead", 2026, value=Decimal("3712790422.00"), source="2026 budget, p. 21")]
    text, exact = ans.write_budget_cells(Need("q", operation="compare"), cells, "en")
    assert text.splitlines()[0] == "*Government House* (code 011100100100):"
    assert "2025 approved budget ₦4.20 billion; 2026 approved budget ₦3.71 billion; change -₦489.02 million (-11.6%)" in text
    assert "4,201,809,645.00" in exact and "3,712,790,422.00" in exact and "change: -489,019,223.00" in exact


def test_dtm_cells_rank_lgas() -> None:
    need = Need("q", measures=["idp_count"], geo_level="lga", operation="rank", top_n=2)
    cell = Cell("idp_count", Entity("state", "Sokoto"), "lga",
                value=[("Tangaza", 19151), ("Sabon Birni", 40729), ("Tambuwal", 17143)])
    text = ans.write_dtm_cells(need, [cell], "IOM DTM API (Baseline), Round 18, reporting date 2025-10-31", "en")
    assert text.splitlines() == ["By LGA (3 LGAs), the most:", "1. Sabon Birni: 40,729", "2. Tangaza: 19,151"]


def test_a_state_idp_figure_is_answered_side_by_side_unless_dtm_is_named() -> None:
    plan = ans.Plan("What is the current state of IDPs in Sokoto?", ["IDPs"], [], original="Yaya halin 'yan gudun hijira?")
    assert not ans.named_dtm(plan)
    plan = ans.Plan("How many IDPs are in Sokoto according to IOM?", ["IDPs"], [], original="IDPs according to IOM?")
    assert ans.named_dtm(plan)


class _Conn:
    """perf_items has 2026 up to Q2 only."""
    def execute(self, sql, params=()):
        q = 2 if "max(quarter)" in sql and params == (2026,) else None
        return type("R", (), {"fetchone": lambda _s: (q,)})()


def test_a_partial_structured_answer_names_each_missing_cell_with_what_exists() -> None:
    sbs = Entity("sub_agency", "State Bureau of Statistics", "State Bureau of Statistics", "023800400100")
    cells = [Cell("actual_ytd", sbs, "state", "personnel", 2026, 2, value=Decimal("22835577.27"), source="BIR Q2, p. 20"),
             Cell("actual_ytd", sbs, "state", "personnel", 2026, 3),
             Cell("approved", sbs, "state", "personnel", 2023)]
    text, _ = ans.write_budget_cells(Need("q"), cells, "en", _Conn())
    assert "• Personnel (salaries): spent so far (Q1–Q2) ₦22.84 million" in text
    assert "Not in the documents:" in text
    assert "State Bureau of Statistics Personnel (salaries) 2026 spent so far (Q1–Q3): the latest implementation " \
           "report is Q2 2026" in text
    assert "the 2023 budget isn't in the library (approved budgets: 2024–2026)" in text


def test_the_structured_partial_is_kept_unless_the_text_paths_answer_fully() -> None:
    held = ans.Answer("held", True, True, partial=True)
    assert ans.keep_better(ans.Answer("text", True, True), held).text == "text"
    assert ans.keep_better(ans.Answer("none", False, True), held).text == "held"
    assert ans.keep_better(ans.Answer("half", True, True, partial=True), held).text == "held"
    assert ans.keep_better(ans.Answer("none", False, True), None).text == "none"


def test_a_level_nothing_reports_is_a_coverage_gap_not_not_found() -> None:
    need = Need("q", measures=["idp_count"], geo_level="town", topics=["displacement_humanitarian"])
    gap = ans.level_gap(need, "en")
    assert gap.startswith("ℹ️ IDPs figures are published by LGA and statewide;") and "covers only Sokoto town" in gap
    assert ans.level_gap(Need("q", measures=["idp_count"], geo_level="lga", topics=["displacement_humanitarian"]),
                         "en") == ""


def test_the_time_budget_keeps_what_was_verified(monkeypatch) -> None:
    import asyncio
    held = ans.Answer("held partial", True, True, partial=True)

    async def slow(question, lang, conn, box=None, **kw):
        plan = ans.Plan("q", ["q"], [])
        plan.held = held
        box["plan"] = plan
        await asyncio.sleep(1)
    monkeypatch.setattr(ans, "_answer_question", slow)
    monkeypatch.setattr(ans, "LOOP_BUDGET_S", 0.05)
    assert asyncio.run(ans.answer_question("q", "en", None)).text == "held partial"
