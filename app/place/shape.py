"""The plot shape a farmer gives when SAM 3.1 can't draw an accepted outline (docs/place-history.md §4):

- a size ("3 acres", "2 ha", "hekta 2", "kadada 3"): a circle of that area around the pin;
- 3–6 corner pins sent within CORNER_TTL_S: joined into the plot polygon (ordered around their centre, checked
  for a sensible shape and an area of MIN_HA–MAX_HA).
The shape and the pins live only in memory (app/geo/location.py), never in the database or the logs. Answers
say which shape was used: the satellite outline, the circle of the size given, or the corner pins.
"""

from __future__ import annotations

import math
import re

from shapely.geometry import Polygon

from app.place.outline import MAX_HA, MIN_HA
from app.place.raster import circle

ACRE_HA = 0.404686
CORNER_TTL_S = 10 * 60
MIN_CORNERS, MAX_CORNERS = 3, 6
MAX_SIZE_HA = 500.0          # a size over this is not a farm plot for a 10 m history: ask again

_NUM = r"(\d+(?:[.,]\d+)?|\d+\s*(?:/|da)\s*\d+)"
SIZE = re.compile(rf"(?i)(?:{_NUM}\s*(ha\b|hekta\w*|hectares?|acres?|kadad\w*|ek[aæ]\w*)|"
                  rf"(ha\b|hekta\w*|hectares?|acres?|kadad\w*|ek[aæ]\w*)\s*{_NUM})")
BARE_NUMBER = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*$")
CORNER_WORDS = re.compile(r"(?i)\b(?:corners?|kusurw\w*|gefuna|iyak\w*|boundary\s+pins?|these\s+are\s+the\s+pins)\b")
DONE_WORDS = re.compile(r"(?i)^\s*(?:done|finished|that'?s\s+all|all\s+sent|an\s+gama|na\s+gama|shi\s+ke\s+nan|"
                        r"ya\s+isa|haka\s+ne)\s*[.!]?\s*$")
SKIP_WORDS = re.compile(r"(?i)^\s*(?:skip|don'?t\s+know|i\s+don'?t\s+know|no\s+idea|not\s+sure|tsallake|ban\s+sani\s+ba|"
                        r"ban\s+san(?:i)?\s+ba|ban\s+tabbata\s+ba|a'?a|no)\s*[.!]?\s*$")


def _number(s: str) -> float | None:
    s = s.strip().replace(",", ".")
    if m := re.match(r"^(\d+)\s*(?:/|da)\s*(\d+)$", s):      # "1/2", "2 da rabi" is not this; a plain fraction
        a, b = int(m.group(1)), int(m.group(2))
        return a / b if b else None
    try:
        return float(s)
    except ValueError:
        return None


def parse_area_ha(text: str, asked: bool = False) -> float | None:
    """Hectares from a farm size in words, or None. A bare number counts only when the size was asked, and is
    read as hectares (the answer says 'circle of N ha you gave')."""
    text = text or ""
    m = SIZE.search(text)
    if m:
        num = _number(m.group(1) or m.group(4) or "")
        unit = (m.group(2) or m.group(3) or "").lower()
        if num is None or num <= 0:
            return None
        ha = num * ACRE_HA if unit.startswith(("acre", "kadad", "ek")) else num
        return round(ha, 2) if ha <= MAX_SIZE_HA else None
    if asked and (m := BARE_NUMBER.match(text)):
        num = _number(m.group(1))
        return round(num, 2) if num and 0 < num <= MAX_SIZE_HA else None
    return None


def circle_of(lon: float, lat: float, area_ha: float) -> dict:
    """A circle of the given area around the pin."""
    radius_m = math.sqrt(area_ha * 10_000.0 / math.pi)
    return circle(lon, lat, radius_m, points=48)


def _metres(points: list[tuple[float, float]], lat0: float) -> list[tuple[float, float]]:
    k = 111_320.0
    return [((lon) * k * math.cos(math.radians(lat0)), lat * k) for lat, lon in points]


def corners_polygon(points: list[tuple[float, float]]) -> tuple[dict | None, float, str]:
    """(GeoJSON polygon, area in ha, note) from 3–6 (lat, lon) corner pins ordered around their centre; the
    polygon is None with the reason when the pins are too few, too many, too close, or make no sensible shape
    (self-crossing, thinner than a strip, or outside MIN_HA–MAX_HA)."""
    pts = [(float(a), float(b)) for a, b in points]
    if len(pts) < MIN_CORNERS:
        return None, 0.0, "too_few"
    if len(pts) > MAX_CORNERS:
        return None, 0.0, "too_many"
    lat0 = sum(p[0] for p in pts) / len(pts)
    xy = _metres(pts, lat0)
    cx, cy = sum(p[0] for p in xy) / len(xy), sum(p[1] for p in xy) / len(xy)
    order = sorted(range(len(xy)), key=lambda i: math.atan2(xy[i][1] - cy, xy[i][0] - cx))
    ring_m = [xy[i] for i in order]
    poly = Polygon(ring_m)
    if not poly.is_valid or poly.area <= 0:
        return None, 0.0, "not_a_shape"
    area_ha = poly.area / 10_000.0
    if area_ha < MIN_HA:
        return None, round(area_ha, 2), "too_small"
    if area_ha > MAX_HA:
        return None, round(area_ha, 2), "too_big"
    hull = poly.convex_hull
    if poly.area < 0.5 * hull.area:                      # a star or a bow tie, not a field
        return None, round(area_ha, 2), "not_a_shape"
    minx, miny, maxx, maxy = poly.bounds
    if min(maxx - minx, maxy - miny) < 15.0 or poly.area < 0.15 * (maxx - minx) * (maxy - miny):
        return None, round(area_ha, 2), "too_thin"      # a strip thinner than a few pixels
    ring = [[pts[i][1], pts[i][0]] for i in order]
    ring.append(ring[0])
    return {"type": "Polygon", "coordinates": [ring]}, round(area_ha, 2), ""


def centroid(geometry: dict) -> tuple[float, float]:
    """(lat, lon) of a polygon's centre."""
    c = Polygon(geometry["coordinates"][0]).centroid
    return float(c.y), float(c.x)


def shape_from_size(lat: float, lon: float, area_ha: float) -> dict:
    return {"geometry": circle_of(lon, lat, area_ha), "method": "given_circle", "area_ha": round(area_ha, 2)}


def shape_from_corners(points: list[tuple[float, float]]) -> dict | None:
    geom, area_ha, note = corners_polygon(points)
    if geom is None:
        return None
    return {"geometry": geom, "method": "corners", "area_ha": area_ha, "corners": len(points)}


FIT_M = 30.0              # a point this close to the plot (or to a declined plot's pin) is the same farm


def fits(shape: dict | None, anchor: tuple[float, float] | None, lat: float, lon: float, tol_m: float = FIT_M) -> bool:
    """Whether a remembered shape belongs to the farm at (lat, lon): its polygon contains the point (within a few
    metres); a declined size ({"declined": True}) belongs to the pin it was declined for (within `tol_m`). A new
    farm pin outside the plot starts a new plot (follow-up review, finding 2: farm B was analysed with farm A's
    circle)."""
    import math

    from shapely.geometry import Point, shape as to_shape
    if not shape:
        return True
    if shape.get("geometry"):
        deg = tol_m / 111_320.0
        return to_shape(shape["geometry"]).buffer(deg).covers(Point(lon, lat))
    if anchor is None:
        return True
    dy = (lat - anchor[0]) * 111_320.0
    dx = (lon - anchor[1]) * 111_320.0 * math.cos(math.radians(lat))
    return math.hypot(dx, dy) <= tol_m
