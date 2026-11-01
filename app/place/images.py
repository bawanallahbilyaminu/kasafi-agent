"""The two images of a place-history answer (docs/place-history.md §5), drawn with matplotlib like the hazard maps
(app/maps/render.py: same size, fonts and footer so they read on a phone):

- place_chart: peak rainy-season greenness per year as bars (hatched where the year had too few clear images,
  a marker on years below what the rain predicts) over a second panel with the June–October rain. Two panels on
  one time axis, never two scales on one plot. One hue each; the legend names every mark; the clear-image count
  is printed under each year.
- place_map: the plot outline on the Sentinel-2 true-colour chip, the JRC water frequency shaded in one blue ramp,
  the nearest water body when it was used, the pin, a scale bar and the LGA name.

Both carry Hausa or English labels, colour-blind-safe colours (one hue per measure, no red–green pair, hatching
and markers next to colour), the source stamps (Copernicus Sentinel-2, JRC, Open-Meteo, ESA) and stay under
WhatsApp's image limit (render.MAX_BYTES).
"""

from __future__ import annotations

import logging
import math
import textwrap
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Polygon as MplPolygon  # noqa: E402

from app.maps.render import DPI, FIGSIZE, FOOT, INK, LABEL, LEGEND, MUTED, SMALL, SUBTITLE, TITLE, MapImage, pt  # noqa: E402
from app.maps.render import _finish, _scale_bar  # noqa: E402
from app.place import history as H  # noqa: E402
from app.place import stac  # noqa: E402
from app.place.outline import CHIP_M, Chip, Outline, true_colour  # noqa: E402

log = logging.getLogger(__name__)

MAX_MAP_M = 4600.0          # the widest map (the nearest water body is looked for within 2 km)

GREEN, GREEN_EDGE = "#2f7d5b", "#1f5a40"          # one hue for greenness
THIN_FILL, THIN_EDGE = "#ece9e3", "#8f8c85"       # a year with too few clear images: hatched neutral
RAIN = "#3a6fb0"                                   # one hue for rain
FLAG = "#b3581a"                                   # 'below what the rain predicts': a marker and a label, never colour alone
OUTLINE, OUTLINE_CIRCLE = "#ffd500", "#ffd500"
NEAREST = "#56b4e9"
PIN = "#d62d20"

T = {
    "en": {
        "chart_title": "Peak rainy-season greenness, {lga} LGA",
        "chart_sub": "{first}–{last} · NDVI, 90th percentile of clear images June–October · Sentinel-2, 10 m",
        "y_green": "Peak greenness (NDVI)", "y_rain": "June–October rain (mm)",
        "clear": "clear images",
        "leg_green": "Year with 8+ clear images", "leg_thin": "Too few clear images (under 8): not compared",
        "leg_flag": "Below what the rain predicts", "leg_rain": "June–October rain, Open-Meteo (ERA5-Land)",
        "chart_foot": "Sources: Copernicus Sentinel-2 L2A via Microsoft Planetary Computer; Open-Meteo archive "
                      "(ERA5-Land). Peak greenness is compared with the plot's own years, rain-adjusted; a dry "
                      "year is not a decline.",
        "chart_caption": "Peak rainy-season greenness per year at this spot ({first}–{last}) with June–October "
                         "rain; hatched years had too few clear images.",
        "map_title": "Your plot on the satellite image, {lga} LGA",
        "map_sub": "Sentinel-2 true colour, {day} (10 m), about {km} km across",
        "leg_outline": "Approximate plot outline (from the image; not a boundary)",
        "leg_circle": "Circle of about 1 ha around your pin (no outline could be drawn)",
        "leg_given": "Circle of {ha} ha around your pin (the size you gave)",
        "leg_corners": "Plot from your {n} corner pins (approximate; not a boundary)",
        "leg_water": "How often water was seen, 1984–2020 (JRC): light = rarely, dark = most months",
        "leg_nearest": "Nearest water body, {km} km",
        "leg_nearest_named": "Nearest water body: {name}, {km} km",
        "leg_pin": "Your pin",
        "map_foot": "Sources: Copernicus Sentinel-2 L2A via Microsoft Planetary Computer; JRC Global Surface Water "
                    "v1.3; outline by SAM 3.1 (Meta) from the image, approximate.",
        "map_caption": "The plot outline ({how}) on the Sentinel-2 image of {day}; blue shading shows how often "
                       "water was seen there in 1984–2020.",
        "how_sam": "approximate, about {ha} ha", "how_circle": "a circle of about 1 ha",
        "how_given": "the circle of {ha} ha you gave", "how_corners": "from your {n} corner pins, about {ha} ha",
    },
    "ha": {
        "chart_title": "Koriyar damina a ƙololuwa, Ƙaramar Hukumar {lga}",
        "chart_sub": "{first}–{last} · NDVI, kashi na 90 na hotuna bayyanannu Yuni–Oktoba · Sentinel-2, mita 10",
        "y_green": "Koriya a ƙololuwa (NDVI)", "y_rain": "Ruwan sama Yuni–Oktoba (mm)",
        "clear": "hotuna bayyanannu",
        "leg_green": "Shekara mai hotuna bayyanannu 8 ko fiye",
        "leg_thin": "Hotuna bayyanannu kaɗan ne (ƙasa da 8): ba a kwatanta ba",
        "leg_flag": "Ƙasa da abin da ruwan saman ya nuna", "leg_rain": "Ruwan sama Yuni–Oktoba, Open-Meteo (ERA5-Land)",
        "chart_foot": "Madogara: Copernicus Sentinel-2 L2A ta Microsoft Planetary Computer; Open-Meteo archive "
                      "(ERA5-Land). Ana kwatanta koriya da shekarun gonar kanta bisa ruwan sama; shekarar fari "
                      "ba raguwa ba ce.",
        "chart_caption": "Koriyar damina a ƙololuwa a kowace shekara a wannan wuri ({first}–{last}) tare da ruwan "
                         "sama na Yuni–Oktoba; shekarun da aka zana da layuka ba su da isassun hotuna bayyanannu.",
        "map_title": "Gonarka a hoton tauraron ɗan adam, Ƙaramar Hukumar {lga}",
        "map_sub": "Sentinel-2, launin gaske, {day} (mita 10), kusan kilomita {km} faɗi",
        "leg_outline": "Iyakar gona ta kiyasi (daga hoton; ba iyakar mallaka ba)",
        "leg_circle": "Da'ira ta kusan hekta 1 kewaye da wurinka (ba a iya zana iyaka ba)",
        "leg_given": "Da'irar hekta {ha} kewaye da wurinka (girman da ka bayar)",
        "leg_corners": "Gona daga wuraren kusurwoyi {n} da ka aiko (kiyasi; ba iyakar mallaka ba)",
        "leg_water": "Yawan ganin ruwa, 1984–2020 (JRC): mai haske = da wuya, mai duhu = mafi yawan watanni",
        "leg_nearest": "Tafkin ruwa mafi kusa, kilomita {km}",
        "leg_nearest_named": "Tafkin ruwa mafi kusa: {name}, kilomita {km}",
        "leg_pin": "Wurinka",
        "map_foot": "Madogara: Copernicus Sentinel-2 L2A ta Microsoft Planetary Computer; JRC Global Surface Water "
                    "v1.3; iyaka daga SAM 3.1 (Meta) bisa hoton, kiyasi ce.",
        "map_caption": "Iyakar gona ({how}) a hoton Sentinel-2 na {day}; shuɗin inuwa yana nuna yawan ganin ruwa a "
                       "can a 1984–2020.",
        "how_sam": "kiyasi, kusan hekta {ha}", "how_circle": "da'ira ta kusan hekta 1",
        "how_given": "da'irar hekta {ha} da ka bayar", "how_corners": "daga wuraren kusurwoyi {n} da ka aiko, kusan hekta {ha}",
    },
}


def _day(d: date, lang: str) -> str:
    from app.place.answer import MONTHS
    return f"{d.day} {MONTHS['ha' if lang == 'ha' else 'en'][d.month - 1]} {d.year}"


# --- the chart ---------------------------------------------------------------------------------------------------

def place_chart(h: H.History, lang: str, lga: str) -> MapImage:
    t = T["ha" if lang == "ha" else "en"]
    years = [y for y in sorted(h.years) if h.years[y].season_obs > 0 or h.years[y].rain_season_mm is not None]
    years = [y for y in years if y >= H.GOOD_FROM - 1]
    rows = [h.years[y] for y in years]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=FIGSIZE, sharex=True, gridspec_kw={"height_ratios": [3, 1.6]})
    fig.subplots_adjust(left=0.12, right=0.97, top=0.84, bottom=0.27, hspace=0.12)
    # greenness bars: one hue; a thin year hatched in a neutral; a flagged year marked and labelled
    for y, r in zip(years, rows):
        v = r.ndvi_p90
        if v is None:
            ax.text(y, 0.01, "–", ha="center", va="bottom", fontsize=LABEL, color=MUTED)
            continue
        if r.usable:
            ax.bar(y, v, width=0.72, color=GREEN, edgecolor=GREEN_EDGE, linewidth=0.8, zorder=3)
        else:
            ax.bar(y, v, width=0.72, facecolor=THIN_FILL, edgecolor=THIN_EDGE, hatch="///", linewidth=0.8, zorder=3)
        if h.fit and h.fit.flags.get(y) == "below":
            ax.plot([y], [max(v, 0) + 0.03], marker="v", markersize=11, color=FLAG, zorder=5, linestyle="none")
    ymax = max([r.ndvi_p90 or 0 for r in rows] + [0.3])
    ymin = min([r.ndvi_p90 or 0 for r in rows] + [0.0])          # open water has a negative NDVI: shown as it is
    ax.set_ylim(ymin - (0.05 if ymin < 0 else 0), ymax * 1.25)
    ax.axhline(0, color="#c9c6bf", linewidth=0.8, zorder=1)
    ax.set_ylabel(t["y_green"], fontsize=LABEL, color=INK)
    ax.tick_params(axis="y", labelsize=LABEL, colors=INK, length=0)
    ax.grid(axis="y", color="#e4e2dd", linewidth=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c9c6bf")
    # rain: a line with markers in its own panel on the same years
    rain_years = [y for y, r in zip(years, rows) if r.rain_season_mm is not None]
    rain = [h.years[y].rain_season_mm for y in rain_years]
    if rain:
        ax2.plot(rain_years, rain, color=RAIN, linewidth=2.2, marker="o", markersize=7, zorder=3)
        for y, v in zip(rain_years, rain):
            if y == rain_years[-1] or v == max(rain) or v == min(rain):
                ax2.annotate(f"{v:.0f}", (y, v), xytext=(0, 7), textcoords="offset points", ha="center",
                             fontsize=SMALL, color=INK)
        ax2.set_ylim(0, max(rain) * 1.35)
    ax2.set_ylabel(t["y_rain"], fontsize=LABEL, color=INK)
    ax2.tick_params(axis="y", labelsize=LABEL, colors=INK, length=0)
    ax2.tick_params(axis="x", labelsize=LABEL, colors=INK, length=0)
    ax2.grid(axis="y", color="#e4e2dd", linewidth=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax2.spines[s].set_visible(False)
    ax2.spines["bottom"].set_color("#c9c6bf")
    ax2.set_xticks(years)
    ax2.set_xticklabels([str(y) for y in years], rotation=0)
    ax2.set_xlim(years[0] - 0.7, years[-1] + 0.7)
    # the clear-image count under each year
    for y, r in zip(years, rows):
        ax2.annotate(str(r.season_obs), (y, 0), xytext=(0, -34), textcoords="offset points", ha="center", va="top",
                     fontsize=SMALL, color=MUTED, annotation_clip=False)
    ax2.annotate("\n".join(t["clear"].split()), (years[0] - 0.7, 0), xytext=(-4, -34), textcoords="offset points",
                 ha="right", va="top", fontsize=SMALL, color=MUTED, annotation_clip=False, linespacing=1.1)
    handles = [Patch(facecolor=GREEN, edgecolor=GREEN_EDGE, label=t["leg_green"]),
               Patch(facecolor=THIN_FILL, edgecolor=THIN_EDGE, hatch="///", label=t["leg_thin"]),
               Line2D([], [], color=FLAG, marker="v", markersize=10, linestyle="none", label=t["leg_flag"]),
               Line2D([], [], color=RAIN, marker="o", markersize=7, linewidth=2.2, label=t["leg_rain"])]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=1, fontsize=LEGEND, frameon=False,
               handlelength=1.6, borderaxespad=0.0)
    first, last = years[0], years[-1]
    jpeg = _finish(fig, ax, t["chart_title"].format(lga=lga or "–"), t["chart_sub"].format(first=first, last=last),
                   t["chart_foot"], aspect=False)
    return MapImage(jpeg, t["chart_caption"].format(first=first, last=last))


# --- the map -----------------------------------------------------------------------------------------------------

def jrc_window(lon: float, lat: float, bbox: tuple) -> np.ndarray | None:
    """JRC occurrence over the chip's bbox at 30 m (255 = no data -> 0)."""
    items = stac.search(stac.JRC, lon, lat, "1984-01-01", "2030-01-01", limit=1)
    if not items:
        return None
    n = max(4, math.ceil((bbox[3] - bbox[1]) * 111_320.0 / 30.0))
    got = H._window(stac.JRC, items[0]["id"], bbox, (n, n), ["occurrence"])
    if got is None:
        return None
    occ = got[0]["occurrence"].astype(float)
    occ[occ == 255] = 0
    return occ


def place_map(chip: Chip, outline: Outline | None, h: H.History, lang: str, lga: str, occ: np.ndarray | None,
              lat: float, lon: float) -> MapImage:
    t = T["ha" if lang == "ha" else "en"]
    minx, miny, maxx, maxy = chip.bbox
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.25)
    ax.imshow(chip.rgb, extent=(minx, maxx, miny, maxy), interpolation="bilinear", zorder=1)
    if occ is not None and (occ > 0).any():
        shade = np.ma.masked_where(occ <= 0, occ)
        ax.imshow(shade, extent=(minx, maxx, miny, maxy), cmap="Blues", vmin=0, vmax=100, alpha=0.7,
                  interpolation="nearest", zorder=2)
    handles = []
    if outline is not None:
        ring = outline.geometry["coordinates"][0]
        style = {"edgecolor": OUTLINE, "linewidth": 3.0, "facecolor": "none", "zorder": 5}
        if not outline.is_plot:
            style["linestyle"] = (0, (4, 2))
        ax.add_patch(MplPolygon(ring, closed=True, **style))
        handles.append(Line2D([], [], color=OUTLINE, linewidth=3.0, linestyle="-" if outline.is_plot else "--",
                              label=_shape_words(t, outline, "leg")))
    if occ is not None and (occ > 0).any():
        handles.append(Patch(facecolor="#9ecae1", edgecolor="#2171b5", label=t["leg_water"]))
    if h.nearest_water and h.nearest_water.get("outline"):
        nw = h.nearest_water
        ring = nw["outline"]["coordinates"][0]
        ax.add_patch(MplPolygon(ring, closed=True, edgecolor=NEAREST, linewidth=2.5, facecolor="none", zorder=5))
        ax.plot([lon, nw["lon"]], [lat, nw["lat"]], color=NEAREST, linewidth=1.6, linestyle=":", zorder=5)
        name = str(nw.get("name_ha" if lang == "ha" else "name") or nw.get("name") or "")
        handles.append(Line2D([], [], color=NEAREST, linewidth=2.5, label=t["leg_nearest_named" if name else "leg_nearest"]
                              .format(name=name, km=f"{nw['distance_m'] / 1000:.1f}")))
        if name:                                                # the name on the map, by the body
            ax.annotate(name, (nw["lon"], nw["lat"]), xytext=(4, 4), textcoords="offset points", fontsize=LEGEND,
                        color="#0b2545", zorder=8, path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    if h.water_name and (h.water_type == "permanent" or h.on_water):      # the body under the pin
        ax.annotate(h.water_name, (lon, lat), xytext=(10, -14), textcoords="offset points", fontsize=LEGEND,
                    color="#0b2545", zorder=8, path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    ax.scatter([lon], [lat], s=160, marker="o", facecolor=PIN, edgecolor="#ffffff", linewidth=1.8, zorder=7)
    handles.append(Line2D([], [], color=PIN, marker="o", markersize=10, markeredgecolor="#ffffff", linestyle="none",
                          label=t["leg_pin"]))
    side = maxx - minx
    _scale_bar(ax, (minx + maxx) / 2, (miny + maxy) / 2, side, lat)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    for hd in handles:                                     # a long Hausa label wraps instead of running off the image
        hd.set_label(textwrap.fill(hd.get_label(), 58))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=1, fontsize=LEGEND, frameon=False,
               handlelength=1.8, borderaxespad=0.0)
    km = side * 111.32 * math.cos(math.radians(lat))
    jpeg = _finish(fig, ax, t["map_title"].format(lga=lga or "–"),
                   t["map_sub"].format(day=_day(chip.day, lang), km=f"{km:.0f}" if km >= 1.5 else "1"), t["map_foot"])
    return MapImage(jpeg, t["map_caption"].format(how=_shape_words(t, outline, "how"), day=_day(chip.day, lang)))


def _shape_words(t: dict, outline: Outline | None, kind: str) -> str:
    """The legend ('leg') or caption ('how') words for the shape used: the satellite outline, the 1 ha circle, the
    circle of a size the user gave, or the user's corner pins."""
    if outline is None or outline.method == "circle":
        return t[f"{kind}_circle"]
    if outline.method == "given_circle":
        return t[f"{kind}_given"].format(ha=f"{outline.area_ha:g}")
    if outline.method == "corners":
        return t[f"{kind}_corners"].format(n=outline.corners or "", ha=f"{outline.area_ha:.1f}")
    return t[f"{kind}_outline"] if kind == "leg" else t["how_sam"].format(ha=f"{outline.area_ha:.1f}")


# --- the ward choropleth (planner answers) ---------------------------------------------------------------------------

AREA_RAMP = ("#eef3ea", "#c7dcc0", "#8fbb8a", "#4f8f5c", "#1f5a40")        # one hue, light -> dark (greenness)
FLOOD_RAMP = ("#eceff4", "#bcd0e6", "#86aad3", "#4b7fb8", "#1f4e8c")       # one hue, light -> dark (water, floods)
BARE_RAMP = ("#f4efe6", "#e4cfae", "#d0a870", "#b07c3c", "#7a4f1d")        # one hue (bare soil)
RAIN_RAMP = FLOOD_RAMP
A = {
    "en": {"title": "{short}, {area}, {year}", "title_noyear": "{short}, {area}",
           "legend": "Colour: {what} per {unit}, five equal-count classes. Grey hatched: low data or no cropland.",
           "caption": "{short} by {unit} in {area}{year}: {lo} to {hi}; darkest = highest.",
           "low": "Low data / no cropland", "ward": "ward", "lga": "LGA",
           "area_lga": "{lga} LGA", "area_state": "Sokoto State",
           "src": "{source}; boundaries GRID3 wards, OCHA COD-AB LGAs."},
    "ha": {"title": "{short}, {area}, {year}", "title_noyear": "{short}, {area}",
           "legend": "Launi: {what} a kowace {unit}, aji biyar masu yawan daidai. Toka mai layuka: ƙarancin bayanai ko babu gona.",
           "caption": "{short} a kowace {unit} a {area}{year}: daga {lo} zuwa {hi}; mafi duhu = mafi girma.",
           "low": "Ƙarancin bayanai / babu gona", "ward": "gunduma", "lga": "ƙaramar hukuma",
           "area_lga": "Ƙaramar Hukumar {lga}", "area_state": "Jihar Sokoto",
           "src": "{source}; iyakoki gundumomin GRID3, ƙananan hukumomin OCHA COD-AB."},
}


def area_map(conn, s: dict, lang: str, today: date | None = None) -> MapImage | None:
    """{"kind": "area_map", "measure", "key", "year", "level": ward | lga, "unit": LGA pcode | NG034}."""
    import geopandas as gpd
    from shapely import wkb
    from app.maps.render import base, _draw_base
    from app.place.planner import MEASURES, W as PW, low_data_cut, rows_for
    from app.sources.lga_names import name_of
    t, pw = A["ha" if lang == "ha" else "en"], PW["ha" if lang == "ha" else "en"]
    key, measure, year, level, unit = s["key"], s["measure"], int(s["year"]), s["level"], s["unit"]
    spec = MEASURES[key]
    within = unit if unit != "NG034" else None
    rows = rows_for(conn, measure, level, year, within)
    if not rows:
        return None
    cut = low_data_cut(rows, measure)
    vals = {code: v for code, _, v, n in rows if v is not None and (n is None or n > cut)}
    if level == "ward":
        q = "SELECT wardcode, name, ST_AsBinary(geom) FROM ward" + (" WHERE lga_pcode = %s" if within else "")
        recs = conn.execute(q, (within,) if within else ()).fetchall()
    else:
        recs = conn.execute("SELECT pcode, name, ST_AsBinary(geom) FROM lga").fetchall()
    gdf = gpd.GeoDataFrame({"code": [r[0] for r in recs], "name": [r[1] for r in recs]},
                           geometry=[wkb.loads(bytes(r[2])) for r in recs], crs="EPSG:4326")
    gdf["value"] = [vals.get(c) for c in gdf["code"]]
    ramp = {"greenness": AREA_RAMP, "flood": FLOOD_RAMP, "flood_map": FLOOD_RAMP, "water": FLOOD_RAMP,
            "bare": BARE_RAMP, "rain": RAIN_RAMP}[key]
    have = sorted(v for v in gdf["value"] if v is not None)
    if not have:
        return None
    breaks = [have[min(len(have) - 1, int(len(have) * q))] for q in (0.2, 0.4, 0.6, 0.8)]

    def cls(v):
        return sum(1 for b in breaks if v > b)

    lgas, lines = base(conn)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.27)
    for _, r in gdf.iterrows():
        if r["value"] is None:
            gpd.GeoSeries([r.geometry], crs="EPSG:4326").plot(ax=ax, facecolor="#e6e4df", edgecolor="#9a9890", hatch="///",
                                                              linewidth=0.5, zorder=2)
        else:
            gpd.GeoSeries([r.geometry], crs="EPSG:4326").plot(ax=ax, facecolor=ramp[cls(r["value"])], edgecolor="#ffffff",
                                                              linewidth=0.7, zorder=2)
    frame = lgas[lgas["pcode"] == within] if within else lgas
    frame.boundary.plot(ax=ax, color=INK, linewidth=1.4, zorder=4)
    if within:
        minx, miny, maxx, maxy = frame.total_bounds
        pad = max(maxx - minx, maxy - miny) * 0.06
        ax.set_xlim(minx - pad, maxx + pad)
        ax.set_ylim(miny - pad, maxy + pad)
        # the top three and bottom three named on the map
        ranked = sorted([r for r in gdf.itertuples() if r.value is not None], key=lambda r: -r.value)
        for r in ranked[:3] + ranked[-3:]:
            c = r.geometry.representative_point()
            ax.annotate(r.name, (c.x, c.y), fontsize=SMALL, color=INK, ha="center", va="center", zorder=7,
                        bbox={"boxstyle": "round,pad=0.2", "fc": "#ffffff", "ec": "none", "alpha": 0.85})
    else:
        lgas.boundary.plot(ax=ax, color="#ffffff", linewidth=0.9, zorder=3)
        if level == "lga":
            for r in lgas.itertuples():
                c = r.geometry.representative_point()
                ax.annotate(r.name, (c.x, c.y), fontsize=pt(13), color=INK, ha="center", va="center", zorder=7)
    labels = []
    lo_edges = [have[0]] + breaks
    hi_edges = breaks + [have[-1]]
    for i in range(5):
        labels.append(f"{spec['fmt'].format(lo_edges[i])} – {spec['fmt'].format(hi_edges[i])}")
    handles = [Patch(facecolor=ramp[i], edgecolor="#ffffff", label=labels[i]) for i in range(5)]
    handles.append(Patch(facecolor="#e6e4df", edgecolor="#9a9890", hatch="///", label=t["low"]))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.09), ncol=2, fontsize=LEGEND, frameon=False,
               handlelength=1.6, borderaxespad=0.0)
    area = t["area_lga"].format(lga=name_of(unit)) if within else t["area_state"]
    short = pw["short"][key]
    title = (t["title"] if year else t["title_noyear"]).format(short=short[0].upper() + short[1:], area=area, year=year)
    source = conn.execute("SELECT source FROM ward_history WHERE measure = %s LIMIT 1", (measure,)).fetchone()[0]
    unit_word = t[level]
    jpeg = _finish(fig, ax, title, t["legend"].format(what=short, unit=unit_word), t["src"].format(source=source))
    caption = t["caption"].format(short=short[0].upper() + short[1:], unit=unit_word, area=area,
                                  year=f", {year}" if year else "", lo=spec["fmt"].format(have[0]),
                                  hi=spec["fmt"].format(have[-1]))
    return MapImage(jpeg, caption)


# --- from an answer's spec ---------------------------------------------------------------------------------------

def draw_place(conn, s: dict, lang: str, today: date | None = None) -> MapImage | None:
    """{"kind": "place_chart" | "place_map", "lat", "lon", "lga"}: from the caches the answer just filled (the
    history, the outline), plus the chip and the JRC window for the map (two small requests)."""
    from app.place.outline import Outline, _load, fallback
    today = today or date.today()
    lat, lon, lga = float(s["lat"]), float(s["lon"]), str(s.get("lga") or "")
    if (shape := s.get("shape")) and shape.get("geometry"):          # the shape the user gave (memory only)
        outline = Outline.from_shape(shape)
    else:
        outline = (_load(conn, H.cell_id(lat, lon)) if conn is not None else None) or fallback(lon, lat, "no_segment")
    h = H.point_history(conn, lat, lon, today=today, polygon=outline.geometry if outline.is_plot else None,
                        water=bool(s.get("water")))
    if s["kind"] == "place_chart":
        return place_chart(h, lang, lga)
    item = None
    if outline.scene:
        found = stac.search(stac.S2, lon, lat, "2015-01-01", "2030-01-01", limit=1, ids=[outline.scene])
        item = found[0] if found else None
    # the map shows the nearest water body too: widen the chip when it lies beyond the usual 1 km
    side_m = CHIP_M
    if h.nearest_water:
        side_m = min(MAX_MAP_M, max(CHIP_M, 2.0 * (float(h.nearest_water["distance_m"]) + 250.0)))
    chip = true_colour(lon, lat, today, item=item, side_m=side_m)
    if chip is None:
        return None
    occ = jrc_window(lon, lat, chip.bbox)
    return place_map(chip, outline, h, lang, lga, occ, lat, lon)
