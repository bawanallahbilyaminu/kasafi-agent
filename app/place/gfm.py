"""Copernicus Global Flood Monitoring (GFM) on the 200 m state grid: the primary observed-flood source for the
ward, LGA, state and pin flood answers (docs/place-history.md §16). Our own radar (s1_flood_share) is the check.

GFM's ensemble flood extent (three algorithms on every Sentinel-1 pass, 20 m, 2015→) is public: a STAC at
stac.eodc.eu (collection 'GFM') and cloud-optimised GeoTIFFs on data.eodc.eu, read with range requests from their
overviews, so no account is needed. GFM's own exclusion mask marks where radar can't judge water (built-up areas,
radar shadow, dry sand that already looks like water): floods there are never counted, and every answer says how
much of the area that is. Reference (normal) water is not flood in GFM.

Per season (July–November), per date: the tiles of one pass are joined (max), the flooded fraction of each cell
summed per unit. Stored per unit and year in ward_history:
- gfm_union_ha: land flooded on at least one pass (n_obs = passes covering half the unit)
- gfm_max_ha, gfm_max_doy: the largest single pass and its day of year
- gfm_crop_ha / gfm_plain_ha: the union on cropland outside the river floodplain / inside the floodplain (JRC: water
  seen in some years 1984–2021), so answers say which is which
- gfm_union_share: gfm_union_ha over the unit's land (the area ranking and map)
- gfm_excluded_share: the unit's land inside GFM's exclusion mask (mean over passes)
- unosat_ha: land inside UNOSAT's event maps (all land, to compare with gfm_union_ha)
and per unit once (year 0): land_ha, jrc_plain_ha (water in some years), jrc_often_ha (in half the years or more).
The season's cell rasters go to data/place/gfm/<year>.tif (flood fraction at any pass, passes, excluded fraction)
for pin answers. Attribution: "Contains modified Copernicus Emergency Management Service information [years]".
Information only, never an official warning.
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import httpx
import numpy as np

log = logging.getLogger(__name__)

STAC = "https://stac.eodc.eu/api/v1/search"
COLLECTION = "GFM"
FIRST_YEAR = 2015
MONTHS = ("07-01", "11-30")            # the Rima and Sokoto rivers flood August–October; UNOSAT mapped November 2024
SEEN = 0.5                              # a pass counts for a unit when it covers half the unit's cells
FLOODPLAIN_OCC = 1.0                    # JRC occurrence (%) at or over which a cell is river floodplain
OFTEN_REC = 50.0                        # JRC recurrence (%): under water in half the years or more
GFM_DIR = Path(os.environ.get("KASAFI_PLACE_DIR", "data/place")) / "gfm"
SOURCE = ("Copernicus Global Flood Monitoring (GFM, ensemble flood extent, Sentinel-1, 20 m read at 200 m); "
          "contains modified Copernicus Emergency Management Service information")
WORKERS = 6


def attribution(years: list[int] | tuple[int, ...]) -> str:
    ys = sorted(set(int(y) for y in years if y))
    span = f"{ys[0]}–{ys[-1]}" if len(ys) > 1 else str(ys[0]) if ys else str(date.today().year)
    return f"Contains modified Copernicus Emergency Management Service information [{span}]"


# --- the catalogue --------------------------------------------------------------------------------------------------

def search(bbox: tuple[float, float, float, float], start: str, end: str) -> list[dict]:
    """Every GFM item over the box between the dates (pages followed)."""
    body = {"collections": [COLLECTION], "bbox": list(bbox), "limit": 1000,
            "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z"}
    out: list[dict] = []
    with httpx.Client(timeout=120) as client:
        r = client.post(STAC, json=body)
        while True:
            r.raise_for_status()
            page = r.json()
            out += page.get("features", [])
            nxt = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
            if not nxt:
                break
            r = client.post(nxt["href"], json=nxt.get("body") or body) if nxt.get("method") == "POST" else client.get(nxt["href"])
    return out


# --- one tile onto the grid ---------------------------------------------------------------------------------------

def read_on_grid(href: str, grid) -> np.ndarray | None:
    """An asset's 0/1 band as a fraction per grid cell (NaN where the tile has no data), read from the COG's
    overviews over the grid's box only and averaged onto the grid."""
    import rasterio
    from affine import Affine
    from rasterio.warp import Resampling, reproject, transform_bounds
    from rasterio.windows import from_bounds

    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MAX_RETRY="3",
                      GDAL_HTTP_RETRY_DELAY="2"):
        with rasterio.open(href) as src:
            b = transform_bounds("EPSG:4326", src.crs, *grid.bbox)
            win = from_bounds(*b, transform=src.transform).intersection(
                rasterio.windows.Window(0, 0, src.width, src.height)).round_offsets().round_lengths()
            if win.width <= 0 or win.height <= 0:
                return None
            f = max(1, int(round(200.0 / abs(src.res[0])) // 2))      # read at ~2 source pixels per grid cell
            shape = (max(1, int(win.height // f)), max(1, int(win.width // f)))
            arr = src.read(1, window=win, out_shape=shape, resampling=Resampling.nearest)
            tr = src.window_transform(win) * Affine.scale(win.width / shape[1], win.height / shape[0])
            crs = src.crs
    vals = np.where(arr == 255, np.nan, (arr == 1).astype("float32")).astype("float32")
    out = np.full(grid.shape, np.nan, dtype="float32")
    reproject(vals, out, src_transform=tr, src_crs=crs, src_nodata=np.nan, dst_transform=grid.transform,
              dst_crs="EPSG:4326", dst_nodata=np.nan, resampling=Resampling.average)
    return out


# --- a season ---------------------------------------------------------------------------------------------------------

def season(grid, units, crop: np.ndarray, plain: np.ndarray, year: int, workers: int = WORKERS,
           write_dir: Path | None = GFM_DIR) -> list[tuple]:
    """ward_history rows for one season (see the module docstring); writes the season's cell raster."""
    from app.place.area import per_unit
    feats = search(grid.bbox, f"{year}-{MONTHS[0]}", f"{year}-{MONTHS[1]}")
    by_day: dict[str, list[dict]] = defaultdict(list)
    for f in feats:
        if "ensemble_flood_extent" in f.get("assets", {}):
            by_day[f["properties"]["datetime"][:10]].append(f)
    lat = (grid.bbox[1] + grid.bbox[3]) / 2
    cell_ha = grid.cell_m2(lat) / 10_000
    union = np.full(grid.shape, np.nan, dtype="float32")
    passes = np.zeros(grid.shape, dtype="float32")
    excl_sum = np.zeros(grid.shape, dtype="float32")
    excl_n = np.zeros(grid.shape, dtype="float32")
    land = {lvl: labels > 0 for lvl, labels in (("ward", units.ward_labels), ("lga", units.lga_labels))}
    best: dict[tuple[str, str], tuple[float, int]] = {}        # unit -> (largest pass ha, day of year)
    covered: dict[tuple[str, str], int] = defaultdict(int)

    def read(f):
        a = f["assets"]
        for attempt in range(3):           # a COG block read can fail transiently: twice more, then the tile is left out
            try:
                fl = read_on_grid(a["ensemble_flood_extent"]["href"], grid)
                ex = read_on_grid(a["exclusion_mask"]["href"], grid) if "exclusion_mask" in a else None
                return fl, ex
            except Exception as e:         # noqa: BLE001 - rasterio raises several kinds
                if attempt == 2:
                    log.warning("gfm: tile %s left out: %s", f.get("id", "?")[:70], type(e).__name__)
                    return None, None
                time.sleep(3 * (attempt + 1))
        return None, None

    def sums(values: np.ndarray, valid: np.ndarray):
        def fn(labels):
            m = valid & (labels > 0)
            k = np.bincount(labels[m], weights=values[m].astype("float64"), minlength=labels.max() + 1)
            return {i: float(k[i]) for i in range(1, len(k))}
        return per_unit(units, fn)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for day in sorted(by_day):
            fl_day = np.full(grid.shape, np.nan, dtype="float32")
            ex_day = np.full(grid.shape, np.nan, dtype="float32")
            for fl, exm in ex.map(read, by_day[day]):
                if fl is not None:
                    fl_day = np.fmax(fl_day, fl)
                if exm is not None:
                    ex_day = np.fmax(ex_day, exm)
            seen = np.isfinite(fl_day)
            if not seen.any():
                continue
            union = np.fmax(union, fl_day)
            passes += seen
            ok = np.isfinite(ex_day)
            excl_sum[ok] += ex_day[ok]
            excl_n += ok
            doy = date.fromisoformat(day).timetuple().tm_yday
            cover = sums(np.ones(grid.shape, "float32"), seen)
            total = sums(np.ones(grid.shape, "float32"), np.ones(grid.shape, bool))
            flood = sums(np.nan_to_num(fl_day), seen)
            for key, n in cover.items():
                if total.get(key) and n / total[key] >= SEEN:
                    covered[key] += 1
                    ha = flood.get(key, 0.0) * cell_ha
                    if ha > best.get(key, (0.0, 0))[0]:
                        best[key] = (ha, doy)
            log.info("gfm %s: %d tiles, flooded %.0f ha in the state", day, len(by_day[day]),
                     float(np.nansum(fl_day[land["lga"]])) * cell_ha)
    excluded = np.where(excl_n > 0, excl_sum / np.maximum(excl_n, 1), np.nan).astype("float32")
    u = np.nan_to_num(union)
    seen_any = np.isfinite(union)
    all_ha = sums(u, seen_any)
    crop_ha = sums(u, seen_any & crop & ~plain)
    plain_ha = sums(u, seen_any & plain)
    land_n = sums(np.ones(grid.shape, "float32"), np.ones(grid.shape, bool))
    excl_ha = sums(np.nan_to_num(excluded), np.isfinite(excluded))
    rows = []
    for key, n_land in land_n.items():
        if not n_land:
            continue
        lvl, code = key
        n = covered.get(key, 0)
        if n == 0:
            rows.append((code, lvl, "gfm_union_ha", year, None, 0, SOURCE))
            continue
        land_ha = n_land * cell_ha
        ha = all_ha.get(key, 0.0) * cell_ha
        rows += [(code, lvl, "gfm_union_ha", year, round(ha, 1), n, SOURCE),
                 (code, lvl, "gfm_union_share", year, round(ha / land_ha, 5), n, SOURCE),
                 (code, lvl, "gfm_max_ha", year, round(best.get(key, (0.0, 0))[0], 1), n, SOURCE),
                 (code, lvl, "gfm_max_doy", year, float(best[key][1]) if key in best else None, n, SOURCE),
                 (code, lvl, "gfm_crop_ha", year, round(crop_ha.get(key, 0.0) * cell_ha, 1), n, SOURCE),
                 (code, lvl, "gfm_plain_ha", year, round(plain_ha.get(key, 0.0) * cell_ha, 1), n, SOURCE),
                 (code, lvl, "gfm_excluded_share", year, round(excl_ha.get(key, 0.0) / n_land, 4), n, SOURCE)]
    if write_dir is not None:
        write_season(grid, year, union, passes, excluded, write_dir)
    log.info("gfm %d: %d items on %d dates; %d rows", year, len(feats), len(by_day), len(rows))
    return rows


def write_season(grid, year: int, union: np.ndarray, passes: np.ndarray, excluded: np.ndarray, out: Path) -> Path:
    import rasterio
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{year}.tif"
    with rasterio.open(path, "w", driver="GTiff", width=grid.width, height=grid.height, count=3, dtype="float32",
                       crs="EPSG:4326", transform=grid.transform, nodata=np.nan, compress="deflate", predictor=3) as dst:
        dst.write(np.stack([union, passes, excluded]).astype("float32"))
        dst.set_band_description(1, "flooded fraction on any pass")
        dst.set_band_description(2, "passes")
        dst.set_band_description(3, "excluded fraction (mean over passes)")
    return path


def static_rows(grid, units, occ: np.ndarray | None, rec: np.ndarray | None, unosat: dict[int, np.ndarray]) -> list[tuple]:
    """Per unit: land_ha, jrc_plain_ha, jrc_often_ha (year 0) and unosat_ha per map year (all land)."""
    from app.place.area import SOURCES, per_unit
    lat = (grid.bbox[1] + grid.bbox[3]) / 2
    cell_ha = grid.cell_m2(lat) / 10_000

    def count(flag: np.ndarray):
        def fn(labels):
            k = np.bincount(labels[flag & (labels > 0)], minlength=labels.max() + 1)
            return {i: int(k[i]) for i in range(1, len(k))}
        return per_unit(units, fn)

    rows = []
    every = np.ones(grid.shape, bool)
    for (lvl, code), n in count(every).items():
        rows.append((code, lvl, "land_ha", 0, round(n * cell_ha, 1), None, "GRID3 wards, OCHA COD-AB LGAs"))
    if occ is not None:
        for (lvl, code), n in count(floodplain(occ)).items():
            rows.append((code, lvl, "jrc_plain_ha", 0, round(n * cell_ha, 1), None, SOURCES["jrc"]))
    if rec is not None:
        for (lvl, code), n in count(np.isfinite(rec) & (rec >= OFTEN_REC)).items():
            rows.append((code, lvl, "jrc_often_ha", 0, round(n * cell_ha, 1), None, SOURCES["jrc"]))
    for year, mask in unosat.items():
        for (lvl, code), n in count(mask).items():
            rows.append((code, lvl, "unosat_ha", year, round(n * cell_ha, 1), None, SOURCES["unosat"]))
    return rows


def floodplain(occ: np.ndarray) -> np.ndarray:
    """Cells the river has covered in some years (JRC occurrence at or over FLOODPLAIN_OCC)."""
    return np.isfinite(occ) & (occ >= FLOODPLAIN_OCC)


def unosat_masks(grid) -> dict[int, np.ndarray]:
    from rasterio.features import rasterize
    from app.place.floods import load_maps
    g = load_maps()
    if g is None:
        return {}
    out = {}
    for year, grp in g.groupby(g["period_start"].str[:4]):
        out[int(year)] = rasterize([(geom, 1) for geom in grp.geometry if geom is not None and not geom.is_empty],
                                   out_shape=grid.shape, transform=grid.transform, fill=0, dtype="uint8").astype(bool)
    return out


# --- a pin ------------------------------------------------------------------------------------------------------------

def at_pin(lat: float, lon: float, radius_cells: int = 1, folder: Path | None = None) -> dict[int, dict]:
    """Per season on file: {'flood_ha', 'passes', 'excluded'} in the (2r+1)² cells around the pin (600 m square
    for r=1): flooded area at any pass, the fewest passes over those cells, the mean excluded fraction."""
    import rasterio
    folder = folder or GFM_DIR
    out = {}
    if not folder.exists():
        return out
    for path in sorted(folder.glob("*.tif")):
        try:
            year = int(path.stem)
        except ValueError:
            continue
        with rasterio.open(path) as src:
            row, col = src.index(lon, lat)
            if not (0 <= row < src.height and 0 <= col < src.width):
                continue
            r0, c0 = max(0, row - radius_cells), max(0, col - radius_cells)
            win = rasterio.windows.Window(c0, r0, 2 * radius_cells + 1, 2 * radius_cells + 1)
            a = src.read(window=win)
            cell_ha = abs(src.res[0] * src.res[1]) * (111_320.0 ** 2) * np.cos(np.radians(lat)) / 10_000
        fl, ps, ex = a[0], a[1], a[2]
        if not np.isfinite(fl).any():
            continue
        out[year] = {"flood_ha": round(float(np.nansum(fl)) * cell_ha, 1), "passes": int(np.nanmin(ps)),
                     "excluded": round(float(np.nanmean(ex)) if np.isfinite(ex).any() else 0.0, 3),
                     "area_ha": round(fl.size * cell_ha, 1)}
    return out
