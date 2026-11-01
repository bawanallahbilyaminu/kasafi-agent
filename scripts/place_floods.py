"""Flood evidence for named test pins (data/private/place_pins.yaml, outside git): radar passes under water per
year with dates, the optical water months, and the official flood maps touching the pin's 1 ha circle.
Usage: uv run python scripts/place_floods.py [--pins dundaye,kwalkwalawa,goronyo_dam] [--fresh]"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place import answer as A  # noqa: E402
from app.place import floods  # noqa: E402
from app.place.history import cell_id, point_history  # noqa: E402
from app.place.raster import circle  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pins", default="dundaye,kwalkwalawa,goronyo_dam")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--file", default=str(ROOT / "data/private/place_pins.yaml"))
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "rasterio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    pins = yaml.safe_load(open(a.file, encoding="utf-8"))
    pins = pins if isinstance(pins, list) else pins.get("pins", [])
    want = [w.strip() for w in a.pins.split(",") if w.strip()]
    today = date.today()
    with psycopg.connect(get_settings().db_url()) as conn:
        for p in pins:
            s = re.sub(r"[^a-z0-9]+", "_", p["name"].lower())
            if not any(w in s for w in want):
                continue
            lat, lon = float(p["lat"]), float(p["lon"])
            if a.fresh:
                conn.execute("DELETE FROM sat_cache WHERE cell = %s AND layer = 's1'", (cell_id(lat, lon),))
                conn.commit()
            t0 = time.perf_counter()
            h = point_history(conn, lat, lon, today=today, water=True)
            t1 = time.perf_counter()
            h.floods = floods.flood_evidence(conn, lat, lon, circle(lon, lat), today=today, on_water=h.on_water)
            t2 = time.perf_counter()
            ref = h.floods.reference
            print(f"\n=== {p['name']}  (history {t1 - t0:.1f}s, floods {t2 - t1:.1f}s; dry-season reference "
                  f"{ref.vv_db} dB over {ref.passes} passes {ref.seasons}; on water: {h.on_water})")
            for y, r in sorted(h.floods.radar.items()):
                print(f"  {y}: {r.passes:2} radar passes Jul–Oct, under water on {r.water_passes}: {', '.join(r.water) or '-'}"
                      f"   VV dB: {' '.join(f'{d[5:]}={v:.0f}' for d, v in sorted(r.vv_db.items()))}")
            print("  optical water months:", {y: r.water_months for y, r in sorted(h.years.items()) if r.water_months} or "-")
            print("  official maps:", h.floods.official or "none touch the plot")
            print("  EN:", A.flood_sentence(h, "en"))
            print("  HA:", A.flood_sentence(h, "ha"))


if __name__ == "__main__":
    main()
