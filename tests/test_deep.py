"""Deep analysis for broad questions (app/agent/deep.py): detection, dimension planning, sources, claim checks, the
cost and time caps, neutral synthesis, the brief. Free: the model clients are stubs."""

import asyncio
import json
import re
import time

import pytest

from app.agent import deep as D
from app.providers.chat import ChatResult
from tests.helpers import make_settings


class StubModel:
    """Plans dimensions, reads pages (a claim per page: the first number the page prints, so the code check
    passes), and writes a synthesis citing the claims; counts calls."""
    provider = "Stub"
    default_model = "stub"

    def __init__(self, delay: float = 0.0, bad_figure: bool = False):
        self.calls, self.delay, self.bad_figure = [], delay, bad_figure

    async def chat(self, messages, **kw):
        system = messages[0]["content"]
        user = messages[-1]["content"]
        self.calls.append(system[:30])
        if self.delay:
            await asyncio.sleep(self.delay)
        if system.startswith("You plan an analysis"):
            body = {"subject": "primary health care", "dimensions": [
                {"name": "facilities and infrastructure", "queries": ["PHC facilities", "renovation"]},
                {"name": "staffing", "queries": ["health workers", "nurses midwives"]},
                {"name": "funding and spending", "queries": ["budget", "expenditure"], "money": True},
                {"name": "plans and targets", "queries": ["targets", "plan"]}]}
        elif system.startswith("You read pages"):
            claims = []
            for m in re.finditer(r"--- page (\d+) ---\n(.*?)(?=\n--- page |\Z)", user, re.S):
                num = re.search(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+(?:\.\d+)?%", m.group(2))
                if num:
                    claims.append({"dimension": "facilities and infrastructure", "statement": "A figure printed",
                                   "value": num.group(0), "unit": "", "year": "2024", "entity": "Sokoto",
                                   "page": int(m.group(1))})
            claims.append({"dimension": "staffing", "statement": "invented", "value": "987,654,321", "page": 1})
            body = {"claims": claims}
        else:
            first = re.search(r"\[C1\] .*?\| value (\S+)", user)
            v = first.group(1) if first else "0"
            extra = " The rate was 77.7% in 2025 [C1]." if self.bad_figure else ""
            body = {"summary": f"The library holds figures on primary health care. One reads {v} [C1].{extra} "
                               "Facilities are poor in some LGAs.",
                    "sections": [{"dimension": "facilities and infrastructure", "text": f"{v} [C1]."}],
                    "differ": "Sources cover different years.", "missing": "No staffing figures by LGA."}
        return ChatResult(json.dumps(body), "stub", "stop")

    async def aclose(self):
        return None


# --- detection and planning -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("q, deep", [
    ("Whats the state of PHCs in sokoto state", True), ("Give me an overview of primary health care", True),
    ("How is basic education doing in Sokoto?", True), ("Yaya yanayin cibiyoyin kiwon lafiya a Sokoto?", True),
    ("Ina son bayani dalla-dalla kan ilimi", True), ("How many PHCs are in Sokoto State?", False),
    ("What is the 2026 health budget?", False),
])
def test_broad_questions_are_detected(q, deep) -> None:
    assert D.deep_question(q) is deep


def test_dimensions_come_from_the_model_or_the_fixed_list() -> None:
    subject, dims = asyncio.run(D.plan_dimensions(StubModel(), "state of PHCs", "What is the state of PHCs?"))
    assert subject == "primary health care" and [d.name for d in dims][:2] == ["facilities and infrastructure",
                                                                                "staffing"]
    assert next(d for d in dims if d.name == "funding and spending").money

    class Broken(StubModel):
        async def chat(self, messages, **kw):
            raise RuntimeError("down")
    _, dims = asyncio.run(D.plan_dimensions(Broken(), "q", "q"))
    assert len(dims) == len(D.DEFAULT_DIMENSIONS)


# --- claims, caps, synthesis --------------------------------------------------------------------------------------

def test_a_claim_counts_only_when_its_value_is_printed_on_its_page() -> None:
    pages = {7: "Total cost N15,900,000,000.", 13: "Coverage 61%."}
    assert D.verify_claim({"value": "N15,900,000,000", "page": 7}, pages)
    assert D.verify_claim({"value": "₦15.9 billion", "page": 7}, pages)
    assert not D.verify_claim({"value": "61%", "page": 7}, pages)
    assert not D.verify_claim({"value": "987,654,321", "page": 13}, pages) and not D.verify_claim({"value": "x"}, pages)


def readings(n):
    return [D.Reading(f"doc{i}", f"Doc {i}", 2024, [(1, f"Page {i} prints 1,234 facilities.")], ["staffing"])
            for i in range(n)]


def test_reading_stops_at_the_cost_cap() -> None:
    spend = {"usd": 0.0}
    model = StubModel()
    orig = model.chat

    async def costly(messages, **kw):
        spend["usd"] += 0.05
        return await orig(messages, **kw)
    model.chat = costly
    dims = [D.Dimension("staffing", ["x"])]
    claims, stopped = asyncio.run(D.read_all(model, readings(12), "PHC", dims, make_settings(), cost_cap=0.20,
                                             spent=lambda: spend["usd"]))
    assert "cost cap" in stopped and 4 <= len(model.calls) <= 4 + D.CONCURRENT
    assert all(c.value == "1,234" for c in claims)                        # the invented figure never passes


def test_reading_stops_at_the_deadline() -> None:
    dims = [D.Dimension("staffing", ["x"])]
    t0 = time.perf_counter()
    claims, stopped = asyncio.run(D.read_all(StubModel(delay=2.0), readings(3), "PHC", dims, make_settings(),
                                             deadline_s=0.3, spent=lambda: 0.0))
    assert time.perf_counter() - t0 < 1.5 and claims == [] and "time" in stopped


def test_the_synthesis_keeps_only_verified_figures_and_no_verdict_words() -> None:
    claims = [D.Claim("facilities and infrastructure", "PHCs in the registry", "1,234", "", "2024", "Sokoto",
                      "doc0", "Doc 0", 1)]
    text = D.keep_verified("There are 1,234 PHCs [C1]. The rate was 77.7% in 2025 [C1]. Facilities are poor.", claims)
    assert "1,234" in text and "77.7" not in text and "poor" not in text
    assert D.cite("There are 1,234 PHCs [C1].", claims) == "There are 1,234 PHCs (Doc 0, p. 1)."


def test_render_gives_a_summary_then_a_message_per_dimension_and_the_brief_offer() -> None:
    r = D.DeepResult("Summary.", [("facilities", "1,234 PHCs."), ("staffing", "500 nurses.")], "Different years.",
                     "No LGA data.", [], ["doc0"], 0.05, 40.0)
    summary, parts = D.render(r, "en")
    assert summary == "Summary." and parts[0].startswith("*facilities*") and parts[1].startswith("*staffing*")
    assert "Where sources differ" in parts[2] and "full brief" in parts[2]


def test_the_full_brief_is_a_pdf_with_every_claim() -> None:
    claims = [D.Claim("staffing", "Nurses in PHCs", "500", "", "2024", "Sokoto", "doc0", "Doc 0", 3)]
    pdf = D.brief_pdf("State of PHCs?", D.DeepResult("Summary.", [("staffing", "500 nurses.")], "", "", claims,
                                                      ["doc0"], 0.0, 1.0))
    assert pdf[:4] == b"%PDF" and len(pdf) > 1000


# --- the whole analysis on the dev library (stubbed models) ----------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM doc_cards LIMIT 1")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database: {e}")
    yield c
    c.close()


def test_a_deep_analysis_reads_across_the_library_within_its_limits(conn) -> None:
    notes = []

    async def notify(text):
        notes.append(text)
    r = asyncio.run(D.deep_answer(conn, "Whats the state of PHCs in sokoto state",
                                  "What is the state of primary health care centres in Sokoto State?", "en",
                                  client=StubModel(bad_figure=True), open_client=StubModel(), settings=make_settings(),
                                  notify=notify))
    assert 3 <= len(r.documents) <= D.MAX_DOCS + D.EXTRA_DOCS + 1 and r.claims
    assert "registry:facilities" in r.documents                           # the registry counts for facilities
    assert all(c.value != "987,654,321" for c in r.claims)                # invented figures never pass the check
    assert "77.7" not in r.summary and "poor" not in r.summary            # unverified figure and verdict word gone
    assert notes[0].startswith("🧭") and notes[1].startswith("📚 Reading") and notes[2].startswith("✍️")


def test_citations_are_given_once_per_message_without_a_page_for_the_registry_and_amounts_in_house_style() -> None:
    claims = [D.Claim("f", "s", "15,000,000.00", "", "2025", "", "budget-2025", "Sokoto State Government 2025 Approved "
                      "Budget", 45),
              D.Claim("f", "s", "934", "", "2024", "", "registry:facilities", "Health facility registry (NHFR / GRID3)",
                      0),
              D.Claim("f", "s", "1", "", "", "", "rop", "State Health Resource Optimization Plan (ROP) to Improve "
                      "Healthcare Services in Sokoto", 9)]
    text = D.cite("15,000,000.00 NGN for renovation [C1]. 150,000,000.00 NGN for solar [C1]. 934 facilities [C2]. "
                  "Readiness [C3].", claims)
    assert text.count("(Sokoto State Government 2025 Approved Budget, p. 45)") == 1
    assert "(GRID3/NHFR registry, Nov 2024)" in text and "p. 0" not in text
    assert "₦15 million for renovation" in text and "NGN" not in text
    assert "Improve Healthcare…" in text or "Improve…" in text and "Hea," not in text


# --- the 3 Nov brief review: measures, selection, years, differences, amounts -----------------------------------

def C(dim, statement, value, kind="", measure="", year="", entity="Sokoto State", doc="msp", doc_year=2020, page=6,
      unit=""):
    return D.Claim(dim, statement, value, unit, year, entity, doc, "Sokoto State Minimum Service Package", page,
                   measure, kind, doc_year)


@pytest.mark.parametrize("q, subject", [("What's the state of PHCs in Sokoto?", "primary health care"),
                                        ("Yaya yanayin cibiyoyin kiwon lafiya a Sokoto?", "primary health care"),
                                        ("How is basic education doing?", "basic education"),
                                        ("What's the situation of roads in Sokoto?", None)])
def test_a_known_subject_has_a_measure_checklist(q, subject) -> None:
    cl = D.checklist_for(q)
    assert (cl.subject if cl else None) == subject
    if cl and subject == "primary health care":
        ids = {m.id for d in cl.dimensions for m in d.measures}
        assert {"fac_count", "fac_need", "staff_have", "staff_need", "money_alloc", "money_actual", "cov_imm",
                "cov_anc", "cov_sba", "emonc", "plan_targets"} <= ids


def test_serial_numbers_codes_and_background_are_never_figures() -> None:
    assert D.junk(C("f", "Serial number of the facility in the table", "12"))
    assert D.junk(C("f", "Facility code", "34/12/1/1/1/0012"))
    assert D.junk(C("f", "Budget line", "23020106"))
    assert D.junk(C("f", "Sokoto State has 23 LGAs", "23"))
    assert D.junk(C("f", "Number of political wards in the state", "244"))
    assert D.junk(C("f", "WHO estimates that 20-40% of health spending is wasted", "20-40%", entity="Global"))
    assert D.junk(C("f", "Background", "5", kind="context"))
    assert not D.junk(C("f", "Total personnel in the PHC system", "11202"))
    assert not D.junk(C("f", "Number of PHC facilities in Sokoto State", "798", "aggregate", "fac_count"))
    assert not D.junk(C("f", "Number of political wards", "244"), "how many wards are there")   # asked: kept


def test_claims_are_ranked_by_informativeness_and_capped_per_dimension() -> None:
    dims = [D.Dimension("staffing", [], measures=[D.Measure("staff_have", "available"),
                                                  D.Measure("staff_need", "required")])]
    claims = [C("staffing", "The blueprint has 18 objectives", "18", "detail"),
              C("staffing", "Nurses/midwives available", "78", "aggregate", "staff_have"),
              C("staffing", "Nurses/midwives required", "244", "target", "staff_need"),
              C("staffing", "CHEWs available", "787", "aggregate", "staff_have"),
              C("staffing", "JCHEWs required", "3,125", "target", "staff_need"),
              C("staffing", "Medical officers required", "46", "target", "staff_need"),
              C("staffing", "Nurses/midwives required (copy)", "244", "target", "staff_need")]
    got = D.select_claims(claims, dims)
    assert [c.value for c in got][:2] == ["244", "78"]                     # required and available, same cadre
    assert [c.value for c in got].index("3,125") < [c.value for c in got].index("787")   # targets before totals
    assert "18" not in [c.value for c in got]                              # trivia never fills a full dimension
    assert len(got) <= D.PER_DIMENSION and sum(c.measure == "staff_need" for c in got) == D.PER_MEASURE
    assert [c.value for c in got].count("244") == 1                        # the same figure once
    cov = D.coverage(got, dims)
    assert cov == [("staffing", ["available", "required"], [])]


def test_staffing_pairs_required_and_available_for_the_same_cadre() -> None:
    """The server run of 3 Nov set 3,125 JCHEWs and 46 medical officers required against 3,395 frontline staff and
    1,927 CHOs: no cadre on both sides. The nurse/midwife pair is the comparison."""
    dims = [D.Dimension("staffing", [], measures=[D.Measure("staff_have", "available"),
                                                  D.Measure("staff_need", "required")])]
    claims = [C("staffing", "3,125 JCHEWs are required under the MSP", "3,125", "target", "staff_need"),
              C("staffing", "At least 46 medical officers are required", "46", "target", "staff_need"),
              C("staffing", "At least 244 Nurses/midwives are required", "244", "target", "staff_need"),
              C("staffing", "Frontline staff available total 3,395 personnel", "3,395", "aggregate", "staff_have"),
              C("staffing", "1,927 Community Health Officers among frontline staff", "1,927", "aggregate",
                "staff_have"),
              C("staffing", "78 Nurse/Midwives among frontline clinical staff", "78", "aggregate", "staff_have")]
    got = [c.value for c in D.select_claims(claims, dims)]
    assert "244" in got and "78" in got


def test_every_measure_found_keeps_a_claim_before_any_measure_gets_a_second() -> None:
    """3 Nov live run: EmONC's 7.6% was read, but two antenatal-care and two immunisation figures (higher scores)
    filled the dimension's 5 places, and EmONC was reported 'not found'."""
    dims = [D.phc_checklist().dimensions[3]]
    claims = [C("service coverage", f"ANC figure {i}", f"{20 + i}.1%", "share", "cov_anc", "2024") for i in range(2)]
    claims += [C("service coverage", f"Births figure {i}", f"{40 + i}.1%", "share", "cov_sba", "2024")
               for i in range(2)]
    claims += [C("service coverage", f"Vaccination figure {i}", f"{60 + i}.1%", "share", "cov_imm", "2021")
               for i in range(2)]
    claims += [C("service coverage", "Share of BEmONC facilities fully functioning", "7.6%", "detail", "emonc")]
    got = D.select_claims(claims, dims)
    assert len(got) == D.PER_DIMENSION and "7.6%" in [c.value for c in got]
    assert D.coverage(got, dims)[0][2] == []                               # nothing reported missing


@pytest.mark.parametrize("statement, unit", [("The Blueprint 2023-2026 has 262 interventions", "interventions"),
                                             ("The Blueprint has 18 objectives", ""),
                                             ("The plan has one goal", "goal"),
                                             ("It sets 27 priority initiatives", "")])
def test_how_a_plan_is_organised_is_not_a_finding(statement, unit) -> None:
    assert D.junk(C("plans", statement, "18", "target", unit=unit))
    assert not D.junk(C("plans", "92 PHCs to be equipped and staffed by 2025", "92", "target", "plan_targets"))


def test_a_figure_without_its_own_year_carries_its_documents_date_and_no_year_is_invented() -> None:
    c = C("f", "Number of PHC facilities", "798", "aggregate", "fac_count")
    assert c.when == "as of the 2020 report"
    assert D.Claim("f", "s", "934", "", "", "", "registry:facilities", D.REGISTRY_REF, 0).when == "Nov 2024"
    text = D.keep_verified("Sokoto had 798 PHC facilities as of the 2020 report [C1]. In 2016 assessment, 798 "
                           "facilities were counted [C1]. There were 798 facilities, with year not stated [C1].", [c])
    assert "as of the 2020 report" in text and "2016" not in text and "not stated" not in text


def test_a_national_surveys_figures_are_never_given_as_sokotos() -> None:
    survey = D.Reading("ndhs-2024", "Nigeria DHS 2024", 2024, [(241, "63% of women received ANC")], national=True)
    state = D.Reading("ndhs-2024", "Nigeria DHS 2024", 2024, [(250, "Sokoto 26.4 13.0")], national=True)
    plan = D.Reading("msp", "Sokoto MSP", 2020, [(6, "798 facilities")])
    assert not D.national_ok(survey, "Women age 15-49", "63% of women received ANC")
    assert not D.national_ok(survey, "Nigeria", "Sokoto ... 63%")
    assert D.national_ok(state, "Sokoto", "Sokoto 26.4 13.0", "26.4")
    assert D.national_ok(plan, "Sokoto State", "798 facilities")
    assert not D.national_ok(plan, "Nigeria (national)", "")


MICS_197 = """P a g e |182
Table TC.1.3: Vaccinations by background characteristics (Valid dose coverage) (Continued)
""" + ("Percentage of children age 12-23 months currently vaccinated against vaccine preventable childhood diseases "
       "according to vaccination records (Valid dose coverageA,B), Nigeria MICS, 2021") + """
BCG Polio ... Basic antigens All 1YL antigens No vaccinations
Total 54.8 39.0 52.4 46.7 31.8 40.2 29.9 38.9 52.4 46.8 32.2 52.6 47.4 32.4 34.2 32.8 30.3 23.5 14.1 44.6 5,652
Sokoto 14.8 4.5 13.5 9.1 5.8 6.8 5.6 4.9 13.6 7.8 5.1 13.6 9.1 5.8 5.4 4.0 3.6 3.7 0.0 85.2 141"""


def test_a_survey_figure_is_bound_to_the_sokoto_row_and_carries_its_tables_basis() -> None:
    """MICS 'no vaccinations' 85.2 is the Sokoto row's own column of Table TC.1.3 (valid dose, by vaccination
    records); the crude table (card or mother's report) prints 50.7. A figure that isn't in the Sokoto row, e.g. a
    value worked out from another column or the Total row's, never counts."""
    mics = D.Reading("mics-2021", "Nigeria MICS 2021", 2021, [(197, MICS_197)], national=True)
    assert D.national_ok(mics, "Sokoto", MICS_197, "85.2")
    assert not D.national_ok(mics, "Sokoto", MICS_197, "44.6")           # the Total row's
    assert not D.national_ok(mics, "Sokoto", MICS_197, "86.0")           # not printed in the row
    assert D.table_basis(MICS_197) == ("Table TC.1.3: Vaccinations by background characteristics (Valid dose "
                                       "coverage); according to vaccination records")
    c = D.Claim("service coverage", "No vaccinations", "85.2", "%", "2021", "Sokoto", "mics-2021", "MICS", 197,
                "cov_imm", "share", 2021, basis=D.table_basis(MICS_197))
    assert "basis: Table TC.1.3" in D.claims_block([c], D.phc_checklist().dimensions)
    assert "crude coverage" in " ".join(m.queries[0] for d in D.phc_checklist().dimensions for m in d.measures
                                        if m.id == "cov_imm")


def test_the_not_found_line_uses_hausa_measure_names_in_a_hausa_answer() -> None:
    dims = D.phc_checklist().dimensions
    ha = D.missing_line(D.coverage([], dims[3:4]), "ha", dims)
    assert "allurar rigakafi" in ha and "EmONC" in ha and "immunisation" not in ha
    assert "immunisation coverage" in D.missing_line(D.coverage([], dims[3:4]), "en", dims)


def test_the_same_number_from_two_findings_on_a_page_is_two_claims_and_a_denominator_isnt_repeated() -> None:
    """3 Nov live run: '26 PHCs out of 84 met the minimum human resources requirements' (ROP p. 9) was lost to
    '26 facilities to build' (MSP p. 7) by a value-only dedupe, and '84 PHCs assessed' was said instead."""
    dims = [D.phc_checklist().dimensions[0]]
    build = C("facilities and infrastructure", "26 facilities need to be constructed", "26", "gap", "fac_need", page=7)
    met = D.Claim("facilities and infrastructure", "26 PHCs out of 84 PHCs assessed met the minimum human resources "
                  "requirements", "26", "PHCs", "", "Sokoto State", "rop", "ROP", 9, "fac_need", "gap", 2023)
    assessed = D.Claim("facilities and infrastructure", "84 PHCs were assessed for DRF readiness", "84", "PHCs", "",
                       "Sokoto State", "rop", "ROP", 9, "fac_count", "detail", 2023)
    got = D.select_claims([build, met, assessed], dims)
    assert met in got and build in got and assessed not in got


def test_a_zero_coverage_figure_beside_a_non_zero_one_is_dropped_and_crude_coverage_leads() -> None:
    dims = [D.phc_checklist().dimensions[3]]
    valid = D.Claim("service coverage", "basic antigens, valid dose", "3.7", "%", "2021", "Sokoto", "mics", "MICS",
                    197, "cov_imm", "share", 2021, basis="Table TC.1.3 (Valid dose coverage); according to vaccination "
                    "records")
    zero = D.Claim("service coverage", "all 1YL antigens", "0.0", "%", "2021", "Sokoto", "mics", "MICS", 197,
                   "cov_imm", "share", 2021, basis=valid.basis)
    crude = D.Claim("service coverage", "basic antigens, crude", "7.2", "%", "2021", "Sokoto", "mics", "MICS", 190,
                    "cov_imm", "share", 2021, basis="Table TC.1.2 (Crude coverage); according to vaccination card or "
                    "mother's report")
    got = D.select_claims([valid, zero, crude], dims)
    assert zero not in got and got[0] is crude
    alone = D.select_claims([zero], dims)                                  # a zero with nothing beside it stays
    assert alone == [zero]


def test_kasafis_own_wording_prints_large_counts_with_separators() -> None:
    assert D.thousands("within a total of 11202 personnel in 2020 (MSP, p. 1234)") == \
        "within a total of 11,202 personnel in 2020 (MSP, p. 1234)"
    assert D.thousands("3395 staff, code 052100300100, ₦1,221,243,045.30, 14.8%") == \
        "3,395 staff, code 052100300100, ₦1,221,243,045.30, 14.8%"


def test_the_share_swing_is_cited_with_both_budgets() -> None:
    c = D.Claim("funding", "share moved", "92,523,418,285.85", "NGN", "2026", "Sokoto State", "budget-2026-approved",
                "Sokoto State FY 2026 Budget", 27, refs=[("Sokoto State Government 2025 Approved Budget", 19)])
    assert D.source_ref(c) == "Sokoto State FY 2026 Budget, p. 27; Sokoto State Government 2025 Approved Budget, p. 19"


def test_amounts_keep_their_space_and_house_style() -> None:
    assert D.house_amounts("₦1 NGN") == "₦1"                               # never '₦₦1'
    assert D.house_amounts("15,000,000.00 NGN allocated to renovation") == "₦15 million allocated to renovation"
    assert D.house_amounts("a target of NGN4 billion NGN in 2023") == "a target of ₦4 billion in 2023"
    assert D.merge_refs("₦7.12 billion (Budget 2026, p. 18) (Budget 2026, p. 32)") == \
        "₦7.12 billion (Budget 2026, pp. 18, 32)"


def test_the_synthesis_is_told_to_compare_like_with_like_and_what_a_difference_is() -> None:
    s = D.SYNTH_SYSTEM
    assert "5-6 plain sentences that answer the question across the dimensions" in s
    assert "same measure for the same place and period" in s and "measure different things" in s
    assert "never write that a year is not stated" in s
    dims = D.phc_checklist().dimensions
    block = D.claims_block([C("staffing", "Nurses required", "244", "target", "staff_need")], dims)
    assert "## staffing" in block and "measure: staff required" in block and "when: as of the 2020 report" in block


def test_the_agencys_money_comes_from_the_budget_and_bir_rows(conn) -> None:
    claims = D.money_claims(conn, D.phc_checklist(), "funding and spending")
    by = {(c.measure, c.kind, c.year): c for c in claims if "revised budget for" not in c.statement and
          "final budget for" not in c.statement}
    approved = by[("money_alloc", "trend", "2025")]
    assert approved.value == "13,196,854,692.00" and approved.doc_id == "budget-2025-approved" and approved.from_rows
    assert by[("money_actual", "trend", "2024")].doc_id == "bpr-2024-q4"          # the Q4 report's full year
    share = by[("money_alloc", "share", "2025")]
    assert share.calculated and share.value == "26.6%" and "calculated" in share.statement
    spent = by[("money_actual", "gap", "2025")]
    assert spent.value == "11.3%" and spent.doc_id == "bir-2025-q4"           # the final budget's share spent,
    assert "full year 2025 (Q1-Q4, from the Q4 2025 budget implementation report)" in spent.statement   # its period
    swing = next(c for c in claims if c.statement.startswith("Kasafi's calculation"))
    # 26.6% -> 5.9%: same agency code and HEALTH total both years; the Ministry of Health's capital explains it
    assert "26.6% (2025) to 5.9% (2026)" in swing.statement and "code 052100300100" in swing.statement
    assert "Ministry of Health capital" in swing.statement and swing.value == "92,523,418,285.85"
    assert "own capital went from ₦11,920,018,880.00 to ₦5,797,000,000.00" in swing.statement
    assert swing.refs[0][1] == 19 and "2025" in swing.refs[0][0]           # the 2025 share's own page
