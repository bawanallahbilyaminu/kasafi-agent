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

import asyncio
import hashlib
import hmac
import logging
from collections import OrderedDict
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import SecretStr

from app.config import get_settings
from app.evidence.crops import send_evidence
from app.users import get_store
from app.whatsapp.client import WhatsAppClient, mask_phone
from app.whatsapp.conversation import handle

log = logging.getLogger(__name__)

CROP_DEADLINE_S = 45.0     # an answer's evidence crops: sent within this after the text, or left out
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


REDELIVERY_S = 900
_delivered: dict[str, float] = {}            # message id -> when first seen (in memory, 15 minutes)


def first_delivery(message_id: str) -> bool:
    """False for a message id seen in the last 15 minutes: WhatsApp can deliver one message twice."""
    import time
    now = time.monotonic()
    for k in [k for k, at in _delivered.items() if now - at > REDELIVERY_S]:
        _delivered.pop(k, None)
    if not message_id:
        return True
    if message_id in _delivered:
        return False
    _delivered[message_id] = now
    return True


def sent_key(out) -> tuple:
    """What makes two messages of one turn the same one."""
    import hashlib
    image = hashlib.sha1(out.image).hexdigest() if getattr(out, "image", None) else ""
    loc = tuple(sorted((out.location or {}).items())) if getattr(out, "location", None) else ()
    return (out.text, image, loc, bool(getattr(out, "location_request", False)), tuple(out.buttons or ()),
            bool(getattr(out, "menu", None)))


def unique_crops(crops, turn: set) -> list:
    """Each cited page's crop once per turn."""
    out = []
    for c in crops or []:
        key = ("crop", c.doc_id, c.page, c.figure)
        if key not in turn:
            turn.add(key)
            out.append(c)
    return out


async def deliver(client, to: str, out) -> None:
    """One message, split rather than cut: text over WhatsApp's 4,096 characters goes in several messages; a
    caption, a buttons body or a location request over 1,024 sends its text first and keeps a whole last part."""
    from app.whatsapp.client import SHORT_LIMIT, split_text
    if getattr(out, "document", None):           # a PDF brief: its caption with it, any rest as text after
        data, filename = out.document
        parts = split_text(out.text, SHORT_LIMIT)
        await client.send_document(to, data, filename, parts[0])
        for part in split_text("\n\n".join(parts[1:])) if len(parts) > 1 else []:
            await client.send_text(to, part)
    elif getattr(out, "image", None):
        parts = split_text(out.text, SHORT_LIMIT)
        await client.send_image(to, out.image, parts[0])
        for part in split_text("\n\n".join(parts[1:])) if len(parts) > 1 else []:
            await client.send_text(to, part)
    elif getattr(out, "location", None):
        await client.send_location(to, **out.location)
    elif getattr(out, "menu", None):              # the menu: an interactive list (app/whatsapp/menu.py)
        await client.send_list(to, out.text, out.menu["button"], out.menu["sections"], out.menu.get("header", ""))
    elif getattr(out, "location_request", False) or out.buttons:
        parts = split_text(out.text, SHORT_LIMIT)
        for part in split_text("\n\n".join(parts[:-1])) if len(parts) > 1 else []:
            await client.send_text(to, part)
        if out.buttons:
            await client.send_buttons(to, parts[-1], out.buttons)
        else:
            await client.send_location_request(to, parts[-1])
    else:
        for part in split_text(out.text):
            await client.send_text(to, part)


async def _reply(messages: list[dict[str, Any]]) -> None:
    client = WhatsAppClient()
    settings, store = get_settings(), get_store()
    try:
        for msg in messages:
            if not first_delivery(msg.get("id", "")):
                log.info("message delivered again by WhatsApp: ignored")     # no second reply to one message
                continue
            turn: set = set()                                                   # what this turn has sent

            async def send(out, to=msg["from"], turn=turn) -> None:
                if (key := sent_key(out)) in turn:
                    log.info("identical message in one turn: sent once")
                    return
                turn.add(key)
                await deliver(client, to, out)

            typing = start_typing(client, msg, store, settings)                 # never awaited before the answer
            try:
                for out in await handle(msg, client, store=store, settings=settings, notify=send):
                    await send(out)
                    if crops := unique_crops(out.crops, turn):   # after the text: a slow crop never delays it
                        try:                                     # and never holds the rest past its own deadline
                            n = await asyncio.wait_for(send_evidence(client, msg["from"], crops, out.lang, settings),
                                                       CROP_DEADLINE_S)
                            log.info("evidence images sent: %d of %d", n, len(crops))
                        except asyncio.TimeoutError:
                            log.warning("evidence images not sent within %.0f s", CROP_DEADLINE_S)
                log.info("reply sent to %s", mask_phone(msg["from"]))
            except Exception as e:  # one failed reply must not stop the rest; the user never gets silence
                log.exception("reply to %s failed", mask_phone(msg.get("from", "")))
                try:
                    from app.agent.trace import save_failure
                    from app.users import user_key
                    from app.whatsapp.conversation import Out
                    from app.whatsapp.messages import t
                    user = store.get(user_key(msg["from"], settings)) if msg.get("from") else None
                    lang = (user.lang if user and user.lang else None) or "ha"
                    await send(Out(t("answer_failed", lang), lang=lang))
                    if settings.has_database:
                        save_failure(settings, "(reply failed)", lang, f"{type(e).__name__}: {e}"[:300], 0.0)
                except Exception:                                   # noqa: BLE001
                    log.exception("apology to %s failed too", mask_phone(msg.get("from", "")))
            finally:
                if typing is not None:                  # done long ago, or cut off now: never blocks a reply
                    typing.cancel()
    finally:
        await client.aclose()


TYPING_TIMEOUT_S = 3.0
TYPING_REPEAT_S = 18.0      # WhatsApp shows the indicator for at most 25 s, and drops it at any message we send
TYPING_MOST_S = 360.0       # never past the longest answer limit (a turn with a document fetch: 5 minutes)


def start_typing(client, msg: dict[str, Any], store, settings) -> asyncio.Task | None:
    """The typing indicator on the user's message (marked read), for consented users only: fire and forget, at
    most TYPING_TIMEOUT_S a call, a failure logged and nothing else. WhatsApp drops it after 25 s and at any
    message we send (a progress line), so it is sent again every TYPING_REPEAT_S until the reply is out and the
    task is cancelled (4 Nov 2026: the phone showed nothing while a 30-60 s answer was being written)."""
    from app.users import user_key
    msg_id = msg.get("id", "")
    if not msg_id or not msg.get("from") or not hasattr(client, "mark_typing"):
        return None
    try:
        user = store.get(user_key(msg["from"], settings))
    except Exception:                       # noqa: BLE001
        return None
    if not (user and user.consented):       # after the consent gate only
        return None

    async def run() -> None:
        started = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - started < TYPING_MOST_S:
            try:
                await asyncio.wait_for(client.mark_typing(msg_id), TYPING_TIMEOUT_S)
            except asyncio.CancelledError:
                raise
            except Exception as e:          # noqa: BLE001 - a missing indicator never matters
                log.info("typing indicator not shown: %s", type(e).__name__)
                return
            await asyncio.sleep(TYPING_REPEAT_S)
    return asyncio.get_running_loop().create_task(run())


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
