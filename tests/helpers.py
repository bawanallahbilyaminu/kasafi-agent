"""Shared test helpers for the conversation flow."""

import asyncio

from pydantic import SecretStr

from app.config import Settings
from app.users import UserStore
from app.whatsapp.conversation import handle


def make_settings(**kw) -> Settings:
    base = {"kasafi_hash_key": SecretStr("test-hash-key"), "meta_api_key": SecretStr("k")}
    return Settings(_env_file=None, **{**base, **kw})


def run_handle(msg: dict, *, store: UserStore | None = None, settings: Settings | None = None, voice_calls=None,
               notified: list | None = None):
    store = store or UserStore(":memory:")

    async def fake_voice(m, wa, *, lang, settings):
        if voice_calls is not None:
            voice_calls.append(lang)
        return f"VOICE[{lang}]"

    async def notify(out):
        if notified is not None:
            notified.append(out)

    outs = asyncio.run(handle(msg, None, store=store, settings=settings or make_settings(), voice_fn=fake_voice,
                              notify=notify))
    return outs, store
