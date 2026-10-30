"""WhatsApp Cloud API: send messages and fetch/delete received media.

Graph API at https://graph.facebook.com/<version> with `Authorization: Bearer <WHATSAPP_TOKEN>`
(developers.facebook.com, "Text messages" and "Media"):
- send:     POST /<phone_number_id>/messages
- media:    GET /<media_id> returns {url, mime_type, sha256, file_size}. The url expires after
            5 minutes and must be downloaded with the same token.
- delete:   DELETE /<media_id>. Received media otherwise persists on Meta's side for 30 days.
- upload:   POST /<phone_number_id>/media (multipart: file, type, messaging_product) returns {id}; an
            image message then sends that id with a caption (evidence crops of public documents).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import time
from urllib.parse import urlparse

import httpx

from app.config import Settings, get_settings

log = logging.getLogger(__name__)
GRAPH_URL = "https://graph.facebook.com"
MAX_MEDIA_BYTES = 16 * 1024 * 1024  # WhatsApp's audio limit
# The token goes with the download, so only send it to Meta-owned hosts.
MEDIA_HOST_SUFFIXES = (".fbsbx.com", ".facebook.com", ".whatsapp.net", ".fbcdn.net")


class MediaError(RuntimeError):
    pass


def mask_phone(number: str) -> str:
    """For logs only: keep the last 2 digits."""
    return f"**{number[-2:]}" if number else "?"


def _sha256_matches(data: bytes, expected: str | None) -> bool:
    """WhatsApp reports sha256 as base64 in some places and hex in others; accept either."""
    if not expected:
        return True
    digest = hashlib.sha256(data).digest()
    return expected.strip() in {digest.hex(), base64.b64encode(digest).decode()}


class WhatsAppClient:
    def __init__(self, settings: Settings | None = None, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
        settings = settings or get_settings()
        if settings.whatsapp_token is None or not settings.whatsapp_phone_number_id:
            raise RuntimeError("WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID must be set (see .env.example)")
        self.phone_number_id = settings.whatsapp_phone_number_id
        self._pending_deletes: set[asyncio.Task] = set()
        self._http = httpx.AsyncClient(
            base_url=f"{GRAPH_URL}/{settings.whatsapp_api_version}",
            headers={"Authorization": f"Bearer {settings.whatsapp_token.get_secret_value()}"},
            timeout=30.0,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self.drain()   # finish background media deletes before the HTTP client goes away
        await self._http.aclose()

    def delete_media_later(self, media_id: str) -> None:
        """Delete Meta's copy in the background so the user's reply isn't held up (it took ~4 s on the VPS)."""
        task = asyncio.create_task(self._timed_delete(media_id))
        self._pending_deletes.add(task)
        task.add_done_callback(self._pending_deletes.discard)

    async def drain(self) -> None:
        if self._pending_deletes:
            await asyncio.gather(*self._pending_deletes, return_exceptions=True)

    async def _timed_delete(self, media_id: str) -> None:
        t0 = time.perf_counter()
        try:
            ok = await self.delete_media(media_id)
        except httpx.HTTPError as e:
            log.info("media delete failed: %s after %.1fs", type(e).__name__, time.perf_counter() - t0)
            return
        log.info("media delete %s in %.1fs", "done" if ok else "not accepted", time.perf_counter() - t0)

    async def send_text(self, to: str, body: str) -> dict:
        resp = await self._http.post(f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body[:4096]},
        })
        if not resp.is_success:
            # The Graph error body can echo the number, so log only the status and numeric error code.
            log.warning("WhatsApp send to %s failed: HTTP %s, Graph error code %s",
                        mask_phone(to), resp.status_code, _graph_code(resp))
            resp.raise_for_status()
        return resp.json()

    async def send_buttons(self, to: str, body: str, buttons: list[tuple[str, str]]) -> dict:
        """Interactive reply-buttons message: at most 3 buttons, titles of 20 characters or fewer, body of 1024 or fewer."""
        if not 1 <= len(buttons) <= 3 or any(len(title) > 20 for _, title in buttons) or len(body) > 1024:
            raise ValueError("WhatsApp reply buttons: 1-3 buttons, titles <= 20 chars, body <= 1024 chars")
        resp = await self._http.post(f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": [{"type": "reply", "reply": {"id": i, "title": title}} for i, title in buttons]},
            },
        })
        if not resp.is_success:
            log.warning("WhatsApp buttons to %s failed: HTTP %s, Graph error code %s",
                        mask_phone(to), resp.status_code, _graph_code(resp))
            resp.raise_for_status()
        return resp.json()

    async def send_location_request(self, to: str, body: str) -> dict:
        """Interactive location request message: the user's "Share location" button (body of 1024 or fewer)."""
        resp = await self._http.post(f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {"type": "location_request_message", "body": {"text": body[:1024]},
                            "action": {"name": "send_location"}},
        })
        if not resp.is_success:
            log.warning("WhatsApp location request to %s failed: HTTP %s, Graph error code %s",
                        mask_phone(to), resp.status_code, _graph_code(resp))
            resp.raise_for_status()
        return resp.json()

    async def upload_media(self, data: bytes, mime: str = "image/jpeg", filename: str = "evidence.jpg") -> str:
        resp = await self._http.post(f"/{self.phone_number_id}/media",
                                     data={"messaging_product": "whatsapp", "type": mime},
                                     files={"file": (filename, data, mime)})
        if not resp.is_success:
            log.warning("WhatsApp media upload failed: HTTP %s, Graph error code %s", resp.status_code, _graph_code(resp))
            resp.raise_for_status()
        return str(resp.json()["id"])

    async def send_image(self, to: str, jpeg: bytes, caption: str = "") -> dict:
        media_id = await self.upload_media(jpeg)
        resp = await self._http.post(f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {"id": media_id, "caption": caption[:1024]},
        })
        if not resp.is_success:
            log.warning("WhatsApp image to %s failed: HTTP %s, Graph error code %s",
                        mask_phone(to), resp.status_code, _graph_code(resp))
            resp.raise_for_status()
        return resp.json()

    async def download_media(self, media_id: str, *, max_bytes: int = MAX_MEDIA_BYTES) -> bytes:
        """Fetch a received media file into memory (never to disk)."""
        meta = await self._http.get(f"/{media_id}", params={"phone_number_id": self.phone_number_id})
        if not meta.is_success:
            raise MediaError(f"media lookup failed: HTTP {meta.status_code}, Graph error code {_graph_code(meta)}")
        info = meta.json()
        url = info.get("url", "")
        host = urlparse(url).hostname or ""
        if urlparse(url).scheme != "https" or not host.endswith(MEDIA_HOST_SUFFIXES):
            raise MediaError(f"refusing media URL on unexpected host {host!r}")
        if int(info.get("file_size") or 0) > max_bytes:
            raise MediaError(f"media too large: {info.get('file_size')} bytes")

        chunks, size = [], 0
        async with self._http.stream("GET", url) as resp:
            if not resp.is_success:
                raise MediaError(f"media download failed: HTTP {resp.status_code}")
            async for chunk in resp.aiter_bytes():
                size += len(chunk)
                if size > max_bytes:
                    raise MediaError("media too large while downloading")
                chunks.append(chunk)
        data = b"".join(chunks)
        if not _sha256_matches(data, info.get("sha256")):
            raise MediaError("media sha256 mismatch")
        return data

    async def delete_media(self, media_id: str) -> bool:
        """Ask Meta to delete its copy (best effort; it otherwise keeps it for 30 days)."""
        resp = await self._http.delete(f"/{media_id}", params={"phone_number_id": self.phone_number_id})
        if not resp.is_success:
            log.info("media delete not accepted: HTTP %s, Graph error code %s", resp.status_code, _graph_code(resp))
        return resp.is_success


def _graph_code(resp: httpx.Response) -> int | None:
    try:
        return resp.json().get("error", {}).get("code")
    except ValueError:
        return None
