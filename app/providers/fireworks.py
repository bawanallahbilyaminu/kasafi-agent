"""Fireworks AI client for Muse Spark Open, and the hosts that serve Muse Spark Open (`open_hosts`).

OpenAI-compatible at https://api.fireworks.ai/inference/v1; serverless model
`accounts/fireworks/models/muse-spark-open` (Fireworks' model page, Oct 30 2026: $1.25 / $0.15 cached / $4.25 per
1M tokens, reasoning, function calling). It always reasons: pass an explicit effort and a generous max_tokens.

Since 4 Nov 2026 Fireworks is the only host by default: Baseten's credit ran out (every call a 402), so it serves
nothing unless KASAFI_OPEN_HOSTS names it again.
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


def open_hosts(settings: Settings, *, timeout: float | None = None, max_retries: int | None = None,
               first: str = "") -> list["ChatClient"]:
    """The hosts that serve Muse Spark Open, in order, from KASAFI_OPEN_HOSTS (default "fireworks"): a host is
    used only when it is named there and its key is set. `first` moves one named host to the front. [] when no
    host can be made (no key): the callers then stay on Muse Spark or skip the step."""
    kw = {k: v for k, v in (("timeout", timeout), ("max_retries", max_retries)) if v is not None}
    names = [n.strip().lower() for n in (settings.kasafi_open_hosts or "").split(",") if n.strip()]
    if first and first.lower() in names:
        names.remove(first.lower())
        names.insert(0, first.lower())
    out: list[ChatClient] = []
    for name in names:
        if name == "fireworks" and settings.fireworks_api_key:
            out.append(FireworksClient(settings, **kw))
        elif name == "baseten" and settings.baseten_api_key:
            from app.providers.baseten import BasetenClient
            out.append(BasetenClient(settings, **kw))
    return out


def open_model(settings: Settings, **kw) -> "OpenModel | None":
    """Muse Spark Open from the configured hosts, or None when none can be made."""
    hosts = open_hosts(settings, **kw)
    return OpenModel(hosts) if hosts else None


class BatchModel:
    """Muse Spark Open standing in for Muse Spark in eval runs and batch jobs (settings.kasafi_batch_provider).
    Open always reasons and its max_tokens counts the reasoning too, so every call gets at least MIN_TOKENS and a
    low effort; calls written for Muse Spark (400-3000 tokens) would otherwise end empty."""

    MIN_TOKENS = 8000

    def __init__(self, settings: Settings) -> None:
        hosts = open_hosts(settings, first=settings.kasafi_batch_provider.lower())
        if not hosts:
            raise RuntimeError("no Muse Spark Open host: FIREWORKS_API_KEY is not set (KASAFI_OPEN_HOSTS)")
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
    return BatchModel if settings.kasafi_batch_provider.lower() in ("open", "fireworks", "baseten") else None


class OpenModel:
    """Muse Spark Open from whichever host answers, in order (open_hosts); each call uses the host's own model
    ID, whatever `model` the caller passed. Usage is recorded under the host that answered."""

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
