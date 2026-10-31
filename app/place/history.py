"""Point history: what Sentinel-2 shows about a pin (or a small plot) year by year, with the season's rain,
the JRC water history and the land cover, cached per ~100 m cell (docs/place-history.md §3, §7).

Per scene (Feb–Oct, less than MAX_CLOUD % cloud over the tile) the plot's window is fetched in one request from
the Planetary Computer data API as a small GeoTIFF holding the bands needed that month, on a 10 m grid in WGS84:
only the window is read, never a scene. Clouds, shadows and no-data are masked with the scene classification
(SCL, 20 m); a scene counts when at least half the plot's pixels are clear, and its value is the median over
those. Per year: the rainy season's (June–October) 90th-percentile NDVI with the clear-observation count, the
August–September share of clear observations under water (NDWI > 0), the dry season's (February–April) median
BSI; a year is usable with MIN_OBS+ clear season observations. Rain per season from Open-Meteo.

The cache (sat_cache) is keyed by the cell, the layer and the year: never by a user. Past years are final;
the current year is recomputed after STALE_DAYS.
"""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

import httpx
import numpy as np
from rasterio.errors import NotGeoreferencedWarning
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile

import warnings

warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)     # geometry_mask's scratch dataset

from app.place import fit as fitting
from app.place import indices, rain, stac
from app.place.raster import circle

log = logging.getLogger(__name__)

DATA_API = "https://planetarycomputer.microsoft.com/api/data/v1/item/bbox"
SEASON, WATER_MONTHS, DRY = (6, 10), (8, 9), (2, 4)
MIN_OBS = 8                  # clear season observations before a year enters the fit, the flags and the trends
MIN_P90 = 3                  # clear season observations before a peak-greenness figure is shown at all (hatched)
MAX_CLOUD = 70.0             # tile-level cloud cover above which a scene isn't even looked at
FIRST_YEAR, GOOD_FROM = 2015, 2017     # 2015–2016 (one satellite) count only where a year passes the threshold
PIXEL_M = 10.0
STALE_DAYS = 7
WORKERS = 12
TIMEOUT = 60.0
JRC_DIR = Path("data/place/jrc")        # yearly water classes clipped to Sokoto, if ever exported (none yet: README roadmap)
WORLDCOVER = {10: "trees", 20: "shrubland", 30: "grassland", 40: "cropland", 50: "built-up", 60: "bare or sparse",
              70: "snow", 80: "open water", 90: "wetland", 95: "mangroves", 100: "moss and lichen"}
NOT_VEGETATED = {"built-up": "built-up area", "bare or sparse": "bare ground", "open water": "open water"}
NDVI_VEGETATED = 0.2         # a place whose peak greenness sits under this in most years gets no greenness claims
WATER_OCCURRENCE = 50.0      # JRC occurrence (% of observed months) at which a pixel counts as a water body
WATER_SEARCH_M = 2000.0      # how far from the pin the nearest water body is looked for
RESOLUTION = "Sentinel-2: NDVI and NDWI at 10 m, BSI and the cloud mask at 20 m; JRC water at 30 m; rain from a ~9 km grid"


@dataclass
class Scene:
    id: str
    day: date
    cloud: float
    baseline: str


@dataclass
class Observation:
    day: date
    ndvi: float | None = None
    ndwi: float | None = None
    bsi: float | None = None
    clear: float = 0.0


@dataclass
class YearRow:
    year: int
    season_obs: int = 0                 # clear observations, June–October
    ndvi_p90: float | None = None
    water_obs: int = 0                  # clear observations, August–September
    water_share: float | None = None    # share of them with the plot under water
    water_months: list[int] = field(default_factory=list)   # months (Feb–Oct) whose clear observations were mostly water
    dry_obs: int = 0
    bsi_dry: float | None = None        # February–April median
    rain_season_mm: float | None = None
    rain_year_mm: float | None = None
    rain_days: int = 0                  # season days with data (an incomplete season shows)

    @property
    def usable(self) -> bool:
        """Enough clear images for the year to enter the fit, the flags and the trends; otherwise the year is
        shown hatched as 'too few clear images' (its figure, if any, is from MIN_P90+ observations)."""
        return self.season_obs >= MIN_OBS and self.ndvi_p90 is not None


@dataclass
class History:
    cell: str
    lat: float
    lon: float
    years: dict[int, YearRow]
    fit: fitting.Fit | None = None
    trends: dict[str, tuple[str, float]] = field(default_factory=dict)
    jrc: dict = field(default_factory=dict)
    landcover: str | None = None                 # ESA WorldCover 2021 majority class: a 2021 snapshot, said as such
    kind: str | None = None                      # 'built-up area' | 'bare ground' | 'open water' | 'little vegetation' | None (vegetated)
    nearest_water: dict | None = None            # the nearest JRC water body when asked for and the place isn't water
    floods: object | None = None                 # app.place.floods.FloodEvidence (radar passes, official maps)
    resolution: str = RESOLUTION
    timing: dict[str, float] = field(default_factory=dict)
    from_cache: bool = False

    def usable_years(self) -> list[int]:
        return sorted(y for y, r in self.years.items() if r.usable)

    @property
    def vegetated(self) -> bool:
        return self.kind is None

    @property
    def on_water(self) -> bool:
        """The plot itself is a water body: JRC saw water in half the observed months, or WorldCover says water."""
        occ = self.jrc.get("occurrence")
        return (occ is not None and occ >= WATER_OCCURRENCE) or self.landcover == "open water"

    @property
    def water_seen(self) -> bool:
        """Any sign of water at the plot: a JRC occurrence, or a month whose clear images were mostly water."""
        return self.on_water or bool(self.jrc.get("occurrence")) or any(r.water_months for r in self.years.values())


def place_kind(landcover: str | None, years: dict[int, YearRow]) -> str | None:
    """What a place is when it isn't vegetation, so no greenness trend or rain-adjusted claim is made about it:
    the WorldCover class when that is built-up, bare or water; else 'little vegetation' when the peak greenness
    sits under NDVI_VEGETATED in most years with a figure; None for a vegetated place."""
    if landcover in NOT_VEGETATED:
        return NOT_VEGETATED[landcover]
    peaks = [r.ndvi_p90 for r in years.values() if r.ndvi_p90 is not None]
    if peaks and float(np.median(peaks)) < NDVI_VEGETATED:
        return "little vegetation"
    return None


def cell_id(lat: float, lon: float) -> str:
    """The cache key: the coordinate rounded to 0.001° (about 100 m), never the pin itself."""
    return f"{lat:.3f},{lon:.3f}"


def bbox_of(geom: dict) -> tuple[float, float, float, float]:
    xs = [x for ring in geom["coordinates"] for x, _ in ring]
    ys = [y for ring in geom["coordinates"] for _, y in ring]
    return min(xs), min(ys), max(xs), max(ys)


def grid_shape(bbox: tuple[float, float, float, float], lat: float) -> tuple[int, int]:
    """Pixels across the bbox at about PIXEL_M (width, height)."""
    import math
    w_m = (bbox[2] - bbox[0]) * 111_320.0 * math.cos(math.radians(lat))
    h_m = (bbox[3] - bbox[1]) * 111_320.0
    return max(2, math.ceil(w_m / PIXEL_M)), max(2, math.ceil(h_m / PIXEL_M))


def assets_for(month: int) -> list[str]:
    """The bands a scene needs by month: NDVI and NDWI all year (a reservoir or a fadama pond is wet in the dry
    season, not only in August–September), BSI in the dry season. SCL always. One request either way."""
    if DRY[0] <= month <= DRY[1]:
        return ["B02", "B03", "B04", "B08", "B11", "SCL"]
    return ["B03", "B04", "B08", "SCL"]


def scenes(lon: float, lat: float, start: date, end: date) -> list[Scene]:
    """Sentinel-2 L2A scenes over the point, February–October, one per day (the clearer of two overlapping tiles)."""
    items = stac.search(stac.S2, lon, lat, start.isoformat(), end.isoformat(), max_cloud=MAX_CLOUD,
                        fields=["id", "properties.datetime", "properties.eo:cloud_cover",
                                "properties.s2:processing_baseline"])
    by_day: dict[date, Scene] = {}
    for it in items:
        p = it["properties"]
        day = date.fromisoformat(p["datetime"][:10])
        if not (DRY[0] <= day.month <= SEASON[1]):
            continue
        s = Scene(it["id"], day, float(p.get("eo:cloud_cover") or 0.0), str(p.get("s2:processing_baseline") or ""))
        if day not in by_day or s.cloud < by_day[day].cloud:
            by_day[day] = s
    return [by_day[d] for d in sorted(by_day)]


def fetch_window(client: httpx.Client, scene: Scene, bbox: tuple, shape: tuple[int, int],
                 assets: list[str]) -> tuple[dict[str, np.ndarray], object] | None:
    """The plot's window of a scene: {band: array} on a WGS84 grid of `shape`, plus the grid's transform.
    One request; None when the API has no data for it."""
    url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{shape[0]}x{shape[1]}.tif"
    params = [("collection", stac.S2), ("item", scene.id), ("resampling", "nearest")] + [("assets", a) for a in assets]
    r = client.get(url, params=params, headers=stac._headers())
    if r.status_code != 200:
        log.info("place: window of %s: HTTP %s", scene.id, r.status_code)
        return None
    with MemoryFile(r.content) as mf, mf.open() as src:
        data = src.read()
        tr = src.transform
    return {a: data[i] for i, a in enumerate(assets)}, tr


def observe(client: httpx.Client, scene: Scene, geom: dict, bbox: tuple, shape: tuple[int, int]) -> Observation | None:
    assets = assets_for(scene.day.month)
    got = fetch_window(client, scene, bbox, shape, assets)
    if got is None:
        return None
    bands, tr = got
    inside = geometry_mask([geom], out_shape=bands["SCL"].shape, transform=tr, invert=True)
    if not inside.any():
        inside[bands["SCL"].shape[0] // 2, bands["SCL"].shape[1] // 2] = True
    clear = indices.clear_mask(bands["SCL"])
    obs = Observation(scene.day, clear=indices.clear_fraction(bands["SCL"], inside))
    refl = {a: indices.reflectance(bands[a], scene.baseline) for a in assets if a != "SCL"}
    if "B04" in refl and "B08" in refl:
        obs.ndvi = indices.plot_value(indices.ndvi(refl["B04"], refl["B08"]), clear, inside)
    if "B03" in refl:
        obs.ndwi = indices.plot_value(indices.ndwi(refl["B03"], refl["B08"]), clear, inside)
    if "B11" in refl:
        obs.bsi = indices.plot_value(indices.bsi(refl["B02"], refl["B04"], refl["B08"], refl["B11"]), clear, inside)
    return obs


def year_rows(observations: list[Observation], years: list[int]) -> dict[int, YearRow]:
    rows = {y: YearRow(y) for y in years}
    for y in years:
        season = [o.ndvi for o in observations if o.day.year == y and SEASON[0] <= o.day.month <= SEASON[1]
                  and o.ndvi is not None]
        water = [o.ndwi for o in observations if o.day.year == y and WATER_MONTHS[0] <= o.day.month <= WATER_MONTHS[1]
                 and o.ndwi is not None]
        dry = [o.bsi for o in observations if o.day.year == y and DRY[0] <= o.day.month <= DRY[1] and o.bsi is not None]
        r = rows[y]
        r.season_obs = len(season)
        if len(season) >= MIN_P90:
            r.ndvi_p90 = round(float(np.percentile(season, 90)), 3)
        r.water_obs = len(water)
        if water:
            r.water_share = round(sum(1 for v in water if v > indices.NDWI_WATER) / len(water), 2)
        by_month: dict[int, list[float]] = {}
        for o in observations:
            if o.day.year == y and o.ndwi is not None:
                by_month.setdefault(o.day.month, []).append(o.ndwi)
        r.water_months = sorted(m for m, vs in by_month.items() if float(np.median(vs)) > indices.NDWI_WATER)
        r.dry_obs = len(dry)
        if dry:
            r.bsi_dry = round(float(np.median(dry)), 3)
    return rows


def compute_years(lat: float, lon: float, geom: dict, years: list[int], *, workers: int = WORKERS,
                  progress=None) -> dict[int, YearRow]:
    """The Sentinel-2 measures for these years (the scenes fetched side by side)."""
    bbox, shape = bbox_of(geom), grid_shape(bbox_of(geom), lat)
    todo = scenes(lon, lat, date(min(years), 2, 1), date(max(years), 10, 31))
    todo = [s for s in todo if s.day.year in years]
    log.info("place: %d scenes for %d years at %s", len(todo), len(years), cell_id(lat, lon))
    observations: list[Observation] = []
    with httpx.Client(timeout=TIMEOUT) as client, ThreadPoolExecutor(max_workers=workers) as ex:
        for i, obs in enumerate(ex.map(lambda s: observe(client, s, geom, bbox, shape), todo), 1):
            if obs is not None:
                observations.append(obs)
            if progress and i % 25 == 0:
                progress(i, len(todo))
    return year_rows(observations, years)


# --- the long water history and the land cover ----------------------------------------------------------------

def jrc_summary(lon: float, lat: float, geom: dict) -> dict:
    """JRC Global Surface Water (v1.3, 1984–2020, 30 m) at the plot: occurrence (% of observed months with water),
    recurrence (% of years with water), seasonality (months a year), as medians over the plot; and, from the
    yearly classes clipped to Sokoto (data/place/jrc, when present), the years the plot was under water."""
    out: dict = {"source": "JRC Global Surface Water v1.3 (1984–2020), Planetary Computer", "years_under_water": None}
    items = stac.search(stac.JRC, lon, lat, "1984-01-01", "2030-01-01", limit=1)
    if items:
        bbox, shape = bbox_of(geom), grid_shape(bbox_of(geom), lat)
        shape = (max(2, shape[0] // 3), max(2, shape[1] // 3))                  # 30 m pixels
        url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{shape[0]}x{shape[1]}.tif"
        assets = ["occurrence", "recurrence", "seasonality"]
        params = [("collection", stac.JRC), ("item", items[0]["id"]), ("resampling", "nearest")] + \
                 [("assets", a) for a in assets]
        with httpx.Client(timeout=TIMEOUT) as c:
            r = c.get(url, params=params, headers=stac._headers())
        if r.status_code == 200:
            with MemoryFile(r.content) as mf, mf.open() as src:
                data = src.read()
                tr = src.transform
            inside = geometry_mask([geom], out_shape=data[0].shape, transform=tr, invert=True)
            if not inside.any():
                inside[data[0].shape[0] // 2, data[0].shape[1] // 2] = True
            for i, a in enumerate(assets):
                vals = data[i][inside]
                vals = vals[vals != 255]                                        # 255: no data
                out[a] = round(float(np.median(vals)), 1) if vals.size else None
    out.update(jrc_years(geom))
    return out


def jrc_years(geom: dict, folder: Path = JRC_DIR) -> dict:
    """From the clipped yearly classes (1 not water, 2 seasonal, 3 permanent, 0 no data): the years at least
    half the plot's observed pixels were water, and whether permanent or seasonal."""
    from app.place.raster import read_plot
    files = sorted(folder.glob("yearly_*.tif")) if folder.exists() else []
    if not files:
        return {}
    years, kinds = [], {}
    for f in files:
        year = int(f.stem.split("_")[1])
        arr, plot = read_plot(str(f), geom)
        vals = arr[plot.inside]
        vals = vals[vals != 0]
        if not vals.size:
            continue
        water = (vals >= 2).mean()
        if water >= 0.5:
            years.append(year)
            kinds[year] = "permanent" if (vals == 3).mean() >= 0.5 else "seasonal"
    return {"years_under_water": years, "water_kind": kinds,
            "years_covered": (int(files[0].stem.split("_")[1]), int(files[-1].stem.split("_")[1]))}


def _window(collection: str, item: str, bbox: tuple, shape: tuple[int, int], assets: list[str]) -> tuple | None:
    """A small window of any Planetary Computer item as ({asset: array}, transform), or None."""
    url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{shape[0]}x{shape[1]}.tif"
    params = [("collection", collection), ("item", item), ("resampling", "nearest")] + [("assets", a) for a in assets]
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(url, params=params, headers=stac._headers())
    if r.status_code != 200:
        return None
    with MemoryFile(r.content) as mf, mf.open() as src:
        data = src.read()
        tr = src.transform
    return {a: data[i] for i, a in enumerate(assets)}, tr


def nearest_water(lon: float, lat: float, radius_m: float = WATER_SEARCH_M) -> dict | None:
    """The nearest JRC water body (occurrence >= WATER_OCCURRENCE, 30 m pixels) within radius_m of the pin: the
    distance to its nearest pixel, a point inside it for the Sentinel-2 history (the nearest pixel whose
    neighbours are all water, so a 1 ha plot there sits on water, not on the shore), its area and outline (the
    connected pixels, as a WGS84 polygon for the map). None when there is none."""
    import math
    items = stac.search(stac.JRC, lon, lat, "1984-01-01", "2030-01-01", limit=1)
    if not items:
        return None
    dlat = radius_m / 111_320.0
    dlon = radius_m / (111_320.0 * math.cos(math.radians(lat)))
    bbox = (lon - dlon, lat - dlat, lon + dlon, lat + dlat)
    n = max(4, math.ceil(2 * radius_m / 30.0))
    got = _window(stac.JRC, items[0]["id"], bbox, (n, n), ["occurrence"])
    if got is None:
        return None
    return water_body(got[0]["occurrence"], got[1], lon, lat, radius_m)


def water_body(occ: np.ndarray, tr, lon: float, lat: float, radius_m: float = WATER_SEARCH_M) -> dict | None:
    """nearest_water's arithmetic on an occurrence window (255 = no data) with its transform."""
    import math
    from collections import deque
    from rasterio.features import shapes
    water = (occ != 255) & (occ >= WATER_OCCURRENCE)
    if not water.any():
        return None
    rows, cols = np.indices(occ.shape)
    xs = tr.c + (cols + 0.5) * tr.a
    ys = tr.f + (rows + 0.5) * tr.e
    dist = np.hypot((xs - lon) * 111_320.0 * math.cos(math.radians(lat)), (ys - lat) * 111_320.0)
    dist_w = np.where(water, dist, np.inf)
    r0, c0 = np.unravel_index(int(np.argmin(dist_w)), occ.shape)
    if dist_w[r0, c0] > radius_m:
        return None
    # the connected water body holding that pixel (4-connected flood fill on a grid of at most a few hundred squared)
    body = np.zeros_like(water)
    q = deque([(r0, c0)])
    body[r0, c0] = True
    while q:
        r, c = q.popleft()
        for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= rr < occ.shape[0] and 0 <= cc < occ.shape[1] and water[rr, cc] and not body[rr, cc]:
                body[rr, cc] = True
                q.append((rr, cc))
    interior = body.copy()
    interior[1:-1, 1:-1] &= body[:-2, 1:-1] & body[2:, 1:-1] & body[1:-1, :-2] & body[1:-1, 2:]
    interior[0, :] = interior[-1, :] = interior[:, 0] = interior[:, -1] = False
    pick = interior if interior.any() else body
    r1, c1 = np.unravel_index(int(np.argmin(np.where(pick, dist, np.inf))), occ.shape)
    outline = None
    for geom, val in shapes(body.astype("uint8"), mask=body, transform=tr):
        if val == 1 and (outline is None or len(geom["coordinates"][0]) > len(outline["coordinates"][0])):
            outline = geom
    pixel_ha = abs(tr.a * tr.e) * (111_320.0 ** 2) * math.cos(math.radians(lat)) / 10_000.0
    return {"lat": round(float(ys[r1, c1]), 5), "lon": round(float(xs[r1, c1]), 5),
            "distance_m": int(round(float(dist_w[r0, c0]))), "occurrence": int(occ[r1, c1]),
            "area_ha": round(float(body.sum()) * pixel_ha, 1), "outline": outline,
            "source": "JRC Global Surface Water v1.3 (1984–2020), Planetary Computer"}


def landcover(lon: float, lat: float, geom: dict) -> str | None:
    """The plot's majority ESA WorldCover 2021 class (10 m)."""
    items = [it for it in stac.search(stac.WORLDCOVER, lon, lat, "2021-01-01", "2021-12-31", limit=2)]
    if not items:
        return None
    bbox, shape = bbox_of(geom), grid_shape(bbox_of(geom), lat)
    url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{shape[0]}x{shape[1]}.tif"
    params = [("collection", stac.WORLDCOVER), ("item", items[0]["id"]), ("assets", "map"), ("resampling", "nearest")]
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(url, params=params, headers=stac._headers())
    if r.status_code != 200:
        return None
    with MemoryFile(r.content) as mf, mf.open() as src:
        data = src.read(1)
        tr = src.transform
    inside = geometry_mask([geom], out_shape=data.shape, transform=tr, invert=True)
    vals = data[inside] if inside.any() else data.ravel()
    vals = vals[vals != 0]
    if not vals.size:
        return None
    top = int(np.bincount(vals.astype(int)).argmax())
    return WORLDCOVER.get(top, str(top))


# --- cache ---------------------------------------------------------------------------------------------------

def _load(conn, cell: str) -> dict[tuple[str, int], tuple[dict, date]]:
    rows = conn.execute("SELECT layer, year, values, computed_at FROM sat_cache WHERE cell = %s", (cell,)).fetchall()
    return {(layer, year): (vals, at) for layer, year, vals, at in rows}


def _save(conn, cell: str, layer: str, year: int, values: dict, source: str, clear_obs: int | None,
          today: date) -> None:
    conn.execute(
        "INSERT INTO sat_cache (cell, layer, year, values, clear_obs, source, computed_at) VALUES (%s, %s, %s, %s, %s, "
        "%s, %s) ON CONFLICT (cell, layer, year) DO UPDATE SET values = EXCLUDED.values, clear_obs = EXCLUDED.clear_obs, "
        "source = EXCLUDED.source, computed_at = EXCLUDED.computed_at",
        (cell, layer, year, json.dumps(values), clear_obs, source, today))
    conn.commit()


def _fresh(entry: tuple[dict, date] | None, year: int, today: date) -> bool:
    """A cached row is used when the year is over, or it was computed in the last STALE_DAYS."""
    if entry is None:
        return False
    return year < today.year or (today - entry[1]).days < STALE_DAYS


# --- the whole history -----------------------------------------------------------------------------------------

def point_history(conn, lat: float, lon: float, *, today: date | None = None, polygon: dict | None = None,
                  workers: int = WORKERS, progress=None, water: bool = False) -> History:
    """The place's history from the cache, computing what is missing. `polygon` is a GeoJSON polygon (WGS84) for a
    plot; a pin alone becomes a circle of about 1 ha. With `water` (the question is about a pond, a dam, a lake
    or flooding) and the place itself not water, the nearest water body within WATER_SEARCH_M gets its own
    history, attached as `nearest_water`."""
    today = today or date.today()
    h = _point_history(conn, lat, lon, today=today, polygon=polygon, workers=workers, progress=progress)
    if water and not h.on_water:
        t0 = time.perf_counter()
        cached = _load(conn, h.cell) if conn is not None else {}
        near = cached.get(("nearest_water", 0), (None, None))[0]
        if ("nearest_water", 0) not in cached:
            try:
                near = nearest_water(lon, lat) or {}
                if conn is not None:
                    _save(conn, h.cell, "nearest_water", 0, near, "JRC GSW v1.3", None, today)
            except (httpx.HTTPError, OSError) as e:
                log.warning("place: nearest water failed: %s", e)
                near = None
        if near:
            near = dict(near)
            near["history"] = _point_history(conn, near["lat"], near["lon"], today=today, workers=workers,
                                             progress=progress)
            h.nearest_water = near
        h.timing["nearest_water"] = time.perf_counter() - t0
        h.timing["total"] += h.timing["nearest_water"]
    return h


def _point_history(conn, lat: float, lon: float, *, today: date, polygon: dict | None = None,
                   workers: int = WORKERS, progress=None) -> History:
    cell = cell_id(lat, lon)
    geom = polygon or circle(lon, lat)
    years = list(range(FIRST_YEAR, today.year + 1))
    t0 = time.perf_counter()
    timing: dict[str, float] = {}
    cached = _load(conn, cell) if conn is not None else {}
    missing = [y for y in years if not _fresh(cached.get(("s2", y)), y, today)]
    rows: dict[int, YearRow] = {}
    for y in years:
        if y not in missing:
            rows[y] = YearRow(**cached[("s2", y)][0])
    if missing:
        fresh = compute_years(lat, lon, geom, missing, workers=workers, progress=progress)
        for y, r in fresh.items():
            rows[y] = r
            if conn is not None:
                _save(conn, cell, "s2", y, {k: v for k, v in asdict(r).items() if not k.startswith("rain")},
                      "Sentinel-2 L2A, Planetary Computer", r.season_obs, today)
    timing["sentinel2"] = time.perf_counter() - t0
    # rain: one call for every year when any year is missing or the current one is stale
    t1 = time.perf_counter()
    if any(not _fresh(cached.get(("rain", y)), y, today) for y in years):
        daily = rain.daily_rain(lat, lon, date(FIRST_YEAR, 1, 1), today - timedelta(days=1))
        for y, vals in rain.by_year(daily).items():
            if y in years:
                cached[("rain", y)] = (vals, today)
                if conn is not None:
                    _save(conn, cell, "rain", y, vals, "Open-Meteo archive (ERA5-Land)", None, today)
    for y in years:
        if ("rain", y) in cached:
            v = cached[("rain", y)][0]
            rows[y].rain_season_mm, rows[y].rain_year_mm = v.get("season_mm"), v.get("year_mm")
            rows[y].rain_days = int(v.get("season_days") or 0)
    timing["rain"] = time.perf_counter() - t1
    t2 = time.perf_counter()
    if ("jrc", 0) not in cached:
        try:
            cached[("jrc", 0)] = (jrc_summary(lon, lat, geom), today)
            if conn is not None:
                _save(conn, cell, "jrc", 0, cached[("jrc", 0)][0], "JRC GSW v1.3", None, today)
        except (httpx.HTTPError, OSError) as e:
            log.warning("place: JRC summary failed: %s", e)
    if ("landcover", 0) not in cached:
        try:
            cached[("landcover", 0)] = ({"class": landcover(lon, lat, geom)}, today)
            if conn is not None:
                _save(conn, cell, "landcover", 0, cached[("landcover", 0)][0], "ESA WorldCover 2021", None, today)
        except (httpx.HTTPError, OSError) as e:
            log.warning("place: WorldCover failed: %s", e)
    timing["context"] = time.perf_counter() - t2
    h = History(cell, lat, lon, rows, jrc=cached.get(("jrc", 0), ({}, today))[0],
                landcover=(cached.get(("landcover", 0), ({}, today))[0] or {}).get("class"), timing=timing,
                from_cache=not missing)
    h.kind = place_kind(h.landcover, rows)
    usable = h.usable_years()
    if h.vegetated:
        # greenness claims only about vegetation: a market, a dune or a reservoir has no 'decline'
        pts = {y: (rows[y].ndvi_p90, rows[y].rain_season_mm) for y in usable
               if rows[y].rain_season_mm is not None and (y < today.year or rows[y].rain_days >= 150)}
        h.fit = fitting.rain_fit(pts)
        if (t := fitting.trend({y: rows[y].ndvi_p90 for y in usable})) is not None:
            h.trends["greenness"] = t
    if h.kind in (None, "bare ground", "little vegetation"):
        if (t := fitting.trend({y: rows[y].bsi_dry for y in usable if rows[y].bsi_dry is not None})) is not None:
            h.trends["bare_soil"] = t
    timing["total"] = time.perf_counter() - t0
    return h
