"""Public legal pages needed to publish the Meta app: /privacy and /data-deletion.

Plain English, written for the Nigeria Data Protection Act 2023 (NDPA). Each
page states what Kasafi actually does, so if behaviour changes (retention, providers,
the delete command) the page must change with it.
"""

from html import escape
from pathlib import Path
from string import Template

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.config import get_settings

router = APIRouter()
_DIR = Path(__file__).parent
LAST_UPDATED = "27 October 2026"


def _contact_html() -> str:
    email = get_settings().privacy_contact_email
    whatsapp = 'send <strong>GOGE BAYANAI</strong> or <strong>DELETE MY DATA</strong> to Kasafi on WhatsApp'
    if email:
        e = escape(email)
        return f'email <a href="mailto:{e}">{e}</a>, or {whatsapp}'
    return whatsapp


def _render(name: str) -> str:
    page = Template((_DIR / name).read_text(encoding="utf-8"))
    style = (_DIR / "style.css").read_text(encoding="utf-8")
    return page.substitute(style=style, contact=_contact_html(), updated=LAST_UPDATED)


@router.get("/privacy", response_class=HTMLResponse)
def privacy() -> str:
    return _render("privacy.html")


@router.get("/data-deletion", response_class=HTMLResponse)
def data_deletion() -> str:
    return _render("data-deletion.html")
