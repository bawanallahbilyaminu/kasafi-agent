"""Run the hazard fetchers once by hand: every layer that is due (or the ones named), after making sure the fetch
points exist (docs/hazard-and-services.md section 4). The app runs the same on a schedule with KASAFI_HAZARD_FETCH.

    uv run python scripts/fetch_hazards.py                    # the layers that are due
    uv run python scripts/fetch_hazards.py forecast air       # these layers now
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.hazards.fetch import run_due, run_layer  # noqa: E402
from app.hazards.points import ensure_points  # noqa: E402


async def main(layers: list[str]) -> None:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
    s = get_settings()
    with psycopg.connect(s.db_url(), autocommit=True) as conn:
        print("points:", ensure_points(conn))
        print({layer: await run_layer(conn, layer, s) for layer in layers} if layers else await run_due(conn, s))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
