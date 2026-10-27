"""Voice notes: download, transcribe (combined STT pipeline), discard, read back.

Privacy (docs/architecture.md "Data retention", halalnumeriq.com.ng/kasafi/privacy):
- The audio is held in memory only (ffmpeg's temp file is deleted at once), dropped as soon
  as it is transcribed, and Meta's copy is deleted. Nothing is written to our storage.
- Only the audio goes to the model APIs, never the phone number or WhatsApp name.
- Only pilot numbers (KASAFI_PILOT_NUMBERS) are processed during the hackathon (CLAUDE.md rule 7).
- Logs record timings and confidence, never the transcript.

Per the speech decision, unclear audio is never answered: when the pipeline isn't sure,
the reply is a read-back question ("Kana nufin …?").
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.chat import ProviderError
from app.providers.meta import MetaClient
from app.providers.stt import SpeechResult, TranscriptionFailed, VoiceNoteTooLong, transcribe_voice_note
from app.whatsapp.client import MediaError, WhatsAppClient, mask_phone

log = logging.getLogger(__name__)

NOT_IN_PILOT = (
    "Kasafi yana cikin gwaji, kuma ba a buɗe saƙon murya ga kowa ba tukuna. Don Allah ka rubuta tambayarka.\n"
    "Kasafi is in a pilot; voice notes aren't open to everyone yet. Please type your question."
)
TOO_LONG = "Saƙon murya ya yi tsawo. Don Allah ka tura gajere (ƙasa da minti {minutes}), ko ka rubuta tambayarka."
NOT_HEARD = "Yi haƙuri, ban ji saƙon muryar sosai ba. Don Allah ka sake turawa, ko ka rubuta tambayarka."
READ_BACK = "Na ji kamar ka ce:\n«{transcript}»\n\nKana nufin haka? Ka amsa *Eh*, ko ka sake faɗa ko rubuta tambayarka."
HEARD = "Na ji tambayarka:\n«{transcript}»\n\n(Kasafi yana gwaji: amsoshi za su zo nan ba da jimawa ba.)"


def is_pilot(number: str, settings: Settings) -> bool:
    return "".join(ch for ch in number if ch.isdigit()) in settings.pilot_numbers


def compose_reply(result: SpeechResult) -> str:
    transcript = result.transcript.strip()
    if not transcript:
        return NOT_HEARD
    template = READ_BACK if result.needs_confirmation else HEARD
    return template.format(transcript=transcript[:1000])


async def reply_for_voice(
    msg: dict[str, Any],
    wa: WhatsAppClient,
    *,
    settings: Settings | None = None,
    meta_client_factory: type[MetaClient] = MetaClient,
) -> str:
    settings = settings or get_settings()
    sender = msg.get("from", "")
    media_id = (msg.get("audio") or {}).get("id")
    if not is_pilot(sender, settings):
        log.info("voice note from non-pilot %s not processed", mask_phone(sender))
        return NOT_IN_PILOT
    if not media_id:
        return NOT_HEARD

    t0 = time.perf_counter()
    try:
        audio = await wa.download_media(media_id)
    except MediaError as e:
        log.warning("voice note download failed for %s: %s", mask_phone(sender), e)
        return NOT_HEARD

    try:
        async with meta_client_factory(settings) as client:
            result = await transcribe_voice_note(audio, client, settings=settings,
                                                 max_seconds=settings.voice_max_seconds)
    except VoiceNoteTooLong as e:
        log.info("voice note from %s too long: %s", mask_phone(sender), e)
        return TOO_LONG.format(minutes=settings.voice_max_seconds // 60)
    except (TranscriptionFailed, ProviderError, httpx.HTTPError) as e:
        log.warning("transcription failed for %s: %s", mask_phone(sender), type(e).__name__)
        return NOT_HEARD
    finally:
        del audio  # drop the only in-memory copy
        try:
            await wa.delete_media(media_id)
        except httpx.HTTPError as e:  # best effort; the reply still goes out
            log.info("media delete failed: %s", type(e).__name__)

    log.info("voice note from %s: confidence=%s read_back=%s hypotheses=%s took=%.1fs",
             mask_phone(sender), result.confidence, result.needs_confirmation,
             sorted(result.hypotheses), time.perf_counter() - t0)
    return compose_reply(result)
