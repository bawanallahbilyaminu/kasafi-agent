"""Fetch OpenStreetMap place names in Sokoto State (cities, towns, villages, hamlets, localities) for the gazetteer.

One Overpass API query for place nodes inside the state's bounding box, written to
data/geo/osm_places_sokoto.geojson (not in git); scripts/import_geo.py keeps the ones inside Sokoto's LGAs.
OSM data is (c) OpenStreetMap contributors, ODbL: credited wherever a place is used.

    uv run python scripts/fetch_osm_places.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "geo" / "osm_places_sokoto.geojson"
OVERPASS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
BBOX = (10.9, 3.4, 14.0, 6.9)                 # south, west, north, east: Sokoto State and a margin
QUERY = (f"[out:json][timeout:120];node[place~\"^(city|town|village|hamlet|suburb|neighbourhood|locality|"
         f"isolated_dwelling|quarter)$\"]{BBOX};out;")


def main() -> None:
    for url in OVERPASS:                       # the main instance, then a mirror (both are often busy)
        try:
            r = httpx.post(url, data={"data": QUERY}, timeout=180,
                           headers={"User-Agent": "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"})
            r.raise_for_status()
            break
        except httpx.HTTPError as e:
            print(f"{url}: {type(e).__name__}")
    else:
        raise SystemExit("no Overpass instance answered; try again later")
    feats = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [e["lon"], e["lat"]]},
              "properties": {"name": e["tags"].get("name"), "name:ha": e["tags"].get("name:ha"),
                             "place": e["tags"].get("place"), "osm_id": e["id"]}}
             for e in r.json().get("elements", []) if e.get("tags", {}).get("name")]
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    print(len(feats), "named places ->", OUT)


if __name__ == "__main__":
    sys.exit(main())
