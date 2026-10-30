"""Kasafi FastAPI app: WhatsApp webhook, legal pages and health check."""

import logging
import os

from fastapi import FastAPI

from app.admin import router as admin_router
from app.legal import router as legal_router
from app.whatsapp.webhook import router as whatsapp_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


class _RedactQuery(logging.Filter):
    """Drop query strings from access logs: Meta's verify request carries the verify token in the URL."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple) and len(record.args) >= 3 and isinstance(record.args[2], str):
            path, sep, _ = record.args[2].partition("?")
            if sep:
                record.args = (*record.args[:2], f"{path}?[redacted]", *record.args[3:])
        return True


logging.getLogger("uvicorn.access").addFilter(_RedactQuery())
# httpx logs each request's full URL at INFO; ReliefWeb's appname travels in the query string
logging.getLogger("httpx").setLevel(logging.WARNING)

# No /docs, /redoc or /openapi.json in production: they list the routes and help nobody but a scanner.
app = FastAPI(title="Kasafi", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(whatsapp_router)
app.include_router(legal_router)
app.include_router(admin_router)


@app.on_event("startup")
async def _warm_line_model() -> None:
    # Load the budget-line embedding model now, not on the first user's question (a few seconds).
    import asyncio

    from app.retrieval.line_meaning import embed_queries
    asyncio.get_running_loop().run_in_executor(None, embed_queries, ["warm up"])
    asyncio.get_running_loop().run_in_executor(None, _build_missing_entities)


_crawler: set = set()


@app.on_event("startup")
async def _crawl_libraries() -> None:
    # The registry's crawled libraries (Sokoto State Bureau of Statistics): new documents indexed weekly.
    import asyncio

    from app.acquisition.crawl import crawl_weekly
    from app.config import get_settings
    s = get_settings()
    if s.has_database and os.environ.get("KASAFI_CRAWL", "true").lower() != "false":
        task = asyncio.get_running_loop().create_task(crawl_weekly(s))
        _crawler.add(task)               # keep a reference while it runs


def _build_missing_entities() -> None:
    """Budgets and reports indexed before the structured core existed get their entities (once, a few seconds)."""
    import psycopg

    from app.config import get_settings
    from app.retrieval.entities import build_missing
    s = get_settings()
    if not s.has_database:
        return
    try:
        with psycopg.connect(s.db_url(), connect_timeout=5) as conn:
            for b in build_missing(conn):
                logging.getLogger(__name__).info("entities built at startup: %s", b.summary()[:300])
    except Exception as e:      # the analysis tools then say they have no data; search still answers
        logging.getLogger(__name__).warning("entity build at startup failed: %s", type(e).__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    # Set at image build time by deploy/remote.sh, so deploys can confirm the new container is serving.
    return {"commit": os.environ.get("KASAFI_COMMIT", "unknown")}
