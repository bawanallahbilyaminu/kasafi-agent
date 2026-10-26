"""Meta Model API client (https://dev.meta.ai/docs).

OpenAI-compatible Chat Completions at `{base_url}/chat/completions` with
`Authorization: Bearer <META_API_KEY>`. Audio goes in as an `input_audio`
content part (base64, format "wav" or "mp3").

Retries 429/500/503 with backoff, honouring Retry-After (per the docs' error
handling page). Other errors raise immediately. The API key never appears in
exceptions or logs.
"""

from __future__ import annotations

import asyncio
import base64
import random
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx

from app.config import Settings, get_settings

RETRYABLE_STATUS = {429, 500, 503}
AudioFormat = Literal["wav", "mp3"]


class MetaAPIError(RuntimeError):
    def __init__(self, status: int, message: str, type_: str | None = None) -> None:
        super().__init__(f"Meta API {status} ({type_ or 'unknown'}): {message}")
        self.status = status
        self.type = type_


@dataclass
class ChatResult:
    content: str
    model: str
    finish_reason: str | None
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def text_part(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def audio_part(audio: bytes, fmt: AudioFormat) -> dict[str, Any]:
    return {
        "type": "input_audio",
        "input_audio": {"data": base64.b64encode(audio).decode("ascii"), "format": fmt},
    }


class MetaClient:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
    ) -> None:
        settings = settings or get_settings()
        if settings.meta_api_key is None:
            raise RuntimeError("META_API_KEY is not set (see .env.example)")
        self.default_model = settings.meta_model
        self.max_retries = max_retries
        self._http = httpx.AsyncClient(
            base_url=settings.meta_base_url,
            headers={"Authorization": f"Bearer {settings.meta_api_key.get_secret_value()}"},
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> MetaClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        **params: Any,
    ) -> ChatResult:
        body = {"model": model or self.default_model, "messages": messages, **params}
        data = await self._post_json("/chat/completions", body)
        choice = data["choices"][0]
        return ChatResult(
            content=choice["message"].get("content") or "",
            model=data.get("model", body["model"]),
            finish_reason=choice.get("finish_reason"),
            usage=data.get("usage") or {},
            raw=data,
        )

    async def list_models(self) -> list[str]:
        resp = await self._request("GET", "/models")
        return [m["id"] for m in resp.json().get("data", [])]

    async def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return (await self._request("POST", path, json=body)).json()

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            resp = await self._http.request(method, path, **kwargs)
            if resp.is_success:
                return resp
            if resp.status_code not in RETRYABLE_STATUS or attempt == self.max_retries:
                raise _error_from(resp)
            await asyncio.sleep(_retry_delay(resp, attempt))
        raise AssertionError("unreachable")


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    retry_after = resp.headers.get("retry-after")
    if retry_after and retry_after.isdigit():
        return float(retry_after)
    return min(2**attempt, 30) + random.uniform(0, 0.5)


def _error_from(resp: httpx.Response) -> MetaAPIError:
    try:
        err = resp.json().get("error") or {}
        return MetaAPIError(resp.status_code, err.get("message", resp.text[:300]), err.get("type"))
    except ValueError:
        return MetaAPIError(resp.status_code, resp.text[:300] or resp.reason_phrase)
