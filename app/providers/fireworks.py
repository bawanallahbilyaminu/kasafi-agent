"""Fireworks AI client for Muse Spark Open, the fallback host when Baseten fails (credits, errors).

OpenAI-compatible at https://api.fireworks.ai/inference/v1; serverless model
`accounts/fireworks/models/muse-spark-open` (Fireworks' model page, Oct 30 2026: $1.25 / $0.15 cached / $4.25 per
1M tokens, reasoning, function calling). Like Baseten's, it always reasons: pass an explicit effort and a
generous max_tokens.
"""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings
from app.providers.chat import ChatClient, ChatResult

log = logging.getLogger(__name__)


class FireworksClient(ChatClient):
    provider = "Fireworks"

    def __init__(self, settings: Settings | None = None, *, transport: httpx.AsyncBaseTransport | None = None,
                 timeout: float = 180.0, max_retries: int = 3) -> None:
        settings = settings or get_settings()
        if settings.fireworks_api_key is None:
            raise RuntimeError("FIREWORKS_API_KEY is not set (see .env.example)")
        super().__init__(base_url=settings.fireworks_base_url, api_key=settings.fireworks_api_key.get_secret_value(),
                         default_model=settings.fireworks_model, transport=transport, timeout=timeout,
                         max_retries=max_retries)


class BatchModel:
    """Muse Spark Open standing in for Muse Spark in eval runs and batch jobs (settings.kasafi_batch_provider).
    Open always reasons and its max_tokens counts the reasoning too (Baseten docs), so every call gets at least
    MIN_TOKENS and a low effort; calls written for Muse Spark (400-3000 tokens) would otherwise end empty."""

    MIN_TOKENS = 8000

    def __init__(self, settings: Settings) -> None:
        from app.providers.baseten import BasetenClient
        order = [BasetenClient, FireworksClient]
        if settings.kasafi_batch_provider.lower() == "fireworks":
            order.reverse()
        keys = {BasetenClient: settings.baseten_api_key, FireworksClient: settings.fireworks_api_key}
        hosts = [cls(settings) for cls in order if keys[cls]]
        if not hosts:
            raise RuntimeError("KASAFI_BATCH_PROVIDER is set but neither BASETEN_API_KEY nor FIREWORKS_API_KEY is")
        self.open = OpenModel(hosts)
        self.provider = self.open.provider
        self.default_model = self.open.default_model

    async def __aenter__(self) -> "BatchModel":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.open.__aexit__(*exc)

    async def aclose(self) -> None:
        await self.open.__aexit__()

    async def chat(self, messages: list[dict], *, model: str | None = None, **params) -> ChatResult:
        params["max_tokens"] = max(int(params.get("max_tokens") or 0), self.MIN_TOKENS)
        if params.get("reasoning_effort") in (None, "minimal"):
            params["reasoning_effort"] = "low"
        return await self.open.chat(messages, model=model, **params)


def batch_factory(settings: Settings):
    """The client class to use instead of Muse Spark for this run, or None (live: Muse Spark)."""
    return BatchModel if settings.kasafi_batch_provider.lower() in ("baseten", "fireworks") else None


class OpenModel:
    """Muse Spark Open from whichever host answers, in order (Baseten, then Fireworks); each call uses the
    host's own model ID, whatever `model` the caller passed. Usage is recorded under the host that answered."""

    provider = "Muse Spark Open"

    def __init__(self, hosts: list[ChatClient]) -> None:
        self.hosts = hosts
        self.default_model = hosts[0].default_model

    async def __aenter__(self) -> OpenModel:
        return self

    async def __aexit__(self, *exc: object) -> None:
        for h in self.hosts:
            await h.aclose()

    async def chat(self, messages: list[dict], *, model: str | None = None, **params) -> ChatResult:
        last: Exception | None = None
        for h in self.hosts:
            try:
                return await h.chat(messages, model=h.default_model, **params)
            except Exception as e:      # noqa: BLE001 - the next host answers instead
                last = e
                log.info("Muse Spark Open on %s failed (%s); next host", h.provider, type(e).__name__)
        raise last or RuntimeError("no Muse Spark Open host")
