import asyncio
import base64
import json

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.providers import chat
from app.providers.meta import MetaAPIError, MetaClient, audio_part, text_part

FAKE_KEY = "test-key-not-real"


def _settings() -> Settings:
    return Settings(_env_file=None, meta_api_key=SecretStr(FAKE_KEY))


def _completion(content: str) -> dict:
    return {
        "id": "x",
        "object": "chat.completion",
        "created": 0,
        "model": "muse-spark-1.3",
        "choices": [
            {"index": 0, "finish_reason": "stop",
             "message": {"role": "assistant", "content": content, "refusal": None}}
        ],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
    }


def _run(coro):
    return asyncio.run(coro)


def test_chat_sends_auth_and_parses_reply() -> None:
    seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["auth"] = req.headers["authorization"]
        seen["url"] = str(req.url)
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json=_completion("Sannu!"))

    async def go():
        async with MetaClient(_settings(), transport=httpx.MockTransport(handler)) as c:
            return await c.chat([{"role": "user", "content": "Hi"}])

    result = _run(go())
    assert result.content == "Sannu!"
    assert result.usage["total_tokens"] == 5
    assert seen["auth"] == f"Bearer {FAKE_KEY}"
    assert seen["url"] == "https://api.meta.ai/v1/chat/completions"
    assert seen["body"]["model"] == "muse-spark-1.3"


def test_audio_part_is_base64_input_audio() -> None:
    part = audio_part(b"\x00\x01", "wav")
    assert part["type"] == "input_audio"
    assert part["input_audio"] == {"data": base64.b64encode(b"\x00\x01").decode(), "format": "wav"}
    assert text_part("a") == {"type": "text", "text": "a"}


def test_retries_on_429_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"retry-after": "0"},
                                  json={"error": {"message": "slow down", "type": "rate_limit_error"}})
        return httpx.Response(200, json=_completion("ok"))

    async def go():
        async with MetaClient(_settings(), transport=httpx.MockTransport(handler)) as c:
            return await c.chat([{"role": "user", "content": "Hi"}])

    assert _run(go()).content == "ok"
    assert calls["n"] == 2


def test_non_retryable_error_raises_without_leaking_key() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "bad param", "type": "invalid_request_error"}})

    async def go():
        async with MetaClient(_settings(), transport=httpx.MockTransport(handler)) as c:
            await c.chat([{"role": "user", "content": "Hi"}])

    with pytest.raises(MetaAPIError) as exc:
        _run(go())
    assert exc.value.status == 400
    assert "bad param" in str(exc.value)
    assert FAKE_KEY not in str(exc.value)


def test_missing_key_fails_fast() -> None:
    with pytest.raises(RuntimeError, match="META_API_KEY"):
        MetaClient(Settings(_env_file=None, meta_api_key=None))


def test_retry_delay_uses_retry_after() -> None:
    resp = httpx.Response(503, headers={"retry-after": "7"})
    assert chat._retry_delay(resp, 0) == 7.0
