"""Smoke test for the Meta Model API: list models, then one short Hausa chat.

Usage:  uv run python scripts/hello_meta.py [--model muse-spark-1.3]
Needs META_API_KEY in .env. Uses only our own test text (no user data).
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.providers.meta import MetaClient  # noqa: E402


async def main(model: str | None) -> None:
    async with MetaClient() as client:
        models = await client.list_models()
        print("Models:", ", ".join(sorted(models)))
        result = await client.chat(
            [
                {"role": "system", "content": "Kai mataimaki ne mai amsa a takaice cikin Hausa."},
                {"role": "user", "content": "Sannu! Mene ne kasafin kudi? Amsa a jimla daya."},
            ],
            model=model,
            # max_tokens caps reasoning + visible output combined (docs: /docs/reasoning),
            # so keep reasoning low and leave room for the answer.
            reasoning_effort="low",
            max_tokens=1000,
        )
        print(f"\n[{result.model}] finish={result.finish_reason} usage={result.usage}")
        print(result.content)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=None)
    asyncio.run(main(p.parse_args().model))
