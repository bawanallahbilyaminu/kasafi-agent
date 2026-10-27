"""Shared test helpers for the conversation flow."""

import asyncio

from pydantic import SecretStr

from app.config import Settings
from app.providers.stt import SpeechResult
from app.users import UserStore
from app.whatsapp.conversation import handle
from app.whatsapp.corrections import Resolution, quick_resolve
from app.whatsapp.voice import VoiceOutcome, compose_reply


def make_settings(**kw) -> Settings:
    base = {"kasafi_hash_key": SecretStr("test-hash-key"), "meta_api_key": SecretStr("k")}
    return Settings(_env_file=None, **{**base, **kw})


def heard(transcript: str, *, confirm: bool = False, english: str = "") -> SpeechResult:
    return SpeechResult(transcript=transcript, english=english or transcript, language="ha",
                        confidence="low" if confirm else "high", needs_confirmation=confirm)


def run_handle(msg: dict, *, store: UserStore | None = None, settings: Settings | None = None, voice_calls=None,
               notified: list | None = None, spoken: SpeechResult | None = None, corrections: dict | None = None,
               resolve_calls: list | None = None):
    """Run the conversation flow with fakes.

    spoken:      what the fake voice pipeline "heard" (None means a plain VOICE[lang] reply)
    corrections: {reply: Resolution} returned by the fake model merge (default: kind "new")
    """
    store = store or UserStore(":memory:")

    async def fake_voice(m, wa, *, lang, settings):
        if voice_calls is not None:
            voice_calls.append(lang)
        if spoken is None:
            return VoiceOutcome(f"VOICE[{lang}]")
        return VoiceOutcome(compose_reply(spoken, lang), spoken)

    async def fake_resolve(pending, reply, *, settings):
        if quick := quick_resolve(reply):
            return quick
        if resolve_calls is not None:
            resolve_calls.append((pending, reply))
        res = (corrections or {}).get(reply, Resolution("new", reply))
        if isinstance(res, Exception):
            raise res
        return res

    async def notify(out):
        if notified is not None:
            notified.append(out)

    outs = asyncio.run(handle(msg, None, store=store, settings=settings or make_settings(), voice_fn=fake_voice,
                              notify=notify, resolve_fn=fake_resolve))
    return outs, store
