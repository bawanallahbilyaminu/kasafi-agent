"""Kasafi FastAPI app: WhatsApp webhook (coming next) and health check."""

from fastapi import FastAPI

app = FastAPI(title="Kasafi", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
