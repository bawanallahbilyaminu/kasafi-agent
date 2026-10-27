from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    resp = TestClient(app).get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_version_reports_build_commit(monkeypatch) -> None:
    monkeypatch.setenv("KASAFI_COMMIT", "abc1234")
    assert TestClient(app).get("/version").json() == {"commit": "abc1234"}
