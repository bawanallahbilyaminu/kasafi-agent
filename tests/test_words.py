"""docs/planner-variance.md fixes 1, 3 and 5: what the words settle (English, Hausa, code-switched), how the plan
is corrected and logged, the second opinion on conflicts, and the quote attribution on fact cards."""

from __future__ import annotations

import pytest

from app.agent import words as W
from app.agent.answer import Plan, narrative_subject
from app.agent.need import Need
from app.agent.periods import asked_period


@pytest.mark.parametrize("q,quarter", [
    ("How much did the Ministry of Lands and Housing spend from January to September 2025?", 3),
    ("spent by the end of Q3 2025, against its revised budget", 3),
    ("Me aka kashe daga Janairu zuwa Satumba 2025 a Ma'aikatar Ilimi?", 3),
    ("Nawa aka kashe har zuwa ƙarshen Q2 2026?", 2),
    ("Nawa aka kashe zuwa karshen watan Yuni 2025?", 2),
    ("Ministry of Health ta kashe nawa a rubu'i na farko na 2026?", 1),
    ("Janairu zuwa Disamba 2025, nawa aka kashe?", 4),
    ("watanni tara na farko na 2025", 3),
])
def test_periods_in_english_hausa_and_code_switched_wording(q, quarter) -> None:
    p = asked_period(q)
    assert p is not None and p.quarter == quarter
    assert W.facts_from(q).period == p


@pytest.mark.parametrize("q,measures", [
    ("How much had teh State Enviromental Protection Agency spent by the end of Q3 2025, agianst its revised budget?",
     ["actual_ytd", "revised"]),
    ("State Environmental Protection Agency ta kashe kudi nawa har zuwa karshen Q3 2025, idan aka kwatanta da revised budget dinta?",
     ["actual_ytd", "revised"]),
    ("Kasafin da aka sabunta na 2025 na hukumar ruwa nawa ne, kuma nawa aka kashe zuwa ƙarshen Q2?", ["actual_ytd", "revised"]),
    ("Nawa aka ware wa Ma'aikatar Lafiya a 2026?", ["approved"]),
    ("What was the approved and the revised budget of the Ministry of Health in 2025?", ["revised", "approved"]),
    ("What share of its revised budget had the Ministry of Works spent by Q2 2026?", ["actual_ytd", "revised", "performance_pct"]),
    ("How many IDPs are in Gada LGA?", []),
])
def test_measure_words(q, measures) -> None:
    assert W.facts_from(q).measures == measures


def test_split_words_in_both_languages() -> None:
    assert W.facts_from("What are the personnel, overhead and capital allocations of Fertilizer and Agricultral Supplies "
                        "Company in 2025?").splits == ["personnel", "overhead", "capital"]
    assert W.facts_from("Nawa ne kuɗin albashi da na gudanarwa na Ma'aikatar Ilimi a 2026?").splits == ["personnel", "overhead"]
    assert W.facts_from("Capital budget of the Ministry of Works in 2026").splits == ["capital"]
    assert W.facts_from("Total budget of the Ministry of Works in 2026").splits == []


@pytest.mark.parametrize("q,publishers,compare,topic", [
    ("A cewar NBS, menene MPI na jihar Sokoto, kuma a cewar SBS nawa ne ya inganta?", ["nbs_mpi", "sokoto_mpi"], True, "poverty_welfare"),
    ("According to SBS, what was Sokoto's multidimensional poverty incidence in 2022?", ["sokoto_mpi"], False, "poverty_welfare"),
    ("Bisa ga rahoton World Bank, nawa ne talauci a Sokoto, kuma ya ragu idan aka kwatanta da NBS?", ["worldbank_poverty", "nbs_mpi"], True, "poverty_welfare"),
    ("According to IOM, how many IDPs are in Sokoto, and has it changed since 2024?", ["iom_dtm"], False, "displacement_humanitarian"),
    ("How much is budgeted for roads in 2026?", [], False, ""),
])
def test_publishers_change_and_topic_words(q, publishers, compare, topic) -> None:
    f = W.facts_from(q)
    assert f.publishers == publishers and f.compare == compare and f.topic == topic


def test_a_named_line_is_recognised_and_a_generic_name_is_not() -> None:
    f = W.facts_from("How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?")
    assert f.line_name.lower().startswith("procurment of 5n0 peugout 406")
    assert W.facts_from('How much is budgeted for "Construction of Rural Roads under Rural Access" in 2026?').line_name
    assert not W.facts_from("How much is budgeted for the Ministry of Agriculture in 2026?").line_name
    assert not W.facts_from("Nawa aka ware wa Ma'aikatar Lafiya a 2026?").line_name


def _plan(**need) -> Plan:
    p = Plan("ZEBRA question", ["x"], ["bir-2025-q3", "bir-2025-q4", "budget-2025-approved"])
    p.original = "ZEBRA question"
    p.need = Need("ZEBRA question", measures=need.get("measures", ["actual_ytd"]), splits=need.get("splits", []),
                  time=need.get("time", {"kind": "year", "year": 2025}), operation=need.get("operation", "lookup"),
                  topics=need.get("topics", []))
    return p


def test_enforce_overrides_only_what_the_words_settle_and_logs_each_override() -> None:
    p = _plan(time={"kind": "quarter", "year": 2025, "quarter": 4}, measures=["actual_ytd"])
    f = W.facts_from("How much had the State Environmental Protection Agency spent by the end of Q3 2025, against its revised budget?")
    overrides = W.enforce(p, f, {"bir-2025-q3", "bir-2025-q4"})
    assert p.need.time == {"kind": "quarter", "year": 2025, "quarter": 3}
    assert p.doc_ids == ["bir-2025-q3", "budget-2025-approved"]           # the Q4 report left out
    assert p.need.measures == ["actual_ytd", "revised"]
    assert [o["field"] for o in overrides] == ["time", "doc_ids", "measures"]
    assert all({"field", "from", "to", "rule"} <= set(o) for o in overrides)
    assert p.words["overrides"] == overrides and p.words["facts"]["period"] == "Q1-Q3 2025"
    assert "ZEBRA" not in str(p.words)                                       # fields only, never the message text
    # nothing named: nothing changed
    p2 = _plan(measures=["other"], time={"kind": "latest"})
    assert W.enforce(p2, W.facts_from("List the LGAs of Sokoto State"), set()) == [] and p2.need.measures == ["other"]
    assert p2.need.time == {"kind": "latest"} and p2.words["overrides"] == []


def test_enforce_splits_compare_topic_and_named_line() -> None:
    p = _plan(splits=["personnel"], measures=["approved"])
    W.enforce(p, W.facts_from("What are the personnel, overhead and capital allocations of Fertilizer and Agricultural Supplies Company in 2025?"), set())
    assert p.need.splits == ["personnel", "overhead", "capital"]
    p = _plan(operation="lookup", topics=[])
    W.enforce(p, W.facts_from("A cewar NBS, menene MPI na jihar Sokoto, kuma a cewar SBS nawa ne ya inganta?"), set())
    assert p.need.operation == "compare" and p.need.topics == ["poverty_welfare"]
    p = _plan()
    p.line_search = {"terms": ["Peugeot 406", "vehicles"], "years": [2026]}
    p.category = {"terms": ["vehicles"], "scope": "statewide", "year": 2026, "measure": "approved"}
    W.enforce(p, W.facts_from("How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?"), set())
    assert p.line_search["terms"][0].lower().startswith("procurment of 5n0") and p.category == {}


def test_conflicting_periods_are_left_to_the_second_opinion() -> None:
    f = W.facts_from("Compare spending by the end of Q2 2025 with January to September 2025")
    assert f.period is None and f.conflicts == [{"field": "time", "values": [2, 3]}]
    p = _plan(time={"kind": "year", "year": 2025})
    W.enforce(p, f, set())
    assert p.need.time == {"kind": "year", "year": 2025} and W.disputed_fields(p, f) == ["time"]
    other = _plan(time={"kind": "quarter", "year": 2025, "quarter": 3})
    taken = W.take_second_opinion(p, other, f, ["time"])
    assert taken == [{"field": "time", "from": {"kind": "year", "year": 2025}, "to": {"kind": "quarter", "year": 2025, "quarter": 3}}]
    assert p.need.time["quarter"] == 3
    same = _plan(time={"kind": "year", "year": 2025})
    assert W.take_second_opinion(_plan(time={"kind": "year", "year": 2025}), same, f, ["time"]) == []


def test_narrative_subject() -> None:
    p = Plan("What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?", [], [])
    p.original = p.english_question
    assert narrative_subject(p) == "revenue performance"
    p = Plan("How much was spent on roads?", [], [])
    p.original = p.english_question
    assert narrative_subject(p) == ""


def test_a_quoted_earlier_figure_equal_to_another_publishers_own_is_labelled_as_cited() -> None:
    from app.acquisition.registry import registry
    from app.agent.topics import Card, attribute_quotes, cited_from_other
    topic = registry().topics["poverty_welfare"]
    pubs = {p.id: p for p in topic.publishers}
    nbs, sbs = pubs["nbs_mpi"], pubs["sokoto_mpi"]
    own = Card(nbs, "nbs-mpi-2022", "Nigeria MPI 2022", 123, "90.5%", "%", "incidence", "2022", "Sokoto State", "2022",
               measure="headcount_pct")
    quoted = Card(sbs, "mpi-2025-sokoto", "Sokoto MPI 2025", 36, "91%", "%", "2022 baseline headcount", "2022",
                  "Sokoto State", "2025", measure="headcount_pct")
    theirs = Card(sbs, "mpi-2025-sokoto", "Sokoto MPI 2025", 33, "59.1%", "%", "headcount", "2025", "Sokoto State", "2025",
                  measure="headcount_pct")
    out = attribute_quotes([own, quoted, theirs])
    assert out == [quoted] and cited_from_other(quoted) and "NBS" in quoted.based_on and "2022" in quoted.based_on
    assert not cited_from_other(theirs) and not cited_from_other(own)
