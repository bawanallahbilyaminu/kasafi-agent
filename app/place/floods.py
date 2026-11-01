"""Flood evidence for a plot from three sources, combined for the answer (docs/place-history.md §12, step 2b):

1. Radar: Sentinel-1 passes July–October with the plot reading as open water (app/place/radar.py), per year
   since 2017, cached in sat_cache (layer 's1').
2. Optical: the months Sentinel-2 saw water at the plot (app/place/history.py, NDWI; masked under cloud).
3. Official maps: UNOSAT's satellite-detected water extents over Nigeria, clipped to Sokoto
   (data/place/floodmaps/*.gpkg, scripts/fetch_floodmaps.py): whether the plot falls inside one, with its dates.

The answer never says "never flooded": "no flood water seen" with the reason (floods under crops read bright on
radar and green on optical, short floods fall between passes, optical water under cloud is masked).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.place import radar
from app.place.history import History, _fresh, _load, _save, cell_id
from app.place.radar import SOURCE as RADAR_SOURCE
from app.place.radar import Reference

log = logging.getLogger(__name__)

FLOODMAPS = Path(os.environ.get("KASAFI_PLACE_DIR", "data/place")) / "floodmaps"   # /data/place on the server
_maps_cache: dict[str, object] = {}


@dataclass
class FloodEvidence:
    radar: dict[int, radar.RadarYear] = field(default_factory=dict)
    official: list[dict] = field(default_factory=list)       # [{"source", "code", "period_start", "period_end"}]
    maps_loaded: bool = False                                  # the clipped official maps exist on this server
    radar_source: str = RADAR_SOURCE
    reference: Reference = field(default_factory=Reference)      # the plot's dry-season VV (radar.Reference)

    def radar_years_with_water(self) -> list[int]:
        return sorted(y for y, r in self.radar.items() if r.water)

    @property
    def any_flood(self) -> bool:
        return bool(self.radar_years_with_water() or self.official)


# --- radar, cached per cell and year --------------------------------------------------------------------------

def radar_history(conn, lat: float, lon: float, geom: dict, *, today: date, years: list[int] | None = None,
                  workers: int = radar.WORKERS, on_water: bool = False, key: str | None = None
                  ) -> tuple[dict[int, radar.RadarYear], radar.Reference]:
    """The per-year passes (cached per cell and year, or in memory under a plot's key) judged against the plot's
    dry-season reference (cached as layer 's1ref'; refreshed once a year): the water dates are recomputed from the
    stored per-pass values, so a changed rule needs no cache purge."""
    years = years or list(range(radar.FIRST_YEAR, today.year + 1))
    cell = key or cell_id(lat, lon)
    cached = _load(conn, cell)
    hit = cached.get(("s1ref", 0))
    if hit is not None and (today - hit[1]).days < 365:
        v = hit[0]
        ref = radar.Reference(v.get("vv_db"), int(v.get("passes") or 0), str(v.get("seasons") or ""))
    else:
        ref = radar.dry_reference(lat, lon, geom, today, workers=workers)
        if conn is not None:
            _save(conn, cell, "s1ref", 0, {"vv_db": ref.vv_db, "passes": ref.passes, "seasons": ref.seasons},
                  radar.SOURCE, ref.passes, today)
    rows: dict[int, radar.RadarYear] = {}
    missing = []
    for y in years:
        hit = cached.get(("s1", y))
        if _fresh(hit, y, today):
            v = hit[0]
            rows[y] = radar.RadarYear(y, int(v.get("passes") or 0), list(v.get("water") or []), dict(v.get("vv_db") or {}))
        else:
            missing.append(y)
    if missing:
        fresh = radar.radar_years(lat, lon, geom, missing, workers=workers, reference=ref.vv_db, on_water=on_water)
        for y, r in fresh.items():
            rows[y] = r
            if conn is not None:
                _save(conn, cell, "s1", y, {"year": y, "passes": r.passes, "water": r.water, "vv_db": r.vv_db},
                      radar.SOURCE, r.passes, today)
    radar.rejudge(rows, ref.vv_db, on_water)
    return rows, ref


# --- official flood maps ----------------------------------------------------------------------------------------

def load_maps(folder: Path = FLOODMAPS):
    """The clipped official maps (GeoPackages) as one GeoDataFrame, read once; None without the files."""
    key = str(folder)
    if key in _maps_cache:
        return _maps_cache[key]
    files = sorted(folder.glob("*.gpkg")) if folder.exists() else []
    if not files:
        _maps_cache[key] = None
        return None
    import geopandas as gpd
    import pandas as pd
    frames = [gpd.read_file(f) for f in files]
    g = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    _maps_cache[key] = g
    return g


def official_maps_at(geom: dict, folder: Path = FLOODMAPS) -> list[dict]:
    """The official maps whose flood water touches the plot, oldest first (one entry per map)."""
    g = load_maps(folder)
    if g is None or not len(g):
        return []
    from shapely.geometry import shape
    plot = shape(geom)
    hits = g[g.intersects(plot)]
    out = []
    for code, grp in hits.groupby("code", sort=False):
        first = grp.iloc[0]
        out.append({"source": str(first["source"]), "code": str(code), "period_start": str(first["period_start"]),
                    "period_end": str(first["period_end"]), "licence": str(first.get("licence", ""))})
    return sorted(out, key=lambda m: m["period_start"])


# --- all three together ------------------------------------------------------------------------------------------

def flood_evidence(conn, lat: float, lon: float, geom: dict, *, today: date, workers: int = radar.WORKERS,
                   on_water: bool = False, key: str | None = None) -> FloodEvidence:
    """`on_water`: JRC or WorldCover already call the plot a water body, so a dark dry season is water, not sand.
    `key`: the history's cache key (a cell, or a plot's in-memory key)."""
    ev = FloodEvidence()
    try:
        ev.radar, ev.reference = radar_history(conn, lat, lon, geom, today=today, workers=workers, on_water=on_water,
                                               key=key)
    except Exception as e:                                   # noqa: BLE001 - radar is one of three sources
        log.warning("place: radar failed: %s", type(e).__name__)
    try:
        ev.maps_loaded = load_maps() is not None
        ev.official = official_maps_at(geom)
    except Exception as e:                                   # noqa: BLE001
        log.warning("place: official flood maps failed: %s", type(e).__name__)
    return ev


def optical_years(h: History) -> list[int]:
    """Years in which Sentinel-2 saw water at the plot in the flood months (July–October)."""
    return sorted(y for y, r in h.years.items() if any(radar.FLOOD_MONTHS[0] <= m <= radar.FLOOD_MONTHS[1]
                                                        for m in r.water_months))


def dry_season_years(h: History) -> list[int]:
    """Years in which Sentinel-2 saw water at the plot in the dry season (February–April)."""
    return sorted(y for y, r in h.years.items() if any(2 <= m <= 4 for m in r.water_months))


# --- what kind of water a cell is -------------------------------------------------------------------------------

PERMANENT, SEASONAL, FLOOD = "permanent", "seasonal", "flood"


def classify_water(h: History, ev: FloodEvidence | None = None) -> str | None:
    """permanent: water in the dry season and the wet season in most years (or JRC/WorldCover call it water);
    seasonal: water in most wet seasons, dry in the dry season; flood: water in a wet season at a cell that is
    normally dry (fewer than half the years); None: no water seen. Only a flood is called a flood."""
    data_years = sorted(y for y, r in h.years.items() if r.season_obs or r.dry_obs or r.water_months)
    if not data_years:
        return PERMANENT if h.on_water else None
    wet = set(optical_years(h))
    if ev is not None:
        wet |= set(ev.radar_years_with_water())
    dry = set(dry_season_years(h))
    half = len(data_years) / 2
    if h.on_water or (len(dry) >= half and len(wet) >= half):
        return PERMANENT
    if len(wet) >= half:
        return SEASONAL
    if wet:
        return FLOOD
    return None


def flood_years(h: History, ev: FloodEvidence | None) -> list[int]:
    """The years with flood water at a normally dry cell (optical or radar); [] for water bodies."""
    if classify_water(h, ev) != FLOOD:
        return []
    wet = set(optical_years(h))
    if ev is not None:
        wet |= set(ev.radar_years_with_water())
    return sorted(wet)
