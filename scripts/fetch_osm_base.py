"""Our own base map's lines (docs/hazard-and-services.md section 8): Sokoto's main roads (trunk, primary, secondary)
and rivers from OpenStreetMap through Overpass, once, into data/geo/osm_base_sokoto.geojson (not in git);
scripts/import_geo.py clips them to Sokoto's LGAs into the basemap table. No third-party map tiles are used.
Map data © OpenStreetMap contributors (ODbL).

    uv run python scripts/fetch_osm_base.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "geo" / "osm_base_sokoto.geojson"
OVERPASS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter")
BBOX = (10.9, 3.4, 14.0, 6.9)                 # south, west, north, east: Sokoto State and a margin
QUERIES = (f"[out:json][timeout:180];way[highway~\"^(trunk|primary|secondary)$\"]{BBOX};out geom;",
           f"[out:json][timeout:180];way[waterway=river]{BBOX};out geom;")


def overpass(query: str) -> list[dict]:
    for url in OVERPASS:                       # the main instance, then mirrors (all are often busy)
        try:
            r = httpx.post(url, data={"data": query}, timeout=240,
                           headers={"User-Agent": "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"})
            r.raise_for_status()
            return r.json().get("elements", [])
        except httpx.HTTPError as e:
            print(f"{url}: {type(e).__name__} {getattr(getattr(e, 'response', None), 'status_code', '')}")
    raise SystemExit("no Overpass instance answered; try again later")


def main() -> None:
    feats = []
    for e in (x for q in QUERIES for x in overpass(q)):
        tags, geom = e.get("tags", {}), e.get("geometry") or []
        if len(geom) < 2:
            continue
        kind = "river" if tags.get("waterway") == "river" else tags.get("highway", "")
        feats.append({"type": "Feature",
                      "geometry": {"type": "LineString", "coordinates": [[g["lon"], g["lat"]] for g in geom]},
                      "properties": {"kind": kind, "name": tags.get("name"), "osm_id": e["id"]}})
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    print(len(feats), "roads and rivers ->", OUT)


if __name__ == "__main__":
    sys.exit(main())
