"""Point history for the private test pins (data/private/place_pins.yaml, outside git): a table per pin and the
time of a first and a cached request. Usage: uv run python scripts/place_pins.py [--pins N] [--no-cache]"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place.history import cell_id, point_history  # noqa: E402


def fmt(v, nd=2):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pins", type=int, default=0, help="only the first N pins")
    ap.add_argument("--no-cache", action="store_true", help="clear the pins' cache rows first (a first request)")
    ap.add_argument("--file", default=str(ROOT / "data/private/place_pins.yaml"))
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "rasterio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    pins = yaml.safe_load(open(a.file, encoding="utf-8"))
    pins = pins if isinstance(pins, list) else pins.get("pins", [])
    if a.pins:
        pins = pins[: a.pins]
    with psycopg.connect(get_settings().db_url()) as conn:
        for p in pins:
            lat, lon = float(p["lat"]), float(p["lon"])
            if a.no_cache:
                conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell_id(lat, lon),))
                conn.commit()
            t0 = time.perf_counter()
            h = point_history(conn, lat, lon)
            first = time.perf_counter() - t0
            t0 = time.perf_counter()
            h2 = point_history(conn, lat, lon)
            cached = time.perf_counter() - t0
            print(f"\n=== {p['name']}  (cell {h.cell}; land cover: {h.landcover or '-'})")
            print(f"first request {first:.1f}s ({', '.join(f'{k} {v:.1f}s' for k, v in h.timing.items() if k != 'total')}); "
                  f"cached {cached:.1f}s (from cache: {h2.from_cache})")
            print(f"{'year':4} {'obs':>3} {'NDVI p90':>8} {'rain mm':>8} {'fit':>7} {'wet obs':>7} {'water':>6} "
                  f"{'dry obs':>7} {'BSI':>6}  water months")
            for y in sorted(h.years):
                r = h.years[y]
                flag = (h.fit.flags.get(y, "") if h.fit else "")
                print(f"{y:4} {r.season_obs:3} {fmt(r.ndvi_p90, 3):>8} {fmt(r.rain_season_mm, 0):>8} {flag:>7} "
                      f"{r.water_obs:7} {fmt(r.water_share):>6} {r.dry_obs:7} {fmt(r.bsi_dry, 3):>6}  "
                      f"{','.join(str(m) for m in r.water_months) or '-'}"
                      + ("" if r.usable else "   too few clear images"))
            print("usable years:", h.usable_years(), "| trends:", h.trends,
                  "| fit:", (f"sd {h.fit.sd:.3f}, slope {h.fit.slope * 100:.3f}/100 mm" if h.fit else "none (fewer than 5 years)"))
            j = h.jrc
            print(f"JRC: occurrence {fmt(j.get('occurrence'))}% recurrence {fmt(j.get('recurrence'))}% seasonality "
                  f"{fmt(j.get('seasonality'))} months; years under water: {j.get('years_under_water')}")


if __name__ == "__main__":
    main()
