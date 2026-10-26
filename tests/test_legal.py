import pytest
from fastapi.testclient import TestClient

from app import legal
from app.config import Settings
from app.data_rights import DELETED_REPLY, is_delete_command
from app.main import app
from app.whatsapp.webhook import echo_reply


@pytest.mark.parametrize("path", ["/privacy", "/data-deletion"])
def test_pages_render_without_placeholders(path: str) -> None:
    r = TestClient(app).get(path)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html")
    assert "$" not in r.text  # every template variable substituted
    assert "Nigeria Data Protection" in r.text and "GOGE BAYANAI" in r.text


def test_contact_email_shown_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(legal, "get_settings", lambda: Settings(_env_file=None, privacy_contact_email="a@b.example"))
    assert 'mailto:a@b.example' in TestClient(app).get("/privacy").text


@pytest.mark.parametrize("text", ["GOGE BAYANAI", "goge bayanai!", " Delete my data. ", "Goge bayanaina"])
def test_delete_command_variants(text: str) -> None:
    assert is_delete_command(text)
    assert echo_reply({"type": "text", "from": "0000000000", "text": {"body": text}}) == DELETED_REPLY


def test_question_mentioning_delete_is_not_a_command() -> None:
    assert not is_delete_command("Me yasa aka goge bayanai a kasafin 2025?")
