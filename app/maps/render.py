"""Maps rendered on our server with geopandas and matplotlib (docs/hazard-and-services.md section 8), on our own
base layer: LGA boundaries (OCHA COD-AB) with main roads and rivers from OpenStreetMap (the basemap table,
scripts/import_geo.py). No third-party tiles.

- hazard_map: Sokoto by LGA for the day's heat category, dust/air (US AQI) or rain class, the user's LGA outlined.
- near_you_map: the user's point rounded to about 1 km, the 3 nearest facilities numbered, the road route to 1.
- river_map: the river points with this week's level against the same time of year, as a model estimate.

Labels in Hausa or English; ordinal one-hue ramps checked with the dataviz validator (light end at least 2:1
against the white surface, visible steps), and every colour named in the legend, so colour never carries a
category alone. Each image comes with a caption that repeats its key numbers. Hazard maps are cached per layer,
day, language, LGA and hour; a near-you map is the user's own and is never cached or written to disk.
"""

from __future__ import annotations

import io
import textwrap
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime

import matplotlib

matplotlib.use("Agg")
import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle, Patch  # noqa: E402
from PIL import Image  # noqa: E402
from shapely import wkb  # noqa: E402

from app.hazards import categories as cat  # noqa: E402
from app.hazards import read  # noqa: E402

# ordinal ramps (dataviz validate_palette.js --ordinal: all checks pass on the white surface)
HEAT = ("below", "caution", "extreme_caution", "danger", "extreme_danger")
HEAT_COLORS = ("#f0a06c", "#eb7b3f", "#d95926", "#ad4317", "#7a2d0e")
AIR = ("good", "moderate", "unhealthy_sensitive", "unhealthy", "very_unhealthy", "hazardous")
AIR_COLORS = ("#f09a63", "#e97c42", "#d96029", "#b94a1b", "#8c3712", "#5c240b")
RAIN = ("none", "light", "moderate", "heavy", "violent")
RAIN_COLORS = ("#e9e7e2", "#86b6ef", "#256abf", "#184f95", "#0d366b")   # 'no rain' a neutral, then blue steps
RIVER = ("low", "normal", "high", "very_high")
RIVER_COLORS = ("#86b6ef", "#256abf", "#184f95", "#0d366b")
INK, MUTED, EDGE, SURFACE = "#1f1f1d", "#6b6a66", "#ffffff", "#ffffff"
ROAD, WATER = "#b9b7b0", "#6da7ec"
MAX_BYTES = 1_000_000                      # far under WhatsApp's 5 MB image limit
YOU_RADIUS = 0.009                         # degrees, ~1 km: where the user is, never more precisely
DPI = 110

T = {
    "en": {"heat": "Heat", "air": "Dust and air quality (US AQI)", "rain": "Rain", "today": "today",
           "tomorrow": "tomorrow", "valid": "Valid {day}", "fetched": "fetched {when}", "you": "You (about here)",
           "near": "Nearest health facilities, {lga} LGA", "route": "Road route to 1",
           "rivers": "Rivers this week against the same time of year",
           "model": "Model estimate (GloFAS); dam releases not included. Not an official warning.",
           "credit": "Map data © OpenStreetMap contributors; boundaries OCHA COD-AB", "your_lga": "Your LGA",
           "levels": {"low": "low", "normal": "normal", "high": "high", "very_high": "very high"},
           "heat_src": "Open-Meteo forecast; US National Weather Service heat index categories",
           "air_src": "Open-Meteo Air Quality (Copernicus CAMS); US AQI categories",
           "rain_src": "Open-Meteo forecast; WMO rain intensity classes",
           "facility_src": "Facilities: GRID3 Nigeria / NHFR (Nov 2024). Opening hours not confirmed."},
    "ha": {"heat": "Zafin rana", "air": "Ƙura da ingancin iska (US AQI)", "rain": "Ruwan sama", "today": "yau",
           "tomorrow": "gobe", "valid": "Na {day}", "fetched": "an samo {when}", "you": "Kai (kusan nan)",
           "near": "Cibiyoyin lafiya mafi kusa, Ƙaramar Hukumar {lga}", "route": "Hanyar mota zuwa 1",
           "rivers": "Koguna a wannan mako idan aka kwatanta da wannan lokaci na shekara",
           "model": "Ƙiyasin samfuri (GloFAS); ba a haɗa ruwan madatsun ruwa ba. Ba gargaɗin hukuma ba ne.",
           "credit": "Bayanan taswira © masu ba da gudummawa ga OpenStreetMap; iyakoki OCHA COD-AB",
           "your_lga": "Ƙaramar hukumarka",
           "levels": {"low": "ƙasa", "normal": "na yau da kullum", "high": "sama", "very_high": "sama sosai"},
           "heat_src": "Hasashen Open-Meteo; matakan ma'aunin zafi na US National Weather Service",
           "air_src": "Open-Meteo Air Quality (Copernicus CAMS); matakan US AQI",
           "rain_src": "Hasashen Open-Meteo; matakan ruwan sama na WMO",
           "facility_src": "Cibiyoyi: GRID3 Nigeria / NHFR (Nuwamba 2024). Ba a tabbatar da lokutan buɗewa ba."},
}


@dataclass
class MapImage:
    jpeg: bytes
    caption: str


# --- the base layer, loaded once per process ------------------------------------------------------------------

_base: dict[str, gpd.GeoDataFrame] = {}
_base_lock = threading.Lock()


def base(conn) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """(LGAs, roads and rivers) as GeoDataFrames in WGS84; the base map lines may be empty (no OSM file)."""
    with _base_lock:
        if "lga" not in _base:
            rows = conn.execute("SELECT pcode, name, ST_AsBinary(geom) FROM lga ORDER BY name").fetchall()
            _base["lga"] = gpd.GeoDataFrame({"pcode": [r[0] for r in rows], "name": [r[1] for r in rows]},
                                            geometry=[wkb.loads(bytes(r[2])) for r in rows], crs="EPSG:4326")
            lines = conn.execute("SELECT kind, ST_AsBinary(geom) FROM basemap").fetchall() \
                if conn.execute("SELECT to_regclass('basemap')").fetchone()[0] else []
            _base["lines"] = gpd.GeoDataFrame({"kind": [r[0] for r in lines]},
                                              geometry=[wkb.loads(bytes(r[1])) for r in lines], crs="EPSG:4326")
        return _base["lga"], _base["lines"]


def _draw_base(ax, lgas, lines, rivers_strong: bool = False) -> None:
    if len(lines):
        roads = lines[lines["kind"] != "river"]
        for kind, width in (("secondary", 0.4), ("primary", 0.6), ("trunk", 0.9)):
            part = roads[roads["kind"] == kind]
            if len(part):
                part.plot(ax=ax, color=ROAD, linewidth=width, zorder=2)
        water = lines[lines["kind"] == "river"]
        if len(water):
            water.plot(ax=ax, color=WATER, linewidth=1.2 if rivers_strong else 0.7, zorder=2)


CROWD = 0.16              # degrees: a name point this close to another's has no room for its label


def crowded(name: str, points: dict) -> bool:
    p = points[name]
    return any(n != name and ((q.x - p.x) ** 2 + (q.y - p.y) ** 2) ** 0.5 < CROWD for n, q in points.items())


def _leader_labels(ax, small: list) -> None:
    """Labels for LGAs too small to hold their name (the Sokoto city cluster): set outward from the cluster's
    centre, each with a thin leader line to its LGA."""
    if not small:
        return
    cx = sum(p.x for _, p in small) / len(small)
    cy = sum(p.y for _, p in small) / len(small)
    for i, (name, p) in enumerate(sorted(small, key=lambda s: s[1].x)):
        dx, dy = p.x - cx, p.y - cy
        n = (dx * dx + dy * dy) ** 0.5 or 1.0
        ux, uy = (dx / n, dy / n) if (dx or dy) else ((-1.0, 0.0) if i % 2 else (1.0, 0.0))
        tx, ty = p.x + ux * 0.22, p.y + uy * 0.22
        ax.annotate(name, (p.x, p.y), xytext=(tx, ty), fontsize=6.6, color=INK, zorder=6,
                    ha="left" if ux >= 0 else "right", va="center",
                    bbox={"boxstyle": "round,pad=0.2", "fc": "#ffffff", "ec": "none", "alpha": 0.9},
                    arrowprops={"arrowstyle": "-", "color": INK, "linewidth": 0.6})


def _place_labels(ax, items: list[tuple[float, float, str]], fontsize: float = 7.6) -> None:
    """Point labels, each at the first of a few offsets whose box overlaps no label already placed."""
    ax.autoscale_view()
    placed: list[tuple[float, float, float, float]] = []
    char_w, line_h = 0.58 * fontsize * DPI / 72, 1.35 * fontsize * DPI / 72
    for x, y, text in items:
        px, py = ax.transData.transform((x, y))
        lines = text.split("\n")
        w, h = char_w * max(len(s) for s in lines), line_h * len(lines)
        for ox, oy, ha in ((12, 8, "left"), (12, -8 - h, "left"), (-12, 8, "right"), (-12, -8 - h, "right"),
                           (12, 30, "left"), (-12, 30, "right"), (12, -30 - h, "left"), (-12, -30 - h, "right")):
            x0 = px + ox if ha == "left" else px + ox - w
            box = (x0, py + oy, x0 + w, py + oy + h)
            if not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
                break
        placed.append(box)
        ax.annotate(text, (x, y), xytext=(ox, oy), textcoords="offset points", fontsize=fontsize, color=INK,
                    ha=ha, va="bottom", zorder=7,
                    bbox={"boxstyle": "round,pad=0.25", "fc": "#ffffff", "ec": "none", "alpha": 0.9})


def _finish(fig, ax, title: str, subtitle: str, footer: str) -> bytes:
    ax.set_axis_off()
    ax.set_aspect(1.0 / 0.974)            # degrees near 13° N: a longitude degree is ~0.97 of a latitude degree
    fig.text(0.03, 0.965, title, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.925, subtitle, fontsize=9.5, color=MUTED, va="top")
    fig.text(0.03, 0.015, textwrap.fill(footer, 128), fontsize=7.5, color=MUTED, va="bottom", linespacing=1.3)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor=SURFACE)
    plt.close(fig)
    img = Image.open(io.BytesIO(buf.getvalue())).convert("RGB")
    for q in (85, 75, 65):
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=q, optimize=True)
        if out.tell() <= MAX_BYTES:
            break
    return out.getvalue()


def _day_word(day: date, today: date, lang: str) -> str:
    t = T[lang]
    return t["today"] if day == today else t["tomorrow"] if (day - today).days == 1 else day.strftime("%a %d %b")


# --- 1. the hazard choropleth -----------------------------------------------------------------------------------

def lga_values(conn, layer: str, day: date) -> dict[str, tuple[str, float, str]]:
    """LGA name -> (category, value, value text) for the day, from hazard_values (each LGA's centroid point)."""
    out = {}
    for pid, lga in read.point_ids(conn, read.Where("state")):
        if layer == "air":
            r = read.air_day(conn, pid, lga, day)
            if r:
                out[lga] = (r.category, r.aqi_max, f"AQI {r.aqi_max:.0f}")
        else:
            r = read.heat_day(conn, pid, lga, day)
            if r and layer == "heat":
                out[lga] = (r.category, r.category_value, f"{r.category_value:.0f} °C")
            elif r:
                out[lga] = (r.rain_class, r.rain_mm, f"{r.rain_mm:.1f} mm")
    return out


_cache: dict[tuple, tuple[float, MapImage]] = {}
_cache_lock = threading.Lock()


def hazard_map(conn, layer: str, day: date, lang: str = "en", highlight: str = "", today: date | None = None
               ) -> MapImage | None:
    """Sokoto by LGA for the day: heat category, US AQI category (dust and fine particles) or rain class; None
    when the layer has no data for the day."""
    lang = lang if lang in T else "en"
    hour = datetime.now().strftime("%Y%m%d%H")
    key = ("hazard", layer, day, lang, highlight, hour)
    with _cache_lock:
        if key in _cache:
            return _cache[key][1]
    values = lga_values(conn, layer, day)
    if not values:
        return None
    order, colors = {"heat": (HEAT, HEAT_COLORS), "air": (AIR, AIR_COLORS), "rain": (RAIN, RAIN_COLORS)}[layer]
    lgas, lines = base(conn)
    t = T[lang]
    fig, ax = plt.subplots(figsize=(8.6, 9.4))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.17)
    shade = {c: colors[i] for i, c in enumerate(order)}
    fills = [shade.get(values.get(n, ("",))[0], "#f4f3f0") for n in lgas["name"]]       # no data: a pale grey
    lgas.plot(ax=ax, color=fills, edgecolor=EDGE, linewidth=1.2, zorder=1)
    _draw_base(ax, lgas, lines)
    lgas.boundary.plot(ax=ax, color=EDGE, linewidth=1.2, zorder=3)        # a white gap between the fills
    if highlight:
        mine = lgas[lgas["pcode"] == highlight]
        if len(mine):
            mine.boundary.plot(ax=ax, color=INK, linewidth=2.6, zorder=4)
    small = []
    points = {row["name"]: row.geometry.representative_point() for _, row in lgas.iterrows()}
    for _, row in lgas.iterrows():
        p = points[row["name"]]
        if crowded(row["name"], points):             # the Sokoto city LGAs: labelled outside, with a leader
            small.append((row["name"], p))
            continue
        dark = values.get(row["name"], ("",))[0] in order[3:] or layer == "rain" and \
            values.get(row["name"], ("",))[0] in order[2:]
        ax.text(p.x, p.y, row["name"], fontsize=6.6, ha="center", va="center", zorder=5,
                color="#ffffff" if dark else INK)
    _leader_labels(ax, small)
    present = [c for c in order if any(v[0] == c for v in values.values())]
    handles = [Patch(facecolor=shade[c], edgecolor=MUTED if c == "none" else shade[c], linewidth=0.6,
                     label=f"{cat.label(c, lang)} ({sum(v[0] == c for v in values.values())})") for c in order]
    if highlight:
        handles.append(Line2D([0], [0], color=INK, linewidth=2.6, label=t["your_lga"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.06), ncol=3, frameon=False, fontsize=8.2)
    top = max(values.items(), key=lambda kv: kv[1][1])
    fetched = read.freshness(conn, "air" if layer == "air" else "forecast").fetched_at
    day_word = _day_word(day, today or day, lang)
    title = f"{t[layer]}: {day_word}"
    subtitle = t["valid"].format(day=day.strftime("%d %b %Y")) + (
        f" · {t['fetched'].format(when=fetched.astimezone(read.LAGOS).strftime('%d %b %H:%M'))}" if fetched else "")
    jpeg = _finish(fig, ax, title, subtitle, f"{t[layer + '_src']}. {t['credit']}.")
    worst = cat.label(top[1][0], lang)
    caption = {"en": f"{t[layer]} {day_word}: highest in {top[0]}, {top[1][2]} ({worst}). "
                     + "; ".join(f"{cat.label(c, lang)}: {sum(v[0] == c for v in values.values())} LGAs"
                                 for c in reversed(present)) + ".",
               "ha": f"{t[layer]} {day_word}: mafi yawa a {top[0]}, {top[1][2]} ({worst}). "
                     + "; ".join(f"{cat.label(c, lang)}: ƙananan hukumomi {sum(v[0] == c for v in values.values())}"
                                 for c in reversed(present)) + "."}[lang]
    img = MapImage(jpeg, caption)
    with _cache_lock:
        _cache[key] = (time.time(), img)
        for k in [k for k, (at, _) in _cache.items() if time.time() - at > 3600]:
            _cache.pop(k, None)
    return img


def render_specs(settings, specs: list[dict], lang: str, today: date | None = None) -> list[MapImage]:
    """The maps an answer asked for ({"kind": "hazard", "layer", "day", "highlight"} or {"kind": "river", "day"}),
    each drawn from its own connection; a map that can't be drawn is left out (the text answer stands)."""
    import logging

    import psycopg
    out = []
    try:
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            for s in specs:
                day = date.fromisoformat(s["day"])
                m = hazard_map(conn, s["layer"], day, lang, s.get("highlight", ""), today) if s["kind"] == "hazard" \
                    else river_map(conn, day, lang, today)
                if m is not None:
                    out.append(m)
    except Exception as e:                        # noqa: BLE001 - a map is extra; never lose the answer over it
        logging.getLogger(__name__).warning("map failed: %s", type(e).__name__)
    return out


# --- 2. near you ------------------------------------------------------------------------------------------------

def approx(lat: float, lon: float) -> tuple[float, float]:
    """The user's point as the map draws it: rounded to 0.01 degree (about 1 km)."""
    return round(lat, 2), round(lon, 2)


def near_you_map(conn, lat: float, lon: float, lga: str, facilities: list, route: list[tuple[float, float]] | None,
                 lang: str = "en", caption: str = "") -> MapImage:
    """The user's point (rounded to about 1 km), the facilities numbered 1-3, the road route to 1 when ORS gave it.
    Never cached: it is the user's own."""
    lang = lang if lang in T else "en"
    t = T[lang]
    me = approx(lat, lon)
    lgas, lines = base(conn)
    xs = [me[1]] + [f.lon for f in facilities] + [p[0] for p in route or []]
    ys = [me[0]] + [f.lat for f in facilities] + [p[1] for p in route or []]
    pad = max(0.025, 0.15 * max(max(xs) - min(xs), max(ys) - min(ys)))
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    side = max(x1 - x0, y1 - y0)                       # a square frame
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    fig, ax = plt.subplots(figsize=(8.6, 9.4))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.15)
    lgas.plot(ax=ax, color="#f4f3f0", edgecolor="#d8d6d0", linewidth=1.0, zorder=1)
    _draw_base(ax, lgas, lines)
    for _, row in lgas.iterrows():
        p = row.geometry.representative_point()
        if cx - side / 2 < p.x < cx + side / 2 and cy - side / 2 < p.y < cy + side / 2:
            ax.text(p.x, p.y, row["name"], fontsize=9, color=MUTED, ha="center", va="center", zorder=2,
                    style="italic")
    if route:
        ax.plot([p[0] for p in route], [p[1] for p in route], color="#256abf", linewidth=2.4, zorder=5,
                solid_capstyle="round")
        # off the road network: the route starts at the nearest road, joined to 'about here' by a dashed line
        ax.plot([me[1], route[0][0]], [me[0], route[0][1]], color="#256abf", linewidth=1.2, linestyle=(0, (3, 3)),
                zorder=5)
    # 'about here': the rounded point is within ~0.7 km of the user; a ~1 km circle holds both it and the route's
    # start (which ORS took from the point rounded to ~100 m)
    ax.add_patch(Circle((me[1], me[0]), YOU_RADIUS, facecolor="#256abf", alpha=0.18, edgecolor="#256abf",
                        linewidth=1.2, zorder=6))
    for i, f in enumerate(facilities, 1):
        ax.scatter([f.lon], [f.lat], s=230, color=INK, edgecolor="#ffffff", linewidth=2, zorder=8)
        ax.text(f.lon, f.lat, str(i), color="#ffffff", fontsize=9, fontweight="bold", ha="center", va="center",
                zorder=9)
    ax.set_xlim(cx - side / 2, cx + side / 2)
    ax.set_ylim(cy - side / 2, cy + side / 2)
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#9ec5f4", markeredgecolor="#256abf",
                      markersize=11, label=t["you"])]
    handles += [Line2D([0], [0], marker="o", color="none", markerfacecolor=INK, markersize=10,
                       label=f"{i}. {f.name}") for i, f in enumerate(facilities, 1)]
    if route:
        handles.append(Line2D([0], [0], color="#256abf", linewidth=2.4, label=t["route"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.045), ncol=2, frameon=False, fontsize=8.4)
    jpeg = _finish(fig, ax, t["near"].format(lga=lga), "", f"{t['facility_src']} {t['credit']}.")
    return MapImage(jpeg, caption)


# --- 3. rivers --------------------------------------------------------------------------------------------------

def river_map(conn, day: date, lang: str = "en", today: date | None = None) -> MapImage | None:
    """The river points with the day's GloFAS discharge and its level for the time of year; None without data."""
    lang = lang if lang in T else "en"
    hour = datetime.now().strftime("%Y%m%d%H")
    key = ("river", day, lang, hour)
    with _cache_lock:
        if key in _cache:
            return _cache[key][1]
    rows = read.river_days(conn, day)
    if not rows:
        return None
    pts = {r[0]: (r[1], r[2]) for r in conn.execute(
        "SELECT name, ST_Y(geom), ST_X(geom) FROM hazard_point WHERE kind = 'river'").fetchall()}
    t = T[lang]
    lgas, lines = base(conn)
    shade = dict(zip(RIVER, RIVER_COLORS))
    fig, ax = plt.subplots(figsize=(8.6, 9.4))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.17)
    lgas.plot(ax=ax, color="#f4f3f0", edgecolor="#d8d6d0", linewidth=1.0, zorder=1)
    _draw_base(ax, lgas, lines, rivers_strong=True)
    from app.hazards.answer import discharge
    labels = []
    for r in rows:
        if r.point not in pts:
            continue
        y, x = pts[r.point]
        ax.scatter([x], [y], s=210, color=shade[r.level], edgecolor="#ffffff", linewidth=2, zorder=6)
        labels.append((x, y, f"{r.point}\n{discharge(r.discharge)} m³/s, {t['levels'][r.level]}"))
    _place_labels(ax, labels)
    handles = [Patch(facecolor=shade[lv], label=t["levels"][lv]) for lv in RIVER]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=4, frameon=False, fontsize=8.6)
    fetched = rows[0].fetched_at
    day_word = _day_word(day, today or day, lang)
    subtitle = t["valid"].format(day=day.strftime("%d %b %Y")) + (
        f" · {t['fetched'].format(when=fetched.astimezone(read.LAGOS).strftime('%d %b %H:%M'))}" if fetched else "")
    jpeg = _finish(fig, ax, f"{t['rivers']}: {day_word}", subtitle, f"{t['model']} {t['credit']}.")
    caption = "; ".join(f"{r.point}: {discharge(r.discharge)} m³/s, {t['levels'][r.level]}" for r in rows) + \
        f". {t['model']}"
    img = MapImage(jpeg, caption)
    with _cache_lock:
        _cache[key] = (time.time(), img)
    return img
