"""One-time download of the JRC Global Surface Water yearly history (water class per year, 30 m), clipped to
Sokoto State plus a 5 km buffer, into data/place/jrc/yearly_<year>.tif (outside git; synced to the server like
data/geo). The yearly history is published only through Google Earth Engine (JRC/GSW1_4/YearlyHistory,
1984–2021; GSW1_5 adds 2022–2024), so this needs a Google account registered for Earth Engine (free for
non-commercial use) and `uv run earthengine authenticate` once; EE_PROJECT names the Cloud project.

    uv run python scripts/jrc_yearly_ee.py [--years 1984-2024] [--out data/place/jrc]

Each year is exported in four quarters of the bounding box (Earth Engine's download limit is ~32 MB a request)
and merged. Classes: 0 no data, 1 not water, 2 seasonal water, 3 permanent water. Only the clips are kept.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

BUFFER_M = 5000
COLLECTIONS = {"JRC/GSW1_4/YearlyHistory": range(1984, 2022),
               "projects/global-surface-water/assets/GSW1_5/YearlyHistory_2022_2024": range(2022, 2025)}


def sokoto_bounds() -> tuple[float, float, float, float]:
    """The state's LGAs united and buffered, from PostGIS (the lga table)."""
    import psycopg
    from app.config import get_settings
    with psycopg.connect(get_settings().db_url()) as conn:
        row = conn.execute(
            "SELECT ST_XMin(g), ST_YMin(g), ST_XMax(g), ST_YMax(g) FROM (SELECT ST_Buffer(ST_Union(geom)::geography, "
            "%s)::geometry AS g FROM lga) x", (BUFFER_M,)).fetchone()
    return tuple(float(v) for v in row)


def download(image, region: list, path: Path) -> None:
    url = image.getDownloadURL({"region": region, "scale": 30, "crs": "EPSG:4326", "format": "GEO_TIFF"})
    with urllib.request.urlopen(url, timeout=600) as r:
        data = r.read()
    if data[:2] == b"PK":                                 # a zip with one tif inside
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next(n for n in z.namelist() if n.endswith(".tif"))
            data = z.read(name)
    path.write_bytes(data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="1984-2024")
    ap.add_argument("--out", default=str(ROOT / "data/place/jrc"))
    a = ap.parse_args()
    import ee
    import rasterio
    from rasterio.merge import merge
    ee.Initialize(project=os.environ.get("EE_PROJECT") or None)
    y0, y1 = (int(x) for x in a.years.split("-"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    minx, miny, maxx, maxy = sokoto_bounds()
    midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
    quarters = [[minx, miny, midx, midy], [midx, miny, maxx, midy], [minx, midy, midx, maxy], [midx, midy, maxx, maxy]]
    for coll, years in COLLECTIONS.items():
        for year in years:
            if not (y0 <= year <= y1) or (out / f"yearly_{year}.tif").exists():
                continue
            img = ee.ImageCollection(coll).filter(ee.Filter.eq("year", year)).first().select("waterClass")
            parts = []
            for i, q in enumerate(quarters):
                part = out / f"_part_{year}_{i}.tif"
                download(img, q, part)
                parts.append(part)
            srcs = [rasterio.open(p) for p in parts]
            mosaic, tr = merge(srcs)
            profile = srcs[0].profile | {"height": mosaic.shape[1], "width": mosaic.shape[2], "transform": tr,
                                         "compress": "deflate", "tiled": True, "blockxsize": 256, "blockysize": 256}
            with rasterio.open(out / f"yearly_{year}.tif", "w", **profile) as dst:
                dst.write(mosaic)
            for s in srcs:
                s.close()
            for p in parts:
                p.unlink()
            print("wrote", out / f"yearly_{year}.tif")


if __name__ == "__main__":
    main()
