"""Legal pages: /privacy, /data-deletion and /terms redirect to the published site.

The live pages (registered in the Meta app) are on halalnumeriq.com.ng/kasafi.
docs/site/*.md is the version-controlled copy of their text. If behaviour changes
(retention, providers, the delete command), update both.
"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import get_settings

router = APIRouter()
PAGES = ("privacy", "data-deletion", "terms")


def _redirect(page: str) -> RedirectResponse:
    return RedirectResponse(f"{get_settings().legal_site_url.rstrip('/')}/{page}", status_code=307)


for _page in PAGES:
    router.add_api_route(f"/{_page}", lambda p=_page: _redirect(p), methods=["GET"], include_in_schema=False)
