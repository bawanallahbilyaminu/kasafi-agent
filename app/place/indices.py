"""Spectral indices from Sentinel-2 L2A bands, and the scene-classification (SCL) clear mask.

Reflectance: L2A digital numbers are reflectance x 10000; from processing baseline 04.00 (January 2022) an
offset of 1000 is added, which the index must take off first or every ratio shifts. 0 is no data.

NDVI (greenness) = (B08 - B04) / (B08 + B04), 10 m
NDWI (surface water, McFeeters) = (B03 - B08) / (B03 + B08), 10 m; water where NDWI > 0
BSI (bare soil) = ((B11 + B04) - (B08 + B02)) / ((B11 + B04) + (B08 + B02)); B11 is 20 m, so BSI is 20 m
SCL (20 m): 4 vegetation, 5 not vegetated, 6 water are clear; 0 no data, 1 saturated, 2 dark, 3 cloud shadow,
7 unclassified, 8-9 clouds, 10 cirrus, 11 snow are masked.
"""

from __future__ import annotations

import numpy as np

CLEAR = (4, 5, 6)
OFFSET_BASELINE = "04.00"
NDWI_WATER = 0.0


def reflectance(dn: np.ndarray, baseline: str | None) -> np.ndarray:
    """Digital numbers to reflectance (float, NaN where no data), with the baseline-04 offset taken off."""
    x = dn.astype("float64")
    x[dn == 0] = np.nan
    if baseline and str(baseline) >= OFFSET_BASELINE:
        x = x - 1000.0
    return x / 10000.0


def _ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        out = num / den
    out[~np.isfinite(out)] = np.nan
    return out


def ndvi(b04: np.ndarray, b08: np.ndarray) -> np.ndarray:
    return _ratio(b08 - b04, b08 + b04)


def ndwi(b03: np.ndarray, b08: np.ndarray) -> np.ndarray:
    return _ratio(b03 - b08, b03 + b08)


def bsi(b02: np.ndarray, b04: np.ndarray, b08: np.ndarray, b11: np.ndarray) -> np.ndarray:
    return _ratio((b11 + b04) - (b08 + b02), (b11 + b04) + (b08 + b02))


def clear_mask(scl: np.ndarray) -> np.ndarray:
    return np.isin(scl, CLEAR)


def plot_value(index: np.ndarray, clear: np.ndarray, inside: np.ndarray, *, min_clear: float = 0.5) -> float | None:
    """The plot's value for one scene: the median of the index over its clear pixels, or None when fewer than
    `min_clear` of the plot's pixels are clear (clouds, shadows, no data)."""
    pixels = inside & np.isfinite(index)
    if not pixels.any():
        return None
    ok = pixels & clear
    if ok.sum() < min_clear * inside.sum():
        return None
    return float(np.median(index[ok]))


def clear_fraction(scl: np.ndarray, inside: np.ndarray) -> float:
    if not inside.any():
        return 0.0
    return float(clear_mask(scl)[inside].mean())
