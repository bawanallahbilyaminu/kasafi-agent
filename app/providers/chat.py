"""Shared OpenAI-compatible Chat Completions client.

Meta Model API and Baseten both speak this protocol; they differ in base URL,
key and how audio is attached, so each provider subclasses ChatClient and
implements `audio_part`. Everything that calls a model takes a ChatClient, so
providers can be swapped.

Retries 429/500/503 with backoff, honouring Retry-After. Other errors raise
immediately. The API key never appears in exceptions or logs.
"""

from __future__ import annotations

import asyncio
import random
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

RETRYABLE_STATUS = {429, 500, 503}
_THINK_BLOCK = re.compile(r"^\s*<think>.*?</think>\s*", re.DOTALL)


class ProviderError(RuntimeError):
    def __init__(self, provider: str, status: int, message: str, type_: str | None = None) -> None:
        super().__init__(f"{provider} API {status} ({type_ or 'unknown'}): {message}")
        self.status = status
        self.type = type_


@dataclass
class ChatResult:
    content: str
    model: str
    finish_reason: str | None
    reasoning: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def text_part(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


class ChatClient:
    provider = "chat"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        default_model: str,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
    ) -> None:
        self.default_model = default_model
        self.max_retries = max_retries
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> ChatClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    def audio_part(self, wav: bytes) -> dict[str, Any]:
        raise NotImplementedError(f"{self.provider} has no audio input")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        **params: Any,
    ) -> ChatResult:
        body = {"model": model or self.default_model, "messages": messages, **params}
        data = (await self._request("POST", "/chat/completions", json=body)).json()
        choice = data["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        # Reasoning should arrive in reasoning_content; strip an inline <think> block just in case.
        if m := _THINK_BLOCK.match(content):
            reasoning = reasoning or m.group(0).strip()[7:-8].strip()
            content = content[m.end():]
        return ChatResult(
            content=content,
            model=data.get("model", body["model"]),
            finish_reason=choice.get("finish_reason"),
            reasoning=reasoning,
            usage=data.get("usage") or {},
            raw=data,
        )

    async def list_models(self) -> list[str]:
        resp = await self._request("GET", "/models")
        return [m["id"] for m in resp.json().get("data", [])]

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            resp = await self._http.request(method, path, **kwargs)
            if resp.is_success:
                return resp
            if resp.status_code not in RETRYABLE_STATUS or attempt == self.max_retries:
                raise self._error_from(resp)
            await asyncio.sleep(_retry_delay(resp, attempt))
        raise AssertionError("unreachable")

    def _error_from(self, resp: httpx.Response) -> ProviderError:
        try:
            err = resp.json().get("error") or {}
            if isinstance(err, str):
                err = {"message": err}
            return ProviderError(self.provider, resp.status_code,
                                 err.get("message", resp.text[:300]), err.get("type"))
        except ValueError:
            return ProviderError(self.provider, resp.status_code, resp.text[:300] or resp.reason_phrase)


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    retry_after = resp.headers.get("retry-after")
    if retry_after and retry_after.isdigit():
        return float(retry_after)
    return min(2**attempt, 30) + random.uniform(0, 0.5)
