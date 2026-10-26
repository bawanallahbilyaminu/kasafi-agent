"""Baseten Model APIs client for Muse Spark Open (https://docs.baseten.co).

OpenAI-compatible at https://inference.baseten.co/v1. The hackathon key only
works with `meta-models/muse-spark-open-1026` (the docs' `meta-models/muse-spark-open`
is not valid for it).

- Reasoning: Muse Spark Open always reasons. Reasoning arrives in
  `reasoning_content`, `reasoning_effort` defaults to xhigh, and `max_tokens`
  caps reasoning + answer together. So callers should pass an explicit effort
  and a generous max_tokens.
- Audio: an `audio_url` content part (an HTTPS URL or a base64 data URL),
  shaped like `image_url`.
"""

from __future__ import annotations

import base64
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.chat import ChatClient


def audio_url_part(wav: bytes, mime: str = "audio/wav") -> dict[str, Any]:
    data = base64.b64encode(wav).decode("ascii")
    return {"type": "audio_url", "audio_url": {"url": f"data:{mime};base64,{data}"}}


class BasetenClient(ChatClient):
    provider = "Baseten"

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 180.0,
        max_retries: int = 3,
    ) -> None:
        settings = settings or get_settings()
        if settings.baseten_api_key is None:
            raise RuntimeError("BASETEN_API_KEY is not set (see .env.example)")
        super().__init__(
            base_url=settings.baseten_base_url,
            api_key=settings.baseten_api_key.get_secret_value(),
            default_model=settings.baseten_model,
            transport=transport, timeout=timeout, max_retries=max_retries,
        )

    def audio_part(self, wav: bytes) -> dict[str, Any]:
        return audio_url_part(wav)
