"""Multi-source topic answers: publisher choice, the number check on fact cards, and the code-written reply."""

from datetime import date, datetime

import pytest

from app.acquisition.registry import Publisher, registry
from app.agent import topics as tp
from app.agent.answer import Plan, topic_route

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
