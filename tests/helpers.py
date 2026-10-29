"""Shared test helpers for the conversation flow."""

import asyncio

from pydantic import SecretStr

from app.config import Settings
from app.guardrails.scope import Verdict, keyword_check
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
               resolve_calls: list | None = None, model_verdicts: dict | None = None, guard_calls: list | None = None,
               answer_calls: list | None = None, answer_error: Exception | None = None,
               history_calls: list | None = None, answer_delay: float = 0.0):
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

    async def fake_guard(texts, *, settings):
        """Real keyword tier; model tier replaced by model_verdicts {text: category}."""
        if guard_calls is not None:
            guard_calls.append(list(texts))
        if cat := keyword_check(texts):
            return Verdict(cat, "keyword")
        for text in texts:
            if text in (model_verdicts or {}):
                return Verdict(model_verdicts[text], "model")
        return Verdict("ok", "none")

    async def fake_answer(question, lang, *, settings, notify=None, history=None):
        """Stands in for answer_from_documents. Only used when answer_calls is given."""
        if answer_error is not None:
            raise answer_error
        answer_calls.append((question, lang))
        if history_calls is not None:
            history_calls.append(history)
        if answer_delay:
            await asyncio.sleep(answer_delay)
        return f"ANSWER[{lang}]: {question}"

    async def notify(out):
        if notified is not None:
            notified.append(out)

    outs = asyncio.run(handle(msg, None, store=store, settings=settings or make_settings(), voice_fn=fake_voice,
                              notify=notify, resolve_fn=fake_resolve, guard_fn=fake_guard,
                              **({"answer_fn": fake_answer} if answer_calls is not None or answer_error else {})))
    return outs, store
