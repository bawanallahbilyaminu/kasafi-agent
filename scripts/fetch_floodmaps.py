"""Official satellite flood-extent maps for Sokoto (docs/place-history.md §12, step 2b): UNOSAT's country-wide
"satellite detected water extents over Nigeria" layers on HDX (CC BY-SA; VIIRS 375 m, 5-day composites), fetched,
clipped to Sokoto State's LGAs plus a 5 km buffer and kept as GeoPackages under data/place/floodmaps/ (outside
git; synced to the server like data/geo). The country files are deleted after clipping.

Usage: uv run python scripts/fetch_floodmaps.py [--keep-raw]
Each clipped file carries: source, code, period_start, period_end, hdx dataset, licence.
"""

from __future__ import annotations

import argparse
import io
import logging
import shutil
import sys
import zipfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import geopandas as gpd  # noqa: E402
from shapely import wkb  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

OUT = ROOT / "data/place/floodmaps"
UA = "kasafi-agent/0.1 (hackathon; https://github.com)"
# HDX datasets (data.humdata.org/dataset/<dataset>), checked 31 Oct 2026; all CC BY-SA, source UNOSAT
MAPS = [
    {"code": "FL20221019NGA", "period": ("2022-10-01", "2022-10-25"),
     "dataset": "satellite-detected-water-extents-between-1-and-25-october-2022-over-nigeria",
     "url": "https://unosat.org/static/unosat_filesystem/3427/FL20221019NGA_SHP.zip"},
    {"code": "FL20240902NGA_sep", "period": ("2024-09-05", "2024-09-09"),
     "dataset": "satellite-detected-water-extents-from-5-to-9-september-2024-over-nigeria",
     "url": "https://unosat.org/static/unosat_filesystem/3963/FL20240902NGA_SHP.zip"},
    {"code": "FL20240902NGA_nov", "period": ("2024-11-09", "2024-11-13"),
     "dataset": "satellite-detected-water-extents-from-9-to-13-november-2024-over-nigeria",
     "url": "https://unosat.org/static/unosat_filesystem/4021/FL20240902NGA_gdb.zip"},
]
LICENCE = "CC BY-SA 4.0 (UNOSAT via HDX)"
BUFFER_M = 5000


def sokoto_area():
    import psycopg
    from app.config import get_settings
    with psycopg.connect(get_settings().db_url()) as conn:
        rows = conn.execute("SELECT ST_AsBinary(geom) FROM lga").fetchall()
    polys = [wkb.loads(bytes(r[0])) for r in rows]
    state = gpd.GeoSeries([unary_union(polys)], crs="EPSG:4326")
    return state.to_crs("EPSG:32631").buffer(BUFFER_M).to_crs("EPSG:4326").iloc[0]


def water_layers(folder: Path) -> list[Path]:
    """The vector files in an unzipped UNOSAT archive that hold water extents (shapefile or file geodatabase)."""
    found = [p for p in folder.rglob("*.shp") if "water" in p.name.lower() or "flood" in p.name.lower()]
    found += [p for p in folder.rglob("*.gdb") if p.is_dir()]
    return found or list(folder.rglob("*.shp"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--only", default="", help="one map code (a rerun after a dropped download)")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUT.mkdir(parents=True, exist_ok=True)
    area = sokoto_area()
    for m in MAPS:
        if a.only and m["code"] != a.only:
            continue
        raw = OUT / "raw" / m["code"]
        if raw.exists():
            shutil.rmtree(raw)
        raw.mkdir(parents=True)
        logging.info("fetching %s (%s)", m["code"], m["url"])
        # unosat.org served about 17 KB/s on 31 Oct 2026: a 15 MB file takes a quarter of an hour
        with httpx.Client(timeout=httpx.Timeout(3600, connect=60), follow_redirects=True, headers={"User-Agent": UA}) as c:
            r = c.get(m["url"])
            r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            for info in z.infolist():                      # no path escapes from an archive we didn't write
                if ".." in info.filename or info.filename.startswith(("/", "\\")):
                    continue
                z.extract(info, raw)
        parts = []
        for layer in water_layers(raw):
            try:
                if layer.suffix == ".gdb":
                    for name in pyogrio_layers(layer):
                        g = gpd.read_file(layer, layer=name)
                        if g.geom_type.isin(["Polygon", "MultiPolygon"]).any():
                            parts.append(clip(g, area, name))
                else:
                    parts.append(clip(gpd.read_file(layer), area, layer.stem))
            except Exception as e:                        # noqa: BLE001 - one odd layer never loses the rest
                logging.warning("  %s: %s", layer.name, e)
        parts = [p for p in parts if p is not None and len(p)]
        if not parts:
            logging.warning("  nothing of %s falls in Sokoto", m["code"])
        else:
            g = gpd.GeoDataFrame(gpd.pd.concat(parts, ignore_index=True), crs="EPSG:4326")
            g["source"] = "UNOSAT"
            g["code"], g["period_start"], g["period_end"] = m["code"], m["period"][0], m["period"][1]
            g["dataset"], g["licence"] = m["dataset"], LICENCE
            out = OUT / f"{m['code']}_{m['period'][0]}_{m['period'][1]}.gpkg"
            g[["layer", "source", "code", "period_start", "period_end", "dataset", "licence", "geometry"]].to_file(
                out, driver="GPKG")
            logging.info("  %s: %d features, %.1f km² in Sokoto (+5 km)", out.name, len(g),
                         g.to_crs("EPSG:32631").area.sum() / 1e6)
        if not a.keep_raw:
            shutil.rmtree(raw)
    if not a.keep_raw and (OUT / "raw").exists():
        shutil.rmtree(OUT / "raw", ignore_errors=True)


def pyogrio_layers(path: Path) -> list[str]:
    import pyogrio
    return [name for name, _ in pyogrio.list_layers(path)]


def clip(g, area, layer: str):
    if g.crs is None:
        g = g.set_crs("EPSG:4326")
    g = g.to_crs("EPSG:4326")
    g = g[g.geom_type.isin(["Polygon", "MultiPolygon"])]
    g = g[g.intersects(area)]
    if not len(g):
        return None
    g = g.copy()
    g["geometry"] = g.geometry.intersection(area)
    g["layer"] = layer
    return g[["layer", "geometry"]]


if __name__ == "__main__":
    main()
