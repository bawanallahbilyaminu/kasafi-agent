"""Maps rendered on our server with geopandas and matplotlib (docs/hazard-and-services.md section 8), on our own
base layer: LGA boundaries (OCHA COD-AB) with main roads and rivers from OpenStreetMap (the basemap table,
scripts/import_geo.py). No third-party tiles.

- hazard_map: Sokoto by LGA for the day's heat category, dust/air (US AQI) or rain class, each LGA's value printed
  on it, the user's LGA outlined. When most LGAs share one category, those are shaded by their value within it
  (lighter to darker), so the map still shows differences; a legend line says what the shading means.
- near_you_map: framed on the user's ~1 km circle and the facilities (at least ~2 km across), the facilities
  numbered with road distance and time in the legend, the main towns nearby, a scale bar, the road route to 1.
- river_map: the river points with today's level against normal for the time of year, each label joined to its
  point by a leader line; a model estimate.

Sizes are for the output image (946 x 1034 px): titles at least 28 px, near-you labels at least 20 px, so the map
reads on a phone. Heat and rain use ordinal one-hue ramps checked with the dataviz validator; air uses the US EPA's
official AQI colours (green to maroon), which people know and which keep neighbouring categories distinct. Every
colour is named in the legend, so colour never carries a category alone. Each image comes with a caption that
repeats its key numbers. Hazard maps are cached per layer, day, language, LGA and hour; a near-you map is the
user's own and is never cached or written to disk.
"""

from __future__ import annotations

import io
import math
import re
import textwrap
import threading
import time
from collections import Counter
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
AIR_COLORS = ("#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023")   # US EPA AQI colours
RAIN = ("none", "light", "moderate", "heavy", "violent")
RAIN_COLORS = ("#e9e7e2", "#86b6ef", "#256abf", "#184f95", "#0d366b")   # 'no rain' a neutral, then blue steps
RIVER = ("low", "normal", "high", "very_high")
RIVER_COLORS = ("#86b6ef", "#256abf", "#184f95", "#0d366b")
INK, MUTED, EDGE, SURFACE = "#1f1f1d", "#6b6a66", "#ffffff", "#ffffff"
ROAD, WATER = "#b9b7b0", "#6da7ec"
MAX_BYTES = 1_000_000                      # far under WhatsApp's 5 MB image limit
YOU_RADIUS = 0.009                         # degrees, ~1 km: where the user is, never more precisely
DPI = 110
FIGSIZE = (8.6, 9.4)                       # 946 x 1034 px


def pt(px: float) -> float:
    """Points for a size in output pixels."""
    return px * 72 / DPI


TITLE, SUBTITLE, LABEL, LEGEND, SMALL, FOOT = pt(28.5), pt(18), pt(20.5), pt(20.5), pt(15), pt(14)
MIN_SIDE = 0.02                            # degrees, ~2.2 km: the near-you map is never zoomed in further
DOMINANT = 0.75                            # this share of LGAs in one category: shade by value within it

T = {
    "en": {"heat": "Heat", "air": "Dust and air quality (US AQI)", "rain": "Rain", "today": "today",
           "tomorrow": "tomorrow", "valid": "Valid {day}", "fetched": "fetched {when}", "old": " (older than usual)",
           "you": "You (about here)",
           "near": "Nearest health facilities, {lga} LGA", "route": "Road route to 1",
           "rivers": "River levels {day} vs. normal for {period} {month}",
           "periods": {"early": "early", "mid": "mid", "late": "late"},
           "months": ("January", "February", "March", "April", "May", "June", "July", "August", "September",
                      "October", "November", "December"),
           "model": "Model estimate (GloFAS); dam releases not included. Not an official warning.",
           "credit": "Map data © OpenStreetMap contributors; boundaries OCHA COD-AB", "your_lga": "Your LGA",
           "levels": {"low": "low", "normal": "normal", "high": "high", "very_high": "very high"},
           "heat_src": "Open-Meteo forecast; US National Weather Service heat index categories",
           "air_src": "Open-Meteo Air Quality (Copernicus CAMS); US AQI categories and colours (US EPA)",
           "rain_src": "Open-Meteo forecast; WMO rain intensity classes",
           "facility_src": "Facilities: GRID3 Nigeria / NHFR (Nov 2024). Opening hours not confirmed.",
           "legend_cat": "Colour: each LGA's {scale} category. Numbers: {measure}.",
           "legend_within": "Most LGAs are {cat}: within it, darker means higher ({lo} to {hi}). Numbers: {measure}.",
           "scales": {"heat": "heat", "air": "US AQI", "rain": "rain intensity"},
           "measures": {"heat": "the day's highest temperature or heat index, °C", "air": "the day's highest US AQI",
                        "rain": "the day's rain, mm"},
           "dist_road": "{km} km, about {mins}", "dist_line": "about {km} km (straight line)",
           "river_legend": "Colour: today's flow against the same time of year since {year}."},
    "ha": {"heat": "Zafin rana", "air": "Ƙura da ingancin iska (US AQI)", "rain": "Ruwan sama", "today": "yau",
           "tomorrow": "gobe", "valid": "Na {day}", "fetched": "an samo {when}", "old": " (ya daɗe fiye da yadda aka saba)",
           "you": "Kai (kusan nan)",
           "near": "Cibiyoyin lafiya mafi kusa, Ƙaramar Hukumar {lga}", "route": "Hanyar mota zuwa 1",
           "rivers": "Matakan koguna {day} idan aka kwatanta da na yau da kullum a {period} {month}",
           "periods": {"early": "farkon", "mid": "tsakiyar", "late": "ƙarshen"},
           "months": ("Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba",
                      "Oktoba", "Nuwamba", "Disamba"),
           "model": "Ƙiyasin samfuri (GloFAS); ba a haɗa ruwan madatsun ruwa ba. Ba gargaɗin hukuma ba ne.",
           "credit": "Bayanan taswira © masu ba da gudummawa ga OpenStreetMap; iyakoki OCHA COD-AB",
           "your_lga": "Ƙaramar hukumarka",
           "levels": {"low": "ƙasa", "normal": "na yau da kullum", "high": "sama", "very_high": "sama sosai"},
           "heat_src": "Hasashen Open-Meteo; matakan ma'aunin zafi na US National Weather Service",
           "air_src": "Open-Meteo Air Quality (Copernicus CAMS); matakai da launukan US AQI (US EPA)",
           "rain_src": "Hasashen Open-Meteo; matakan ruwan sama na WMO",
           "facility_src": "Cibiyoyi: GRID3 Nigeria / NHFR (Nuwamba 2024). Ba a tabbatar da lokutan buɗewa ba.",
           "legend_cat": "Launi: matakin {scale} na kowace ƙaramar hukuma. Lambobi: {measure}.",
           "legend_within": "Yawancin ƙananan hukumomi suna {cat}: a cikinsa, mai duhu ya fi yawa ({lo} zuwa {hi}). "
                            "Lambobi: {measure}.",
           "scales": {"heat": "zafi", "air": "US AQI", "rain": "ruwan sama"},
           "measures": {"heat": "mafi girman zafin iska ko ma'aunin zafi na ranar, °C",
                        "air": "mafi girman US AQI na ranar", "rain": "ruwan saman ranar, mm"},
           "dist_road": "kilomita {km}, kusan {mins}", "dist_line": "kusan kilomita {km} (a miƙe)",
           "river_legend": "Launi: kwararar yau idan aka kwatanta da wannan lokaci na shekara tun {year}."},
}


@dataclass
class MapImage:
    jpeg: bytes
    caption: str


# --- colours ----------------------------------------------------------------------------------------------------

def _rgb(h: str) -> tuple[float, float, float]:
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _hex(c) -> str:
    return "#%02x%02x%02x" % tuple(round(max(0.0, min(1.0, v)) * 255) for v in c)


def _mix(a: str, b: str, t: float) -> str:
    return _hex(tuple(x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))))


def within(color: str, f: float) -> str:
    """A category's colour shaded by a value's place in that category's range (f 0..1): from a pale tint up to the
    category's own colour, never darker (darker would look like the next category)."""
    return _mix(color, "#ffffff", 0.6 * (1 - max(0.0, min(1.0, f))))


def dark(color: str) -> bool:
    """Text on this fill should be white (relative luminance under ~0.4)."""
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.18


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


def _draw_base(ax, lgas, lines, rivers_strong: bool = False, scale: float = 1.0) -> None:
    if len(lines):
        roads = lines[lines["kind"] != "river"]
        for kind, width in (("secondary", 0.4), ("primary", 0.6), ("trunk", 0.9)):
            part = roads[roads["kind"] == kind]
            if len(part):
                part.plot(ax=ax, color=ROAD, linewidth=width * scale, zorder=2)
        water = lines[lines["kind"] == "river"]
        if len(water):
            water.plot(ax=ax, color=WATER, linewidth=(1.2 if rivers_strong else 0.7) * scale, zorder=2)


CROWD = 0.16              # degrees: a name point this close to another's has no room for its label


def crowded(name: str, points: dict) -> bool:
    p = points[name]
    return any(n != name and ((q.x - p.x) ** 2 + (q.y - p.y) ** 2) ** 0.5 < CROWD for n, q in points.items())


def _leader_labels(ax, small: list, fontsize: float = pt(13)) -> None:
    """Labels for LGAs too small to hold their name (the Sokoto city cluster): stacked in the empty space to the
    south-east of the cluster, outside the other LGAs' labels, each with a thin leader line to its LGA."""
    if not small:
        return
    cx = sum(p.x for _, p in small) / len(small)
    cy = sum(p.y for _, p in small) / len(small)
    for i, (name, p) in enumerate(sorted(small, key=lambda s: -s[1].y)):
        tx, ty = cx + LEADER_DX, cy - LEADER_DY - 0.12 * i
        ax.annotate(name, (p.x, p.y), xytext=(tx, ty), fontsize=fontsize, color=INK, zorder=6, ha="left",
                    va="center", bbox={"boxstyle": "round,pad=0.2", "fc": "#ffffff", "ec": MUTED, "lw": 0.5,
                                       "alpha": 0.95},
                    arrowprops={"arrowstyle": "-", "color": INK, "linewidth": 0.8, "shrinkA": 0, "shrinkB": 2})


LEADER_DX, LEADER_DY = 1.05, 0.62          # degrees from the Sokoto city cluster to its label stack (east of Tureta)


def _place_labels(ax, items: list[tuple[float, float, str]], fontsize: float = pt(16)) -> None:
    """Point labels, each at the first of a few offsets whose box overlaps no label already placed, joined to its
    point by a leader line so it is clear which point it belongs to."""
    ax.autoscale_view()
    placed: list[tuple[float, float, float, float]] = []
    char_w, line_h = 0.58 * fontsize * DPI / 72, 1.35 * fontsize * DPI / 72
    for x, y, text in items:
        px, py = ax.transData.transform((x, y))
        lines = text.split("\n")
        w, h = char_w * max(len(s) for s in lines), line_h * len(lines)
        for ox, oy, ha in ((22, 14, "left"), (22, -14 - h, "left"), (-22, 14, "right"), (-22, -14 - h, "right"),
                           (22, 44, "left"), (-22, 44, "right"), (22, -44 - h, "left"), (-22, -44 - h, "right")):
            x0 = px + ox if ha == "left" else px + ox - w
            box = (x0, py + oy, x0 + w, py + oy + h)
            if not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
                break
        placed.append(box)
        ax.annotate(text, (x, y), xytext=(ox, oy), textcoords="offset points", fontsize=fontsize, color=INK,
                    ha=ha, va="bottom", zorder=7,
                    bbox={"boxstyle": "round,pad=0.25", "fc": "#ffffff", "ec": MUTED, "lw": 0.6, "alpha": 0.95},
                    arrowprops={"arrowstyle": "-", "color": INK, "linewidth": 0.9, "shrinkA": 0, "shrinkB": 9})


def _finish(fig, ax, title: str, subtitle: str, footer: str, legend_line: str = "", legend_y: float = 0.0) -> bytes:
    ax.set_axis_off()
    ax.set_aspect(1.0 / 0.974)            # degrees near 13° N: a longitude degree is ~0.97 of a latitude degree
    lines = textwrap.wrap(title, 48)
    fig.text(0.03, 0.972, "\n".join(lines), fontsize=TITLE, fontweight="bold", color=INK, va="top", linespacing=1.15)
    if subtitle:
        fig.text(0.03, 0.972 - 0.036 * len(lines) - 0.008, subtitle, fontsize=SUBTITLE, color=MUTED, va="top")
    if legend_line:
        fig.text(0.5, legend_y, textwrap.fill(legend_line, 78), fontsize=SMALL, color=INK, ha="center", va="bottom",
                 linespacing=1.25)
    fig.text(0.03, 0.012, textwrap.fill(footer, 104), fontsize=FOOT, color=MUTED, va="bottom", linespacing=1.3)
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


def _fetched(conn, layer: str, at: datetime | None, lang: str, now: datetime | None = None) -> str:
    """' · fetched 31 Oct 06:05', marked when older than twice the layer's fetch interval (never passed off as
    current)."""
    if at is None:
        return ""
    t = T[lang]
    stale = read.freshness(conn, layer, now).stale
    return f" · {t['fetched'].format(when=at.astimezone(read.LAGOS).strftime('%d %b %H:%M'))}" + (t["old"] if stale
                                                                                                   else "")


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


def short_value(layer: str, v: float) -> str:
    """The number printed on an LGA: '37°', '182', '2.4'."""
    return f"{v:.0f}°" if layer == "heat" else f"{v:.0f}" if layer == "air" else f"{v:.1f}"


SPREAD = {"heat": 1.0, "air": 5.0, "rain": 0.5}     # less spread than this within the category: nothing to shade


def fills(layer: str, values: dict[str, tuple[str, float, str]]) -> tuple[dict[str, str], str, tuple]:
    """Each LGA's fill, and the dominant category with its value range when most LGAs share one (those LGAs are
    shaded by value within it); ('', ()) otherwise."""
    order, colors = {"heat": (HEAT, HEAT_COLORS), "air": (AIR, AIR_COLORS), "rain": (RAIN, RAIN_COLORS)}[layer]
    shade = dict(zip(order, colors))
    out = {n: shade.get(v[0], "#f4f3f0") for n, v in values.items()}
    if not values:
        return out, "", ()
    dom, n = Counter(v[0] for v in values.values()).most_common(1)[0]
    vals = [v[1] for v in values.values() if v[0] == dom]
    lo, hi = min(vals), max(vals)
    if n < DOMINANT * len(values) or hi - lo < SPREAD[layer] or dom not in shade:
        return out, "", ()
    for name, v in values.items():
        if v[0] == dom:
            out[name] = within(shade[dom], (v[1] - lo) / (hi - lo))
    return out, dom, (lo, hi)


_cache: dict[tuple, tuple[float, MapImage]] = {}
_cache_lock = threading.Lock()


def hazard_map(conn, layer: str, day: date, lang: str = "en", highlight: str = "", today: date | None = None
               ) -> MapImage | None:
    """Sokoto by LGA for the day: heat category, US AQI category (dust and fine particles) or rain class, with each
    LGA's value printed; None when the layer has no data for the day."""
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
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.87, bottom=0.235)
    shade = dict(zip(order, colors))
    fill, dom, span = fills(layer, values)
    lgas.plot(ax=ax, color=[fill.get(n, "#f4f3f0") for n in lgas["name"]], edgecolor=EDGE, linewidth=1.2, zorder=1)
    _draw_base(ax, lgas, lines)
    lgas.boundary.plot(ax=ax, color=EDGE, linewidth=1.2, zorder=3)        # a white gap between the fills
    if highlight:
        mine = lgas[lgas["pcode"] == highlight]
        if len(mine):
            mine.boundary.plot(ax=ax, color=INK, linewidth=2.8, zorder=4)
    small = []
    points = {row["name"]: row.geometry.representative_point() for _, row in lgas.iterrows()}
    for _, row in lgas.iterrows():
        name, p = row["name"], points[row["name"]]
        v = values.get(name)
        if crowded(name, points):                    # the Sokoto city LGAs: labelled outside, with a leader
            small.append((f"{name} {short_value(layer, v[1])}" if v else name, p))
            continue
        ink = "#ffffff" if dark(fill.get(name, "#f4f3f0")) else INK
        ax.text(p.x, p.y + 0.028, name, fontsize=pt(12.5), ha="center", va="bottom", zorder=5, color=ink)
        if v:
            ax.text(p.x, p.y + 0.02, short_value(layer, v[1]), fontsize=pt(17), fontweight="bold", ha="center",
                    va="top", zorder=5, color=ink)
    _leader_labels(ax, small)
    present = [c for c in order if any(v[0] == c for v in values.values())]
    handles = [Patch(facecolor=shade[c], edgecolor=MUTED if c in ("none",) or layer == "air" else shade[c],
                     linewidth=0.6, label=f"{cat.label(c, lang)} ({sum(v[0] == c for v in values.values())})")
               for c in order]
    if highlight:
        handles.append(Line2D([0], [0], color=INK, linewidth=2.8, label=t["your_lga"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=2 if layer == "air" else 3,
               frameon=False, fontsize=pt(16.5), handlelength=1.6, columnspacing=1.4)
    measure = t["measures"][layer]
    legend_line = (t["legend_within"].format(cat=cat.label(dom, lang), lo=short_value(layer, span[0]),
                                             hi=short_value(layer, span[1]), measure=measure) if dom else
                   t["legend_cat"].format(scale=t["scales"][layer], measure=measure))
    top = max(values.items(), key=lambda kv: kv[1][1])
    fetched = read.freshness(conn, "air" if layer == "air" else "forecast").fetched_at
    day_word = _day_word(day, today or day, lang)
    title = f"{t[layer]}: {day_word}"
    subtitle = t["valid"].format(day=day.strftime("%d %b %Y")) + _fetched(
        conn, "air" if layer == "air" else "forecast", fetched, lang)
    jpeg = _finish(fig, ax, title, subtitle, f"{t[layer + '_src']}. {t['credit']}.", legend_line, 0.19)
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


def frame(me: tuple[float, float], facilities: list) -> tuple[float, float, float]:
    """(centre lon, centre lat, side in degrees): the user's ~1 km circle and the facilities with padding, at least
    MIN_SIDE across."""
    xs = [me[1] - YOU_RADIUS, me[1] + YOU_RADIUS] + [f.lon for f in facilities]
    ys = [me[0] - YOU_RADIUS, me[0] + YOU_RADIUS] + [f.lat for f in facilities]
    side = max(MIN_SIDE, 1.3 * max(max(xs) - min(xs), max(ys) - min(ys)))
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, side


GENERIC = set("""bone centre center health clinic clinics hospital hospitals general primary post maternity specialist
comprehensive the of and phc dispensary model cottage medical orthopaedic orthopedic eye dental federal state teaching
university women children child welfare mch unit care basic referral public private laboratory lab diagnostic
facility national community home nursing new old main""".split())


def vague(name: str) -> bool:
    """A name that says what a facility is but not where ('Bone Centre', 'General Hospital')."""
    return all(w in GENERIC for w in re.findall(r"[a-z]+", (name or "").lower()))


def nearest_town(conn, lat: float, lon: float, fallback: str = "") -> str:
    row = conn.execute("SELECT name FROM place WHERE kind IN ('city', 'town', 'village') AND ST_DWithin(geom::geography, "
                       "ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 8000) ORDER BY geom <-> "
                       "ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1", (lon, lat, lon, lat)).fetchone()
    return row[0] if row else fallback


def towns_in(conn, cx: float, cy: float, side: float, near: tuple[float, float], most: int = 6) -> list:
    """(name, lat, lon) of the main places in the frame: the city and towns, then villages nearest the user when the
    frame is small."""
    h = side / 2
    rows = conn.execute(
        "SELECT name, ST_Y(geom), ST_X(geom), kind FROM place WHERE kind IN ('city', 'town', 'village') AND "
        "geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326) ORDER BY (kind = 'village'), geom <-> "
        "ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 40", (cx - h, cy - h, cx + h, cy + h, near[1], near[0])).fetchall()
    out, seen = [], set()
    for name, lat, lon, kind in rows:
        if kind == "village" and (side > 0.12 or sum(1 for o in out if o[3] == "village") >= 3):
            continue
        if name.lower() not in seen:
            seen.add(name.lower())
            out.append((name, lat, lon, kind))
    return [o[:3] for o in out[:most]]


def spread_markers(points: list[tuple[float, float]], sep: float,
                   keep_clear: list[tuple[float, float, float]] = ()) -> list[tuple[float, float]]:
    """Marker positions no closer than `sep` to each other, nor within (x, y, distance) of `keep_clear` (the
    user's circle): a marker that would overlap moves out (its true point keeps a dot and a leader line)."""
    out: list[tuple[float, float]] = []

    def free(px: float, py: float) -> bool:
        return all(math.hypot(px - ox, py - oy) >= sep for ox, oy in out) and \
            all(math.hypot(px - kx, py - ky) >= d for kx, ky, d in keep_clear)
    for i, (x, y) in enumerate(points):
        px, py = x, y
        for step in range(1, 12):
            if free(px, py):
                break
            a = math.radians(45 + 120 * i + 30 * step)
            px, py = x + sep * math.cos(a) * (1 + step / 3), y + sep * math.sin(a) * (1 + step / 3)
        out.append((px, py))
    return out


def _scale_bar(ax, cx: float, cy: float, side: float, lat: float) -> None:
    """A scale bar in the lower left: about a quarter of the frame, rounded to 0.5, 1, 2, 5, 10, 20 or 50 km."""
    km_per_deg = 111.32 * math.cos(math.radians(lat))
    want = side * km_per_deg / 4
    km = min((0.5, 1, 2, 5, 10, 20, 50), key=lambda k: abs(math.log(k / want)))
    x0, y0 = cx - side / 2 + side * 0.05, cy - side / 2 + side * 0.06
    x1 = x0 + km / km_per_deg
    ax.add_patch(plt.Rectangle((x0 - side * 0.015, y0 - side * 0.02), x1 - x0 + side * 0.03, side * 0.075,
                               facecolor="#ffffff", alpha=0.85, edgecolor="none", zorder=9))
    ax.plot([x0, x1], [y0, y0], color=INK, linewidth=3, zorder=10, solid_capstyle="butt")
    for x in (x0, x1):
        ax.plot([x, x], [y0 - side * 0.006, y0 + side * 0.012], color=INK, linewidth=1.6, zorder=10)
    ax.text((x0 + x1) / 2, y0 + side * 0.016, f"{km:g} km", fontsize=pt(18), color=INK, ha="center", va="bottom",
            zorder=10)


def legend_name(conn, f) -> str:
    """'Bone Centre, Wurno' for a name that doesn't say where; the name itself otherwise."""
    return f"{f.name}, {nearest_town(conn, f.lat, f.lon, f.lga)}" if vague(f.name) else f.name


def distance_words(f, lang: str) -> str:
    from app.geo.facilities import _mins
    t = T[lang]
    if f.road_km is not None and f.minutes is not None:
        return t["dist_road"].format(km=f"{f.road_km:g}", mins=_mins(lang, f.minutes))
    return t["dist_line"].format(km=f"{f.km:.1f}")


def near_you_map(conn, lat: float, lon: float, lga: str, facilities: list, route: list[tuple[float, float]] | None,
                 lang: str = "en", caption: str = "") -> MapImage:
    """The user's point (rounded to about 1 km), the facilities numbered 1-3 with road distance and time in the
    legend, the main towns, a scale bar, the road route to 1 when ORS gave it. Never cached: it is the user's own."""
    lang = lang if lang in T else "en"
    t = T[lang]
    me = approx(lat, lon)
    lgas, lines = base(conn)
    cx, cy, side = frame(me, facilities)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.27)
    lgas.plot(ax=ax, color="#f4f3f0", edgecolor="#c9c6bf", linewidth=1.6, zorder=1)
    _draw_base(ax, lgas, lines, scale=2.0)
    if route:
        ax.plot([p[0] for p in route], [p[1] for p in route], color="#256abf", linewidth=4, zorder=5,
                solid_capstyle="round")
        # off the road network: the route starts at the nearest road, joined to 'about here' by a dashed line
        ax.plot([me[1], route[0][0]], [me[0], route[0][1]], color="#256abf", linewidth=2, linestyle=(0, (3, 3)),
                zorder=5)
    # 'about here': the rounded point is within ~0.7 km of the user; a ~1 km circle holds both it and the route's
    # start (which ORS took from the point rounded to ~100 m)
    ax.add_patch(Circle((me[1], me[0]), YOU_RADIUS, facecolor="#256abf", alpha=0.18, edgecolor="#256abf",
                        linewidth=2, zorder=6))
    sep = side * 0.06
    marks = spread_markers([(f.lon, f.lat) for f in facilities], sep, [(me[1], me[0], YOU_RADIUS + sep * 0.6)])
    for i, (f, (mx, my)) in enumerate(zip(facilities, marks), 1):
        if (mx, my) != (f.lon, f.lat):           # moved apart: its true point keeps a dot and a leader line
            ax.plot([f.lon, mx], [f.lat, my], color=INK, linewidth=1.2, zorder=7)
            ax.scatter([f.lon], [f.lat], s=40, color=INK, zorder=7)
        ax.scatter([mx], [my], s=900, color=INK, edgecolor="#ffffff", linewidth=2.5, zorder=8)
        ax.text(mx, my, str(i), color="#ffffff", fontsize=pt(24), fontweight="bold", ha="center", va="center",
                zorder=9)
    taken = [(me[1], me[0])] + marks
    for k, (name, plat, plon) in enumerate(towns_in(conn, cx, cy, side, me)):
        near = min(taken, key=lambda q: math.hypot(plon - q[0], plat - q[1]))
        close = math.hypot(plon - near[0], plat - near[1]) < sep * 1.4
        if close and k:                          # only the town nearest the user is labelled beside a marker
            continue
        left = close and near[0] >= plon         # the label goes on the side away from the marker
        if not close:
            ax.scatter([plon], [plat], s=36, color=MUTED, zorder=4)
        dx = (sep * 0.75 if close else side * 0.012) * (-1 if left else 1)
        ax.text(plon + dx, plat, name, fontsize=LABEL, color=INK, ha="right" if left else "left", va="center",
                zorder=10, style="italic",
                bbox={"boxstyle": "round,pad=0.15", "fc": "#ffffff", "ec": "none", "alpha": 0.8})
        taken.append((plon, plat))
    _scale_bar(ax, cx, cy, side, me[0])
    ax.set_xlim(cx - side / 2, cx + side / 2)
    ax.set_ylim(cy - side / 2, cy + side / 2)
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#9ec5f4", markeredgecolor="#256abf",
                      markersize=16, label=t["you"])]
    handles += [Line2D([0], [0], marker="o", color="none", markerfacecolor=INK, markersize=14,
                       label=f"{i}. {legend_name(conn, f)}: {distance_words(f, lang)}")
                for i, f in enumerate(facilities, 1)]
    if route:
        handles.append(Line2D([0], [0], color="#256abf", linewidth=4, label=t["route"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.06), ncol=1, frameon=False,
               fontsize=LEGEND, handletextpad=0.6, labelspacing=0.35)
    jpeg = _finish(fig, ax, t["near"].format(lga=lga), "", f"{t['facility_src']} {t['credit']}.")
    return MapImage(jpeg, caption)


# --- 3. rivers --------------------------------------------------------------------------------------------------

def river_title(lang: str, day: date, today: date) -> str:
    t = T[lang]
    period = "early" if day.day <= 10 else "mid" if day.day <= 20 else "late"
    return t["rivers"].format(day=_day_word(day, today, lang), period=t["periods"][period],
                              month=t["months"][day.month - 1])


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
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.2)
    lgas.plot(ax=ax, color="#f4f3f0", edgecolor="#d8d6d0", linewidth=1.0, zorder=1)
    _draw_base(ax, lgas, lines, rivers_strong=True)
    from app.hazards.answer import discharge
    labels = []
    for r in rows:
        if r.point not in pts:
            continue
        y, x = pts[r.point]
        ax.scatter([x], [y], s=320, color=shade[r.level], edgecolor="#ffffff", linewidth=2.5, zorder=6)
        labels.append((x, y, f"{r.point}\n{discharge(r.discharge)} m³/s, {t['levels'][r.level]}"))
    _place_labels(ax, labels)
    handles = [Patch(facecolor=shade[lv], label=t["levels"][lv]) for lv in RIVER]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=4, frameon=False,
               fontsize=pt(17))
    fetched = rows[0].fetched_at
    subtitle = t["valid"].format(day=day.strftime("%d %b %Y")) + _fetched(conn, "flood", fetched, lang)
    jpeg = _finish(fig, ax, river_title(lang, day, today or day), subtitle, f"{t['model']} {t['credit']}.",
                   t["river_legend"].format(year=min(r.since for r in rows).year), 0.13)
    caption = "; ".join(f"{r.point}: {discharge(r.discharge)} m³/s, {t['levels'][r.level]}" for r in rows) + \
        f". {t['model']}"
    img = MapImage(jpeg, caption)
    with _cache_lock:
        _cache[key] = (time.time(), img)
    return img
