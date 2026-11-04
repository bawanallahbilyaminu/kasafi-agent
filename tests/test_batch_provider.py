"""Eval runs and batch jobs on Muse Spark Open (settings.kasafi_batch_provider): off by default (live users and the
demo stay on Muse Spark), the host order follows the setting, and every call gets the token floor Open needs."""

import asyncio

import pytest
from pydantic import SecretStr

from app.providers.chat import ChatResult
from app.providers.fireworks import BatchModel, batch_factory, open_hosts, open_model
from tests.helpers import make_settings


def test_off_by_default_and_only_for_the_two_open_hosts() -> None:
    assert batch_factory(make_settings()) is None
    assert batch_factory(make_settings(kasafi_batch_provider="meta")) is None
    assert batch_factory(make_settings(kasafi_batch_provider="baseten")) is BatchModel
    assert batch_factory(make_settings(kasafi_batch_provider="Fireworks")) is BatchModel


def keys(**kw):
    return make_settings(baseten_api_key=SecretStr("b"), fireworks_api_key=SecretStr("f"), **kw)


def test_baseten_serves_nothing_unless_the_hosts_setting_names_it() -> None:
    """4 Nov 2026: Baseten's credit ran out (every call a 402). With its key still set, no path uses it."""
    m = BatchModel(keys(kasafi_batch_provider="baseten"))
    assert [h.provider for h in m.open.hosts] == ["Fireworks"]
    asyncio.run(m.aclose())
    assert [h.provider for h in open_hosts(keys())] == ["Fireworks"]
    assert [h.provider for h in open_hosts(keys(kasafi_open_hosts="fireworks, baseten"))] == ["Fireworks", "Baseten"]
    assert open_hosts(make_settings(baseten_api_key=SecretStr("b"))) == []        # no Fireworks key: no host
    assert open_model(make_settings()) is None


@pytest.mark.parametrize("choice, first", [("baseten", "Baseten"), ("fireworks", "Fireworks")])
def test_host_order_follows_the_setting_among_the_named_hosts(choice: str, first: str) -> None:
    m = BatchModel(keys(kasafi_batch_provider=choice, kasafi_open_hosts="fireworks,baseten"))
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
