"""The water-body layer (docs/place-history.md §14): every JRC water body in Sokoto State, with a name where one is
known. GRID3's water file isn't available, so the bodies come from JRC Global Surface Water occurrence (water in
at least OCCURRENCE % of the observed months, 1984–2020, 30 m pixels grouped into 8-connected bodies) and the names
from OpenStreetMap (natural=water, water=reservoir|lake|pond, via Overpass; ODbL) with data/geo/water_bodies.yaml
overriding them. Built once by scripts/build_water_bodies.py into data/geo/water_bodies.geojson (outside git,
synced to the server with --sync-geo), read here for "the nearest water body" names and the maps.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

LAYER = Path("data/geo/water_bodies.geojson")
OVERRIDES = Path("data/geo/water_bodies.yaml")
OSM_CACHE = Path("data/geo/osm_water_sokoto.json")
OCCURRENCE = 50
SEASONAL_OCCURRENCE = 10     # a seasonal lake (Kware Lake, Lake Kalmalo) holds water in 10–50% of the months
MIN_BODY_HA = 0.3            # three 30 m pixels: single-pixel specks are noise
MIN_SEASONAL_HA = 1.0
RES_M = 30.0
TILE_PX = 2000               # the data API caps a window at 2048 px
NAME_REACH_M = 400.0         # an OSM point names the body it falls in, or the nearest within this
OVERPASS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")


@dataclass
class Body:
    id: int
    name: str
    name_ha: str
    source: str              # osm | yaml | ''
    area_ha: float
    occurrence: float
    lat: float
    lon: float
    geometry: dict
    seasonal: bool = False   # water in SEASONAL_OCCURRENCE–OCCURRENCE % of the months (a seasonal lake's full extent)

    def label(self, lang: str) -> str:
        return (self.name_ha if lang == "ha" and self.name_ha else self.name) or ""


class WaterLayer:
    """The bodies in an STRtree: the body at a point, or the nearest within a radius; permanent bodies before
    the seasonal extents that enclose them."""

    def __init__(self, bodies: list[Body]) -> None:
        from shapely import STRtree
        from shapely.geometry import shape
        self.bodies = bodies
        self._geoms = [shape(b.geometry) for b in bodies]
        self._tree = STRtree(self._geoms) if bodies else None

    def __len__(self) -> int:
        return len(self.bodies)

    @property
    def named(self) -> int:
        return sum(1 for b in self.bodies if b.name)

    def at(self, lon: float, lat: float, seasonal: bool = True) -> Body | None:
        from shapely.geometry import Point
        if self._tree is None:
            return None
        p = Point(lon, lat)
        hits = [self.bodies[int(i)] for i in self._tree.query(p, predicate="intersects")]
        hits = [b for b in hits if seasonal or not b.seasonal]
        return min(hits, key=lambda b: (b.seasonal, b.area_ha)) if hits else None

    def nearest(self, lon: float, lat: float, radius_m: float, seasonal: bool = True) -> tuple[Body, float] | None:
        """(body, distance in m) of the nearest body within radius_m (0 when the point is inside one)."""
        from shapely.geometry import Point, box
        if self._tree is None:
            return None
        if (b := self.at(lon, lat, seasonal)) is not None:
            return b, 0.0
        p = Point(lon, lat)
        dlat = radius_m / 111_320.0
        dlon = radius_m / (111_320.0 * math.cos(math.radians(lat)))
        best: tuple[Body, float] | None = None
        for i in self._tree.query(box(lon - dlon, lat - dlat, lon + dlon, lat + dlat), predicate="intersects"):
            b = self.bodies[int(i)]
            if b.seasonal and not seasonal:
                continue
            g = self._geoms[int(i)]
            q = g.exterior.interpolate(g.exterior.project(p)) if g.geom_type == "Polygon" else g.centroid
            d = math.hypot((q.x - lon) * 111_320.0 * math.cos(math.radians(lat)), (q.y - lat) * 111_320.0)
            if d <= radius_m and (best is None or d < best[1]):
                best = (b, d)
        return best

    def name_near(self, lon: float, lat: float, lang: str, radius_m: float = 60.0) -> str:
        """The name of the body at the point (or within two pixels of it): the permanent body's own name, else
        the name of the seasonal extent it lies in; '' when none is named."""
        from shapely.geometry import Point
        if self._tree is None:
            return ""
        p = Point(lon, lat)
        hits = sorted((self.bodies[int(i)] for i in self._tree.query(p, predicate="intersects")),
                      key=lambda b: (b.seasonal, b.area_ha))
        for b in hits:
            if b.name:
                return b.label(lang)
        hit = self.nearest(lon, lat, radius_m)
        return hit[0].label(lang) if hit and hit[0].name else ""


def load(path: Path = LAYER) -> WaterLayer:
    try:
        fc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return WaterLayer([])
    bodies = []
    for f in fc.get("features", []):
        p = f.get("properties") or {}
        bodies.append(Body(int(p.get("id", len(bodies))), str(p.get("name") or ""), str(p.get("name_ha") or ""),
                           str(p.get("source") or ""), float(p.get("area_ha") or 0), float(p.get("occurrence") or 0),
                           float(p.get("lat") or 0), float(p.get("lon") or 0), f["geometry"], bool(p.get("seasonal"))))
    return WaterLayer(bodies)


@lru_cache(maxsize=1)
def layer() -> WaterLayer:
    lay = load()
    if not len(lay):
        log.info("place: no water-body layer at %s (scripts/build_water_bodies.py builds it)", LAYER)
    return lay


def name_at(lon: float, lat: float, lang: str) -> str:
    """The named water body under a point: the layer (with the yaml overrides already applied), else the yaml's
    own radius rule (a pin within an entry's radius counts as being in that water body)."""
    lay = layer()
    return (lay.name_near(lon, lat, lang) if len(lay) else "") or override_name(lat, lon, lang)


def overrides(path: Path = OVERRIDES) -> list[dict]:
    import yaml
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except OSError:
        return []


def override_name(lat: float, lon: float, lang: str, path: Path = OVERRIDES) -> str:
    """data/geo/water_bodies.yaml on its own: the entry whose radius holds the point."""
    best, best_d = "", None
    for r in overrides(path):
        d = math.hypot((lon - float(r["lon"])) * 111.32 * math.cos(math.radians(lat)), (lat - float(r["lat"])) * 111.32)
        if d <= float(r.get("radius_km", 1)) and (best_d is None or d < best_d):
            best, best_d = str(r.get("name_ha" if lang == "ha" else "name") or r.get("name") or ""), d
    return best


# --- the build (scripts/build_water_bodies.py) ----------------------------------------------------------------------

def state_tiles(conn) -> tuple[tuple[float, float, float, float], list[tuple[tuple[float, float, float, float], int, int]]]:
    """The state's bbox and the 30 m tiles (bbox, width, height) that cover it, each at most TILE_PX wide."""
    x0, y0, x1, y1 = conn.execute("SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM "
                                  "(SELECT ST_Extent(geom) e FROM lga) s").fetchone()
    bbox = (x0 - 0.01, y0 - 0.01, x1 + 0.01, y1 + 0.01)
    lat = (y0 + y1) / 2
    w = math.ceil((bbox[2] - bbox[0]) * 111_320.0 * math.cos(math.radians(lat)) / RES_M)
    h = math.ceil((bbox[3] - bbox[1]) * 111_320.0 / RES_M)
    nx, ny = math.ceil(w / TILE_PX), math.ceil(h / TILE_PX)
    tiles = []
    for j in range(ny):
        for i in range(nx):
            tw = min(TILE_PX, w - i * TILE_PX)
            th = min(TILE_PX, h - j * TILE_PX)
            tx0 = bbox[0] + (bbox[2] - bbox[0]) * (i * TILE_PX) / w
            tx1 = bbox[0] + (bbox[2] - bbox[0]) * (i * TILE_PX + tw) / w
            ty1 = bbox[3] - (bbox[3] - bbox[1]) * (j * TILE_PX) / h
            ty0 = bbox[3] - (bbox[3] - bbox[1]) * (j * TILE_PX + th) / h
            tiles.append(((tx0, ty0, tx1, ty1), tw, th))
    return bbox, tiles


def occurrence_mosaic(conn, workers: int = 4) -> tuple[np.ndarray, object]:
    """JRC occurrence over the state at 30 m (255 = no data), with its transform."""
    from concurrent.futures import ThreadPoolExecutor
    import httpx
    from rasterio.io import MemoryFile
    from rasterio.transform import from_bounds
    from app.place import stac
    from app.place.history import DATA_API, TIMEOUT
    bbox, tiles = state_tiles(conn)
    items = stac.search(stac.JRC, 0.0, 0.0, "1984-01-01", "2030-01-01", bbox=bbox, fields=["id"], limit=10)
    w = sum(tw for (_, tw, _) in tiles[: math.ceil(len(tiles) / max(1, len({t[0][1] for t in tiles})))]) \
        if tiles else 0
    nx = len({t[0][0] for t in tiles})
    w = sum(tw for (_, tw, _) in tiles[:nx])
    h = sum(th for k, (_, _, th) in enumerate(tiles) if k % nx == 0)
    occ = np.full((h, w), 255, dtype="uint8")

    def read(args):
        k, (tb, tw, th) = args
        got = np.full((th, tw), 255, dtype="uint8")
        with httpx.Client(timeout=TIMEOUT * 5) as c:
            for it in items:
                url = f"{DATA_API}/{tb[0]},{tb[1]},{tb[2]},{tb[3]}/{tw}x{th}.tif"
                params = [("collection", stac.JRC), ("item", it["id"]), ("resampling", "nearest"), ("assets", "occurrence")]
                for attempt in range(4):
                    r = c.get(url, params=params, headers=stac._headers())
                    if r.status_code < 500:
                        break
                if r.status_code != 200:
                    continue
                with MemoryFile(r.content) as mf, mf.open() as src:
                    a = src.read(1)
                if a.shape == got.shape:
                    fill = (got == 255) & (a != 255)
                    got[fill] = a[fill]
        return k, got

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for k, got in ex.map(read, enumerate(tiles)):
            i, j = k % nx, k // nx
            occ[j * TILE_PX: j * TILE_PX + got.shape[0], i * TILE_PX: i * TILE_PX + got.shape[1]] = got
    return occ, from_bounds(*bbox, w, h)


def bodies_from(occ: np.ndarray, transform, inside: np.ndarray | None = None, min_ha: float = MIN_BODY_HA,
                threshold: int = OCCURRENCE, seasonal: bool = False, first_id: int = 1) -> list[Body]:
    """8-connected groups of pixels with occurrence >= threshold, as polygons with their area and mean occurrence."""
    from rasterio.features import shapes
    from shapely.geometry import shape
    water = (occ != 255) & (occ >= threshold)
    if inside is not None:
        water &= inside
    out: list[Body] = []
    lat_mid = transform.f + transform.e * occ.shape[0] / 2
    pixel_ha = abs(transform.a * transform.e) * (111_320.0 ** 2) * math.cos(math.radians(lat_mid)) / 10_000.0
    for geom, val in shapes(water.astype("uint8"), mask=water, connectivity=8, transform=transform):
        if val != 1:
            continue
        poly = shape(geom)
        n_px = poly.area / abs(transform.a * transform.e)
        area_ha = n_px * pixel_ha
        if area_ha < min_ha:
            continue
        c = poly.centroid
        simple = poly.simplify(abs(transform.a) * 0.5, preserve_topology=True)
        out.append(Body(first_id + len(out), "", "", "", round(area_ha, 1), 0.0, round(float(c.y), 5), round(float(c.x), 5),
                        json.loads(json.dumps(simple.__geo_interface__)), seasonal))
    # mean occurrence per body, from the pixels inside
    from rasterio.features import rasterize
    if out:
        labels = rasterize([(b.geometry, k + 1) for k, b in enumerate(out)], out_shape=occ.shape, transform=transform,
                           fill=0, dtype="int32")
        m = labels > 0
        sums = np.bincount(labels[m], weights=occ[m].astype(float), minlength=len(out) + 1)
        counts = np.bincount(labels[m], minlength=len(out) + 1)
        for k, b in enumerate(out, 1):
            if counts[k]:
                b.occurrence = round(float(sums[k] / counts[k]), 1)
    return out


def osm_water(bbox: tuple[float, float, float, float], cache: Path = OSM_CACHE) -> list[dict]:
    """Named OSM water features in the bbox: [{"name", "name_ha", "kind", "lat", "lon"}] (cached as a file so the
    build repeats offline)."""
    import httpx
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    q = (f'[out:json][timeout:120];(way["natural"="water"]({s},{w},{n},{e});relation["natural"="water"]({s},{w},{n},{e});'
         f'way["water"~"reservoir|lake|pond"]({s},{w},{n},{e});node["natural"="water"]({s},{w},{n},{e});'
         f'way["landuse"="reservoir"]({s},{w},{n},{e}););out tags center;')
    data = None
    for url in OVERPASS:
        try:
            r = httpx.post(url, data={"data": q}, timeout=180, headers={"User-Agent": "kasafi-agent/0.1"})
            if r.status_code == 200:
                data = r.json()
                break
        except (httpx.HTTPError, ValueError):
            continue
    if data is None:
        raise RuntimeError("Overpass unavailable")
    out = []
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        if not tags.get("name"):
            continue
        c = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
        if c.get("lat") is None:
            continue
        out.append({"name": tags["name"], "name_ha": tags.get("name:ha", ""), "kind": tags.get("water") or tags.get("natural")
                    or tags.get("landuse") or "", "lat": float(c["lat"]), "lon": float(c["lon"]), "osm": f"{el['type']}/{el['id']}"})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def name_bodies(bodies: list[Body], osm: list[dict], yaml_rows: list[dict]) -> dict[str, int]:
    """OSM names the body a feature's centre falls in (or the nearest within NAME_REACH_M): a permanent body first,
    else the seasonal extent; the yaml rows override: the body holding the point, else the largest body within
    the radius."""
    lay = WaterLayer(bodies)
    n_osm = n_yaml = 0
    for f in sorted(osm, key=lambda f: f["kind"] != "reservoir"):          # reservoirs first: they are the big ones
        hit = lay.nearest(f["lon"], f["lat"], NAME_REACH_M, seasonal=False) or lay.nearest(f["lon"], f["lat"], NAME_REACH_M)
        if hit and not hit[0].name:
            hit[0].name, hit[0].name_ha, hit[0].source = f["name"], f.get("name_ha") or "", "osm"
            n_osm += 1
    for r in yaml_rows:
        lat, lon, radius_m = float(r["lat"]), float(r["lon"]), float(r.get("radius_km", 1)) * 1000.0
        b = lay.at(lon, lat)
        if b is None:
            within = []
            for cand in bodies:
                d = math.hypot((cand.lon - lon) * 111_320.0 * math.cos(math.radians(lat)), (cand.lat - lat) * 111_320.0)
                if d <= radius_m:
                    within.append((cand.area_ha, cand))
            b = max(within, key=lambda t: t[0])[1] if within else None
        if b is not None:
            if b.source != "yaml":
                n_yaml += 1
            b.name, b.name_ha, b.source = str(r.get("name") or b.name), str(r.get("name_ha") or ""), "yaml"
    return {"osm": n_osm, "yaml": n_yaml}


def write(bodies: list[Body], path: Path = LAYER) -> None:
    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": b.geometry, "properties": {
            "id": b.id, "name": b.name, "name_ha": b.name_ha, "source": b.source, "area_ha": b.area_ha,
            "occurrence": b.occurrence, "lat": b.lat, "lon": b.lon, "seasonal": b.seasonal}} for b in bodies]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")


def build(conn, out: Path = LAYER, workers: int = 4) -> dict:
    """The whole build; returns the counts for the report."""
    import time
    from rasterio.features import rasterize
    from shapely import wkb
    t0 = time.time()
    occ, tr = occurrence_mosaic(conn, workers)
    t1 = time.time()
    state = wkb.loads(bytes(conn.execute("SELECT ST_AsBinary(ST_Buffer(ST_Union(geom), 0.01)) FROM lga").fetchone()[0]))
    inside = rasterize([(state, 1)], out_shape=occ.shape, transform=tr, fill=0, dtype="uint8").astype(bool)
    permanent = bodies_from(occ, tr, inside)
    seasonal = bodies_from(occ, tr, inside, MIN_SEASONAL_HA, SEASONAL_OCCURRENCE, seasonal=True,
                           first_id=len(permanent) + 1)
    bodies = permanent + seasonal
    t2 = time.time()
    bbox = (tr.c, tr.f + tr.e * occ.shape[0], tr.c + tr.a * occ.shape[1], tr.f)
    osm = osm_water(bbox)
    named = name_bodies(bodies, osm, overrides())
    write(bodies, out)
    layer.cache_clear()
    return {"bodies": len(permanent), "seasonal": len(seasonal), "named": sum(1 for b in permanent if b.name),
            "seasonal_named": sum(1 for b in seasonal if b.name), "osm_named": named["osm"], "yaml_named": named["yaml"],
            "osm_features": len(osm), "water_pixels": int(((occ != 255) & (occ >= OCCURRENCE) & inside).sum()),
            "area_ha": round(sum(b.area_ha for b in permanent), 1), "largest": sorted(permanent, key=lambda b: -b.area_ha)[:5],
            "named_list": [b for b in bodies if b.name],
            "seconds": {"mosaic": round(t1 - t0), "bodies": round(t2 - t1), "names": round(time.time() - t2)},
            "grid": occ.shape}
