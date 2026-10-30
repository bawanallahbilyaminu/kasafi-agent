"""What a run used: model calls and tokens per provider, web search queries and documents fetched.

Process-wide counters, recorded where the calls are made (ChatClient.chat, find.search_web, library.fetch_and_index),
so an eval run can print its cost at the end (summary()). Prices are per million tokens, from settings
(kasafi_price_*), so they can be corrected without code changes.
"""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class Tokens:
    calls: int = 0
    prompt: int = 0
    cached: int = 0
    completion: int = 0           # includes reasoning tokens (billed as output)

    def add(self, usage: dict) -> None:
        self.calls += 1
        self.prompt += int(usage.get("prompt_tokens") or 0)
        self.cached += int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
        self.completion += int(usage.get("completion_tokens") or 0)


chat: dict[str, Tokens] = defaultdict(Tokens)
by_stage: dict[str, Tokens] = defaultdict(Tokens)    # "provider/stage" -> tokens
counts: dict[str, int] = defaultdict(int)     # serper_queries, documents_fetched, fetch_attempts, answers

# the pipeline stage a model call belongs to (plan, read, compose, topic, ...), set around the call
_stage: ContextVar[str] = ContextVar("kasafi_stage", default="other")


@contextmanager
def stage(name: str):
    token = _stage.set(name)
    try:
        yield
    finally:
        _stage.reset(token)


# identical model calls within an eval run are answered once (enable_cache: eval runners only, never the app);
# the key holds the stage, so the two independent row readings are never one cached reply
_cache: dict[str, object] | None = None


def enable_cache() -> None:
    global _cache
    _cache = {} if _cache is None else _cache


def cache_key(provider: str, body: dict) -> str | None:
    if _cache is None:
        return None
    import hashlib
    import json
    raw = json.dumps([provider, _stage.get(), body], sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def cached(key: str | None):
    if key is not None and _cache is not None and key in _cache:
        counts["cache_hits"] += 1
        return _cache[key]
    return None


def keep(key: str | None, result) -> None:
    if key is not None and _cache is not None:
        _cache[key] = result


def record_chat(provider: str, usage: dict) -> None:
    chat[provider].add(usage)
    by_stage[f"{provider}/{_stage.get()}"].add(usage)


def count(what: str, n: int = 1) -> None:
    counts[what] += n


def reset() -> None:
    chat.clear()
    by_stage.clear()
    counts.clear()


def snapshot() -> dict:
    """The counters as plain data, saved with an eval's checkpoint so a resumed run's cost covers the whole run."""
    return {"chat": {p: vars(t).copy() for p, t in chat.items()},
            "by_stage": {k: vars(t).copy() for k, t in by_stage.items()}, "counts": dict(counts)}


def restore(snap: dict) -> None:
    reset()
    for p, t in (snap.get("chat") or {}).items():
        chat[p] = Tokens(**t)
    for k, t in (snap.get("by_stage") or {}).items():
        by_stage[k] = Tokens(**t)
    counts.update(snap.get("counts") or {})


def eval_settings(settings, *, fetch: bool):
    """An eval case's settings: fetching new documents and the open web only for the cases that need them."""
    return settings.model_copy(update={"kasafi_fetch_enabled": fetch, "kasafi_open_web": fetch})


def dollars(t: Tokens, price_in: float, price_cached: float, price_out: float) -> float:
    return ((t.prompt - t.cached) * price_in + t.cached * price_cached + t.completion * price_out) / 1e6


EVAL_STAGES = ("/paraphrase",)


def prices(settings) -> dict[str, tuple[float, float, float]]:
    return {"Meta": (settings.kasafi_price_meta_in, settings.kasafi_price_meta_cached, settings.kasafi_price_meta_out),
            "Baseten": (settings.kasafi_price_baseten_in, settings.kasafi_price_baseten_cached,
                        settings.kasafi_price_baseten_out),
            "Fireworks": (settings.kasafi_price_fireworks_in, settings.kasafi_price_fireworks_cached,
                          settings.kasafi_price_fireworks_out)}


def total_dollars(settings) -> float:
    p = prices(settings)
    return sum(dollars(t, *p[prov]) for prov, t in chat.items() if prov in p)


def summary(settings, answers: int = 0) -> str:
    """The run's cost, one line per provider, then per answer by stage and provider, then searches and fetches."""
    p = prices(settings)
    lines, total = ["Cost of this run:"], 0.0
    for provider, t in sorted(chat.items()):
        usd = dollars(t, *p[provider]) if provider in p else 0.0
        total += usd
        lines.append(f"  {provider}: {t.calls} calls, {t.prompt:,} prompt tokens ({t.cached:,} cached), "
                     f"{t.completion:,} output tokens -> ${usd:.2f}"
                     + ("" if provider in p else " (no price set)"))
    lines.append(f"  models together: ${total:.2f} (prices per 1M tokens from settings kasafi_price_*)")
    if answers:                      # the eval's own calls (paraphrasing test questions) are not an answer's
        stages = {k: (t, dollars(t, *p.get(k.split("/")[0], (0, 0, 0)))) for k, t in by_stage.items()
                  if not k.endswith(EVAL_STAGES)}
        usd_all = sum(u for _, u in stages.values())
        lines.append(f"  per answer ({answers} answers): ${usd_all / answers:.4f}, "
                     f"{sum(t.calls for t, _ in stages.values()) / answers:.1f} model calls")
        for key, (t, usd) in sorted(stages.items(), key=lambda kv: -kv[1][1]):
            lines.append(f"    {key:<22} {t.calls / answers:5.2f} calls  ${usd / answers:.4f}  "
                         f"({100 * usd / usd_all if usd_all else 0:.0f}%)")
    lines.append(f"  Serper queries: {counts['serper_queries']} | documents fetched: {counts['documents_fetched']} "
                 f"(downloads tried: {counts['fetch_attempts']})"
                 + (f" | identical calls answered from the run's cache: {counts['cache_hits']}"
                    if _cache is not None else ""))
    return "\n".join(lines)
