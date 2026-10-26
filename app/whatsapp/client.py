"""WhatsApp Cloud API: send messages.

POST https://graph.facebook.com/<version>/<phone_number_id>/messages with
`Authorization: Bearer <WHATSAPP_TOKEN>` (developers.facebook.com, "Text messages").
"""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings

log = logging.getLogger(__name__)
GRAPH_URL = "https://graph.facebook.com"


def mask_phone(number: str) -> str:
    """For logs only: keep the last 2 digits."""
    return f"…{number[-2:]}" if number else "?"


class WhatsAppClient:
    def __init__(self, settings: Settings | None = None, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
        settings = settings or get_settings()
        if settings.whatsapp_token is None or not settings.whatsapp_phone_number_id:
            raise RuntimeError("WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID must be set (see .env.example)")
        self._http = httpx.AsyncClient(
            base_url=f"{GRAPH_URL}/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}",
            headers={"Authorization": f"Bearer {settings.whatsapp_token.get_secret_value()}"},
            timeout=30.0,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def send_text(self, to: str, body: str) -> dict:
        resp = await self._http.post("/messages", json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body[:4096]},
        })
        if not resp.is_success:
            # The Graph error body has no secrets in it, but it can echo the number, so log only the status.
            log.warning("WhatsApp send to %s failed: HTTP %s", mask_phone(to), resp.status_code)
            resp.raise_for_status()
        return resp.json()
