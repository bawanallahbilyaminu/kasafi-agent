"""What a run used: model calls and tokens per provider, web search queries and documents fetched.

Process-wide counters, recorded where the calls are made (ChatClient.chat, find.search_web, library.fetch_and_index),
so an eval run can print its cost at the end (summary()). Prices are per million tokens, from settings
(kasafi_price_*), so they can be corrected without code changes.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Tokens:
    calls: int = 0
    prompt: int = 0
    cached: int = 0
    completion: int = 0           # includes reasoning tokens (billed as output)


chat: dict[str, Tokens] = defaultdict(Tokens)
counts: dict[str, int] = defaultdict(int)     # serper_queries, documents_fetched, fetch_attempts


def record_chat(provider: str, usage: dict) -> None:
    t = chat[provider]
    t.calls += 1
    t.prompt += int(usage.get("prompt_tokens") or 0)
    t.cached += int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    t.completion += int(usage.get("completion_tokens") or 0)


def count(what: str, n: int = 1) -> None:
    counts[what] += n


def reset() -> None:
    chat.clear()
    counts.clear()


def eval_settings(settings, *, fetch: bool):
    """An eval case's settings: fetching new documents and the open web only for the cases that need them."""
    return settings.model_copy(update={"kasafi_fetch_enabled": fetch, "kasafi_open_web": fetch})


def dollars(t: Tokens, price_in: float, price_cached: float, price_out: float) -> float:
    return ((t.prompt - t.cached) * price_in + t.cached * price_cached + t.completion * price_out) / 1e6


def summary(settings) -> str:
    """The run's cost, one line per provider, then searches and fetches."""
    prices = {"Meta": (settings.kasafi_price_meta_in, settings.kasafi_price_meta_cached, settings.kasafi_price_meta_out),
              "Baseten": (settings.kasafi_price_baseten_in, settings.kasafi_price_baseten_cached,
                          settings.kasafi_price_baseten_out)}
    lines, total = ["Cost of this run:"], 0.0
    for provider, t in sorted(chat.items()):
        usd = dollars(t, *prices[provider]) if provider in prices else 0.0
        total += usd
        lines.append(f"  {provider}: {t.calls} calls, {t.prompt:,} prompt tokens ({t.cached:,} cached), "
                     f"{t.completion:,} output tokens -> ${usd:.2f}"
                     + ("" if provider in prices else " (no price set)"))
    lines.append(f"  models together: ${total:.2f} (prices per 1M tokens from settings kasafi_price_*)")
    lines.append(f"  Serper queries: {counts['serper_queries']} | documents fetched: {counts['documents_fetched']} "
                 f"(downloads tried: {counts['fetch_attempts']})")
    return "\n".join(lines)
