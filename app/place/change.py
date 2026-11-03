"""Change maps (3 Nov 2026): a WhatsApp list of measures, then of areas, then one map. A measure is offered only
when its data check passes, and an area only when the measure has data at that scale:

- Flood: the seasons with floodwater seen by radar, 2015 to now (Copernicus GFM, app/place/gfm.py), per ward, LGA
  or the state, and per 200 m cell around a pin (this spot ~2 km; 5 km around it) from the season rasters.
- Crops/greenness: the latest complete season's peak greenness against each unit's own usual (MODIS, the
  planner's headline-year rule), per ward, LGA or the state.
- Drought: the latest June–October rain against each LGA's usual (Open-Meteo/ERA5-Land, ~9 km): LGAs and the
  state only, since every ward takes its LGA's figure.
Dropped by the 3 Nov data checks, and said so when asked (DROPPED): land cover (Esri/Impact Observatory annual 10 m
maps call 91 % of Sokoto rangeland and 3–4 % crops, against ~45 % cropland in ESA WorldCover; WorldCover 2020 and
2021 use different algorithms, so they can't be compared) and tree loss (Hansen GFC sees 6 ha of 30 % canopy in the
whole state in 2000; most of its 'loss' is on land it never counted as trees).

The derived rows (gfm_seasons_flooded, modis_peak_change, rain_season_change) are computed from ward_history by
derived_rows() (scripts/precompute_area.py --layers change) and drawn by app/place/images.py: area_map.
"""

from __future__ import annotations

from datetime import date

import numpy as np

from app.place.area import STATE

MEASURES = ("flood", "green", "drought")
AREAS = ("spot", "5km", "ward", "lga", "state")
OFFER = {"flood": AREAS, "green": ("ward", "lga", "state"), "drought": ("lga", "state")}
KEY = {"flood": "gfm_seasons", "green": "green_change", "drought": "rain_change"}       # planner.MEASURES keys
SPOT_SIDE = {"spot": 0.02, "5km": 0.09}          # degrees across: ~2 km around the spot, ~10 km (5 km each way)
SEEN_FRACTION = 0.25                              # a 200 m cell floods in a season when a quarter of it was under water
SEASON_SHARE = 0.001                              # a unit floods in a season when 0.1 % of its land was under water
DROPPED = {
    "en": {"landcover": "Land cover isn't offered: the yearly land-cover maps available disagree with the farmland map "
                        "by a factor of ten in Sokoto, so a change map would show the maps' errors, not real change.",
           "trees": "Tree loss isn't offered: the global tree-loss record sees almost no tree cover in Sokoto (6 ha of "
                    "dense canopy in the whole state in 2000), so its 'loss' here is mostly noise."},
    "ha": {"landcover": "Ba a bayar da canjin yanayin ƙasa ba: taswirorin yanayin ƙasa na shekara-shekara da ake da su "
                        "sun saɓa da taswirar gonaki sau goma a Sokoto, don haka taswirar canji za ta nuna kurakuransu, "
                        "ba canji na gaskiya ba.",
           "trees": "Ba a bayar da asarar bishiyoyi ba: bayanan asarar bishiyoyi na duniya ba sa ganin kusan bishiyoyi "
                    "a Sokoto (hekta 6 na bishiyoyi masu yawa a dukkan jihar a 2000), don haka 'asarar' a nan galibi "
                    "kuskure ce."},
}


# --- the derived rows ---------------------------------------------------------------------------------------------

def derived_rows(conn, today: date) -> list[tuple]:
    """(unit, level, measure, year, value, n_obs, source) for the three change measures."""
    from app.place import flood_record as F
    from app.place import planner as P
    rows: list[tuple] = []
    # flood: seasons with floodwater, per unit (year 0: the whole record); a season counts when at least
    # SEASON_SHARE of the unit's land was under water (never under MIN_HA): any 2 ha in a 70,000 ha LGA is not a flood
    land = {(u, lvl): float(v) for u, lvl, v in conn.execute(
        "SELECT unit, level, value FROM ward_history WHERE measure = 'land_ha' AND year = 0").fetchall()}
    by_unit: dict[tuple[str, str], list[float]] = {}
    for unit, level, year, v, n in conn.execute(
            "SELECT unit, level, year, value, n_obs FROM ward_history WHERE measure = 'gfm_union_ha' AND value IS NOT "
            "NULL AND n_obs > 0").fetchall():
        by_unit.setdefault((unit, level), []).append(float(v))
    src = conn.execute("SELECT source FROM ward_history WHERE measure = 'gfm_union_ha' LIMIT 1").fetchone()
    for (unit, level), vals in by_unit.items():
        need = max(F.MIN_HA, SEASON_SHARE * land.get((unit, level), 0.0))
        rows.append((unit, level, "gfm_seasons_flooded", 0, float(sum(1 for v in vals if v >= need)), len(vals),
                     src[0] if src else ""))
    # greenness and rain: the latest complete season against each unit's own usual
    for measure, out, rel in (("modis_peak", "modis_peak_change", False), ("rain_season_mm", "rain_season_change", True)):
        loaded = P.years_loaded(conn, measure, "lga")
        if not loaded:
            continue
        y = P.headline_year(conn, measure, "lga", loaded, today)[0] if measure == "modis_peak" else \
            max(x for x in loaded if date(x, 10, 31) < today)
        src = conn.execute("SELECT source FROM ward_history WHERE measure = %s LIMIT 1", (measure,)).fetchone()[0]
        for level in ("ward", "lga", "state"):
            units = [r[0] for r in conn.execute("SELECT DISTINCT unit FROM ward_history WHERE measure = %s AND level = %s",
                                                (measure, level)).fetchall()]
            for unit in units:
                s = P.series(conn, measure, level, unit)
                if y not in s:
                    continue
                others = sorted(v for k, v in s.items() if k != y)
                if len(others) < 3:
                    continue
                usual = others[len(others) // 2]
                if rel and usual <= 0:
                    continue
                value = (s[y] / usual - 1.0) if rel else (s[y] - usual)
                rows.append((unit, level, out, y, round(value, 4), len(others), src))
    return rows


def change_year(conn, measure_key: str) -> int:
    from app.place.planner import MEASURES
    row = conn.execute("SELECT max(year) FROM ward_history WHERE measure = %s", (MEASURES[measure_key]["measure"],)).fetchone()
    return int(row[0] or 0)


# --- what is offered ----------------------------------------------------------------------------------------------

def checks(conn) -> dict[str, bool]:
    """Per measure: does its data check pass (the rows exist at the scales offered)?"""
    from app.place.gfm import GFM_DIR
    have = {m: n for m, n in conn.execute(
        "SELECT measure, count(DISTINCT unit) FROM ward_history WHERE measure IN ('gfm_seasons_flooded', "
        "'modis_peak_change', 'rain_season_change') AND level = 'lga' GROUP BY measure").fetchall()}
    return {"flood": have.get("gfm_seasons_flooded", 0) >= 20 and len(list(GFM_DIR.glob("*.tif"))) >= 5,
            "green": have.get("modis_peak_change", 0) >= 20,
            "drought": have.get("rain_season_change", 0) >= 20}


def areas_for(measure: str, place: dict | None) -> list[str]:
    """The areas offered for a measure: the pin's areas only with a place on file (else they are still offered and
    the location is asked for); the ward only with a ward on file."""
    place = place or {}
    out = []
    for a in OFFER[measure]:
        if a == "ward" and place and not place.get("wardcode"):
            continue
        out.append(a)
    return out


def needs_place(area: str) -> bool:
    return area in ("spot", "5km", "ward", "lga")


def spec_for(conn, measure: str, area: str, place: dict) -> dict | None:
    """The map spec for a measure and an area, from the place on file (None when it lacks what the area needs)."""
    key = KEY[measure]
    year = 0 if measure == "flood" else change_year(conn, key)
    if area in ("spot", "5km"):
        if place.get("lat") is None:
            return None
        return {"kind": "change_spot", "area": area, "lat": place["lat"], "lon": place["lon"]}
    if area == "state":
        level = "lga"
        return {"kind": "area_map", "measure": _measure(key), "key": key, "year": year, "level": level, "unit": STATE}
    lga = place.get("lga_pcode")
    if not lga:
        return None
    spec = {"kind": "area_map", "measure": _measure(key), "key": key, "year": year, "level": "ward", "unit": lga}
    if measure == "drought":                       # wards share their LGA's rain: the LGAs of the state
        spec.update({"level": "lga", "unit": STATE})
    if area == "ward" and place.get("wardcode"):
        spec["highlight"] = place["wardcode"]
    return spec


def _measure(key: str) -> str:
    from app.place.planner import MEASURES
    return MEASURES[key]["measure"]


# --- flood around a pin (the season rasters) --------------------------------------------------------------------------

def seasons_grid(lat: float, lon: float, side: float, folder=None):
    """(count of seasons each 200 m cell had floodwater, excluded cells, seasons, extent) around the point."""
    import rasterio
    from rasterio.windows import from_bounds
    from app.place.gfm import GFM_DIR
    folder = folder or GFM_DIR
    box = (lon - side / 2, lat - side / 2, lon + side / 2, lat + side / 2)
    count = excluded = None
    seasons, extent = 0, box
    for path in sorted(folder.glob("*.tif")):
        with rasterio.open(path) as src:
            win = from_bounds(*box, transform=src.transform).round_offsets().round_lengths()
            a = src.read(window=win, boundless=True, fill_value=np.nan)
            b = rasterio.windows.bounds(win, src.transform)
            extent = (b[0], b[2], b[1], b[3])
        union, passes, excl = a[0], a[1], a[2]
        if not np.isfinite(union).any() or np.nanmax(np.nan_to_num(passes)) == 0:
            continue
        seasons += 1
        wet = np.nan_to_num(union) >= SEEN_FRACTION
        count = wet.astype("int16") if count is None else count + wet
        excluded = np.nan_to_num(excl) >= 0.5
    return count, excluded, seasons, extent


WORDS = {
    "en": {"title": "Seasons with floodwater, {first}–{last}", "around": "around your spot", "around5": "within 5 km of you",
           "sub": "200 m squares: rainy seasons (of {n}) with floodwater seen by radar.",
           "never": "none seen", "excluded": "radar can't judge (built-up, dense trees, dry sand)", "you": "you (approx.)",
           "caption": "Seasons with floodwater {where}, {first}–{last}: {max} of {n} at most; {cells} of the {total} "
                      "squares had floodwater in at least one season. Radar can't judge {excl} of the squares.",
           "src": "Copernicus GFM; contains modified Copernicus Emergency Management Service information [{first}–{last}]"},
    "ha": {"title": "Daminun da aka ga ruwan ambaliya, {first}–{last}", "around": "a kewayen wurinku",
           "around5": "cikin kilomita 5 daga gare ku",
           "sub": "Murabba'i na mita 200: daminun (cikin {n}) da radar ta ga ruwan ambaliya.",
           "never": "ba a gani ba", "excluded": "radar ba ta iya tantancewa (gine-gine, bishiyoyi, yashi)",
           "you": "ku (kusan)",
           "caption": "Daminun da aka ga ruwan ambaliya {where}, {first}–{last}: mafi yawa {max} cikin {n}; murabba'i {cells} "
                      "cikin {total} sun sami ruwan ambaliya a ƙalla damina ɗaya. Radar ba ta iya tantance {excl} na murabba'in.",
           "src": "Copernicus GFM; ya ƙunshi bayanan Copernicus Emergency Management Service da aka gyara [{first}–{last}]"},
}


def spot_map(conn, s: dict, lang: str):
    """The flood seasons map around a pin: 200 m squares coloured by how many seasons had floodwater, the squares
    radar can't judge hatched, the point drawn rounded to ~1 km (app/maps/render.py: approx)."""
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.patches import Patch

    from app.maps.render import LEGEND, MapImage, _finish, _local_base, approx, pt
    from app.place.gfm import GFM_DIR
    w = WORDS["ha" if lang == "ha" else "en"]
    lat, lon, side = float(s["lat"]), float(s["lon"]), SPOT_SIDE[s["area"]]
    me = approx(lat, lon)
    count, excluded, n, extent = seasons_grid(me[0], me[1], side)
    if count is None or n == 0:
        return None
    years = sorted(int(p.stem) for p in GFM_DIR.glob("*.tif") if p.stem.isdigit())
    first, last = years[0], years[-1]
    fig, ax = _local_base(conn, me[1], me[0], side, me)
    top = max(1, int(count.max()))
    bounds = [0, 1, 2, 3, 5, max(6, top + 1)]
    colours = ["#ffffff00", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]
    cmap = ListedColormap(colours)
    ax.imshow(np.ma.masked_where(count == 0, count), extent=extent, origin="upper", cmap=cmap,
              norm=BoundaryNorm(bounds, cmap.N), alpha=0.85, zorder=3, interpolation="nearest")
    if excluded is not None and excluded.any():
        ax.contourf(np.linspace(extent[0], extent[1], excluded.shape[1]), np.linspace(extent[3], extent[2], excluded.shape[0]),
                    excluded.astype(float), levels=[0.5, 1.5], colors="none", hatches=["///"], zorder=4)
    labels = ["1", "2", "3–4", f"5–{max(5, top)}"]
    handles = [Patch(facecolor=c, edgecolor="#9a9890", label=lab) for c, lab in zip(colours[1:], labels)]
    handles.append(Patch(facecolor="#ffffff", edgecolor="#9a9890", hatch="///", label=w["excluded"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=3, frameon=False,
               fontsize=LEGEND, handlelength=1.4, columnspacing=1.2)
    where = w["around"] if s["area"] == "spot" else w["around5"]
    jpeg = _finish(fig, ax, w["title"].format(first=first, last=last) + " — " + where,
                   w["sub"].format(n=n), w["src"].format(first=first, last=last), "", 0.16)
    total = count.size
    caption = w["caption"].format(where=where, first=first, last=last, max=int(count.max()), n=n,
                                  cells=int((count > 0).sum()), total=total,
                                  excl=f"{float(excluded.mean()) if excluded is not None else 0.0:.0%}")
    return MapImage(jpeg, caption)
