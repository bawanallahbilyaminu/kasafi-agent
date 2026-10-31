"""Brute-force check of the place-history yearly values for one pin and year, written independently of
app/place (its own STAC calls, its own window reads from the signed cloud-optimised GeoTIFFs, plain Python
loops instead of numpy), so the tests have expected values that don't come from the code under test.

    uv run python scripts/place_check.py LAT LON YEAR [--compare]

Prints the clear season observations, the NDVI 90th percentile, the August–September water share and the
dry-season BSI median; --compare runs app.place.history for the same pin and year and reports the differences.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a"
RADIUS_M = 56.4
CLEAR = {4, 5, 6}


def get_json(url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def scenes(lat: float, lon: float, year: int) -> list[dict]:
    body = {"collections": ["sentinel-2-l2a"], "intersects": {"type": "Point", "coordinates": [lon, lat]},
            "datetime": f"{year}-02-01/{year}-10-31", "limit": 500, "query": {"eo:cloud_cover": {"lt": 70}}}
    items = []
    page = get_json(STAC, body)
    items += page["features"]
    while nxt := next((ln for ln in page.get("links", []) if ln["rel"] == "next"), None):
        page = get_json(nxt["href"], nxt.get("body") or body)
        items += page["features"]
    by_day: dict[str, dict] = {}
    for it in items:
        d = it["properties"]["datetime"][:10]
        if d not in by_day or it["properties"]["eo:cloud_cover"] < by_day[d]["properties"]["eo:cloud_cover"]:
            by_day[d] = it
    return [by_day[d] for d in sorted(by_day)]


def plot_pixels(src, lat: float, lon: float) -> list[tuple[int, int]]:
    """Row/col of every pixel whose centre lies within RADIUS_M of the pin (in the raster's CRS)."""
    from rasterio.warp import transform
    xs, ys = transform("EPSG:4326", src.crs, [lon], [lat])
    cx, cy = xs[0], ys[0]
    r = RADIUS_M
    rows, cols = [], []
    row0, col0 = src.index(cx, cy)
    span = int(r / src.res[0]) + 2
    out = []
    for row in range(row0 - span, row0 + span + 1):
        for col in range(col0 - span, col0 + span + 1):
            x, y = src.xy(row, col)
            if math.hypot(x - cx, y - cy) <= r:
                out.append((row, col))
    return out or [(row0, col0)]


def read_values(url: str, lat: float, lon: float) -> list[float]:
    import rasterio
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_PAM_ENABLED="NO"), rasterio.open(url) as src:
        px = plot_pixels(src, lat, lon)
        rows = [r for r, _ in px]
        cols = [c for _, c in px]
        win = rasterio.windows.Window(min(cols), min(rows), max(cols) - min(cols) + 1, max(rows) - min(rows) + 1)
        arr = src.read(1, window=win, boundless=True, fill_value=0)
        return [float(arr[r - min(rows), c - min(cols)]) for r, c in px]


def refl(v: float, baseline: str) -> float | None:
    if v == 0:
        return None
    return ((v - 1000.0) if baseline >= "04.00" else v) / 10000.0


def scene_value(item: dict, token: str, lat: float, lon: float, kind: str) -> float | None:
    """The plot's median index for a scene, or None when under half its pixels are clear."""
    a = item["assets"]
    baseline = str(item["properties"].get("s2:processing_baseline") or "")
    scl = read_values(a["SCL"]["href"] + "?" + token, lat, lon)       # 20 m: fewer pixels than the 10 m bands
    clear = sum(1 for v in scl if int(v) in CLEAR)
    if clear < 0.5 * len(scl):
        return None
    need = {"ndvi": ["B04", "B08"], "ndwi": ["B03", "B08"], "bsi": ["B02", "B04", "B08", "B11"]}[kind]
    bands = {b: read_values(a[b]["href"] + "?" + token, lat, lon) for b in need}
    n = min(len(v) for v in bands.values())
    vals = []
    for i in range(n):
        r = {b: refl(bands[b][i], baseline) for b in need}
        if any(v is None for v in r.values()):
            continue
        if kind == "ndvi":
            num, den = r["B08"] - r["B04"], r["B08"] + r["B04"]
        elif kind == "ndwi":
            num, den = r["B03"] - r["B08"], r["B03"] + r["B08"]
        else:
            num, den = (r["B11"] + r["B04"]) - (r["B08"] + r["B02"]), (r["B11"] + r["B04"]) + (r["B08"] + r["B02"])
        if den != 0:
            vals.append(num / den)
    return statistics.median(vals) if vals else None


def p90(values: list[float]) -> float:
    """numpy's default (linear) 90th percentile, by hand."""
    v = sorted(values)
    pos = 0.9 * (len(v) - 1)
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lat", type=float)
    ap.add_argument("lon", type=float)
    ap.add_argument("year", type=int)
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()
    token = get_json(SAS)["token"]
    items = scenes(a.lat, a.lon, a.year)
    print(f"{len(items)} scenes in {a.year} (Feb–Oct, tile cloud < 70%)")
    season, water, dry = [], [], []
    for it in items:
        m = int(it["properties"]["datetime"][5:7])
        if 6 <= m <= 10:
            v = scene_value(it, token, a.lat, a.lon, "ndvi")
            if v is not None:
                season.append(v)
        if 8 <= m <= 9:
            v = scene_value(it, token, a.lat, a.lon, "ndwi")
            if v is not None:
                water.append(v)
        if 2 <= m <= 4:
            v = scene_value(it, token, a.lat, a.lon, "bsi")
            if v is not None:
                dry.append(v)
    out = {"season_obs": len(season), "ndvi_p90": round(p90(season), 3) if len(season) >= 3 else None,
           "water_obs": len(water), "water_share": round(sum(1 for v in water if v > 0) / len(water), 2) if water else None,
           "dry_obs": len(dry), "bsi_dry": round(statistics.median(dry), 3) if dry else None}
    print("brute force:", out)
    if a.compare:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from app.place.history import compute_years
        from app.place.raster import circle
        row = compute_years(a.lat, a.lon, circle(a.lon, a.lat), [a.year])[a.year]
        mine = {k: getattr(row, k) for k in out}
        print("app.place:  ", mine)
        for k in out:
            x, y = out[k], mine[k]
            if isinstance(x, float) and isinstance(y, float):
                print(f"  {k}: diff {abs(x - y):.3f}")
            elif x != y:
                print(f"  {k}: {x} vs {y}")


if __name__ == "__main__":
    main()
