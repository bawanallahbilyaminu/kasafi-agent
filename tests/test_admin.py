"""Admin trace page and review queue (app/admin), and the trace record (app/agent/trace.py)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.agent import trace
from app.agent.answer import Answer, Evidence, Plan
from app.agent.line_answer import LineResult, Selection
from app.config import get_settings
from app.main import app
from app.retrieval.line_search import Cell, Line
from tests.helpers import make_settings

AUTH = ("admin", "a-long-test-password")
OPEN = "meta-models/muse-spark-open-1026"


def client(**kw) -> TestClient:
    s = make_settings(**kw)
    app.dependency_overrides[get_settings] = lambda: s
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset():
    yield
    app.dependency_overrides.clear()


def test_admin_pages_do_not_exist_without_a_password() -> None:
    assert client().get("/admin/traces", auth=AUTH).status_code == 404


def test_wrong_credentials_are_refused() -> None:
    c = client(admin_user="admin", admin_password=SecretStr(AUTH[1]))
    r = c.get("/admin/traces", auth=("admin", "nope"))
    assert r.status_code == 401 and "Basic" in r.headers["www-authenticate"]


def test_a_form_post_from_another_site_is_refused() -> None:
    c = client(admin_user="admin", admin_password=SecretStr(AUTH[1]))
    r = c.post("/admin/traces/1/review?review=ok", auth=AUTH, headers={"origin": "https://evil.example"})
    assert r.status_code == 403


def _answer(readers=("muse-spark-1.3", OPEN)) -> Answer:
    line = Line("budget-2026-approved:67:1", "Sokoto State FY 2026 Budget", "budget-2026-approved", 67, "Capital",
                "Counterpart Funds <script>", "Counterpart Funds <script> | 2026 Approved Budget: 70,000,000.00",
                "project", "", "", 1.0, [Cell("2026 Approved Budget", 2026, "approved", "full_year",
                                              Decimal("70000000"))])
    res = LineResult(selections=[Selection(line, line.cells[0])], found="full", readers=list(readers))
    res.picks = [[trace_pick := f"Counterpart Funds <script> | 2026 Approved Budget: 70,000,000.00 "
                  f"(budget-2026-approved p67)"], [trace_pick]]
    return Answer("It is ₦70.00 million [1].", True, True, plan=Plan("How much for counterpart funds?",
                  [], ["budget-2026-approved"]), timings={"plan": 2.1, "answer": 3.4},
                  cited=[Evidence(1, "budget-2026-approved", "Sokoto State FY 2026 Budget", 2026, 67, "text", "")],
                  lines=res)


def test_the_trace_record_keeps_both_readings_and_flags_a_fallback() -> None:
    t = trace.record(_answer())
    assert t["lines"]["readers"] == ["muse-spark-1.3", OPEN] and len(t["lines"]["picks"]) == 2
    assert trace.flags(_answer(), "answered") == []
    assert "Muse Spark Open fell back" in trace.flags(_answer(("muse-spark-1.3", "muse-spark-1.3 (fallback)")),
                                                       "answered")
    assert trace.path(_answer()) == "lines:list"


@pytest.fixture()
def db():
    psycopg = pytest.importorskip("psycopg")
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        conn = psycopg.connect(s.db_url(), connect_timeout=3)
        if not conn.execute("SELECT to_regclass('traces')").fetchone()[0]:
            pytest.skip("traces table not migrated")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield s, conn
    conn.close()


def test_trace_page_shows_both_models_side_by_side_and_escapes_text(db) -> None:
    s, conn = db
    trace.save(conn, _answer(), "en", 6.2)
    tid = conn.execute("SELECT max(id) FROM traces").fetchone()[0]
    try:
        s = s.model_copy(update={"admin_user": "admin", "admin_password": SecretStr(AUTH[1])})
        app.dependency_overrides[get_settings] = lambda: s
        c = TestClient(app)
        r = c.get(f"/admin/traces/{tid}", auth=AUTH)
        assert r.status_code == 200 and r.headers["x-frame-options"] == "DENY"
        assert "Muse Spark · Meta Model API" in r.text and "Muse Spark Open · Baseten" in r.text
        assert "<script>" not in r.text and "&lt;script&gt;" in r.text
        assert "How much for counterpart funds?" in c.get("/admin/traces", auth=AUTH).text
        ok = c.post(f"/admin/traces/{tid}/review?review=wrong", auth=AUTH, headers={"origin": "http://testserver"},
                    follow_redirects=False)
        assert ok.status_code == 303
        assert conn.execute("SELECT review FROM traces WHERE id = %s", (tid,)).fetchone()[0] == "wrong"
        assert c.get("/admin/review", auth=AUTH).status_code == 200
    finally:
        conn.execute("DELETE FROM traces WHERE id = %s", (tid,))
        conn.commit()
