"""'What is the government budgeting for my area?' from a pin (2 Nov live test, the demo opener): sectors matched
by function and agency, projects located in the LGA by sector, progress from the latest report, statewide lines
that may cover it, the follow-up on spending, and never an empty sources line."""

from decimal import Decimal

import pytest

from app.agent import answer as A
from app.agent.analysis import AnalysisResult, Fact, Row, lga_projects
from app.agent.sectors import sector_asked, sector_of

WAMAKKO = {"lat": 13.06, "lon": 5.24, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Bado"}


@pytest.mark.parametrize("q, key", [("What are the farming related budgets in my area?", "agriculture"),
                                    ("kasafin noma a nan", "agriculture"), ("health projects near me", "health"),
                                    ("schools in my LGA", "education"), ("roads here", "roads"),
                                    ("What is the government budgeting for my area in 2026?", None)])
def test_the_sector_a_question_asks(q, key) -> None:
    s = sector_asked(q)
    assert (s.key if s else None) == key


def test_a_line_belongs_to_a_sector_by_function_then_agency_then_name() -> None:
    assert sector_of("AGRICULTURE", "Ministry of Agriculture & Natural Resource").key == "agriculture"
    assert sector_of("", "Fertilizer and Agricultral Supplies Company").key == "agriculture"     # by its agency
    assert sector_of("", "State Agricultural Development Project").key == "agriculture"
    assert sector_of("PUBLIC HEALTH SERVICES", "Ministry of Health").key == "health"
    assert sector_of("EXECUTIVE AND LEGISLATIVE ORGANS", "SSG'S Office", "Construction of a borehole").key == "water"
    assert sector_of("EXECUTIVE AND LEGISLATIVE ORGANS", "SSG'S Office", "Renovation of VIP villas") is None


class P:
    analysis: dict = {}


def test_a_my_area_budget_question_from_a_pin_goes_to_the_lga_tool() -> None:
    spec = A.lga_route("What is the government budgeting for my area in 2026?", P(), WAMAKKO, [])
    assert spec == {"tool": "lga_projects", "lga": "Wamakko", "ward": "Bado", "terms": [],
                    "question": "What is the government budgeting for my area in 2026?", "year": 2026}
    assert A.lga_route("What is the 2026 budget for Tambuwal?", P(), WAMAKKO, []) is None     # a named place wins
    assert A.lga_route("What is the government budgeting for my area?", P(), None, []) is None  # no pin


def test_the_follow_up_on_spending_keeps_the_place_and_the_lines() -> None:
    working = ("🧮 *Working*\n• Source: the 2026 budget's capital project list (budget-2026-approved); only lines whose "
               "location is 33312100 WAMAKKO, agriculture by function and agency.\n• 2026 budget: 4 lines")
    spec = A.lga_route("How much of that has actually been spent?", P(), WAMAKKO, [{"working": working}])
    assert spec["lga"] == "Wamakko" and spec["focus"] == "spent" and spec["terms"] == ["agriculture"]
    assert spec["year"] == 2026
    assert A.lga_route("How much has the Ministry of Health spent?", P(), None, [{"working": working}]) is None


def test_no_sources_line_is_printed_with_nothing_after_it() -> None:
    assert A.sources_line([], "en") == ""
    assert A.sources_line([A.Evidence(1, "budget-2026", "Budget 2026", None, None, "text", "")], "en") == ""


def test_a_long_line_name_is_cut_at_a_word_without_a_dangling_bracket() -> None:
    name = "Construction of Classrooms, Offices, Laboratories and Toilets (AGILE Project) in 23 LGAs"
    assert A.line_name(name) == "Construction of Classrooms, Offices, Laboratories and Toilets…"


def _res(n=4, spent=0, statewide=96) -> AnalysisResult:
    r = AnalysisResult("lga_projects", True, 2026, 2025, "Wamakko", "agriculture")
    for k, v, kind in (("n", n, "count"), ("n_prev", 4, "count"), ("statewide_n", statewide, "count"),
                       ("cur", Decimal("418000000"), "money"), ("prev", Decimal("418000000"), "money"),
                       ("spent", Decimal(spent), "money"), ("statewide_cur", Decimal("32200000000"), "money")):
        r.facts[k] = Fact(v, kind, "budget-2026-approved", 53)
    r.statewide = [Row("Procurement of 250 units of Furgeson Tractors for distribution to farmers", Decimal(4.5e9),
                       "budget-2026-approved", 61)]
    r.groups = [("agriculture", 4, Decimal("418000000"), 53)]
    return r


def _v(r):
    return {k: (A._money(x.value) if x.kind == "money" else f"{x.value:,}") for k, x in r.facts.items()} | \
        {"year": 2026, "prev": 2025, "subject": "Wamakko", "prev_amt": A._money(r.facts["prev"].value)}


def test_the_reply_names_the_sector_progress_and_the_statewide_lines_never_a_bare_no_project() -> None:
    w = A.ANALYSIS_WORDS["en"]
    lead, note = A.lga_text(_res(), w, _v(_res()), "en")
    assert lead.startswith("The 2026 budget has 4 agriculture projects located in Wamakko")
    assert "nothing was spent on them by September 2025" in note and "₦0.00" not in note
    assert "96 statewide agriculture lines" in note and "Furgeson Tractors" in note
    none = _res(n=0)
    none.facts["n_all"] = Fact(163, "count", "budget-2026-approved", 49)
    none.facts["cur_all"] = Fact(Decimal("79980000000"), "money", "budget-2026-approved", 49)
    lead, note = A.lga_text(none, w, _v(none), "en")
    assert lead.startswith("None of the 2026 budget's agriculture projects is located in Wamakko. In all sectors, 163")
    assert "statewide agriculture lines" in note


def test_the_spending_follow_up_leads_with_spending_and_repeats_nothing() -> None:
    lead, note = A.lga_text(_res(spent=10), A.ANALYSIS_WORDS["en"], _v(_res(spent=10)), "en", spent_focus=True)
    # 4 Nov, from the source: the BIRs give spending by project for primary healthcare and basic education (Tables
    # 24 and 29), other sectors by ministry; the lead gives the lines first, then that note; nothing repeated
    assert lead.startswith("The 2026 budget has") and note == ""
    assert "The implementation reports give spending by project only for primary healthcare and basic education; " \
           "other sectors are reported by ministry." in lead
    assert "isn't reported project by project" not in lead


@pytest.mark.parametrize("name, fn, mda, ok", [
    ("PURCHASE OF AEROPLANE", "EXECUTIVE AND LEGISLATIVE ORGANS", "Government House", False),
    ("Purchase of Toyota Hilux vehicles for monitoring", "AGRICULTURE", "Ministry of Agriculture", False),
    ("Construction of office block at the Ministry headquarters", "HEALTH", "Ministry of Health", False),
    ("Construction of Classrooms, Offices, Laboratories and Toilets (AGILE Project)", "SECONDARY EDUCATION",
     "Ministry of Basic and Secondary Education", False),
    ("Procurement of 250 units of Furgeson Tractors for distribution to farmers", "AGRICULTURE",
     "Ministry of Agriculture", True),
    ("Rehabilitation of Sokoto Township Water Works", "WATER SUPPLY", "Ministry of Water Resources", True),
    ("Renovation of 60 primary health care centres across the state", "PUBLIC HEALTH SERVICES",
     "Primary Health Care Development Agency", True),
])
def test_statewide_lines_that_may_cover_an_lga_are_community_programmes(name, fn, mda, ok) -> None:
    from app.agent.analysis import community_line
    assert community_line(name, fn, mda) is ok


@pytest.mark.parametrize("name, ok", [("Construction of ultra modern Villa at Government House Sokoto", True),
                                      ("Renovation of Presidential Lodge and VIP villas in Sokoto", True),
                                      ("Construction for the Completion of College of Medical Sciences Sokoto at "
                                       "SOSUTH Kasarawa Wamakko LGA", False),
                                      ("Demarcation of Livestock Service Centre in Wamakko Local Government", False)])
def test_lines_filed_under_an_lga_that_name_a_place_in_sokoto_city(name, ok) -> None:
    from app.agent.analysis import in_city
    assert in_city(name, "Wamakko") is ok


def test_the_first_sentence_is_short_with_the_leading_sector_and_the_city_lines_are_said() -> None:
    r = _res()
    r.focus = ""
    r.groups = [("health", 87, Decimal("56320000000"), 67), ("education", 55, Decimal("12660000000"), 74)]
    r.facts["city_n"] = Fact(3, "count", "budget-2026-approved", 51)
    lead, note = A.lga_text(r, A.ANALYSIS_WORDS["en"], _v(r), "en")
    assert A.readable_amounts(lead, "en") == ("The 2026 budget has 4 capital projects located in Wamakko, worth "
                                              "₦418.00 million, mostly health (₦56.32 billion).")
    assert "3 lines filed under Wamakko in the budget name a place in Sokoto city" in note


@pytest.mark.parametrize("q, years", [("Over the past 3 years how much have been spent by government in my area?",
                                       [2024, 2025, 2026]),
                                      ("How much was spent here since 2023?", [2023, 2024, 2025, 2026]),
                                      ("budget in my LGA from 2024 to 2025", [2024, 2025]),
                                      ("how much was spent in my area each year", [2024, 2025, 2026]),
                                      ("Nawa aka kashe a nan a cikin shekaru biyu?", [2025, 2026]),
                                      ("What is the government budgeting for my area in 2026?", [])])
def test_the_years_a_time_span_question_covers(q, years) -> None:
    assert A.span_years(q, 2026) == years


def test_a_time_span_over_my_area_is_answered_year_by_year_and_recomputed_in_a_follow_up(monkeypatch) -> None:
    monkeypatch.setattr(A, "lagos_today", lambda: __import__("datetime").date(2026, 11, 3))
    q = "Over the past 3 years how much have been spent by government in my area?"
    working = ("• Source: the 2026 budget's capital project list (budget-2026-approved); only lines whose location "
               "is 33312100 WAMAKKO.")
    spec = A.lga_route(q, P(), WAMAKKO, [{"working": working}])
    assert spec == {"tool": "lga_years", "lga": "Wamakko", "years": [2024, 2025, 2026], "question": q}
    # a follow-up naming a new span keeps the place and recomputes; it never reuses the last reply
    assert A.lga_route("And over the past 2 years?", P(), None, [{"working": working}])["years"] == [2025, 2026]
    years_working = "• Projects located in Wamakko in each year's own budget (location code), 2024-2026"
    spec = A.lga_route("and since 2025?", P(), None, [{"working": years_working}])
    assert spec["tool"] == "lga_years" and spec["lga"] == "Wamakko" and spec["years"] == [2025, 2026]
    spent = A.lga_route("How much has actually been spent in my area?", P(), WAMAKKO, [{"working": years_working}])
    assert spent["tool"] == "lga_projects" and spent["focus"] == "spent"


def test_agency_spending_in_a_place_answer_is_labelled_statewide() -> None:
    for lang in ("en",):
        w = A.ANALYSIS_WORDS[lang]
        assert "statewide, all of" in w["lga_progress"] and "statewide, all of" in w["lga_agencies"]
        assert "not only those in {subject}" in A.YEARS_WORDS[lang]["agency"]


# --- on the dev library -----------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM projects WHERE doc_id = 'budget-2026-approved' LIMIT 1")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database: {e}")
    yield c
    c.close()


def test_farming_in_wamakko_finds_the_agriculture_lines_by_agency(conn) -> None:
    """2 Nov live test: 'No project in the 2026 budget is located in Wamakko' and an empty sources line. By function
    and agency the 2026 budget has agriculture lines there, and statewide ones that may cover it."""
    r = lga_projects(conn, {"lga": "Wamakko", "year": 2026, "terms": ["farming"],
                            "question": "What are the farming related budgets in my area?"})
    assert r.focus == "agriculture" and r.facts["n"].value >= 4 and r.facts["statewide_n"].value > 50
    assert r.statewide and all(x.page for x in r.statewide) and r.facts["n"].page


def test_all_sectors_for_my_area_with_progress_from_the_latest_report(conn) -> None:
    r = lga_projects(conn, {"lga": "Wamakko", "year": 2026, "terms": [], "question": "budgeting for my area"})
    assert r.focus == "" and r.facts["n"].value > 100
    assert [g[0] for g in r.groups][:2] == ["health", "education"]
    assert r.report.startswith("Q") and r.facts["rep_spent"].value > 0 and r.agencies


def test_wamakko_year_by_year_with_each_years_own_budget_and_the_spending_periods(conn) -> None:
    """2 Nov live test: 'used 2024-2026' with no 2024 figure, and two runs with different 2025 figures. Each year
    now comes from its own budget (or, for a year whose project list isn't in the library, the next budget's
    revised column), with project-level spending and its period, and agency spending labelled statewide."""
    from app.agent.analysis import lga_years
    r = lga_years(conn, {"lga": "Wamakko", "years": [2024, 2025, 2026]})
    by = {x.name: x.detail for x in r.rows}
    assert by["2025"]["source"] == "own" and by["2025"]["n"] > 100 and by["2025"]["spent_kind"] in ("actual",
                                                                                                    "jan_sep")
    assert by["2026"]["source"] == "own" and by["2026"]["n"] > 100 and "spent_kind" not in by["2026"]
    assert by["2026"].get("rep_doc")                      # 2026: spending by agency only, from the latest report
    assert by["2024"]["source"] in ("own", "own_named", "next") and by["2024"].get("spent_kind")
    assert r.facts["span_spent"].value == sum(d.get("spent") or 0 for d in by.values())


def test_a_year_whose_budget_prints_no_locations_says_so_and_gives_the_next_budgets_figures(conn) -> None:
    from app.agent.analysis import lga_years
    r = lga_years(conn, {"lga": "Wamakko", "years": [2024]})
    d = r.rows[0].detail
    if d.get("source") != "own_named":
        pytest.skip("the 2024 project list isn't built on this database")
    assert d["n"] > 0 and d.get("next_doc") == "budget-2025-approved" and d["next_n"] > d["n"]
