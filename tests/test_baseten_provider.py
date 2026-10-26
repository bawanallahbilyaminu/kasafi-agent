import asyncio
import base64
import json

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.providers.baseten import BasetenClient, audio_url_part

FAKE_KEY = "test-key-not-real"


def _settings() -> Settings:
    return Settings(_env_file=None, baseten_api_key=SecretStr(FAKE_KEY))


def _chat(message: dict, handler_seen: dict | None = None):
    def handler(req: httpx.Request) -> httpx.Response:
        if handler_seen is not None:
            handler_seen.update(url=str(req.url), auth=req.headers["authorization"], body=json.loads(req.content))
        return httpx.Response(200, json={"model": "meta-models/muse-spark-open-1026", "choices": [
            {"index": 0, "finish_reason": "stop", "message": {"role": "assistant", **message}}]})

    async def go():
        async with BasetenClient(_settings(), transport=httpx.MockTransport(handler)) as c:
            return await c.chat([{"role": "user", "content": "Hi"}], reasoning_effort="low")
    return asyncio.run(go())


def test_uses_hackathon_model_and_separates_reasoning() -> None:
    seen: dict = {}
    r = _chat({"content": "Sannu", "reasoning_content": "thinking..."}, seen)
    assert seen["url"] == "https://inference.baseten.co/v1/chat/completions"
    assert seen["auth"] == f"Bearer {FAKE_KEY}"
    assert seen["body"]["model"] == "meta-models/muse-spark-open-1026"
    assert seen["body"]["reasoning_effort"] == "low"
    assert (r.content, r.reasoning) == ("Sannu", "thinking...")


def test_inline_think_block_is_stripped() -> None:
    r = _chat({"content": "<think>plan</think>\nSannu"})
    assert (r.content, r.reasoning) == ("Sannu", "plan")


def test_audio_url_part_is_data_url() -> None:
    part = audio_url_part(b"RIFF")
    assert part == {"type": "audio_url",
                    "audio_url": {"url": "data:audio/wav;base64," + base64.b64encode(b"RIFF").decode()}}


def test_missing_key_fails_fast() -> None:
    with pytest.raises(RuntimeError, match="BASETEN_API_KEY"):
        BasetenClient(Settings(_env_file=None, baseten_api_key=None))
