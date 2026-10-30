"""Multi-source topic answers: publisher choice, the number check on fact cards, and the code-written reply."""

from datetime import date, datetime

import pytest

from app.acquisition.registry import Publisher, registry
from app.agent import topics as tp
from app.agent.answer import Plan, topic_route
from tests.helpers import make_settings

DTM = Publisher("iom_dtm", "IOM Displacement Tracking Matrix (DTM)", ("dtm.iom.int",), level="lga", tier=1,
                cadence="rounds every 4-6 months", latest_known="Round 18, December 2025", verified="2026-10-29")
UNHCR = Publisher("unhcr_dashboard", "UNHCR Nigeria Forcibly Displaced Populations Dashboard", ("data.unhcr.org",),
                  level="state", tier=2, cadence="monthly (1st of month)", latest_known="1 October 2026",
                  verified="2026-10-29")
SBS = Publisher("sbs", "Durable Solutions for Displacement-Affected Communities in Sokoto Town (Sokoto State Bureau of "
                "Statistics, JIPS, DRC; endorsed by NBS)", ("sbs.sk.gov.ng",), level="town", tier=1,
                scope_note="findings cover Sokoto town only, not the whole state; say so in answers",
                verified="2026-10-29")
MPI = Publisher("mpi_context", "Sokoto State MPI 2025 (mentions IDP estimates)", tier=3)


def card(p, value, ref, geo="Sokoto State", what="IDPs", page=3):
    return tp.Card(p, p.id, f"{p.id} report", page, value, "people", what, ref, geo)


def test_publishers_state_and_lga_level_and_tier_1_first_context_apart() -> None:
    primary, related = tp.choose_publishers(registry().topics["displacement_humanitarian"])
    ids = [p.id for p in primary]
    assert 3 <= len(ids) <= 5 and "iom_dtm" in ids and "unhcr_dashboard" in ids
    assert ids.index("iom_dtm") < ids.index("unhcr_dashboard")                # tier 1 LGA before tier 2 state
    assert "ncfrmi_sema" not in ids                                            # verified: "no"
    assert {p.id for p in related} == {"sokoto_budget_context", "mpi_context"}


def test_a_card_is_kept_only_if_its_figure_is_printed_on_its_page() -> None:
    page = "Sokoto | 181,526 | Round 18\nIDPs in Sokoto town: 10 786 people (2,076 households), 64%"
    assert tp.printed_on("181,526", page) and tp.printed_on("181526", page) and tp.printed_on("10786", page)
    assert tp.printed_on("64%", page) and not tp.printed_on("181,500", page) and not tp.printed_on("6", page)


def test_reply_leads_with_the_newest_and_says_why_they_differ_never_averaging() -> None:
    sources = [tp.SourceResult(DTM, "dtm", status="ok", cards=[card(DTM, "181,526", "Round 18, Oct 2025")]),
               tp.SourceResult(UNHCR, "unhcr", status="ok", cards=[card(UNHCR, "181,526", "March 2026")]),
               tp.SourceResult(SBS, "sbs", status="ok", cards=[card(SBS, "10,786", "March 2026", "Sokoto town")])]
    text, partial = tp.compose(registry().topics["displacement_humanitarian"], sources, [], "en")
    lines = text.splitlines()
    assert lines[0].startswith("📊 Newest figure: *181,526 people*") and "March 2026" in lines[0]
    assert "the same number (181,526) appears in IOM Displacement Tracking Matrix (Round 18, Oct 2025) and UNHCR" in text
    assert "different areas" in text and "doesn't average" in text
    assert "ℹ️ Sokoto State Bureau of Statistics, JIPS, DRC: findings cover Sokoto town only, not the whole state." in text
    assert "say so" not in text and not partial


def test_related_context_goes_last_and_missing_sources_are_named() -> None:
    sources = [tp.SourceResult(DTM, "dtm", status="ok", cards=[card(DTM, "181,526", "Oct 2025")]),
               tp.SourceResult(UNHCR, status="timeout")]
    related = [tp.SourceResult(MPI, "mpi", status="ok", cards=[card(MPI, "51,000", "2025", "Sokoto metropolis")])]
    text, partial = tp.compose(registry().topics["displacement_humanitarian"], sources, related, "ha")
    assert text.index("Masu alaƙa, ba babbar majiyar") > text.index("IOM")
    assert "Ban samu ba: UNHCR Nigeria Forcibly Displaced Populations Dashboard." in text and partial


def test_nbs_labour_figures_carry_the_definition_note() -> None:
    nbs = next(p for p in registry().topics["labour_employment"].publishers if p.id == "nbs_nlfs")
    text, _ = tp.compose(registry().topics["labour_employment"],
                         [tp.SourceResult(nbs, "nlfs", cards=[card(nbs, "1.2%", "2023", what="unemployment rate")])],
                         [], "en")
    assert "ILO 2013 standard" in text and "underemployment" in text


def test_a_monthly_dashboard_must_be_this_months_and_a_report_its_newest_known_year() -> None:
    today = date(2026, 10, 29)
    assert not tp.fresh_enough(UNHCR, ("u", "t", 2026, "", "", datetime(2026, 8, 3), None), today)
    assert tp.fresh_enough(UNHCR, ("u", "t", 2026, "", "", datetime(2026, 10, 2), None), today)
    assert not tp.fresh_enough(DTM, ("d", "DTM R17", 2025, "", "", None, None), date(2026, 10, 29)) is False


@pytest.mark.parametrize("q, plan_kw, topic", [
    ("current state of IDPs in Sokoto", {"current": True}, "displacement_humanitarian"),
    ("employment statistics for Sokoto", {"statistics": True}, "labour_employment"),
    ("How much for health in 2026?", {"statistics": False}, ""),                       # budget money
    ("IDP budget lines in 2026", {"statistics": True, "line_search": {"terms": ["IDP"], "years": [2026]}}, ""),
    ("How many IDPs are in Sokoto according to IOM?",                  # the planner added line_search: no money
     {"line_search": {"terms": ["IDP"], "years": []}}, "displacement_humanitarian"),
    ("How do people in Sokoto cope?", {"statistics": True, "topic": "poverty_welfare"}, "poverty_welfare"),
])
def test_statistics_questions_on_a_multi_source_topic_take_the_topic_path(q: str, plan_kw: dict, topic: str) -> None:
    assert topic_route(q, Plan(q, [q], [], **plan_kw)) == topic


def test_partner_hints_only_give_websites_to_search(tmp_path, monkeypatch) -> None:
    hints = tmp_path / "hints.json"
    hints.write_text('{"partners": [{"name": "A Partner", "website": "a.org", "likely_publishes_reports": true, '
                     '"topics": ["nutrition_food_security"]}, {"name": "B", "website": null, "topics": []}]}',
                     encoding="utf-8")
    monkeypatch.setattr(tp, "HINTS_PATH", hints)
    assert tp.hint_sites("nutrition_food_security") == ["a.org"] and tp.hint_sites("health") == []
    monkeypatch.setattr(tp, "HINTS_PATH", tmp_path / "missing.json")
    assert tp.hint_sites("nutrition_food_security") == []                     # works without the file


class FakeConn:
    """documents rows: (id, title, year, source_url, final_url, fetched_at, edition)."""

    def __init__(self, docs):
        self.docs = docs

    def execute(self, sql, params=()):
        rows = self.docs
        if "source_url, final_url FROM documents WHERE id" in sql:
            rows = [(d[3], d[4]) for d in self.docs if d[0] in params[0]]
        return type("R", (), {"fetchall": lambda _s: rows, "fetchone": lambda _s: rows[0] if rows else None})()


MPI_DOC = ("mpi-2025-sokoto", "Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025", 2025,
           "https://mof.sk.gov.ng/MPI.pdf", None, None, None)
SBS_DOC = ("durable-solutions-2026-sokoto", "Durable Solutions ... Sokoto Town", 2026,
           "https://sbs.sk.gov.ng/api/documents/durable-solutions-report-jips-drc-sbs/download", None, None, None)


def test_an_idp_count_from_the_mpi_is_said_not_to_be_a_primary_source() -> None:
    from app.agent.answer import Evidence, off_topic_note
    plan = Plan("How many IDPs are in Sokoto now?", ["IDPs"], [], current=True)
    cited = [Evidence(1, MPI_DOC[0], MPI_DOC[1], 2025, 40, "text", "")]
    note = off_topic_note(FakeConn([MPI_DOC]), plan, plan.english_question, cited, "en")
    assert note.startswith("⚠️ Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025 isn't a primary source")
    cited = [Evidence(1, SBS_DOC[0], SBS_DOC[1], 2026, 12, "text", "")]
    assert off_topic_note(FakeConn([MPI_DOC, SBS_DOC]), plan, plan.english_question, cited, "en") == ""


def test_quoting_the_durable_solutions_report_says_it_covers_sokoto_town_only() -> None:
    from app.agent.answer import Evidence, scope_notes
    cited = [Evidence(1, SBS_DOC[0], SBS_DOC[1], 2026, 12, "text", "")]
    assert "findings cover Sokoto town only, not the whole state" in scope_notes(FakeConn([SBS_DOC]), cited)


@pytest.mark.parametrize("q, ids", [
    ("How many IDPs in Sokoto according to IOM?", ["iom_dtm"]),
    ("what do unhcr figures say about displaced people", ["unhcr_dashboard"]),
    ("Did aid reach the displaced people in Sokoto?", []),
    ("What does the REACH assessment say?", ["reach_impact"]),
    ("current state of IDPs in Sokoto", []),
])
def test_a_question_naming_a_publisher_is_answered_from_it(q: str, ids: list) -> None:
    assert [p.id for p in tp.named_publishers(registry().topics["displacement_humanitarian"], q)] == ids


def test_a_rate_keeps_its_percent_sign() -> None:
    nbs = next(p for p in registry().topics["labour_employment"].publishers if p.id == "nbs_nlfs")
    c = tp.Card(nbs, "nlfs", "NLFS 2023", 258, "1.2", "%", "unemployment rate", "2023", "Sokoto State")
    text, _ = tp.compose(registry().topics["labour_employment"], [tp.SourceResult(nbs, "nlfs", cards=[c])], [], "en")
    assert "*1.2%*" in text


def test_a_publisher_that_just_failed_isnt_searched_again_for_12_hours(monkeypatch) -> None:
    import asyncio
    import time as t
    calls = []

    async def fake(conn, p, topic, today, res, fetch, http, client, settings):
        calls.append(p.id)
        res.status, res.detail = "not_found", "7 candidates, none matched"
        return res
    monkeypatch.setattr(tp, "_get_document", fake)
    monkeypatch.setattr(tp, "local_documents", lambda conn, p: [])
    tp._missed.clear()
    topic = registry().topics["displacement_humanitarian"]
    go = lambda: asyncio.run(tp.get_document(None, DTM, topic, date(2026, 10, 30), http=None, robots=None,
                                            client=None, settings=None))
    assert go().status == "not_found" and go().detail.endswith("(tried within 12 h)") and calls == ["iom_dtm"]
    tp._missed["iom_dtm"] = (t.time() - 13 * 3600, "not_found", "")
    go()
    assert calls == ["iom_dtm", "iom_dtm"]
    tp._missed.clear()


def test_dtm_figures_come_from_its_api_with_round_date_and_top_lgas(monkeypatch, tmp_path) -> None:
    import asyncio
    from app.sources import dtm
    rounds = [dtm.RoundFigure("Sokoto", 18, "2025-10-31", 181526, {}), dtm.RoundFigure("Sokoto", 17, "2025-05-31", 88562, {})]
    lgas = [dtm.RoundFigure(n, 18, "2025-10-31", v, {}) for n, v in (("Sabon Birni", 40729), ("Tangaza", 19151))]

    async def state(http, s, st):
        return rounds

    async def lga(http, s, st, r):
        return lgas
    monkeypatch.setattr(dtm, "state_rounds", state)
    monkeypatch.setattr(dtm, "lga_round", lga)
    tp._api_cache.clear()
    src = asyncio.run(tp.dtm_api_source(DTM, None, make_settings(kasafi_fetch_dir=str(tmp_path))))
    tp._api_cache.clear()
    assert [c.value for c in src.cards] == ["181,526", "40,729", "88,562"]
    assert src.cards[0].ref_date == "Round 18, reporting date 2025-10-31" and not src.cards[0].doc_id
    assert src.cards[1].what == "in Sabon Birni, the most of its 2 LGAs (then Tangaza 19,151)"


def test_figures_that_are_dtm_counts_are_said_to_be_so_and_the_newest_leads() -> None:
    api = tp.Card(DTM, "", "IOM DTM API (Baseline)", 0, "181,526", "IDPs", "IDPs", "Round 18, reporting date 2025-10-31")
    unhcr = tp.Card(UNHCR, "u", "UNHCR dashboard", 1, "176,099", "individuals", "IDPs", "1 October 2026",
                    based_on="IOM DTM R19")
    sbs = tp.Card(SBS, "s", "Durable Solutions", 12, "over 181,500", "people", "IDPs", "early 2026",
                  based_on="UNHCR and NCFRMI (2026)")                   # cites UNHCR, which cites DTM
    sources = [tp.SourceResult(p, cards=[c]) for p, c in ((SBS, sbs), (DTM, api), (UNHCR, unhcr))]
    text, _ = tp.compose(registry().topics["displacement_humanitarian"], sources, [], "en")
    lines = [l for l in text.splitlines() if l.startswith("• ")]
    assert text.startswith("📊 Newest figure: *176,099 individuals*")
    # a figure the page says is another publisher's is labelled as that publisher's, as cited in the document
    assert [l.split(":")[0] for l in lines] == [
        "• IOM DTM R19, as cited in UNHCR Nigeria Forcibly Displaced Populations Dashboard",
        "• IOM Displacement Tracking Matrix",
        "• UNHCR and NCFRMI (2026), as cited in Sokoto State Bureau of Statistics, JIPS, DRC"]
    assert ("the statewide figures of Sokoto State Bureau of Statistics, JIPS, DRC (over 181,500, via UNHCR Nigeria "
            "Forcibly Displaced Populations Dashboard) / UNHCR Nigeria Forcibly Displaced Populations Dashboard "
            "(176,099, R19) are IOM Displacement Tracking Matrix counts, not separate counts") in text
    assert "These are separate counts" not in text and "IOM DTM API (Baseline)" in text.splitlines()[-1]


def test_an_api_outage_uses_the_last_good_pull_with_its_date(monkeypatch, tmp_path) -> None:
    import asyncio
    from app.sources import dtm
    s = make_settings(dtmapi_subscription_key="k", kasafi_fetch_dir=str(tmp_path))
    good = [dtm.RoundFigure("Sokoto", 18, "2025-10-31", 181526, {"Conflict/violence": 173004})]

    async def ok(http, st, state):
        return good

    async def lgas(http, st, state, r):
        return []

    async def down(http, st, state):
        raise dtm.DtmError("API error: No Country found matching your query.")
    monkeypatch.setattr(dtm, "lga_round", lgas)
    monkeypatch.setattr(dtm, "state_rounds", ok)
    tp._api_cache.clear()
    asyncio.run(tp.dtm_api_source(DTM, None, s))                      # a good pull is kept on disk
    monkeypatch.setattr(dtm, "state_rounds", down)
    tp._api_cache.clear()
    src = asyncio.run(tp.dtm_api_source(DTM, None, s))
    tp._api_cache.clear()
    assert src.status == "ok" and src.cards[0].value == "181,526" and "as pulled on" in src.cards[0].title


# --- multi-source reasoning: measures, primary sources, named publishers, changes -------------------------------

NBS_MPI = Publisher("nbs_mpi", "NBS Nigeria Multidimensional Poverty Index (MPI) 2022", ("nigerianstat.gov.ng",),
                    level="state", tier=1)
SBS_MPI = Publisher("sokoto_mpi", "Sokoto State Bureau of Statistics (SBS) Sokoto State Multidimensional Poverty "
                    "Index (MPI) Report 2025", level="lga", tier=1)
DS = Publisher("sokoto_sbs", "Sokoto State Bureau of Statistics (state surveys and co-published reports)",
               ("sbs.sk.gov.ng",), level="lga", tier=1)


def mpi(p, value, ref, measure, what, based_on="", page=13, doc=None):
    return tp.Card(p, doc or p.id, f"{p.id} report", page, value, "", what, ref, "Sokoto State", "", based_on,
                   measure)


def test_the_kind_of_number_is_checked_against_what_is_printed() -> None:
    assert tp.measure_of("0.239", "", "index") == "index" and tp.measure_of("0.239", "", "") == "index"
    assert tp.measure_of("59.1%", "", "index") == "rate"          # a % is never a 0-1 index
    assert tp.measure_of("59.1%", "%", "headcount") == "headcount" and tp.measure_of("59.1", "", "headcount") == \
        "headcount"
    assert tp.measure_of("0.591", "", "headcount") == "other"     # a fraction or an index: unclear, never compared
    assert tp.measure_of("181,526", "people", "count") == "count"


def test_a_document_is_its_publishers_by_two_title_words_and_its_place() -> None:
    nbs_cpi = ("nbs-cpi-2026-09", "Consumer Price Index (CPI) September 2026", 2026, "https://nigerianstat.gov.ng/download/1",
               None, None, None)
    nbs_mpi = ("nbs-mpi-2022", "Nigeria Multidimensional Poverty Index (2022)", 2022,
               "https://nigerianstat.gov.ng/download/1241254", None, None, None)
    ophi = ("mpi-2026-sokoto", "The global Multidimensional Poverty Index (MPI) 2026: Disaggregation results", 2026,
            "https://ophi.org.uk/x.pdf", None, None, None)
    sbs = ("mpi-2025-sokoto", "Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025", 2025,
           "https://mof.sk.gov.ng/MPI.pdf", None, None, None)

    class Conn:
        def execute(self, *a):
            return type("R", (), {"fetchall": lambda _: [nbs_cpi, nbs_mpi, ophi, sbs]})()
    assert [r[0] for r in tp.local_documents(Conn(), NBS_MPI)] == ["nbs-mpi-2022"]     # not the CPI ('Index')
    assert [r[0] for r in tp.local_documents(Conn(), SBS_MPI)] == ["mpi-2025-sokoto"]  # not OPHI's global note


def test_each_named_publisher_is_required_and_the_topic_word_names_none() -> None:
    topic = registry().topics["poverty_welfare"]
    q = "According to NBS what is Sokoto's MPI, and according to SBS how much has it improved?"
    assert [p.id for p in tp.named_publishers(topic, q)] == ["sokoto_mpi", "nbs_mpi"]
    assert [p.id for p in tp.named_publishers(registry().topics["displacement_humanitarian"],
                                               "How many IDPs according to IOM?")] == ["iom_dtm"]


def test_a_quoted_figure_is_labelled_as_its_publishers_and_its_primary_source_is_sought() -> None:
    quoted = mpi(DS, "91%", "2022", "headcount", "multidimensional poverty incidence", based_on="NBS MPI 2022",
                 doc="durable-solutions-2026-sokoto", page=12)
    sources = [tp.SourceResult(DS, "durable-solutions-2026-sokoto", status="ok", cards=[quoted])]
    assert tp.source_label(quoted, "en") == "NBS MPI 2022, as cited in Sokoto State Bureau of Statistics"
    assert tp.card_year(quoted) == 2022
    assert [p.id for p in tp.primary_sources(registry().topics["poverty_welfare"], sources)] == ["nbs_mpi"]


def test_a_change_is_computed_between_the_same_measure_with_a_comparability_note() -> None:
    cards = [mpi(NBS_MPI, "0.409", "2022", "index", "MPI value", page=123),
             mpi(NBS_MPI, "90.5", "2022", "headcount", "incidence (H, %)", page=123),
             mpi(SBS_MPI, "0.239", "2025", "index", "MPI value"),
             mpi(SBS_MPI, "59.1%", "2025", "headcount", "multidimensionally poor")]
    sources = [tp.SourceResult(NBS_MPI, "nbs", status="ok", cards=cards[:2]),
               tp.SourceResult(SBS_MPI, "sbs", status="ok", cards=cards[2:])]
    text, _ = tp.compose(registry().topics["poverty_welfare"], sources, [], "en",
                         "According to NBS what is Sokoto's MPI, and according to SBS how much has it improved?")
    assert "📈 Change in the index value, 0–1: 0.409 (NBS Nigeria Multidimensional Poverty Index, 2022) → 0.239" in text
    assert "down by 0.17 (41.6% of the earlier value)" in text
    assert "📈 Change in the headcount, % of people: 90.5" in text and "down by 31.4 percentage points" in text
    assert text.count("are different surveys") == 2 and "different measures (index value, 0–1; headcount" in text
    # never an index against a %: no change line mixes them, and no 'why they differ' line compares them
    assert "0.239 (" not in text.split("headcount, % of people:")[-1]
    no_pair = tp.change_lines([cards[0], cards[3]], "how much has it improved?", "en")
    assert no_pair == [tp.W["en"]["no_change"]]
    assert tp.change_lines(cards, "What is Sokoto's MPI?", "en") == []          # not a change question


def test_the_text_before_a_figure_says_whose_it_is() -> None:
    topic = registry().topics["poverty_welfare"]
    sbs_p17 = ("The findings of the 2022 National MPI were sobering for Sokoto State. The report identified that 63% "
               "of persons were poor, but in Sokoto State, the incidence of poverty surged to 91%, the highest.")
    assert tp.quoted_from("91%", sbs_p17, topic, SBS_MPI, 2025) == "NBS Nigeria Multidimensional Poverty Index 2022"
    ds_p12 = "According to the 2022 Nigeria Multidimensional Poverty Index, Sokoto State recorded an incidence at 91%."
    assert tp.quoted_from("91%", ds_p12, topic, DS, 2026).startswith("NBS Nigeria")
    own = "While the NBS 2022 National MPI is the benchmark, this 2025 report finds a headcount of 59.1%."
    assert tp.quoted_from("59.1%", own, topic, SBS_MPI, 2025) == ""            # the report's own figure
    partners = "Prepared with OPHI and UNDP support. The state MPI value is 0.239."
    assert tp.quoted_from("0.239", partners, topic, SBS_MPI, 2025) == ""       # a partner named, no report quoted
    assert tp.SOKOTO_ROW.search("Rivers 0.241 0.219 0.264 Sokoto 0.409 0.391 0.427 90.5")


def test_a_quote_of_a_figure_shown_from_its_source_is_dropped_and_the_source_not_missed() -> None:
    nbs_own = mpi(NBS_MPI, "91%", "2022", "headcount", "incidence", page=16)
    quote = mpi(DS, "91%", "2022", "headcount", "incidence", based_on="NBS MPI 2022", page=12)
    sources = [tp.SourceResult(NBS_MPI, "nbs", status="ok", cards=[nbs_own]),
               tp.SourceResult(DS, "ds", status="ok", cards=[quote])]
    text, _ = tp.compose(registry().topics["poverty_welfare"], sources, [], "en")
    assert "as cited in" not in text and "Couldn't get" not in text


def test_only_the_same_measure_of_the_same_population_is_compared() -> None:
    assert tp.population_of("all", "Child MPI Value") == "children"
    assert tp.population_of("children under 5", "MPI") == "children" and tp.population_of("all", "MPI value") == "all"
    assert tp.measure_of("0.40328", "index 0-1", "index", "Intensity of Poverty (A)") == "other"   # not an MPI value
    assert tp.measure_of("0.415", "", "index", "Child MPI Value: incidence x intensity") == "index"
    assert tp.measure_of("59.1%", "", "rate", "Headcount Ratio (H)") == "headcount"
    assert tp.measure_of("0.409", "", "index", "Multidimensional Poverty Index (MPI) - The share of possible "
                         "deprivations ... computed by multiplying 'Incidence' by 'Intensity'") == "index"
    assert tp.measure_of("5.81 million people", "people", "headcount", "Number of poor - the number of people "
                         "who are multidimensionally poor") == "count"
    assert tp.card_year(mpi(NBS_MPI, "0.409", "2021/22", "index", "MPI")) == 2022
    child = mpi(NBS_MPI, "0.415", "2022", "index", "Child MPI value", page=148)
    child.population = "children"
    sbs = mpi(SBS_MPI, "0.239", "2025", "index", "MPI value")
    sbs.population = "all"
    assert tp.change_lines([child, sbs], "how much has it improved?", "en") == [tp.W["en"]["no_change"]]
    state = mpi(NBS_MPI, "0.409", "2022", "index", "MPI value", page=123)
    state.population = "all"
    assert "0.409 (NBS" in tp.change_lines([child, state, sbs], "how much has it improved?", "en")[0]


def test_a_source_already_answering_is_not_sought_again() -> None:
    quote = mpi(SBS_MPI, "91%", "2022", "headcount", "incidence", based_on="NBS Nigeria Multidimensional Poverty "
                "Index 2022", page=17)
    sources = [tp.SourceResult(SBS_MPI, "sbs", status="ok", cards=[quote]),
               tp.SourceResult(NBS_MPI, "nbs", status="ok", cards=[])]
    sources[1].publisher = registry().topics["poverty_welfare"].publishers[2]          # nbs_mpi, as the registry has it
    assert tp.primary_sources(registry().topics["poverty_welfare"], sources) == []      # not NBS's poverty report


def test_the_state_table_is_read_before_a_summary_or_a_childrens_table() -> None:
    text = {16: "Poverty ranges from 27% in Ondo to 91% in Sokoto.",
            148: "Appendix: Child MPI Incidence Intensity Value ... Rivers 0.291 Sokoto 0.415 0.400 0.429 96.7",
            123: "Appendix D: Tables State MPI Incidence (H, %) Intensity (A, %) Value ... Sokoto 0.409 0.391 0.427 90.5",
            9: "Foreword"}
    assert tp.page_order(text, "What is Sokoto's MPI value?")[:3] == [123, 148, 16]
    assert tp.page_order(text, "What is the child MPI in Sokoto?")[0] == 148


def test_sources_without_a_common_measure_are_each_asked_for_the_others() -> None:
    nbs = tp.SourceResult(NBS_MPI, "nbs", status="ok", cards=[mpi(NBS_MPI, "91%", "2022", "headcount", "incidence")])
    sbs = tp.SourceResult(SBS_MPI, "sbs", status="ok", cards=[mpi(SBS_MPI, "0.239", "2025", "index", "MPI value")])
    for c in nbs.cards + sbs.cards:
        c.population = "all"
    asks = dict((s.publisher.id, want) for s, want in tp.align_wants([nbs, sbs]))
    assert asks == {"nbs_mpi": tp.WANT["index"], "sokoto_mpi": tp.WANT["headcount"]}
    sbs.cards.append(mpi(SBS_MPI, "59.1%", "2025", "headcount", "headcount"))
    sbs.cards[-1].population = "all"
    assert tp.align_wants([nbs, sbs]) == []                   # a common measure: nothing more to ask
    assert tp.across_sources("how much has it improved?") and tp.across_sources("compare NBS and SBS")
    assert not tp.across_sources("What is Sokoto's MPI?")


def test_a_follow_up_naming_a_source_is_a_source_hint() -> None:
    from app.agent.answer import names_source
    assert names_source("poverty_welfare", "There's an NBS MPI report from 2022")
    assert names_source("poverty_welfare", "Check the 2022 survey report")
    assert not names_source("poverty_welfare", "thanks, and in Hausa?")
