"""Eval runs: what they cost, that they fetch only when a case needs it, and that they never message anyone."""

import asyncio
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
