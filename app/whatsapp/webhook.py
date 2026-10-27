"""WhatsApp webhook: verification handshake and incoming messages.

- GET: Meta sends hub.mode=subscribe, hub.verify_token, hub.challenge. Reply 200
  with the challenge if the token matches WHATSAPP_VERIFY_TOKEN.
- POST: verify X-Hub-Signature-256 (HMAC-SHA256 of the raw body, keyed with
  WHATSAPP_APP_SECRET), acknowledge with 200 right away, and reply in the
  background. Meta retries for up to 7 days, so message IDs are de-duplicated.
  What to reply is decided in app/whatsapp/conversation.py (consent, language, limits).

Privacy: logs carry masked numbers and message types only, never message text.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from collections import OrderedDict
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import SecretStr

from app.config import get_settings
from app.users import get_store
from app.whatsapp.client import WhatsAppClient, mask_phone
from app.whatsapp.conversation import handle

log = logging.getLogger(__name__)
router = APIRouter()

class _SeenIds:
    """Bounded set of recently processed message IDs."""

    def __init__(self, maxlen: int = 2000) -> None:
        self._ids: OrderedDict[str, None] = OrderedDict()
        self._maxlen = maxlen

    def add(self, msg_id: str) -> bool:
        """Return True if new, False if seen before."""
        if msg_id in self._ids:
            return False
        self._ids[msg_id] = None
        if len(self._ids) > self._maxlen:
            self._ids.popitem(last=False)
        return True


seen_ids = _SeenIds()


def _secret(value: SecretStr | None) -> str | None:
    """Treat an empty value (e.g. `WHATSAPP_APP_SECRET=` in .env) as not configured."""
    return value.get_secret_value() if value is not None and value.get_secret_value() else None


def valid_signature(body: bytes, header: str | None, secret: str) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def extract_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "messages":
                out.extend(change.get("value", {}).get("messages", []))
    return out


async def _reply(messages: list[dict[str, Any]]) -> None:
    client = WhatsAppClient()
    settings, store = get_settings(), get_store()
    try:
        for msg in messages:
            async def send(out, to=msg["from"]) -> None:
                if out.buttons:
                    await client.send_buttons(to, out.text, out.buttons)
                else:
                    await client.send_text(to, out.text)

            try:
                for out in await handle(msg, client, store=store, settings=settings, notify=send):
                    await send(out)
                log.info("reply sent to %s", mask_phone(msg["from"]))
            except Exception:  # one failed reply must not stop the rest
                log.exception("reply to %s failed", mask_phone(msg.get("from", "")))
    finally:
        await client.aclose()


@router.get("/webhook", response_class=PlainTextResponse)
def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
) -> str:
    expected = _secret(get_settings().whatsapp_verify_token)
    if expected is None:
        log.error("WHATSAPP_VERIFY_TOKEN is not set")
        raise HTTPException(503, "webhook not configured")
    if mode == "subscribe" and hmac.compare_digest(token, expected):
        log.info("webhook verified")
        return challenge
    raise HTTPException(403, "verification failed")


@router.post("/webhook")
async def receive(request: Request, background: BackgroundTasks) -> dict[str, str]:
    secret = _secret(get_settings().whatsapp_app_secret)
    if secret is None:
        log.error("WHATSAPP_APP_SECRET is not set; rejecting webhook")
        raise HTTPException(503, "webhook not configured")
    body = await request.body()
    if not valid_signature(body, request.headers.get("x-hub-signature-256"), secret):
        log.warning("webhook with bad or missing signature rejected")
        raise HTTPException(401, "bad signature")

    payload = await request.json()
    new = [m for m in extract_messages(payload) if m.get("id") and m.get("from") and seen_ids.add(m["id"])]
    for m in new:
        log.info("message %s from %s", m.get("type"), mask_phone(m["from"]))
    if not new:
        log.info("webhook event with no new messages (status update, test or retry)")
    else:
        background.add_task(_reply, new)
    return {"status": "ok"}
