"""Small window reads from cloud-optimised GeoTIFFs (remote, signed, or local clips).

Only the tiles that hold the plot's window are fetched (HTTP range requests): a 1 ha plot in a Sentinel-2
band is one 512 x 512 block. The plot is a GeoJSON polygon in WGS84; a pin becomes a circle of about 1 ha.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.windows import Window, from_bounds

ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
           GDAL_HTTP_MULTIPLEX="YES", VSI_CACHE="TRUE", CPL_VSIL_CURL_CACHE_SIZE="50000000", GDAL_PAM_ENABLED="NO",
           GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="1", GDAL_HTTP_TIMEOUT="40")
PLOT_RADIUS_M = 56.4          # a circle of about 1 ha around a pin


def circle(lon: float, lat: float, radius_m: float = PLOT_RADIUS_M, points: int = 32) -> dict:
    """A GeoJSON polygon approximating a circle around the pin (WGS84)."""
    dlat = radius_m / 111_320.0
    dlon = radius_m / (111_320.0 * math.cos(math.radians(lat)))
    ring = [[lon + dlon * math.cos(2 * math.pi * i / points), lat + dlat * math.sin(2 * math.pi * i / points)]
            for i in range(points)]
    ring.append(ring[0])
    return {"type": "Polygon", "coordinates": [ring]}


@dataclass
class Plot:
    """The plot on one raster grid: the window, its bounds in the raster's CRS and the inside mask."""
    crs: object
    window: Window
    bounds: tuple[float, float, float, float]
    inside: np.ndarray            # True for pixels inside the polygon (at least the pixel under the centroid)


def _plot(src, geom4326: dict) -> Plot:
    g = transform_geom("EPSG:4326", src.crs, geom4326)
    xs = [x for ring in g["coordinates"] for x, _ in ring]
    ys = [y for ring in g["coordinates"] for _, y in ring]
    win = from_bounds(min(xs), min(ys), max(xs), max(ys), src.transform).round_offsets().round_lengths()
    win = Window(win.col_off - 1, win.row_off - 1, max(int(win.width), 1) + 2, max(int(win.height), 1) + 2)
    tr = src.window_transform(win)
    shape = (int(win.height), int(win.width))
    inside = geometry_mask([g], out_shape=shape, transform=tr, invert=True)
    if not inside.any():                              # a plot smaller than a pixel: the pixel under its centre
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        r, c = rasterio.transform.rowcol(tr, cx, cy)
        inside[min(max(r, 0), shape[0] - 1), min(max(c, 0), shape[1] - 1)] = True
    b = rasterio.windows.bounds(win, src.transform)
    return Plot(src.crs, win, b, inside)


def read_plot(url: str, geom4326: dict) -> tuple[np.ndarray, Plot]:
    """The raster's pixels around the plot (band 1) and the plot on that grid. The raster sets the grid."""
    with rasterio.Env(**ENV), rasterio.open(url) as src:
        plot = _plot(src, geom4326)
        arr = src.read(1, window=plot.window, boundless=True, fill_value=0)
    return arr, plot


def read_on_grid(url: str, plot: Plot) -> np.ndarray:
    """Another raster of the same scene read onto the plot's grid (a 20 m band onto the 10 m window: nearest
    neighbour, so SCL classes stay classes). Same CRS assumed (one Sentinel-2 tile)."""
    with rasterio.Env(**ENV), rasterio.open(url) as src:
        win = from_bounds(*plot.bounds, src.transform)
        shape = (int(plot.window.height), int(plot.window.width))
        return src.read(1, window=win, out_shape=shape, resampling=Resampling.nearest, boundless=True,
                        fill_value=0)


def plot_values(url: str, geom4326: dict, *, nodata: tuple[int, ...] = ()) -> np.ndarray:
    """The plot's pixel values of a raster (no-data values left out): for the long-history layers."""
    arr, plot = read_plot(url, geom4326)
    vals = arr[plot.inside]
    return vals[~np.isin(vals, nodata)] if nodata else vals
