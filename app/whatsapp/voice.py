"""Voice notes: download, transcribe (combined STT pipeline), discard, read back.

Callers (app/whatsapp/conversation.py) only get here after the access gate, consent and limits.

Privacy (docs/architecture.md "Data retention", halalnumeriq.com.ng/kasafi/privacy):
- The audio is held in memory only (ffmpeg's temp file is deleted at once), dropped as soon
  as it is transcribed, and Meta's copy is deleted. Nothing is written to our storage.
- Only the audio goes to the model APIs, never the phone number or WhatsApp name.
- Logs record timings and confidence, never the transcript.

Per the speech decision, unclear audio is never answered: when the pipeline isn't sure,
the reply is a read-back question. A medical emergency gets an immediate referral instead.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.providers.chat import ProviderError
from app.providers.meta import MetaClient
from app.providers.stt import SpeechResult, TranscriptionFailed, VoiceNoteTooLong, transcribe_voice_note
from app.whatsapp.client import MediaError, WhatsAppClient, mask_phone
from app.whatsapp.messages import t

log = logging.getLogger(__name__)


@dataclass
class VoiceOutcome:
    text: str                           # the reply to send
    result: SpeechResult | None = None  # None when nothing usable was heard


def is_pilot(number: str, settings: Settings) -> bool:
    return "".join(ch for ch in number if ch.isdigit()) in settings.pilot_numbers


def compose_reply(result: SpeechResult, lang: str = "ha") -> str:
    transcript = result.transcript.strip()
    if not transcript:
        return t("not_heard", lang)
    # Safety first: an emergency gets a referral now, never a read-back or "answer coming soon".
    if is_medical_emergency(transcript, result.english):
        return EMERGENCY_REPLY
    # Read back exactly what was said, in the language it was spoken. The English translation
    # (result.english) is only for searching documents, never shown as the read-back.
    key = "read_back" if result.needs_confirmation else "heard"
    return t(key, lang, transcript=transcript[:1000])


async def reply_for_voice(
    msg: dict[str, Any],
    wa: WhatsAppClient,
    *,
    lang: str = "ha",
    settings: Settings | None = None,
    meta_client_factory: type[MetaClient] = MetaClient,
) -> VoiceOutcome:
    settings = settings or get_settings()
    sender = msg.get("from", "")
    media_id = (msg.get("audio") or {}).get("id")
    if not media_id:
        return VoiceOutcome(t("not_heard", lang))

    t0 = time.perf_counter()
    try:
        audio = await wa.download_media(media_id)
        download_s = time.perf_counter() - t0
    except MediaError as e:
        log.warning("voice note download failed for %s: %s", mask_phone(sender), e)
        return VoiceOutcome(t("not_heard", lang))

    try:
        async with meta_client_factory(settings) as client:
            result = await transcribe_voice_note(audio, client, settings=settings,
                                                 max_seconds=settings.voice_max_seconds)
    except VoiceNoteTooLong as e:
        log.info("voice note from %s too long: %s", mask_phone(sender), e)
        return VoiceOutcome(t("too_long", lang, minutes=settings.voice_max_seconds // 60))
    except (TranscriptionFailed, ProviderError, httpx.HTTPError) as e:
        log.warning("transcription failed for %s: %s", mask_phone(sender), type(e).__name__)
        return VoiceOutcome(t("not_heard", lang))
    finally:
        del audio  # drop the only in-memory copy
        try:
            await wa.delete_media(media_id)
        except httpx.HTTPError as e:  # best effort; the reply still goes out
            log.info("media delete failed: %s", type(e).__name__)

    # Timings only, never the transcript. asr and spark_audio run in parallel, then reconcile.
    tm = result.timings
    log.info("voice note from %s: confidence=%s read_back=%s hypotheses=%s audio=%.0fs | download=%.1fs "
             "convert=%.1fs asr=%.1fs spark_audio=%.1fs reconcile=%.1fs total=%.1fs",
             mask_phone(sender), result.confidence, result.needs_confirmation, sorted(result.hypotheses),
             tm.get("audio", 0), download_s, tm.get("convert", 0), tm.get("asr", 0), tm.get("spark_audio", 0),
             tm.get("reconcile", 0), time.perf_counter() - t0)
    return VoiceOutcome(compose_reply(result, lang), result if result.transcript.strip() else None)


def voice_replies_enabled(lang: str | None) -> bool:
    """Spoken replies (MMS-TTS Hausa, not built yet) only go to users in Hausa mode."""
    return lang == "ha"
