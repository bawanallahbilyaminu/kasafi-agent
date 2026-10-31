"""Flood detection that sees through cloud (docs/place-history.md §12, step 2b): Sentinel-1 radar.

Sentinel-1 RTC (radiometrically terrain-corrected backscatter, 10 m, on the Planetary Computer, keyless through
the same data API route as Sentinel-2) images Sokoto every 6–12 days whatever the weather. Calm open water
scatters the radar beam away from the satellite, so its VV backscatter is very low; soil, crops and buildings
scatter it back. For each July–October pass since FIRST_YEAR the plot's window is read (VV and VH) and the plot
counts as open water when its median VV is under WATER_DB.

The threshold is set against two known pixels (31 Oct 2026, July–October 2024, medians over the 1 ha circle):
    JRC-certain reservoir water at Goronyo (13.512, 5.892): VV -19.4 to -16.6 dB over 6 passes (median -18.5)
    Sokoto Central Market (built-up):                         VV  -2.3 to  +0.9 dB (median  -0.5)
    Dundaye floodplain cropland (not under water):            VV -12.5 to  -5.4 dB (median  -7.3)
WATER_DB = -15 leaves 1.6 dB above the water pixel's brightest pass and 2.5 dB below the cropland's darkest, in
line with the -15 to -18 dB thresholds the flood-mapping literature uses for VV. What it misses: water under
standing crops or trees (the stems bounce the beam back, so flooded vegetation reads bright, not dark), very
rough wind-blown water, and floods between two passes. Answers say so.

Cached per ~100 m cell and year in sat_cache (layer 's1'), never by user.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date

import httpx
import numpy as np
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile

from app.place import stac
from app.place.history import DATA_API, TIMEOUT, WORKERS, bbox_of, grid_shape

log = logging.getLogger(__name__)

S1 = "sentinel-1-rtc"
WATER_DB = -15.0
FLOOD_MONTHS = (7, 10)
FIRST_YEAR = 2017
MIN_PIXELS = 0.5            # share of the plot's pixels with a valid value for a pass to count
SOURCE = "Copernicus Sentinel-1 RTC (VV backscatter), Microsoft Planetary Computer"


@dataclass
class RadarYear:
    year: int
    passes: int = 0
    water: list[str] = field(default_factory=list)     # ISO dates of passes with the plot under water
    vv_db: dict[str, float] = field(default_factory=dict)   # date -> median VV dB (show working)

    @property
    def water_passes(self) -> int:
        return len(self.water)


def to_db(power: np.ndarray) -> np.ndarray:
    p = power.astype(float)
    p[p <= 0] = np.nan
    return 10.0 * np.log10(p)


def plot_db(vv: np.ndarray, inside: np.ndarray) -> float | None:
    """The plot's median VV in dB, or None when fewer than MIN_PIXELS of its pixels have a value."""
    vals = to_db(vv)[inside]
    vals = vals[np.isfinite(vals)]
    if vals.size < max(1, MIN_PIXELS * int(inside.sum())):
        return None
    return float(np.median(vals))


def is_water(db: float | None, threshold: float = WATER_DB) -> bool:
    return db is not None and db < threshold


def passes(lon: float, lat: float, start: date, end: date) -> list[dict]:
    """Sentinel-1 RTC items over the point, July–October, one per day (two overlapping frames share a date)."""
    items = stac.search(S1, lon, lat, start.isoformat(), end.isoformat(),
                        fields=["id", "properties.datetime", "properties.sat:orbit_state",
                                "properties.sat:relative_orbit"])
    by_day: dict[str, dict] = {}
    for it in items:
        day = it["properties"]["datetime"][:10]
        if FLOOD_MONTHS[0] <= int(day[5:7]) <= FLOOD_MONTHS[1] and day not in by_day:
            by_day[day] = it
    return [by_day[d] for d in sorted(by_day)]


def read_pass(client: httpx.Client, item_id: str, geom: dict, bbox: tuple, shape: tuple[int, int]) -> float | None:
    url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{shape[0]}x{shape[1]}.tif"
    params = [("collection", S1), ("item", item_id), ("assets", "vv"), ("resampling", "nearest")]
    r = client.get(url, params=params, headers=stac._headers())
    if r.status_code != 200:
        log.info("place: radar window of %s: HTTP %s", item_id, r.status_code)
        return None
    with MemoryFile(r.content) as mf, mf.open() as src:
        vv = src.read(1)
        tr = src.transform
    inside = geometry_mask([geom], out_shape=vv.shape, transform=tr, invert=True)
    if not inside.any():
        inside[vv.shape[0] // 2, vv.shape[1] // 2] = True
    return plot_db(vv, inside)


def radar_years(lat: float, lon: float, geom: dict, years: list[int], *, workers: int = WORKERS,
                threshold: float = WATER_DB) -> dict[int, RadarYear]:
    """Per year: the July–October passes and those with the plot under water (dates), side by side."""
    bbox, shape = bbox_of(geom), grid_shape(bbox_of(geom), lat)
    todo = [it for it in passes(lon, lat, date(min(years), FLOOD_MONTHS[0], 1), date(max(years), FLOOD_MONTHS[1], 31))
            if int(it["properties"]["datetime"][:4]) in years]
    log.info("place: %d radar passes for %d years at %.3f,%.3f", len(todo), len(years), lat, lon)
    out = {y: RadarYear(y) for y in years}
    with httpx.Client(timeout=TIMEOUT) as client, ThreadPoolExecutor(max_workers=workers) as ex:
        for it, db in zip(todo, ex.map(lambda it: read_pass(client, it["id"], geom, bbox, shape), todo)):
            day = it["properties"]["datetime"][:10]
            r = out[int(day[:4])]
            if db is None:
                continue
            r.passes += 1
            r.vv_db[day] = round(db, 1)
            if is_water(db, threshold):
                r.water.append(day)
    return out


def summarize(rows: dict[int, RadarYear]) -> dict:
    """The cacheable values of a year row."""
    return {y: {"year": y, "passes": r.passes, "water": r.water, "vv_db": r.vv_db} for y, r in rows.items()}
