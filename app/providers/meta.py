"""Meta Model API client (https://dev.meta.ai/docs).

OpenAI-compatible Chat Completions at https://api.meta.ai/v1. Audio goes in as
an `input_audio` content part (base64, format "wav" or "mp3"). Also wraps Muse
Voice Transcribe (POST /asr/transcribe).
"""

from __future__ import annotations

import base64
import json
from typing import Any, Literal

import httpx

from app.config import Settings, get_settings
from app.providers.chat import ChatClient, ChatResult, ProviderError, text_part

AudioFormat = Literal["wav", "mp3"]
MetaAPIError = ProviderError

__all__ = ["ChatResult", "MetaAPIError", "MetaClient", "audio_part", "text_part"]


def audio_part(audio: bytes, fmt: AudioFormat) -> dict[str, Any]:
    return {
        "type": "input_audio",
        "input_audio": {"data": base64.b64encode(audio).decode("ascii"), "format": fmt},
    }


class MetaClient(ChatClient):
    provider = "Meta"

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
        super().__init__(
            base_url=settings.meta_base_url,
            api_key=settings.meta_api_key.get_secret_value(),
            default_model=settings.meta_model,
            transport=transport, timeout=timeout, max_retries=max_retries,
        )

    def audio_part(self, wav: bytes) -> dict[str, Any]:
        return audio_part(wav, "wav")

    async def transcribe(self, wav: bytes, *, model: str = "muse-voice-transcribe-1.0") -> dict[str, Any]:
        """Muse Voice Transcribe (POST /asr/transcribe, multipart `request` JSON + `audio` WAV).

        Returns the raw JSON body; its fields aren't pinned down in the docs yet.
        """
        request = json.dumps({"model": model, "audioEncoding": "WAV", "mode": "PUSH_TO_TALK"})
        files = {
            "request": (None, request, "application/json"),
            "audio": ("audio.wav", wav, "audio/wav"),
        }
        resp = await self._request("POST", "/asr/transcribe", files=files,
                                   headers={"Accept": "application/json"})
        return resp.json()
