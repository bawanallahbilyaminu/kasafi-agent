from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    resp = TestClient(app).get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_version_reports_build_commit(monkeypatch) -> None:
    monkeypatch.setenv("KASAFI_COMMIT", "abc1234")
    assert TestClient(app).get("/version").json() == {"commit": "abc1234"}


def test_db_url_built_from_password_and_host() -> None:
    from pydantic import SecretStr

    from app.config import Settings
    s = Settings(_env_file=None, postgres_password=SecretStr("p@ss/w:rd"), postgres_host="db")
    assert s.db_url() == "postgresql://kasafi:p%40ss%2Fw%3Ard@db:5432/kasafi"      # special chars escaped
    assert s.db_url("psycopg").startswith("postgresql+psycopg://")
    assert Settings(_env_file=None, postgres_password=SecretStr("x")).db_url().endswith("@127.0.0.1:5432/kasafi")
    assert Settings(_env_file=None, database_url=SecretStr("postgresql+psycopg://u:p@h/d")).db_url() == "postgresql://u:p@h/d"
    assert not Settings(_env_file=None).has_database


def test_api_docs_are_not_public() -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    c = TestClient(app)
    assert all(c.get(p).status_code == 404 for p in ("/docs", "/redoc", "/openapi.json"))
