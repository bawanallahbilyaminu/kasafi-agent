"""The plot outline (docs/place-history.md §4): a pin is a point, a farm is a shape.

1. A Sentinel-2 true-colour chip of about CHIP_M around the pin from the clearest recent dry-season scene (the
   fields' edges show best when the land is bare), read through the Planetary Computer data API at 10 m and
   upsampled UPSCALE times for segmentation.
2. SAM 3.1 (Meta Model API) segments the object at the pin (a positive point prompt).
3. The outline is accepted only when it contains the pin and its area is MIN_HA–MAX_HA; otherwise the 1 ha circle
   around the pin is used, and the answer says so. Every answer says the outline is approximate and never a boundary.

Cached per ~100 m cell in plot_outline_cache (migration 0020): the cell, the polygon, the method, the area and the
scene; never the user or the exact pin.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import math
from dataclasses import dataclass
from datetime import date, timedelta

import httpx
import numpy as np
from PIL import Image
from rasterio.features import shapes
from rasterio.io import MemoryFile
from rasterio.transform import Affine
from shapely.geometry import Point, shape

from app.place import indices, stac
from app.place.history import DATA_API, TIMEOUT, cell_id
from app.place.raster import PLOT_RADIUS_M, circle
from app.providers.sam import SamError, point_prompt, segment_masks

log = logging.getLogger(__name__)

CHIP_M = 1000.0              # the chip's side
CHIP_PX = 100                # at 10 m
UPSCALE = 8                  # 800 x 800 px to SAM
MIN_HA, MAX_HA = 0.1, 50.0
DRY_MONTHS = (11, 12, 1, 2, 3, 4)
MAX_CLOUD = 10.0
LOOKBACK_DAYS = 550          # the last two dry seasons
SAM_TIMEOUT = 25.0
STRETCH = 0.30               # reflectance mapped to white (Sokoto's bright soils)


@dataclass
class Chip:
    scene: str
    day: date
    rgb: np.ndarray                  # CHIP_PX x CHIP_PX x 3, uint8
    transform: Affine                # pixel -> WGS84
    bbox: tuple[float, float, float, float]

    def png(self, scale: int = UPSCALE) -> bytes:
        return _encode(self.rgb, scale, "PNG")

    def jpeg(self, scale: int = UPSCALE) -> bytes:
        return _encode(self.rgb, scale, "JPEG")


@dataclass
class Outline:
    geometry: dict                   # GeoJSON polygon, WGS84
    method: str                      # sam | circle
    area_ha: float
    scene: str = ""
    note: str = ""                   # why the circle: no_segment | too_small | too_big | no_pin | no_chip | sam_failed
    from_cache: bool = False

    @property
    def is_plot(self) -> bool:
        return self.method == "sam"


def _encode(rgb: np.ndarray, scale: int, fmt: str) -> bytes:
    img = Image.fromarray(rgb, "RGB")
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format=fmt, **({"quality": 92} if fmt == "JPEG" else {}))
    return buf.getvalue()


def chip_bbox(lon: float, lat: float, side_m: float = CHIP_M) -> tuple[float, float, float, float]:
    dlat = side_m / 2 / 111_320.0
    dlon = side_m / 2 / (111_320.0 * math.cos(math.radians(lat)))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def dry_scene(lon: float, lat: float, today: date) -> dict | None:
    """The clearest recent dry-season scene over the point (the lowest cloud cover, rounded; the newest among
    ties)."""
    start = today - timedelta(days=LOOKBACK_DAYS)
    items = stac.search(stac.S2, lon, lat, start.isoformat(), today.isoformat(), max_cloud=MAX_CLOUD,
                        fields=["id", "properties.datetime", "properties.eo:cloud_cover",
                                "properties.s2:processing_baseline"])
    dry = [it for it in items if int(it["properties"]["datetime"][5:7]) in DRY_MONTHS]
    if not dry:
        return None
    return min(dry, key=lambda it: (round(float(it["properties"].get("eo:cloud_cover") or 0.0)),
                                    -int(it["properties"]["datetime"][:10].replace("-", ""))))


def true_colour(lon: float, lat: float, today: date | None = None, item: dict | None = None,
                side_m: float = CHIP_M) -> Chip | None:
    """The chip: B04, B03, B02 reflectance stretched to 8 bits (one data API request); `side_m` widens it for a
    map that must also show a water body farther away (at 10 m a pixel either way)."""
    today = today or date.today()
    item = item or dry_scene(lon, lat, today)
    if item is None:
        return None
    bbox = chip_bbox(lon, lat, side_m)
    px = max(CHIP_PX, int(round(side_m / 10.0)))
    url = f"{DATA_API}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{px}x{px}.tif"
    assets = ["B04", "B03", "B02"]
    params = [("collection", stac.S2), ("item", item["id"]), ("resampling", "bilinear")] + \
             [("assets", a) for a in assets]
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(url, params=params, headers=stac._headers())
    if r.status_code != 200:
        log.info("place: chip of %s: HTTP %s", item["id"], r.status_code)
        return None
    with MemoryFile(r.content) as mf, mf.open() as src:
        data = src.read()
        tr = src.transform
    baseline = str(item["properties"].get("s2:processing_baseline") or "")
    bands = [indices.reflectance(data[i], baseline) for i in range(3)]
    rgb = np.stack([stretch(b) for b in bands], axis=-1).astype("uint8")
    return Chip(item["id"], date.fromisoformat(item["properties"]["datetime"][:10]), rgb, tr, bbox)


def stretch(band: np.ndarray) -> np.ndarray:
    """A band to 8 bits: the chip's own 2nd–98th percentile to black–white (field edges show on bright Sahel
    soils, where a fixed stretch gives a flat yellow), at least STRETCH wide so a uniform chip stays natural."""
    vals = band[np.isfinite(band)]
    if not vals.size:
        return np.zeros(band.shape, dtype="uint8")
    lo, hi = np.percentile(vals, 2), np.percentile(vals, 98)
    hi = max(hi, lo + STRETCH / 3)
    return (np.nan_to_num(np.clip((band - lo) / (hi - lo), 0, 1)) ** 0.9 * 255).astype("uint8")


def pin_pixel(chip: Chip, lon: float, lat: float, scale: int = UPSCALE) -> tuple[int, int]:
    """(x, y) of the pin on the upsampled chip."""
    col, row = _colrow(chip.transform, lon, lat)
    return int(col * scale), int(row * scale)


def _colrow(tr: Affine, lon: float, lat: float) -> tuple[float, float]:
    return (lon - tr.c) / tr.a, (lat - tr.f) / tr.e


def mask_outline(mask: np.ndarray, chip: Chip, lon: float, lat: float) -> Outline:
    """The accepted polygon of a mask (any size: it is read against the chip's extent), or the circle with a note."""
    h, w = mask.shape
    tr = Affine(chip.transform.a * chip.rgb.shape[1] / w, 0, chip.transform.c,
                0, chip.transform.e * chip.rgb.shape[0] / h, chip.transform.f)
    col, row = _colrow(tr, lon, lat)
    r, c = int(row), int(col)
    if not (0 <= r < h and 0 <= c < w and mask[r, c]):
        return fallback(lon, lat, "no_pin", chip.scene)
    pixel_ha = abs(tr.a * tr.e) * (111_320.0 ** 2) * math.cos(math.radians(lat)) / 10_000.0
    pin = Point(lon, lat)
    for geom, val in shapes(mask.astype("uint8"), mask=mask, transform=tr):
        if val != 1:
            continue
        poly = shape(geom)
        if not poly.contains(pin):
            continue
        area = float(poly.area / abs(tr.a * tr.e)) * pixel_ha
        if area < MIN_HA:
            return fallback(lon, lat, "too_small", chip.scene)
        if area > MAX_HA:
            return fallback(lon, lat, "too_big", chip.scene)
        simple = poly.simplify(abs(tr.a) * 0.6, preserve_topology=True)
        return Outline(json.loads(json.dumps(simple.__geo_interface__)), "sam", round(area, 2), chip.scene)
    return fallback(lon, lat, "no_segment", chip.scene)


def fallback(lon: float, lat: float, note: str, scene: str = "") -> Outline:
    area = math.pi * PLOT_RADIUS_M ** 2 / 10_000.0
    return Outline(circle(lon, lat), "circle", round(area, 2), scene, note)


async def segment_plot(settings, chip: Chip, lon: float, lat: float) -> Outline:
    """SAM 3.1 at the pin on the upsampled chip: the largest accepted segment holding the pin."""
    jpeg = chip.jpeg()
    size = CHIP_PX * UPSCALE
    x, y = pin_pixel(chip, lon, lat)
    try:
        segments = await segment_masks(jpeg, point_prompt(x, y, size, size), settings=settings, timeout=SAM_TIMEOUT)
    except (SamError, httpx.HTTPError, OSError) as e:
        log.warning("place: SAM 3.1 failed: %s", type(e).__name__)
        return fallback(lon, lat, "sam_failed", chip.scene)
    best: Outline | None = None
    for s in segments:
        mask = s.on_frame(size, size)
        if mask is None or not mask.any():
            continue
        o = mask_outline(mask, chip, lon, lat)
        if o.is_plot and (best is None or o.area_ha > best.area_ha):
            best = o
        elif best is None:
            best = o
    return best or fallback(lon, lat, "no_segment", chip.scene)


# --- cache -----------------------------------------------------------------------------------------------------

def _load(conn, cell: str) -> Outline | None:
    row = conn.execute("SELECT geometry, method, area_ha, scene, note FROM plot_outline_cache WHERE cell = %s",
                       (cell,)).fetchone()
    if row is None:
        return None
    return Outline(row[0], row[1], float(row[2]), row[3] or "", row[4] or "", from_cache=True)


def _save(conn, cell: str, o: Outline, today: date) -> None:
    conn.execute(
        "INSERT INTO plot_outline_cache (cell, geometry, method, area_ha, scene, note, computed_at) VALUES "
        "(%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (cell) DO UPDATE SET geometry = EXCLUDED.geometry, method = "
        "EXCLUDED.method, area_ha = EXCLUDED.area_ha, scene = EXCLUDED.scene, note = EXCLUDED.note, "
        "computed_at = EXCLUDED.computed_at",
        (cell, json.dumps(o.geometry), o.method, o.area_ha, o.scene, o.note, today))
    conn.commit()


async def plot_outline(conn, settings, lat: float, lon: float, *, today: date | None = None,
                       chip: Chip | None = None) -> Outline:
    """The plot outline for a pin, from the cache or drawn now (the chip read and SAM 3.1 called)."""
    today = today or date.today()
    cell = cell_id(lat, lon)
    if conn is not None and (cached := _load(conn, cell)) is not None:
        return cached
    chip = chip or await asyncio.to_thread(true_colour, lon, lat, today)
    if chip is None:
        o = fallback(lon, lat, "no_chip")
    elif settings is None or getattr(settings, "meta_api_key", None) is None:
        o = fallback(lon, lat, "sam_failed", chip.scene)
    else:
        o = await segment_plot(settings, chip, lon, lat)
    if conn is not None:
        _save(conn, cell, o, today)
    return o
