"""Render the sample maps into data/samples/ (not in git) from the local database, for review by eye.

    uv run python scripts/map_samples.py

heat.jpg, dust.jpg and river.jpg use today's data; near_you.jpg is from a test point near Goronyo town (no real
user's location) with ORS road distances and route when ORS_API_KEY is set; heat_mixed_simulated.jpg uses made-up
values with several categories, to check how a mixed day reads.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.geo import facilities as fac  # noqa: E402
from app.hazards import read  # noqa: E402
from app.maps import render  # noqa: E402

OUT = Path("data/samples")
TEST_POINT = (13.44, 5.67)              # near Goronyo town: a sample point, not anyone's location


def main() -> None:
    s = get_settings()
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.now(read.LAGOS).date()
    with psycopg.connect(s.db_url()) as conn:
        for layer, name in (("heat", "heat"), ("air", "dust")):
            m = render.hazard_map(conn, layer, today, "en", "NG034006", today)
            print(name, "no data" if m is None else (OUT / f"{name}.jpg").write_bytes(m.jpeg))
        m = render.river_map(conn, today, "en", today)
        print("river", "no data" if m is None else (OUT / "river.jpg").write_bytes(m.jpeg))
        found = fac.nearest_facilities(conn, *TEST_POINT, fac.Filters(levels=("Secondary", "Tertiary")))
        routed = asyncio.run(fac.add_routes(s, *TEST_POINT, found))
        if routed:
            found.sort(key=lambda f: (f.minutes is None, f.minutes or 0))
        line = asyncio.run(fac.route_line(s, *TEST_POINT, found[0])) if found else []
        m = render.near_you_map(conn, *TEST_POINT, "Goronyo", found, line, "en")
        print("near_you", (OUT / "near_you.jpg").write_bytes(m.jpeg), "routed" if routed else "straight line")
        names = [r[0] for r in conn.execute("SELECT name FROM lga ORDER BY name").fetchall()]
        mixed = {}
        for i, n in enumerate(names):
            v = 33.0 + (i * 7 % 19) * 0.6
            mixed[n] = (render.cat.heat_category(v), v, f"{v:.0f} °C")
        render.lga_values = lambda conn, layer, day: mixed          # the simulation only
        render._cache.clear()
        m = render.hazard_map(conn, "heat", today, "en", "", today)
        print("heat_mixed_simulated", (OUT / "heat_mixed_simulated.jpg").write_bytes(m.jpeg))


if __name__ == "__main__":
    main()
