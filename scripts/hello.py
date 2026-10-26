"""Smoke test for the model providers: one short Hausa chat on each.

Usage:  uv run python scripts/hello.py [--provider meta|baseten|both] [--model ...]
Needs META_API_KEY / BASETEN_API_KEY in .env. Uses only our own test text (no user data).
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.providers.baseten import BasetenClient  # noqa: E402
from app.providers.chat import ChatClient  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402

PROVIDERS = {"meta": MetaClient, "baseten": BasetenClient}


async def hello(client: ChatClient, model: str | None, list_models: bool) -> None:
    if list_models:
        print("Models:", ", ".join(sorted(await client.list_models())))
    result = await client.chat(
        [
            {"role": "system", "content": "Kai mataimaki ne mai amsa a takaice cikin Hausa."},
            {"role": "user", "content": "Sannu! Mene ne kasafin kudi? Amsa a jimla daya."},
        ],
        model=model,
        # max_tokens caps reasoning + visible output combined on both providers,
        # so keep reasoning low and leave room for the answer.
        reasoning_effort="low",
        max_tokens=2000,
    )
    print(f"[{client.provider} {result.model}] finish={result.finish_reason} usage={result.usage}")
    print(f"reasoning: {len(result.reasoning)} chars")
    print(result.content)


async def main(provider: str, model: str | None) -> None:
    for name in PROVIDERS if provider == "both" else [provider]:
        print(f"\n=== {name} ===")
        async with PROVIDERS[name]() as client:
            await hello(client, model, list_models=name == "meta")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=[*PROVIDERS, "both"], default="both")
    p.add_argument("--model", default=None)
    a = p.parse_args()
    asyncio.run(main(a.provider, a.model))
