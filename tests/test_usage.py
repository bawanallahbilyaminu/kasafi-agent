"""Eval runs: what they cost, that they fetch only when a case needs it, and that they never message anyone."""

import asyncio
import json
import subprocess
import sys

from app import usage
from app.acquisition import library
from app.agent import answer as ans
from tests.helpers import make_settings


def test_a_runs_cost_is_counted_per_provider_with_cached_tokens_cheaper() -> None:
    usage.reset()
    usage.record_chat("Meta", {"prompt_tokens": 4000, "completion_tokens": 600,
                               "prompt_tokens_details": {"cached_tokens": 3000}})
    usage.record_chat("Baseten", {"prompt_tokens": 1000, "completion_tokens": 1000})
    usage.count("serper_queries", 2)
    out = usage.summary(make_settings())
    assert "Meta: 1 calls, 4,000 prompt tokens (3,000 cached), 600 output tokens -> $0.00" in out
    assert round(usage.dollars(usage.chat["Meta"], 1.25, 0.15, 4.25), 6) == round((1000 * 1.25 + 3000 * 0.15
                                                                                  + 600 * 4.25) / 1e6, 6)
    assert "Serper queries: 2 | documents fetched: 0" in out
    usage.reset()


def test_cost_per_answer_is_broken_down_by_stage_and_provider_without_the_evals_own_calls() -> None:
    usage.reset()
    for stage, prov in (("plan", "Meta"), ("read1", "Meta"), ("read2", "Baseten"), ("paraphrase", "Meta")):
        with usage.stage(stage):
            usage.record_chat(prov, {"prompt_tokens": 1_000_000, "completion_tokens": 0})
    out = usage.summary(make_settings(), answers=2)
    assert "per answer (2 answers): $1.8750, 1.5 model calls" in out           # 3 calls x $1.25, paraphrase out
    assert "Meta/plan" in out and "Baseten/read2" in out and "Meta/paraphrase" not in out
    usage.reset()


def test_identical_calls_in_an_eval_run_are_answered_once_but_never_across_the_two_readings() -> None:
    import httpx

    from app.providers.chat import ChatClient
    sent = []

    def reply(request):
        sent.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
                                         "usage": {"prompt_tokens": 10, "completion_tokens": 1}})
    c = ChatClient(base_url="https://x", api_key="k", default_model="m", transport=httpx.MockTransport(reply))
    usage.reset()
    usage._cache = None
    msgs = [{"role": "user", "content": "q"}]
    asyncio.run(c.chat(msgs))
    asyncio.run(c.chat(msgs))
    assert len(sent) == 2                                      # the app never caches
    usage.enable_cache()
    try:
        for stage in ("read1", "read1", "read2"):
            with usage.stage(stage):
                asyncio.run(c.chat(msgs))
        assert len(sent) == 4 and usage.counts["cache_hits"] == 1    # read2 is its own reading, not read1's reply
    finally:
        usage._cache = None
        usage.reset()


def test_a_stage_on_muse_spark_open_falls_back_to_muse_spark(monkeypatch) -> None:
    calls = []

    class Client:
        def __init__(self, name, fail=False):
            self.name, self.fail = name, fail

        async def chat(self, messages, **kw):
            calls.append((self.name, kw["model"]))
            if self.fail:
                raise RuntimeError("down")
            from app.providers.chat import ChatResult
            return ChatResult(content='{"ok": 1}', model=kw["model"], finish_reason="stop")
    s = make_settings(kasafi_open_stages="plan, compose")
    msgs = [{"role": "user", "content": "q"}]
    assert asyncio.run(ans.stage_json("plan", Client("meta"), Client("open"), s, msgs, reasoning_effort="minimal",
                                      max_tokens=3000)) == {"ok": 1}
    assert calls == [("open", s.baseten_model)]
    calls.clear()
    asyncio.run(ans.stage_json("plan", Client("meta"), Client("open", fail=True), s, msgs,
                               reasoning_effort="minimal", max_tokens=3000))
    assert calls == [("open", s.baseten_model), ("meta", s.meta_model)]
    calls.clear()
    asyncio.run(ans.stage_json("scope", Client("meta"), Client("open"), s, msgs, reasoning_effort="low",
                               max_tokens=100))
    assert calls == [("meta", s.meta_model)]                    # not listed: Muse Spark


def test_muse_spark_open_falls_back_from_baseten_to_fireworks_with_its_own_model_id() -> None:
    import httpx

    from app.providers.baseten import BasetenClient
    from app.providers.fireworks import FireworksClient, OpenModel
    from pydantic import SecretStr
    seen = []

    def host(status):
        def reply(request):
            seen.append((request.url.host, json.loads(request.content)["model"]))
            return httpx.Response(status, json={"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                                                "usage": {}} if status == 200 else {"error": "out of credits"})
        return httpx.MockTransport(reply)
    s = make_settings(baseten_api_key=SecretStr("b"), fireworks_api_key=SecretStr("f"))
    open_model = OpenModel([BasetenClient(s, transport=host(402), max_retries=0),
                            FireworksClient(s, transport=host(200), max_retries=0)])
    r = asyncio.run(open_model.chat([{"role": "user", "content": "q"}], model="ignored"))
    assert r.content == "ok"
    assert seen == [("inference.baseten.co", s.baseten_model), ("api.fireworks.ai", s.fireworks_model)]


def test_the_hazard_keys_are_optional() -> None:
    s = make_settings()
    assert s.ors_api_key is None and s.firms_map_key is None      # everything must work without them


def test_fetching_off_is_not_a_failed_search_and_the_limit_is_said_plainly() -> None:
    s = usage.eval_settings(make_settings(), fetch=False)
    assert not s.kasafi_fetch_enabled and not s.kasafi_open_web
    got = asyncio.run(library.find_and_fetch(None, "Some report", settings=s, client=None, check_local=False))
    assert got.status == "off"
    plan = ans.Plan("q", ["q"], [])
    plan.missing_document = "Sokoto State BIR Q3 2025"
    a = ans._not_found(None, plan, "en", library.Acquired("limit", detail="daily fetch limit"), {})
    assert a.text.startswith("I've reached today's limit for fetching new documents") and "try again tomorrow" in a.text


def test_the_eval_runners_never_load_the_whatsapp_client() -> None:
    code = ("import sys; sys.argv=['x']; sys.path.insert(0,'.'); "
            "import evals.run_answer_eval, evals.complex.run_open, evals.generated.run; "
            "print(any(m.startswith('app.whatsapp') for m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert out.stdout.strip().endswith("False"), out.stderr[-500:]
