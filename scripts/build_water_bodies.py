"""Build the water-body layer (app/place/water.py): JRC occurrence bodies over Sokoto State at 30 m, named from
OpenStreetMap and data/geo/water_bodies.yaml, into data/geo/water_bodies.geojson (outside git).

Usage: uv run python scripts/build_water_bodies.py [--workers 4]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    import psycopg
    from app.config import get_settings
    from app.place import water
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(water.LAYER))
    a = ap.parse_args()
    t0 = time.time()
    with psycopg.connect(get_settings().db_url()) as conn:
        stats = water.build(conn, Path(a.out), a.workers)
    print(f"water bodies: {stats['bodies']} (occurrence >= {water.OCCURRENCE}%, >= {water.MIN_BODY_HA} ha, 8-connected) "
          f"from {stats['water_pixels']} water pixels on a {stats['grid'][1]}x{stats['grid'][0]} grid at 30 m; "
          f"{stats['area_ha']:,.0f} ha in all")
    print(f"seasonal extents (occurrence >= {water.SEASONAL_OCCURRENCE}%, >= {water.MIN_SEASONAL_HA} ha): {stats['seasonal']}")
    print(f"named: {stats['named']} permanent bodies and {stats['seasonal_named']} seasonal extents ({stats['osm_named']} "
          f"from OSM out of {stats['osm_features']} named OSM water features in the box, {stats['yaml_named']} from "
          f"data/geo/water_bodies.yaml)")
    print("largest:", "; ".join(f"{b.name or '(unnamed)'} {b.area_ha:,.0f} ha, {b.occurrence:.0f}%" for b in stats["largest"]))
    print("named:", "; ".join(f"{b.name} ({'seasonal, ' if b.seasonal else ''}{b.area_ha:,.0f} ha, {b.source})"
                              for b in stats["named_list"]))
    print(f"timings {stats['seconds']}; total {time.time() - t0:.0f}s; written to {a.out}")


if __name__ == "__main__":
    main()
