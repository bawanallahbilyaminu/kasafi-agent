import pytest
from fastapi.testclient import TestClient

from app.data_rights import DELETED_REPLY, is_delete_command
from app.main import app
from tests.helpers import run_handle

SITE = "https://halalnumeriq.com.ng/kasafi"


@pytest.mark.parametrize("page", ["privacy", "data-deletion", "terms"])
def test_legal_routes_redirect_to_published_site(page: str) -> None:
    r = TestClient(app).get(f"/{page}", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == f"{SITE}/{page}"


@pytest.mark.parametrize("text", ["GOGE BAYANAI NA", "goge bayanai na!", "Goge bayanaina", " Delete my data. "])
def test_delete_command_variants(text: str) -> None:
    assert is_delete_command(text)
    outs, _ = run_handle({"type": "text", "from": "2340000000001", "text": {"body": text}})
    assert [o.text for o in outs] == [DELETED_REPLY]


def test_question_mentioning_delete_is_not_a_command() -> None:
    assert not is_delete_command("Me yasa aka goge bayanai a kasafin 2025?")


def test_site_pages_match_delete_commands() -> None:
    from pathlib import Path
    page = Path("docs/site/data-deletion.md").read_text(encoding="utf-8")
    assert is_delete_command("GOGE BAYANAI NA") and "GOGE BAYANAI NA" in page and "DELETE MY DATA" in page
