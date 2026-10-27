import asyncio
import base64
import hashlib

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.whatsapp.client import MediaError, WhatsAppClient

AUDIO = b"OggS fake opus bytes"
GOOD_URL = "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=1"


def _settings() -> Settings:
    return Settings(_env_file=None, whatsapp_token=SecretStr("test-token"), whatsapp_phone_number_id="111")


def _handler(seen: list, *, url: str = GOOD_URL, sha: str | None = None, size: int | None = None,
             body: bytes = AUDIO, delete_status: int = 200):
    sha = sha if sha is not None else base64.b64encode(hashlib.sha256(body).digest()).decode()

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.host, req.url.path, req.headers.get("authorization")))
        if req.url.host == "graph.facebook.com" and req.method == "GET":
            return httpx.Response(200, json={"url": url, "mime_type": "audio/ogg; codecs=opus", "sha256": sha,
                                             "file_size": size if size is not None else len(body), "id": "m1"})
        if req.method == "DELETE":
            return httpx.Response(delete_status, json={"success": delete_status == 200})
        return httpx.Response(200, content=body)
    return handler


def _run(coro_fn, handler):
    async def go():
        c = WhatsAppClient(_settings(), transport=httpx.MockTransport(handler))
        try:
            return await coro_fn(c)
        finally:
            await c.aclose()
    return asyncio.run(go())


def test_download_media_two_step_with_token_and_hash_check() -> None:
    seen: list = []
    assert _run(lambda c: c.download_media("m1"), _handler(seen)) == AUDIO
    assert seen[0][:3] == ("GET", "graph.facebook.com", "/v26.0/m1")
    assert seen[1][1] == "lookaside.fbsbx.com" and seen[1][3] == "Bearer test-token"


def test_hex_sha256_also_accepted() -> None:
    assert _run(lambda c: c.download_media("m1"), _handler([], sha=hashlib.sha256(AUDIO).hexdigest())) == AUDIO


def test_refuses_to_send_token_to_non_meta_host() -> None:
    seen: list = []
    with pytest.raises(MediaError, match="unexpected host"):
        _run(lambda c: c.download_media("m1"), _handler(seen, url="https://evil.example.com/a.ogg"))
    assert all(host != "evil.example.com" for _, host, _, _ in seen)


def test_sha_mismatch_and_size_limits() -> None:
    with pytest.raises(MediaError, match="sha256"):
        _run(lambda c: c.download_media("m1"), _handler([], sha="bm90LXRoZS1oYXNo"))
    with pytest.raises(MediaError, match="too large"):
        _run(lambda c: c.download_media("m1", max_bytes=5), _handler([]))
    with pytest.raises(MediaError, match="too large"):
        _run(lambda c: c.download_media("m1", max_bytes=10), _handler([], size=1))  # header lies, stream is checked


def test_delete_media_is_best_effort() -> None:
    assert _run(lambda c: c.delete_media("m1"), _handler([])) is True
    assert _run(lambda c: c.delete_media("m1"), _handler([], delete_status=400)) is False
