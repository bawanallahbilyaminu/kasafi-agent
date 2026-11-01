"""Ward, LGA and state measures, precomputed on one 200 m grid over Sokoto (docs/place-history.md §8, step 3).

Every layer is read from the Planetary Computer data API as a state-wide window on the same grid (GRID_M, under
the API's 2048-pixel cap), then summed per unit with label rasters (a ward id per cell, an LGA id per cell), and
masked to cropland (ESA WorldCover 2021, class 40, majority per cell):

- modis_peak (per year, 2001→): the unit's cropland median NDVI per 16-day MODIS 13Q1 composite (Terra and
  Aqua, pixel reliability good or marginal), then the 90th percentile over the June–October composites; n_obs =
  composites with half the unit's cropland cells good.
- jrc_recurrence_share, jrc_occurrence_mean (year 0): JRC Global Surface Water 1984–2020, averaged to 200 m.
- s1_flood_share (per year, 2017→): Sentinel-1 RTC VV averaged to 200 m over the August–October passes; a cell
  floods when its lowest pass (frame edges excluded) is under WATER_DB and DARKER_DB under the cell's dry-season
  reference (the February–April median: smooth dry sand is dark all year), and it is normally dry (JRC
  recurrence under 50%); the share of such cells among the unit's normally dry cropland cells; n_obs = passes
  covering the unit.
- unosat_share (2022, 2024): the share of cropland cells inside UNOSAT's satellite-detected water extents
  (data/place/floodmaps).
- bsi_share, bsi_median (per year, 2017→): dry-season (February–April) Sentinel-2 BSI from the two clearest
  scenes per tile and year, averaged to 200 m, clouds masked with SCL (mode); the share of cropland cells over
  BSI_BARE and the median.
- rain_season_mm (per year, 2001→): Open-Meteo archive at the LGA's centroid (each ward takes its LGA's series;
  the ERA5-Land grid is ~9 km), June–October.
- cropland_share, cropland_cells (year 0).

Results go to ward_history (migration 0021). Nothing here stores a user or a pin.
"""

from __future__ import annotations

import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date

import httpx
import numpy as np
from rasterio.features import rasterize
from rasterio.io import MemoryFile
from rasterio.transform import from_bounds
from shapely import wkb

from app.place import indices, rain, stac
from app.place.history import DATA_API, TIMEOUT
from app.place.radar import DARKER_DB, WATER_DB, S1, to_db

log = logging.getLogger(__name__)

GRID_M = 200.0
MARGIN = 0.01
MAX_PX = 2048
STATE = "NG034"
CROPLAND = 40
BSI_BARE = 0.25
GOOD_SHARE = 0.5
NORMALLY_DRY = 50.0           # JRC recurrence (%) under which a cell is normally dry
MODIS = "modis-13Q1-061"
S2 = stac.S2
SEASON_DOY = (145, 300)       # MODIS composites starting June–October
S1_MONTHS = ("08-01", "10-31")     # the Rima floods peak late September–October (2022: 1–25 October per UNOSAT)
DRY_MONTHS = ("02-01", "04-30")
WORKERS = 6
SOURCES = {
    "modis": "MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer",
    "jrc": "JRC Global Surface Water v1.3 (1984–2020), Microsoft Planetary Computer",
    "s1": "Copernicus Sentinel-1 RTC (VV), Microsoft Planetary Computer",
    "unosat": "UNOSAT satellite-detected water extents over Nigeria (HDX, CC BY-SA)",
    "bsi": "Copernicus Sentinel-2 L2A (BSI, SCL), Microsoft Planetary Computer",
    "rain": "Open-Meteo archive (ERA5-Land)",
    "cropland": "ESA WorldCover 2021 (class 40), Microsoft Planetary Computer",
}


@dataclass
class Grid:
    bbox: tuple[float, float, float, float]
    width: int
    height: int

    @property
    def transform(self):
        return from_bounds(*self.bbox, self.width, self.height)

    @property
    def shape(self) -> tuple[int, int]:
        return self.height, self.width

    def cell_m2(self, lat: float) -> float:
        dx = (self.bbox[2] - self.bbox[0]) / self.width * 111_320.0 * math.cos(math.radians(lat))
        dy = (self.bbox[3] - self.bbox[1]) / self.height * 111_320.0
        return dx * dy


@dataclass
class Units:
    """Label rasters: a ward id, an LGA id per cell (0 = none), with the ids' codes and names."""
    grid: Grid
    ward_labels: np.ndarray
    lga_labels: np.ndarray
    wards: dict[int, tuple[str, str, str]]      # id -> (wardcode, name, lga_pcode)
    lgas: dict[int, tuple[str, str]]            # id -> (pcode, name)
    centroids: dict[tuple[str, str], tuple[float, float]]   # (level, unit) -> (lat, lon)


def state_grid(conn, res_m: float = GRID_M) -> Grid:
    x0, y0, x1, y1 = conn.execute("SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM "
                                  "(SELECT ST_Extent(geom) e FROM lga) s").fetchone()
    bbox = (x0 - MARGIN, y0 - MARGIN, x1 + MARGIN, y1 + MARGIN)
    lat = (y0 + y1) / 2
    w = math.ceil((bbox[2] - bbox[0]) * 111_320.0 * math.cos(math.radians(lat)) / res_m)
    h = math.ceil((bbox[3] - bbox[1]) * 111_320.0 / res_m)
    if max(w, h) > MAX_PX:
        raise ValueError(f"grid {w}x{h} exceeds the data API's {MAX_PX} px cap: raise res_m")
    return Grid(bbox, w, h)


def load_units(conn, grid: Grid) -> Units:
    wards, lgas, cents = {}, {}, {}
    shapes_w, shapes_l = [], []
    for i, (code, name, lga, g, cy, cx) in enumerate(conn.execute(
            "SELECT wardcode, name, lga_pcode, ST_AsBinary(geom), ST_Y(ST_Centroid(geom)), ST_X(ST_Centroid(geom)) "
            "FROM ward ORDER BY wardcode").fetchall(), 1):
        wards[i] = (code, name, lga or "")
        shapes_w.append((wkb.loads(bytes(g)), i))
        cents[("ward", code)] = (cy, cx)
    for i, (code, name, g, cy, cx) in enumerate(conn.execute(
            "SELECT pcode, name, ST_AsBinary(geom), ST_Y(ST_Centroid(geom)), ST_X(ST_Centroid(geom)) FROM lga "
            "ORDER BY pcode").fetchall(), 1):
        lgas[i] = (code, name)
        shapes_l.append((wkb.loads(bytes(g)), i))
        cents[("lga", code)] = (cy, cx)
    cy, cx = conn.execute("SELECT ST_Y(c), ST_X(c) FROM (SELECT ST_Centroid(ST_Union(geom)) c FROM lga) s").fetchone()
    cents[("state", STATE)] = (cy, cx)
    wl = rasterize(shapes_w, out_shape=grid.shape, transform=grid.transform, fill=0, dtype="int32")
    ll = rasterize(shapes_l, out_shape=grid.shape, transform=grid.transform, fill=0, dtype="int32")
    return Units(grid, wl, ll, wards, lgas, cents)


# --- windows on the grid ------------------------------------------------------------------------------------------

def window(collection: str, item_id: str, assets: list[str], grid: Grid, resampling: str = "nearest",
           client: httpx.Client | None = None) -> dict[str, np.ndarray] | None:
    """A state-wide window of an item on the grid ({asset: array}); None when the API has none."""
    b = grid.bbox
    url = f"{DATA_API}/{b[0]},{b[1]},{b[2]},{b[3]}/{grid.width}x{grid.height}.tif"
    params = [("collection", collection), ("item", item_id), ("resampling", resampling)] + \
             [("assets", a) for a in assets]
    own = client is None
    client = client or httpx.Client(timeout=TIMEOUT * 5)
    try:
        for attempt in range(4):
            try:
                r = client.get(url, params=params, headers=stac._headers())
                if r.status_code < 500:            # a 504 from the data API is transient: try again
                    break
            except httpx.HTTPError as e:
                if attempt == 3:
                    log.warning("area: window of %s failed: %s", item_id, type(e).__name__)
                    return None
            time.sleep(3 * (attempt + 1))
        if r.status_code != 200:
            log.info("area: window of %s: HTTP %s", item_id, r.status_code)
            return None
        with MemoryFile(r.content) as mf, mf.open() as src:
            data = src.read()
        if data.shape[1:] != grid.shape:
            log.warning("area: window of %s came back %s, not %s", item_id, data.shape[1:], grid.shape)
            return None
        return {a: data[i] for i, a in enumerate(assets)}
    finally:
        if own:
            client.close()


def items(collection: str, grid: Grid, start: str, end: str, fields: list[str], max_cloud: float | None = None) -> list[dict]:
    return stac.search(collection, 0.0, 0.0, start, end, bbox=grid.bbox, fields=fields, max_cloud=max_cloud, limit=5000)


# --- per-unit statistics from label rasters ------------------------------------------------------------------------

def unit_median(values: np.ndarray, labels: np.ndarray, valid: np.ndarray) -> dict[int, float]:
    """The median of `values` over the valid cells of each label (0 skipped)."""
    import pandas as pd
    m = valid & (labels > 0)
    if not m.any():
        return {}
    s = pd.Series(values[m].astype(float), index=labels[m])
    return {int(k): float(v) for k, v in s.groupby(level=0).median().items()}


def unit_share(flag: np.ndarray, labels: np.ndarray, among: np.ndarray) -> dict[int, tuple[float, int]]:
    """Per label: (share of `among` cells where `flag`, the count of `among` cells)."""
    n = np.bincount(labels[among], minlength=labels.max() + 1)
    k = np.bincount(labels[among & flag], minlength=labels.max() + 1)
    return {i: (float(k[i]) / float(n[i]), int(n[i])) for i in range(1, len(n)) if n[i] > 0}


def per_unit(units: Units, fn) -> dict[tuple[str, str], object]:
    """fn(labels) -> {label: value} applied to wards, LGAs and the state (one label)."""
    out = {}
    for level, labels, names in (("ward", units.ward_labels, units.wards), ("lga", units.lga_labels, units.lgas)):
        for i, v in fn(labels).items():
            out[(level, names[i][0])] = v
    state = (units.lga_labels > 0).astype("int32")
    for _, v in fn(state).items():
        out[("state", STATE)] = v
    return out


# --- the layers -----------------------------------------------------------------------------------------------------

def cropland(grid: Grid) -> np.ndarray:
    """Cropland (WorldCover class 40) by majority per cell, from every WorldCover tile over the state."""
    tiles = items(stac.WORLDCOVER, grid, "2021-01-01", "2021-12-31", ["id"])
    merged = np.zeros(grid.shape, dtype="uint8")
    for it in tiles:
        got = window(stac.WORLDCOVER, it["id"], ["map"], grid, "mode")
        if got is not None:
            m = got["map"]
            merged[(merged == 0) & (m > 0)] = m[(merged == 0) & (m > 0)]
    log.info("area: WorldCover from %d tiles, cropland cells %d", len(tiles), int((merged == CROPLAND).sum()))
    return merged == CROPLAND


def jrc(grid: Grid) -> tuple[np.ndarray, np.ndarray] | None:
    """(occurrence, recurrence) averaged to the grid, 255/no data -> NaN."""
    its = items(stac.JRC, grid, "1984-01-01", "2030-01-01", ["id"])
    occ = np.full(grid.shape, np.nan, dtype="float32")
    rec = np.full(grid.shape, np.nan, dtype="float32")
    for it in its:
        got = window(stac.JRC, it["id"], ["occurrence", "recurrence"], grid, "average")
        if got is None:
            continue
        for src, dst in ((got["occurrence"], occ), (got["recurrence"], rec)):
            v = src.astype("float32")
            ok = (v >= 0) & (v <= 100)
            dst[ok & np.isnan(dst)] = v[ok & np.isnan(dst)]
    return (occ, rec) if np.isfinite(occ).any() else None


def modis_items(grid: Grid, year: int) -> list[dict]:
    its = items(MODIS, grid, f"{year}-05-20", f"{year}-10-31", ["id", "properties.datetime", "properties.platform"])
    out = []
    for it in its:
        doy = int(it["id"].split(".")[1][5:8]) if ".A" in it["id"] else 0
        if SEASON_DOY[0] <= doy <= SEASON_DOY[1] and "h18v07" in it["id"]:
            out.append(it)
    return out


def modis_year(grid: Grid, units: Units, crop: np.ndarray, year: int, workers: int = WORKERS
               ) -> dict[tuple[str, str], tuple[float | None, int]]:
    """Per unit: (90th-percentile of the composites' cropland median NDVI, composites with half the cells good)."""
    its = modis_items(grid, year)
    medians: dict[tuple[str, str], list[float]] = {}
    counts: dict[tuple[str, str], int] = {}
    crop_n = per_unit(units, lambda labels: {i: n for i, (_, n) in unit_share(crop, labels, crop).items()})
    with httpx.Client(timeout=TIMEOUT * 5) as client, ThreadPoolExecutor(max_workers=workers) as ex:
        for got in ex.map(lambda it: window(MODIS, it["id"], ["250m_16_days_NDVI", "250m_16_days_pixel_reliability"],
                                            grid, "nearest", client), its):
            if got is None:
                continue
            ndvi = got["250m_16_days_NDVI"].astype("float32") / 10000.0
            good = (got["250m_16_days_pixel_reliability"] <= 1) & (got["250m_16_days_NDVI"] > -3000) & crop
            med = per_unit(units, lambda labels: unit_median(ndvi, labels, good))
            share = per_unit(units, lambda labels: unit_share(good, labels, crop))
            for key, v in med.items():
                if share.get(key, (0, 0))[0] >= GOOD_SHARE:
                    medians.setdefault(key, []).append(v)
                    counts[key] = counts.get(key, 0) + 1
    out = {}
    for key in crop_n:
        vals = medians.get(key, [])
        out[key] = (round(float(np.percentile(vals, 90)), 4) if len(vals) >= 3 else None, counts.get(key, 0))
    log.info("area: MODIS %d: %d composites, %d units with a peak", year, len(its),
             sum(1 for v in out.values() if v[0] is not None))
    return out


def swath_edge(has: np.ndarray) -> np.ndarray:
    """Cells with a value next to a cell without one: a frame's edge, where 'average' resampling blends nodata
    into dark values (8% of the 2022 'flooded' cells in the Nov 1 2026 probe sat on one)."""
    gap = ~has
    edge = np.zeros_like(has)
    edge[1:, :] |= gap[:-1, :]
    edge[:-1, :] |= gap[1:, :]
    edge[:, 1:] |= gap[:, :-1]
    edge[:, :-1] |= gap[:, 1:]
    return has & edge


def s1_reference(grid: Grid, year: int, workers: int = WORKERS) -> np.ndarray | None:
    """Each cell's dry-season VV (dB): the median over the February–April frames of the year. Smooth dry sand
    (Gudu's dunes) reads under WATER_DB all year, so a wet-season pass counts as a flood only when it is DARKER_DB
    under this."""
    its = items(S1, grid, f"{year}-{DRY_MONTHS[0]}", f"{year}-{DRY_MONTHS[1]}", ["id", "properties.datetime"])
    stack = []
    with httpx.Client(timeout=TIMEOUT * 5) as client, ThreadPoolExecutor(max_workers=workers) as ex:
        for got in ex.map(lambda it: window(S1, it["id"], ["vv"], grid, "average", client), its):
            if got is not None:
                db = to_db(got["vv"]).astype("float32")
                db[swath_edge(np.isfinite(db))] = np.nan
                stack.append(db)
    if not stack:
        return None
    ref = np.nanmedian(np.stack(stack), axis=0).astype("float32")
    log.info("area: Sentinel-1 dry-season reference %d: %d frames; cells under %.0f dB: %d", year, len(stack), WATER_DB,
             int((ref < WATER_DB).sum()))
    return ref


def s1_year(grid: Grid, units: Units, crop: np.ndarray, dry: np.ndarray, year: int, workers: int = WORKERS,
            reference: np.ndarray | None = None) -> dict[tuple[str, str], tuple[float | None, int]]:
    """Per unit: (share of normally dry cropland cells under water on any August–October pass, passes covering
    the unit). A cell floods when its lowest pass is under WATER_DB, at least DARKER_DB under its dry-season
    reference (when one is given), and not on a frame's edge on that pass."""
    its = items(S1, grid, f"{year}-{S1_MONTHS[0]}", f"{year}-{S1_MONTHS[1]}", ["id", "properties.datetime"])
    lowest = np.full(grid.shape, np.inf, dtype="float32")
    cover: dict[tuple[str, str], int] = {}
    among = crop & dry
    # frames of one date are one pass over the state: their coverage is joined before a unit counts the pass
    has_by_date: dict[str, np.ndarray] = {}
    with httpx.Client(timeout=TIMEOUT * 5) as client, ThreadPoolExecutor(max_workers=workers) as ex:
        for it, got in zip(its, ex.map(lambda it: window(S1, it["id"], ["vv"], grid, "average", client), its)):
            if got is None:
                continue
            db = to_db(got["vv"])
            has = np.isfinite(db)
            good = has & ~swath_edge(has)
            lowest = np.where(good & (db < lowest), db, lowest)
            day = it["properties"]["datetime"][:10]
            has_by_date[day] = has_by_date[day] | has if day in has_by_date else has
    for has in has_by_date.values():
        seen = per_unit(units, lambda labels: unit_share(has, labels, among))
        for key, (share, _) in seen.items():
            if share >= GOOD_SHARE:
                cover[key] = cover.get(key, 0) + 1
    flooded = flood_cells(lowest, reference)
    shares = per_unit(units, lambda labels: unit_share(flooded, labels, among))
    out = {key: (round(share, 4) if cover.get(key, 0) > 0 else None, cover.get(key, 0)) for key, (share, _) in shares.items()}
    log.info("area: Sentinel-1 %d: %d frames, flooded cells %d", year, len(its), int(flooded[among].sum()))
    return out


def flood_cells(lowest: np.ndarray, reference: np.ndarray | None) -> np.ndarray:
    """Under WATER_DB on the lowest pass and, where the dry-season reference is known, DARKER_DB under it."""
    flooded = np.isfinite(lowest) & (lowest < WATER_DB)
    if reference is not None:
        known = np.isfinite(reference)
        flooded &= ~known | ((reference - lowest) >= DARKER_DB)
    return flooded


def unosat_shares(grid: Grid, units: Units, crop: np.ndarray) -> dict[int, dict[tuple[str, str], tuple[float, int]]]:
    """Per map year: per unit the share of cropland cells inside the maps' water extents (n_obs = maps that year)."""
    from app.place.floods import load_maps
    g = load_maps()
    if g is None:
        return {}
    out = {}
    for year, grp in g.groupby(g["period_start"].str[:4]):
        mask = rasterize([(geom, 1) for geom in grp.geometry if geom is not None and not geom.is_empty],
                         out_shape=grid.shape, transform=grid.transform, fill=0, dtype="uint8").astype(bool)
        shares = per_unit(units, lambda labels: unit_share(mask, labels, crop))
        n_maps = grp["code"].nunique()
        out[int(year)] = {key: (round(share, 4), n_maps) for key, (share, _) in shares.items()}
    return out


def dry_scenes(grid: Grid, year: int, per_tile: int = 2) -> list[dict]:
    """The clearest dry-season Sentinel-2 scenes per MGRS tile."""
    its = items(S2, grid, f"{year}-{DRY_MONTHS[0]}", f"{year}-{DRY_MONTHS[1]}",
                ["id", "properties.datetime", "properties.eo:cloud_cover", "properties.s2:mgrs_tile",
                 "properties.s2:processing_baseline"], max_cloud=20.0)
    by_tile: dict[str, list[dict]] = {}
    for it in its:
        by_tile.setdefault(str(it["properties"].get("s2:mgrs_tile")), []).append(it)
    out = []
    for tile, lst in by_tile.items():
        out += sorted(lst, key=lambda it: float(it["properties"].get("eo:cloud_cover") or 0.0))[:per_tile]
    return out


def bsi_year(grid: Grid, units: Units, crop: np.ndarray, year: int, workers: int = WORKERS
             ) -> dict[tuple[str, str], tuple[float | None, float | None, int]]:
    """Per unit: (share of cropland cells with dry-season BSI over BSI_BARE, the median BSI, scenes used)."""
    scenes = dry_scenes(grid, year)
    acc = np.zeros(grid.shape, dtype="float32")
    n = np.zeros(grid.shape, dtype="int16")

    def read(it):
        bands = window(S2, it["id"], ["B02", "B04", "B08", "B11"], grid, "average")
        scl = window(S2, it["id"], ["SCL"], grid, "mode")
        return it, bands, scl

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for it, bands, scl in ex.map(read, scenes):
            if bands is None or scl is None:
                continue
            base = str(it["properties"].get("s2:processing_baseline") or "")
            refl = {k: indices.reflectance(v, base) for k, v in bands.items()}
            bsi = indices.bsi(refl["B02"], refl["B04"], refl["B08"], refl["B11"])
            ok = indices.clear_mask(scl["SCL"]) & np.isfinite(bsi)
            acc[ok] += bsi[ok]
            n[ok] += 1
    mean = np.where(n > 0, acc / np.maximum(n, 1), np.nan)
    has = n > 0
    bare = has & (mean > BSI_BARE)
    shares = per_unit(units, lambda labels: unit_share(bare, labels, crop & has))
    meds = per_unit(units, lambda labels: unit_median(mean, labels, crop & has))
    cover = per_unit(units, lambda labels: unit_share(has, labels, crop))
    out = {}
    for key, (share, _) in shares.items():
        covered = cover.get(key, (0.0, 0))[0] >= GOOD_SHARE
        out[key] = (round(share, 4) if covered else None, round(meds[key], 4) if covered and key in meds else None,
                    len(scenes))
    log.info("area: Sentinel-2 BSI %d: %d scenes", year, len(scenes))
    return out


def rain_years(units: Units, first_year: int, today: date, workers: int = 1) -> dict[tuple[str, str], dict[int, float]]:
    """June–October rain per year at the LGA centroids and the state's; each ward takes its LGA's series (the
    ERA5-Land grid is ~9 km, coarser than most wards). One call at a time with a pause and a long backoff: the
    Open-Meteo archive's hourly quota weighs a 26-year request heavily (31 Oct 2026: 241 of 268 ward calls came
    back 429 at four threads, and a sequential rerun was still limited)."""
    keys = [k for k in units.centroids if k[0] in ("lga", "state")]

    from datetime import timedelta
    end = today - timedelta(days=3)          # the archive runs a few days behind: a later end date is a 400

    def one(key):
        lat, lon = units.centroids[key]
        for attempt in range(6):
            try:
                daily = rain.daily_rain(lat, lon, date(first_year, 1, 1), end)
                time.sleep(0.6)
                return key, {y: v["season_mm"] for y, v in rain.by_year(daily).items()}
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    time.sleep(60 * (attempt + 1))
                    continue
                log.warning("area: rain for %s failed: HTTP %s", key, e.response.status_code)
                return key, {}
            except (httpx.HTTPError, OSError, KeyError) as e:
                log.warning("area: rain for %s failed: %s", key, type(e).__name__)
                return key, {}
        log.warning("area: rain for %s failed: rate-limited six times", key)
        return key, {}

    out = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for key, vals in ex.map(one, keys):
            out[key] = vals
    for code, _, lga in units.wards.values():
        if ("lga", lga) in out:
            out[("ward", code)] = out[("lga", lga)]
    return out


# --- storage ------------------------------------------------------------------------------------------------------

def save(conn, rows: list[tuple[str, str, str, int, float | None, int | None, str]], today: date) -> None:
    """rows: (unit, level, measure, year, value, n_obs, source)."""
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO ward_history (unit, level, measure, year, value, n_obs, source, computed_at) VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (unit, level, measure, year) DO UPDATE SET value = "
            "EXCLUDED.value, n_obs = EXCLUDED.n_obs, source = EXCLUDED.source, computed_at = EXCLUDED.computed_at",
            [r + (today,) for r in rows])
    conn.commit()


def have(conn, measure: str, year: int | None = None) -> bool:
    q = "SELECT 1 FROM ward_history WHERE measure = %s" + (" AND year = %s" if year is not None else "") + " LIMIT 1"
    return conn.execute(q, (measure, year) if year is not None else (measure,)).fetchone() is not None
