"""Kasafi FastAPI app: WhatsApp webhook and health check."""

import logging

from fastapi import FastAPI

from app.whatsapp.webhook import router as whatsapp_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Kasafi", version="0.1.0")
app.include_router(whatsapp_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
