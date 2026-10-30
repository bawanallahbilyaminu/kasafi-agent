"""Where a place is (docs/hazard-and-services.md sections 2-3): a point to its LGA and ward with PostGIS, a typed
place name to a point with the gazetteer.

The COD-AB LGA polygon decides the LGA; the GRID3 ward is given only when its own LGA is that one (the two
layers' borders differ). A point in no LGA is outside Sokoto. Nothing here stores or logs coordinates: callers
get the LGA and ward names and codes, and keep any point in memory only (app/geo/location.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import psycopg


# every facility answer and map carries this line (section 2): the source, its date, and that it may be out of date
FACILITY_NOTE = {
    "en": "Facility list: GRID3 Nigeria / NHFR, updated Nov 2024; opening hours and services aren't confirmed. "
          "Call ahead if you can.",
    "ha": "Jerin cibiyoyin lafiya: GRID3 Nigeria / NHFR, an sabunta Nuwamba 2024; ba a tabbatar da lokutan buɗewa "
          "da ayyukansu ba. Ka kira kafin ka je idan za ka iya.",
}


@dataclass(frozen=True)
class Area:
    lga_pcode: str
    lga: str
    ward: str = ""
    wardcode: str = ""


def locate(conn: psycopg.Connection, lat: float, lon: float) -> Area | None:
    """The LGA (and ward) a point is in, or None outside Sokoto."""
    row = conn.execute(
        "SELECT l.pcode, l.name, w.name, w.wardcode FROM lga l "
        "LEFT JOIN ward w ON w.lga_pcode = l.pcode AND ST_Within(ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), "
        "w.geom) WHERE ST_Within(ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), l.geom) LIMIT 1",
        {"lat": lat, "lon": lon}).fetchone()
    return Area(row[0], row[1], row[2] or "", row[3] or "") if row else None


def name_key(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (s or "").lower().replace("'", "").replace("’", "")))


@dataclass(frozen=True)
class Place:
    name: str
    kind: str
    lga_pcode: str
    lga: str
    lat: float
    lon: float
    source: str


# the most useful kind first when one name is several places: an LGA, then a town, a ward, a village ...
_KIND_ORDER = ("lga", "city", "town", "suburb", "ward", "village", "neighbourhood", "quarter", "hamlet", "locality",
               "settlement", "isolated_dwelling")


def geocode(conn: psycopg.Connection, text: str, most: int = 3) -> list[Place]:
    """Places in Sokoto named in the text ('Kasuwar Gwadabawa', 'Wamako', 'a Goronyo'), best first: the longest
    name the text contains, then the most useful kind. Only our own gazetteer: no external geocoder."""
    words = name_key(text).split()
    if not words:
        return []
    grams = {" ".join(words[i:j]) for i in range(len(words)) for j in range(i + 1, min(len(words), i + 4) + 1)}
    rows = conn.execute(
        "SELECT p.name, p.kind, p.lga_pcode, l.name, ST_Y(p.geom), ST_X(p.geom), p.source, p.name_key FROM place p "
        "JOIN lga l ON l.pcode = p.lga_pcode WHERE p.name_key = ANY(%s)", (sorted(grams),)).fetchall()
    rows.sort(key=lambda r: (-len(r[7]), _KIND_ORDER.index(r[1]) if r[1] in _KIND_ORDER else len(_KIND_ORDER)))
    out, seen = [], set()
    for name, kind, pcode, lga, lat, lon, source, key in rows:
        if (key, pcode) not in seen:
            seen.add((key, pcode))
            out.append(Place(name, kind, pcode, lga, lat, lon, source))
    return out[:most]
