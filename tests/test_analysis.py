"""Analysis tools on the structured budget core (app/agent/analysis.py) and their plain-language replies."""

import asyncio
from decimal import Decimal

import pytest

from app.agent import analysis as an
from app.agent import answer as ans
from app.agent.answer import Plan
from tests.helpers import make_settings
from tests.test_answer import FakeClient


def test_planner_analysis_field_keeps_only_known_tools_and_fields() -> None:
    assert ans._analysis_field({"tool": "project_status", "status": "started", "year": "2026", "terms": ["school"],
                                "sql": "DROP TABLE"}) == {"tool": "project_status", "status": "started",
                                                          "year": 2026, "terms": ["school"]}
    assert ans._analysis_field({"tool": "delete_everything"}) == {}
    assert ans._analysis_field(None) == {}


def test_a_project_named_after_another_lga_is_noted_not_dropped() -> None:
    lgas = {"TAMBUWAL", "BINJI", "SOKOTO SOUTH", "SOKOTO NORTH", "KEBBE"}
    assert an.other_lga("Completion of Premier Hospital at Binji LGA", "TAMBUWAL", lgas) == "Binji"
    assert an.other_lga("Completion of Premier Hospital at Tambuwal LGA", "TAMBUWAL", lgas) == ""
    assert an.other_lga("Construction of New Abdullahi Bara'u Secondary School D/Daji", "TAMBUWAL", lgas) == ""
    assert an.other_lga("Renovation of Sultan Abubakar College, Sokoto South", "TAMBUWAL", lgas) == "Sokoto South"


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


def test_project_status_groups_are_counted_in_sql_and_consistent(conn) -> None:
    """'Ayyuka nawa aka fara a 2025 kuma suke ci gaba a 2026?': the 2026 budget's own 2025 columns."""
    r = an.run_analysis(conn, {"tool": "project_status", "status": "started", "year": 2026})
    n = {k: v.value for k, v in r.facts.items() if v.kind == "count"}
    assert (r.year, r.prev, r.focus) == (2026, 2025, "started")
    assert n["n_started"] + n["n_idle"] == n["n_continuing"]                  # every continuing one is one of these
    assert n["n_continuing"] + n["n_new"] == n["n_all"]
    direct = conn.execute("SELECT count(*), sum(approved_2026) FROM projects WHERE doc_id = 'budget-2026-approved' "
                          "AND jan_sep_2025 > 0 AND approved_2026 > 0").fetchone()
    assert n["n_started"] == direct[0] and r.facts["started_cur"].value == direct[1]
    assert all(row.detail["spent"] > 0 and row.detail["budget"] > 0 for row in r.rows)


def test_lga_projects_are_only_lines_located_in_that_lga(conn) -> None:
    """'Wadanne ayyuka ne za a yi a Tambuwal?': location 33331800 TAMBUWAL only, statewide ones counted apart."""
    r = an.run_analysis(conn, {"tool": "lga_projects", "lga": "Tambuwal", "year": 2026})
    assert r.found and r.subject == "Tambuwal"
    places = {p for (p,) in conn.execute("SELECT DISTINCT location_name FROM projects WHERE doc_id = "
                                         "'budget-2026-approved' AND name = ANY(%s)", ([x.name for x in r.rows],))}
    assert "TAMBUWAL" in places
    n, total = conn.execute("SELECT count(*), sum(approved_2026) FROM projects WHERE doc_id = 'budget-2026-approved' "
                            "AND location_code = '33331800' AND approved_2026 > 0").fetchone()
    assert r.facts["n"].value == n and r.facts["cur"].value == total
    assert r.facts["statewide_n"].value > 500                                  # not split by LGA, so not counted
    binji = [x for x in r.rows if "Binji" in x.name]
    assert binji and binji[0].detail["other_lga"] == "Binji"                   # filed under Tambuwal by the budget
    a = ans.analysis_answer(conn, Plan("q", [], [], analysis={"tool": "lga_projects"}), r, "en", {}, None)
    assert "Completion of Premier Hospital at Binji LGA: ₦2.00 billion (the budget files it under Tambuwal)" in a.text


def test_an_unknown_lga_or_ministry_finds_nothing_rather_than_something_else(conn) -> None:
    assert an.run_analysis(conn, {"tool": "lga_projects", "lga": "Ikeja"}).reason == "no_lga"
    assert an.run_analysis(conn, {"tool": "mda_profile", "mda": "Ministry of Space Travel"}).reason == "no_mda"


def test_mda_profile_separates_allocation_from_spending(conn) -> None:
    r = an.run_analysis(conn, {"tool": "mda_profile", "mda": "Ministry of Health", "year": 2026})
    f = {k: v.value for k, v in r.facts.items()}
    assert f["total"] == Decimal("124405118574.90")                           # 052100000000, with its agencies
    assert f["personnel"] + f["overhead"] + f["capital"] + f.get("debt", 0) == f["total"]
    assert r.facts["cur_spent"].doc_id.startswith("bir-2026") and r.facts["prev_spent"].doc_id == "bir-2025-q4"


def test_reply_leads_in_plain_words_counts_have_no_naira_and_one_sources_line(conn) -> None:
    r = an.run_analysis(conn, {"tool": "project_status", "status": "started", "year": 2026})
    plan = Plan("How many projects started in 2025 continue in 2026?", [], [],
                analysis={"tool": "project_status", "status": "started"})
    a = ans.analysis_answer(conn, plan, r, "ha", {}, None)
    n = r.facts["n_started"].value
    assert a.text.startswith(f"Ayyuka {n} ne aka kashe musu kuɗi a 2025") and f"₦{n}" not in a.text
    assert "an ware musu ₦" in a.text and "an kashe ₦" in a.text             # allocated and spent, said apart
    assert "“An fara” a nan yana nufin an kashe kuɗi a kan aikin a Janairu–Satumba 2025" in a.text  # the definition
    assert f"ayyuka {r.facts['n_continuing'].value} na kasafin 2025 suna ci gaba" in a.text   # the wider count too
    assert a.text.count("Madogara") == 1 and "nuna lissafi" in a.text
    assert "🧮" not in a.text and "started: jan_sep_2025 > 0" in a.working     # the working only on request
    assert len([x for x in a.text.splitlines() if x.startswith("• ")]) <= 5


def test_planned_analysis_answers_without_a_compose_call(monkeypatch) -> None:
    plan = {"english_question": "Which projects are in Tambuwal?", "search_queries": ["Tambuwal projects"],
            "doc_ids": ["budget-2026-approved"], "analysis": {"tool": "lga_projects", "lga": "Tambuwal"}}
    res = an.AnalysisResult("lga_projects", True, 2026, 2025, "Tambuwal", titles={"b": "Budget"})
    for k, v in {"n": 2, "n_prev": 0, "statewide_n": 10}.items():
        res.facts[k] = an.Fact(v, "count", "b", 61)
    for k, v in {"cur": "3000000000.00", "prev": "0", "spent": "0", "statewide_cur": "9000000000.00"}.items():
        res.facts[k] = an.Fact(Decimal(v), "money", "b", 61)
    res.rows = [an.Row("Completion of Premier Hospital at Tambuwal LGA", Decimal("1500000000.00"), "b", 67)]
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "budget-2026-approved", "title": "t"}])
    monkeypatch.setattr(ans, "run_analysis", lambda conn, spec: res)
    fake = FakeClient([plan])
    a = asyncio.run(ans.answer_question("Wadanne ayyuka ne za a yi a Tambuwal?", "en", conn=None,
                                        settings=make_settings(), client_factory=lambda s: fake))
    assert len(fake.calls) == 1                                                 # the planner only
    assert a.text.startswith("The 2026 budget has 2 projects located in Tambuwal, with ₦3.00 billion allocated.")
    assert "not the local government's own allocation" in a.text and "• Completion of Premier Hospital" in a.text
    assert "📄 *Sources:* Budget, p. 61, 67" in a.text
