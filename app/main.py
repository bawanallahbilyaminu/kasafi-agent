"""Kasafi FastAPI app: WhatsApp webhook, legal pages and health check."""

import logging
import os

from fastapi import FastAPI

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

app = FastAPI(title="Kasafi", version="0.1.0")
app.include_router(whatsapp_router)
app.include_router(legal_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    # Set at image build time by deploy/remote.sh, so deploys can confirm the new container is serving.
    return {"commit": os.environ.get("KASAFI_COMMIT", "unknown")}
