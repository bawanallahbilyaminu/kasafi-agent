"""WhatsApp webhook: verification handshake and incoming messages (echo for now).

- GET: Meta sends hub.mode=subscribe, hub.verify_token, hub.challenge. Reply 200
  with the challenge if the token matches WHATSAPP_VERIFY_TOKEN.
- POST: verify X-Hub-Signature-256 (HMAC-SHA256 of the raw body, keyed with
  WHATSAPP_APP_SECRET), acknowledge with 200 right away, and reply in the
  background. Meta retries for up to 7 days, so message IDs are de-duplicated.

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

from app.config import get_settings
from app.whatsapp.client import WhatsAppClient, mask_phone

log = logging.getLogger(__name__)
router = APIRouter()

ECHO_TEXT = "Kasafi (gwaji): na karɓi saƙonka: «{text}»"
ECHO_VOICE = "Kasafi (gwaji): na karɓi saƙon murya. Nan ba da jimawa ba zan iya saurara."
ECHO_OTHER = "Kasafi (gwaji): don Allah ka aiko da rubutu ko saƙon murya."


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


def echo_reply(msg: dict[str, Any]) -> str:
    kind = msg.get("type")
    if kind == "text":
        return ECHO_TEXT.format(text=msg.get("text", {}).get("body", "")[:500])
    if kind == "audio":
        return ECHO_VOICE
    return ECHO_OTHER


async def _reply(messages: list[dict[str, Any]]) -> None:
    client = WhatsAppClient()
    try:
        for msg in messages:
            try:
                await client.send_text(msg["from"], echo_reply(msg))
            except Exception:  # one failed reply must not stop the rest
                log.exception("echo reply to %s failed", mask_phone(msg.get("from", "")))
    finally:
        await client.aclose()


@router.get("/webhook", response_class=PlainTextResponse)
def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
) -> str:
    expected = get_settings().whatsapp_verify_token
    if expected is None:
        log.error("WHATSAPP_VERIFY_TOKEN is not set")
        raise HTTPException(503, "webhook not configured")
    if mode == "subscribe" and hmac.compare_digest(token, expected.get_secret_value()):
        log.info("webhook verified")
        return challenge
    raise HTTPException(403, "verification failed")


@router.post("/webhook")
async def receive(request: Request, background: BackgroundTasks) -> dict[str, str]:
    secret = get_settings().whatsapp_app_secret
    if secret is None:
        log.error("WHATSAPP_APP_SECRET is not set; rejecting webhook")
        raise HTTPException(503, "webhook not configured")
    body = await request.body()
    if not valid_signature(body, request.headers.get("x-hub-signature-256"), secret.get_secret_value()):
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
