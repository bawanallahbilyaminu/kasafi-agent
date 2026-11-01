"""Eval runs and batch jobs on Muse Spark Open (settings.kasafi_batch_provider): off by default (live users and the
demo stay on Muse Spark), the host order follows the setting, and every call gets the token floor Open needs."""

import asyncio

import pytest
from pydantic import SecretStr

from app.providers.chat import ChatResult
from app.providers.fireworks import BatchModel, batch_factory
from tests.helpers import make_settings


def test_off_by_default_and_only_for_the_two_open_hosts() -> None:
    assert batch_factory(make_settings()) is None
    assert batch_factory(make_settings(kasafi_batch_provider="meta")) is None
    assert batch_factory(make_settings(kasafi_batch_provider="baseten")) is BatchModel
    assert batch_factory(make_settings(kasafi_batch_provider="Fireworks")) is BatchModel


def keys(**kw):
    return make_settings(baseten_api_key=SecretStr("b"), fireworks_api_key=SecretStr("f"), **kw)


@pytest.mark.parametrize("choice, first", [("baseten", "Baseten"), ("fireworks", "Fireworks")])
def test_host_order_follows_the_setting(choice: str, first: str) -> None:
    m = BatchModel(keys(kasafi_batch_provider=choice))
    assert m.open.hosts[0].provider == first and len(m.open.hosts) == 2
    asyncio.run(m.aclose())


def test_a_missing_key_leaves_the_other_host_and_no_keys_is_an_error() -> None:
    m = BatchModel(make_settings(kasafi_batch_provider="baseten", fireworks_api_key=SecretStr("f")))
    assert [h.provider for h in m.open.hosts] == ["Fireworks"]
    asyncio.run(m.aclose())
    with pytest.raises(RuntimeError):
        BatchModel(make_settings(kasafi_batch_provider="baseten"))


def test_every_call_gets_the_token_floor_and_a_low_effort() -> None:
    m = BatchModel(keys(kasafi_batch_provider="baseten"))
    seen = {}

    async def fake(messages, *, model=None, **params):
        seen.update(params, model=model)
        return ChatResult("{}", "muse-spark-open", "stop")
    m.open.chat = fake
    asyncio.run(m.chat([{"role": "user", "content": "q"}], model="muse-spark-1.3", reasoning_effort="minimal",
                       max_tokens=400))
    assert seen["max_tokens"] == BatchModel.MIN_TOKENS and seen["reasoning_effort"] == "low"
    asyncio.run(m.chat([], max_tokens=12000, reasoning_effort="high"))
    assert seen["max_tokens"] == 12000 and seen["reasoning_effort"] == "high"
    asyncio.run(m.aclose())
