"""Live regression, 1 Nov 2026 14:08: a MICS question ("gaps in child healthcare and civil registration for Sokoto")
was refused with "couldn't verify the figures": the budget-table entity rule read the survey table's title words as
another entity's row. Survey and statistics tables bind by geography (the Sokoto row, not the national Total or the
zone), indicator, survey year and sub-population; an unbound figure is "figures checked", never a refusal."""

from __future__ import annotations

import pytest

from app.agent import attribution as A
from app.agent.answer import Evidence

MICS_TITLE = "Nigeria 2021 Multiple Indicator Cluster Survey (MICS) and National Immunization Coverage Survey (NICS)"
NATIONAL = Evidence(1, "mics-2021", MICS_TITLE, 2021, 336, "text",
                    "Table PR.1.1: Birth registration\nPercentage of children under age 5 by whether birth is registered and "
                    "percentage of children not registered whose mothers/caretakers know how to register births, Nigeria MICS, 2021\n"
                    "Have birth certificate\nNo birth certificate\nTotal registered\n"
                    "Total 36.0 18.1 3.1 57.3 30,804 32.9 13,162\nSex\nMale 36.9 17.6 3.3 57.8 15,522 33.7 6,556\n"
                    "Age (in months)\n12-23 38.8 15.5 3.0 57.4 5,652 33.0 2,410\nGeopolitical zone\n"
                    "North West 31.7 12.7 3.0 47.4 9,913 30.6 5,211")
STATE = Evidence(2, "mics-2021", MICS_TITLE, 2021, 337, "text",
                 "Table PR.1.1: Birth registration (Continued)\nPercentage of children under age 5 by whether birth is registered, "
                 "Nigeria MICS, 2021\nState\nKebbi 20.1 9.9 2.0 32.0 1,086 23.1 738\nSokoto 11.1 8.7 2.8 22.5 972 16.0 753\n"
                 "Zamfara 10.5 7.0 2.1 19.6 1,120 15.2 900")
VACC = Evidence(3, "mics-2021", MICS_TITLE, 2021, 190, "text",
                "Table TC.1.2: Vaccinations by background characteristics (Crude coverage) (Continued)\nPercentage of children "
                "age 12-23 months currently vaccinated against vaccine preventable childhood diseases (Crude coverage), Nigeria MICS, 2021\n"
                "Basic antigens\nNo vaccinations\nState\nSokoto 33.7 28.7 44.7 31.2 21.0 26.7 12.5 22.5 28.8 18.4 11.5 21.8 14.2 10.0 "
                "19.1 17.1 19.5 7.2 5.8 50.7")
BUDGET = Evidence(9, "budget-2026-approved", "Sokoto State FY 2026 Budget", 2026, 40, "text",
                  "[Table: Total Expenditure by Function]\n04 Health | 2026 Approved Budget 52,179,252,082.91\n"
                  "05 Education | 2026 Approved Budget 61,000,000,000.00")


def test_the_live_mics_answer_is_bound_by_geography_not_refused() -> None:
    text = ("According to MICS 2021, 22.5% of children under 5 in Sokoto had their birth registered, against 57.3% nationally [1][2]. "
            "Only 7.2% of Sokoto's children aged 12-23 months had all basic vaccinations and 50.7% had none [3].")
    att = A.bind(text, [NATIONAL, STATE, VACC])
    assert att.state == "attribution checked", att.problems
    assert [b.claim.number for b in att.bindings] == ["22.5", "57.3", "7.2", "50.7"]
    assert all(b.bound for b in att.bindings)


def test_a_national_figure_given_for_sokoto_is_a_contradiction() -> None:
    att = A.bind("In Sokoto, 57.3% of children under 5 had their birth registered in 2021 [1].", [NATIONAL, STATE])
    assert att.state == "unsupported" and att.problems[0].startswith("geography: 57.3 is the national (Total) figure")
    att = A.bind("Nationally, 22.5% of children had their birth registered [1][2].", [NATIONAL, STATE])
    assert att.state == "unsupported" and att.problems[0].startswith("geography: 22.5 is the Sokoto figure")
    att = A.bind("In the North West zone 22.5% of births were registered [1][2].", [NATIONAL, STATE])
    assert att.state == "unsupported"


def test_a_figure_without_a_geography_or_from_a_row_the_page_cannot_settle_is_figures_checked() -> None:
    att = A.bind("Birth registration stood at 57.3% in 2021 [1].", [NATIONAL])
    assert att.state == "figures checked" and att.ok
    att = A.bind("Among boys 57.8% were registered [1].", [NATIONAL])        # a sub-population row, no geography
    assert att.state == "figures checked"


def test_the_survey_year_and_the_sub_population_are_checked() -> None:
    att = A.bind("In 2024, 22.5% of children in Sokoto had their birth registered [2].", [STATE])
    assert att.state == "unsupported" and att.problems[0].startswith("year: 22.5 is from the 2021 survey")
    att = A.bind("In Sokoto 7.2% of children aged 24-35 months had all basic vaccinations [3].", [VACC])
    assert att.state == "unsupported" and att.problems[0].startswith("subpopulation:")
    att = A.bind("In Sokoto 7.2% of children aged 12-23 months had all basic vaccinations [3].", [VACC])
    assert att.state == "attribution checked", att.problems


def test_rounded_percents_match_and_budget_shares_are_still_not_bound() -> None:
    att = A.bind("About 23% of children in Sokoto had their birth registered in 2021 [2].", [STATE])
    assert att.state == "attribution checked", att.problems
    att = A.bind("Health gets 52,179,252,082.91 in 2026, which is 16.9% of the budget [9].", [BUDGET])
    assert att.state == "attribution checked" and [b.claim.number for b in att.bindings] == ["52,179,252,082.91"]


def test_budget_rows_cited_beside_a_survey_keep_the_strict_rules() -> None:
    att = A.bind("Sokoto registered 22.5% of births [2]; Health was allocated 52,179,252,082.91 in 2026 [9].", [STATE, BUDGET])
    assert att.state == "attribution checked", att.problems
    att = A.bind("Sokoto registered 22.5% of births [2]; Education was allocated 52,179,252,082.91 in 2026 [9].", [STATE, BUDGET])
    assert att.state == "unsupported" and att.problems[0].startswith("entity:")


def test_a_narrative_report_sentence_naming_the_entity_elsewhere_is_not_a_contradiction() -> None:
    emonc = Evidence(1, "emonc-sokoto", "Emergency Obstetric and Newborn Care (EmONC) Assessment, Sokoto State", 2026, 40, "text",
                     "Table 12: Functionality by LGA\nWamakko 8 100.0 0 0.0 8\nThe assessment found that all facilities in Wamakko "
                     "offered the signal functions, however, the strike action at Usmanu Danfodiyo University Teaching Hospital "
                     "limited 24-hour cover.")
    att = A.bind("UNFPA's assessment found that all 8 assessed facilities in Wamakko were functional (100.0%) [1].", [emonc])
    assert att.ok, att.problems


@pytest.mark.parametrize("title,kind", [
    (MICS_TITLE, "survey"), ("Sokoto State FY 2026 Budget", "budget"), ("Budget Implementation Report Q2 2026", "budget"),
    ("Nigeria Demographic and Health Survey 2024 Final Report", "survey"), ("Nigeria Multidimensional Poverty Index (2022)", "survey"),
    ("State Medium Term Expenditure Framework 2025-2027", "budget"), ("Sokoto State Health Annual Operational Plan 2025", "text"),
])
def test_table_kind_from_the_title(title, kind) -> None:
    assert A.kind_of(title) == kind


# --- the survey eval's first run (1 Nov 2026): three more classes -------------------------------------------------

MORTALITY = Evidence(1, "mics-2021", MICS_TITLE, 2021, 105, "text",
                     "Table CS.2: Early childhood mortality rates by socioeconomic characteristics (Continued)\nNeonatal, "
                     "post-neonatal, infant, child and under-five mortality rates for the five-year period preceding the survey, "
                     "Nigeria MICS, 2021\nNeonatal, infant and under-five mortality rates are expressed as deaths per 1,000 live births\n"
                     "States\nSokoto 34 70 104 109 202\nTaraba 40 23 63 34 95")
NDHS_REG = Evidence(1, "ndhs-2024", "Nigeria Demographic and Health Survey 2024 Final Report", 2024, 73, "text",
                    "Table 2.10 Birth registration of children under age 5\nPercentage of de jure children under age 5 whose births "
                    "are registered with the civil authorities, according to background characteristics, Nigeria DHS 2024\n"
                    "North West 23.5 9.2 32.7 10,889\nSokoto 14.2 4.8 19.0 1,051\nTotal 27.5 12.2 39.7 28,015")


def test_per_thousand_is_a_unit_and_the_mortality_answer_binds() -> None:
    att = A.bind("According to MICS 2021, the under-five mortality rate in Sokoto was 202 deaths per 1,000 live births [1].", [MORTALITY])
    assert att.state == "attribution checked", att.problems
    assert [b.claim.number for b in att.bindings] == ["202"]


def test_the_geography_is_the_one_written_next_to_the_figure() -> None:
    text = ("In Sokoto 19.0% of children under 5 had their birth registered (1,051 children), compared with 32.7% in the North "
            "West zone (10,889) and 39.7% nationally (28,015) [1].")
    att = A.bind(text, [NDHS_REG])
    assert att.state != "unsupported", att.problems
    text = "In Sokoto 22.5% of children under 5 had their birth registered, against 57.3% nationally [1][2]."
    assert A.bind(text, [NATIONAL, STATE]).state == "attribution checked"
    text = "Nationally the figure is 57.3% and in North West 47.4% [1]."
    assert A.bind(text, [NATIONAL]).state == "attribution checked"


def test_every_named_source_scopes_the_search() -> None:
    from app.agent.routing import all_sources
    assert all_sources("Birth registration in Sokoto: what did MICS 2021 and NDHS 2024 each find?") == ["MICS", "NDHS"]
    assert all_sources("Who is the nearest doctor?") == []
