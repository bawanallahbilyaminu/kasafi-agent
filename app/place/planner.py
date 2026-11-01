"""The planner's place-history answer for a ward, an LGA or the state (docs/place-history.md §5, step 3), from
the precomputed ward_history table (app/place/area.py), written in code:

1. Summary: which wards (or LGAs, for the state) stand out on the measure asked, with the period and the
   resolution; for greenness, which stood out against their own years and that season's rain; low-data units
   marked, never filled.
2. A ward choropleth map (app/place/images.py: area_map).
3. The ranking: top and bottom five with figures; every unit in "show working".
4. The budget link: this year's agriculture, irrigation, erosion and environment lines for the LGA from the
   structured core (neutral, no verdicts).
Planner answers show the values (a farmer's answer does not).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date

from app.place import fit as fitting
from app.place.area import STATE

log = logging.getLogger(__name__)

MEASURES = {
    "greenness": {"measure": "modis_peak", "first": 2001, "pct": False, "fmt": "{:.2f}",
                  "en": "peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October "
                        "composites)", "ha": "koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na "
                                            "hotunan Yuni–Oktoba)",
                  "high_en": "greenest", "low_en": "least green", "high_ha": "mafi koriya", "low_ha": "mafi ƙarancin koriya"},
    "flood": {"measure": "s1_flood_share", "first": 2017, "pct": True, "fmt": "{:.1%}",
              "en": "share of normally dry cropland under water on at least one August–October radar pass "
                    "(Sentinel-1, 200 m: a cell counts only when most of its 4 ha is open water)",
              "ha": "kashin gonakin da a kullum suka bushe da ruwa ya rufe a aƙalla hoton radar ɗaya na Agusta–Oktoba "
                    "(Sentinel-1, mita 200: sel ɗaya tana ƙidaya ne kawai idan mafi yawan hekta 4 nata ruwa ne a fili)",
              "high_en": "most flooded", "low_en": "least flooded", "high_ha": "mafi ambaliya", "low_ha": "mafi ƙarancin ambaliya"},
    "flood_map": {"measure": "unosat_share", "first": 2022, "pct": True, "fmt": "{:.0%}",
                  "en": "share of cropland inside the UN satellite flood map (UNOSAT, VIIRS 375 m)",
                  "ha": "kashin gonakin da ke cikin taswirar ambaliya ta tauraron ɗan adam ta MDD (UNOSAT, mita 375)",
                  "high_en": "most inside the flood map", "low_en": "least inside", "high_ha": "mafi yawa a cikin taswirar",
                  "low_ha": "mafi ƙaranci"},
    "water": {"measure": "jrc_recurrence_share", "first": 0, "pct": True, "fmt": "{:.0%}",
              "en": "share of cropland with water in half the years 1984–2020 (JRC, 30 m)",
              "ha": "kashin gonakin da ruwa ya kasance a rabin shekarun 1984–2020 (JRC, mita 30)",
              "high_en": "most often under water", "low_en": "least", "high_ha": "mafi yawan ruwa", "low_ha": "mafi ƙaranci"},
    "bare": {"measure": "bsi_share", "first": 2017, "pct": True, "fmt": "{:.0%}",
             "en": "share of cropland reading as bare soil in the dry season (Sentinel-2 BSI, 200 m)",
             "ha": "kashin gonakin da suka nuna ƙasa mara ciyayi a rani (Sentinel-2 BSI, mita 200)",
             "high_en": "most bare", "low_en": "least bare", "high_ha": "mafi ƙasa mara ciyayi", "low_ha": "mafi ƙaranci"},
    "rain": {"measure": "rain_season_mm", "first": 2001, "pct": False, "fmt": "{:.0f} mm",
             "en": "June–October rain at the ward's centre (Open-Meteo archive, ~9 km grid)",
             "ha": "ruwan sama na Yuni–Oktoba a tsakiyar gunduma (Open-Meteo, raga ~kilomita 9)",
             "high_en": "wettest", "low_en": "driest", "high_ha": "mafi ruwa", "low_ha": "mafi bushewa"},
}
MEASURE_WORDS = [
    ("flood_map", re.compile(r"(?i)\b(?:un\s+(?:satellite\s+)?flood\s+map|unosat|flood\s+map|taswirar\s+ambaliya)\b")),
    ("water", re.compile(r"(?i)\b(?:jrc|(?:often|usually|regularly)\s+under\s+water|surface\s+water|standing\s+water|"
                         r"ponds?|wetland|fadama|ruwa(?:n)?\s+(?:fili|tafki)|ruwa\s+ke\s+yawan|yawan\s+ruwa|tafk\w*)\b")),
    ("flood", re.compile(r"(?i)\b(?:flood\w*|under\s+water|inundat\w*|ambaliya\w*|ruwa\s+ya\s+rufe)\b")),
    ("bare", re.compile(r"(?i)\b(?:bare\s+soil|bare\b|erosion|sand|degrad\w*|ƙasa\s+mara\s+ciyayi|kasa\s+mara\s+ciyayi|hamada|zaizay\w*)\b")),
    ("greenness", re.compile(r"(?i)\b(?:green\w*|vegetat\w*|crop\s+(?:cover|growth)|ndvi|koriya\w*|ciyayi|shuke-?shuke)\b")),
    ("rain", re.compile(r"(?i)\b(?:rain(?:fall)?|ruwan\s+sama|damina)\b")),
]
AREA_WORDS = re.compile(r"(?i)\b(?:wards?|lgas?|local\s+government\w*|across|which\s+(?:wards?|lgas?|areas?|parts?)|"
                        r"state-?wide|the\s+state|sokoto\s+state|all\s+(?:wards|lgas)|gundum\w*|ƙaramar\s+hukuma\w*|"
                        r"karamar\s+hukuma\w*|ƙananan\s+hukumomi|kananan\s+hukumomi|jihar?\s+sokoto|fa[ɗd]in\s+jiha\w*|"
                        r"wa[ɗd]anne\b)\b")
MINE = re.compile(r"(?i)\b(?:my\s+(?:farm|plot|land|field)|gonata|gona\s+ta|filina|wannan\s+wuri|this\s+spot|here)\b")
TOP_N = 5


@dataclass
class AreaAnswer:
    text: str
    found: bool
    working: str = ""
    partial: bool = False
    specs: list[dict] = field(default_factory=list)
    level: str = ""              # the units compared: ward | lga
    unit: str = ""               # the LGA pcode, or NG034 for the state
    measure: str = ""
    year: int = 0


W = {
    "en": {
        "head": "*{label}: {area}, {year}*",
        "head_noyear": "*{label}: {area}*",
        "area_lga": "wards of {lga} LGA", "area_state": "the 23 LGAs of Sokoto State", "area_state_wards": "the 244 wards of Sokoto State",
        "summary": "Across {area}, the {year} {short} ranged from {lo} ({lo_unit}) to {hi} ({hi_unit}); the median was "
                   "{med}. {high_word}: {top}. {low_word}: {bottom}.",
        "summary_noyear": "Across {area}, the {short} ranges from {lo} ({lo_unit}) to {hi} ({hi_unit}); the median is "
                          "{med}. {high_word}: {top}. {low_word}: {bottom}.",
        "short": {"greenness": "peak greenness", "flood": "flooded share of normally dry cropland",
                  "flood_map": "share of cropland inside the UN flood map", "water": "share of cropland often under water",
                  "bare": "bare-soil share of cropland", "rain": "June–October rain"},
        "rain_adj": "Against each ward's own years and that season's rain: {parts}.",
        "rain_below": "{units} were less green than the rain would suggest",
        "rain_above": "{units} were greener than usual for the rain",
        "rain_adj_none": "no ward stood out against its own years and the rain",
        "rain_adj_units": "{n} wards had too few years for a rain comparison",
        "low_data": "Low data: {units} ({n} or fewer observations that year) are marked ~ and not ranked.",
        "resolution": "Period {period}; resolution {res}. Cropland only (ESA WorldCover 2021).",
        "ranking_head": "*Ranking ({n} {what})*",
        "top_head": "Highest:", "bottom_head": "Lowest:",
        "row": "{i}. {name}: {value} ({n} obs)",
        "working_head": "All {what}, {measure}, {year}: value (observations behind it; ~ low data; rain flag where fitted).",
        "working_row": "{name} [{code}]: {value} ({n}){flag}",
        "flag_below": " below-rain", "flag_above": " above-rain",
        "budget_head": "*{year} budget lines for {lga} LGA (agriculture, irrigation, erosion, environment)*",
        "budget_row": "• {name}: ₦{amount} ({title}, p. {page})",
        "budget_none": "No {year} budget line for {lga} LGA matches agriculture, irrigation, erosion or environment.",
        "budget_state": "Budget lines are linked per LGA: ask about one LGA to see its lines.",
        "none": "No precomputed satellite measures are loaded for {area} yet.",
        "no_year": "No {short} is available for {year}; the years loaded run {first}–{last}.",
        "sources": "Sources: {source}; boundaries GRID3 wards and OCHA COD-AB LGAs.",
        "neutral": "Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.",
        "and": " and ", "ward": "ward", "wards": "wards", "lga": "LGA", "lgas": "LGAs",
    },
    "ha": {
        "head": "*{label}: {area}, {year}*",
        "head_noyear": "*{label}: {area}*",
        "area_lga": "gundumomin Ƙaramar Hukumar {lga}", "area_state": "ƙananan hukumomi 23 na Jihar Sokoto",
        "area_state_wards": "gundumomi 244 na Jihar Sokoto",
        "summary": "A {area}, {short} na {year} ya tashi daga {lo} ({lo_unit}) zuwa {hi} ({hi_unit}); matsakaici {med}. "
                   "{high_word}: {top}. {low_word}: {bottom}.",
        "summary_noyear": "A {area}, {short} ya tashi daga {lo} ({lo_unit}) zuwa {hi} ({hi_unit}); matsakaici {med}. "
                          "{high_word}: {top}. {low_word}: {bottom}.",
        "short": {"greenness": "koriyar ƙololuwa", "flood": "kashin gonakin da ambaliya ta rufe",
                  "flood_map": "kashin gonaki a cikin taswirar ambaliya ta MDD", "water": "kashin gonakin da ruwa ke yawan rufewa",
                  "bare": "kashin ƙasa mara ciyayi a gonaki", "rain": "ruwan sama na Yuni–Oktoba"},
        "rain_adj": "Idan aka kwatanta kowace gunduma da shekarunta da ruwan saman daminar: {parts}.",
        "rain_below": "{units} sun yi ƙasa da abin da ruwan saman ya nuna",
        "rain_above": "{units} sun fi koriya fiye da yadda ruwan saman ya nuna",
        "rain_adj_none": "babu gundumar da ta bambanta da shekarunta da ruwan sama",
        "rain_adj_units": "gundumomi {n} ba su da isassun shekaru don kwatancen ruwan sama",
        "low_data": "Ƙarancin bayanai: {units} (lura {n} ko ƙasa a shekarar) an yi musu alamar ~ kuma ba a jera su ba.",
        "resolution": "Lokaci {period}; ƙuduri {res}. Gonaki kawai (ESA WorldCover 2021).",
        "ranking_head": "*Jeri ({n} {what})*",
        "top_head": "Mafi girma:", "bottom_head": "Mafi ƙanƙanta:",
        "row": "{i}. {name}: {value} (lura {n})",
        "working_head": "Dukkan {what}, {measure}, {year}: ƙima (lura a bayanta; ~ ƙarancin bayanai; alamar ruwan sama inda aka kwatanta).",
        "working_row": "{name} [{code}]: {value} ({n}){flag}",
        "flag_below": " ƙasa-da-ruwan-sama", "flag_above": " sama-da-ruwan-sama",
        "budget_head": "*Layukan kasafin {year} na Ƙaramar Hukumar {lga} (noma, ban ruwa, zaizayar ƙasa, muhalli)*",
        "budget_row": "• {name}: ₦{amount} ({title}, shafi na {page})",
        "budget_none": "Babu layin kasafin {year} na Ƙaramar Hukumar {lga} da ya shafi noma, ban ruwa, zaizayar ƙasa ko muhalli.",
        "budget_state": "Ana haɗa layukan kasafi ne a kowace ƙaramar hukuma: tambaya game da ƙaramar hukuma ɗaya don ganin nata.",
        "none": "Ba a riga an ɗora ma'aunan tauraron ɗan adam na {area} ba.",
        "no_year": "Babu {short} na {year}; shekarun da aka ɗora {first}–{last}.",
        "sources": "Madogara: {source}; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.",
        "neutral": "Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.",
        "and": " da ", "ward": "gunduma", "wards": "gundumomi", "lga": "ƙaramar hukuma", "lgas": "ƙananan hukumomi",
    },
}
BUDGET_TERMS = ["agric", "irrigat", "erosion", "environment", "fadama", "farm", "flood", "gully", "dam ", "dams", "forest"]


def _t(lang: str) -> dict:
    return W["ha" if lang == "ha" else "en"]


# --- the route ------------------------------------------------------------------------------------------------------

def area_route(question: str, english: str = "") -> tuple[str, str] | None:
    """(level, unit) when a place-history question is about an area, not the user's pin: ('lga', pcode) for an
    LGA named, ('state', NG034) for the state or 'which wards/LGAs'; None otherwise."""
    from app.hazards.advisories import lgas_in
    from app.place.answer import NOT_PLACE, place_route
    text = f"{question} {english}"
    if MINE.search(text) or NOT_PLACE.search(text):
        return None
    measure = measure_asked(text)
    lgas = lgas_in(text)
    if not (AREA_WORDS.search(text) or lgas):
        return None
    if not (place_route(text) or measure in ("flood", "flood_map", "bare", "water", "greenness", "rain") and
            (AREA_WORDS.search(text) or lgas) and re.search(r"(?i)\b(?:wards?|lgas?|gundum|hukum|which|wa[ɗd]anne|"
                                                              r"most|least|mafi|share|kashi)\b", text)):
        return None
    if lgas and not re.search(r"(?i)\b(?:all\s+lgas|which\s+lgas|the\s+state|state-?wide|sokoto\s+state|"
                              r"ƙananan\s+hukumomi|kananan\s+hukumomi|jihar?\s+sokoto)\b", text):
        return ("lga", lgas[0])
    return ("state", STATE)


def measure_asked(text: str) -> str:
    for key, pat in MEASURE_WORDS:
        if pat.search(text):
            return key
    return "greenness"


def year_asked(text: str, today: date) -> int | None:
    m = re.findall(r"\b((?:19|20)\d\d)\b", text)
    return int(m[0]) if m else None


# --- the data ---------------------------------------------------------------------------------------------------------

def rows_for(conn, measure: str, level: str, year: int, within: str | None) -> list[tuple[str, str, float | None, int | None]]:
    """(unit code, name, value, n_obs) for every unit of the level (wards of an LGA when `within`)."""
    if level == "ward":
        q = ("SELECT h.unit, w.name, h.value, h.n_obs FROM ward_history h JOIN ward w ON w.wardcode = h.unit WHERE "
             "h.level = 'ward' AND h.measure = %s AND h.year = %s" + (" AND w.lga_pcode = %s" if within else "") +
             " ORDER BY w.name")
        args = (measure, year, within) if within else (measure, year)
    else:
        q = ("SELECT h.unit, l.name, h.value, h.n_obs FROM ward_history h JOIN lga l ON l.pcode = h.unit WHERE "
             "h.level = 'lga' AND h.measure = %s AND h.year = %s ORDER BY l.name")
        args = (measure, year)
    return [(r[0], r[1], None if r[2] is None else float(r[2]), r[3]) for r in conn.execute(q, args).fetchall()]


def years_loaded(conn, measure: str, level: str) -> list[int]:
    return [r[0] for r in conn.execute("SELECT DISTINCT year FROM ward_history WHERE measure = %s AND level = %s "
                                       "AND value IS NOT NULL ORDER BY year", (measure, level)).fetchall()]


def series(conn, measure: str, level: str, unit: str) -> dict[int, float]:
    """A unit's yearly values, without its low-data years (under 60% of its own median observation count:
    MODIS 2025 has 5 composites against a usual 16–20, so it never enters a rain fit or a trend)."""
    rows = conn.execute(
        "SELECT year, value, n_obs FROM ward_history WHERE measure = %s AND level = %s AND unit = %s AND value IS NOT "
        "NULL AND year > 0 ORDER BY year", (measure, level, unit)).fetchall()
    return drop_low_data({r[0]: (float(r[1]), r[2]) for r in rows})


def drop_low_data(rows: dict[int, tuple[float, int | None]]) -> dict[int, float]:
    import math
    counts = sorted(n for _, n in rows.values() if n is not None)
    if not counts:
        return {y: v for y, (v, _) in rows.items()}
    need = max(2, math.ceil(0.6 * counts[len(counts) // 2]))
    return {y: v for y, (v, n) in rows.items() if n is None or n >= need}


def rain_flags(conn, level: str, units: list[str], year: int) -> dict[str, str]:
    """Per unit: 'below' | 'above' | 'normal' | '' from a rain fit of its own MODIS peaks against its rain."""
    out = {}
    for u in units:
        peaks, rains = series(conn, "modis_peak", level, u), series(conn, "rain_season_mm", level, u)
        pts = {y: (peaks[y], rains[y]) for y in peaks if y in rains}
        f = fitting.rain_fit(pts)
        if f is None or year not in f.flags:
            out[u] = ""
            continue
        r = f.residuals[year]
        out[u] = "below" if f.flags[year] == "below" else ("above" if f.sd > 1e-6 and r > f.sd else "normal")
    return out


def low_data_cut(rows: list[tuple], measure: str) -> int:
    """Units with n_obs at or under this are marked low-data: under 60% of the median count, as for a pin."""
    import math
    counts = sorted(n for _, _, v, n in rows if n is not None and v is not None)
    if not counts or measure in ("jrc_recurrence_share", "unosat_share", "rain_season_mm"):
        return -1
    med = counts[len(counts) // 2]
    return max(2, math.ceil(0.6 * med)) - 1


# --- the answer ---------------------------------------------------------------------------------------------------------

def _fmt(spec: dict, v: float | None) -> str:
    return "–" if v is None else spec["fmt"].format(v)


def _names(items: list[tuple[str, str, float | None, int | None]], spec: dict, lang: str) -> str:
    return ", ".join(f"{name} ({_fmt(spec, v)})" for _, name, v, _ in items)


def area_answer(conn, question: str, english: str, lang: str, level: str, unit: str, today: date,
                measure_key: str | None = None, year: int | None = None) -> AreaAnswer:
    from app.sources.lga_names import name_of
    t = _t(lang)
    text = f"{question} {english}"
    key = measure_key or measure_asked(text)
    spec = MEASURES[key]
    measure = spec["measure"]
    compare = "ward" if level == "lga" else ("ward" if re.search(r"(?i)\bwards?\b|gundum", text) and level == "state" else "lga")
    within = unit if level == "lga" else None
    area = (t["area_lga"].format(lga=name_of(unit)) if level == "lga" else
            t["area_state_wards"] if compare == "ward" else t["area_state"])
    loaded = years_loaded(conn, measure, compare)
    if not loaded:
        return AreaAnswer(t["none"].format(area=area), False, level=compare, unit=unit, measure=measure)
    want = year if year is not None else year_asked(text, today)
    if spec["first"] == 0:
        y = 0
    elif want is not None and want in loaded:
        y = want
    elif want is not None:
        return AreaAnswer(t["no_year"].format(short=t["short"][key], year=want, first=loaded[0], last=loaded[-1]), False,
                          level=compare, unit=unit, measure=measure)
    else:
        y = max(x for x in loaded if x < today.year) if any(x < today.year for x in loaded) else loaded[-1]
    rows = rows_for(conn, measure, compare, y, within)
    if not rows or all(v is None for _, _, v, _ in rows):
        return AreaAnswer(t["none"].format(area=area), False, level=compare, unit=unit, measure=measure, year=y)
    cut = low_data_cut(rows, measure)
    ranked = sorted([r for r in rows if r[2] is not None and (r[3] is None or r[3] > cut)], key=lambda r: -r[2])
    low = [r for r in rows if r[2] is not None and r[3] is not None and r[3] <= cut]
    missing = [r for r in rows if r[2] is None]
    values = [r[2] for r in ranked]
    med = sorted(values)[len(values) // 2] if values else None
    what = t["wards"] if compare == "ward" else t["lgas"]
    head = (t["head"] if y else t["head_noyear"]).format(label=spec[lang if lang == "ha" else "en"], area=area, year=y)
    lines = [head]
    if ranked:
        top, bottom = ranked[:3], ranked[-3:][::-1] if len(ranked) > 3 else []
        lines.append((t["summary"] if y else t["summary_noyear"]).format(
            area=area, year=y, short=t["short"][key], lo=_fmt(spec, ranked[-1][2]), lo_unit=ranked[-1][1],
            hi=_fmt(spec, ranked[0][2]), hi_unit=ranked[0][1], med=_fmt(spec, med),
            high_word=spec[f"high_{'ha' if lang == 'ha' else 'en'}"].capitalize(), top=_names(top, spec, lang),
            low_word=spec[f"low_{'ha' if lang == 'ha' else 'en'}"].capitalize(), bottom=_names(bottom, spec, lang) or "–"))
    flags: dict[str, str] = {}
    if key == "greenness" and y:
        flags = rain_flags(conn, compare, [r[0] for r in ranked], y)
        names = {r[0]: r[1] for r in ranked}
        below = [names[u] for u, f in flags.items() if f == "below"]
        above = [names[u] for u, f in flags.items() if f == "above"]
        unfit = sum(1 for f in flags.values() if f == "")
        parts = []
        if below:
            parts.append(t["rain_below"].format(units=", ".join(below)))
        if above:
            parts.append(t["rain_above"].format(units=", ".join(above)))
        if not parts:
            parts.append(t["rain_adj_none"])
        if unfit:
            parts.append(t["rain_adj_units"].format(n=unfit))
        s = t["rain_adj"].format(parts="; ".join(parts))
        lines.append(s[0].upper() + s[1:])
    if low:
        lines.append(t["low_data"].format(units=", ".join(r[1] for r in low[:6]) + (" …" if len(low) > 6 else ""),
                                          n=cut))
    period = f"{loaded[0]}–{loaded[-1]}" if spec["first"] else "1984–2020"      # the years actually loaded
    res = {"greenness": "250 m", "flood": "200 m", "flood_map": "375 m", "water": "30 m", "bare": "200 m", "rain": "~9 km"}[key]
    lines.append(t["resolution"].format(period=period, res=res))
    # the ranking
    rank_lines = [t["ranking_head"].format(n=len(ranked), what=what), t["top_head"]]
    rank_lines += [t["row"].format(i=i, name=r[1], value=_fmt(spec, r[2]), n=r[3] if r[3] is not None else "–")
                   for i, r in enumerate(ranked[:TOP_N], 1)]
    if len(ranked) > TOP_N:
        rank_lines.append(t["bottom_head"])
        rank_lines += [t["row"].format(i=len(ranked) - j, name=r[1], value=_fmt(spec, r[2]), n=r[3] if r[3] is not None else "–")
                       for j, r in enumerate(reversed(ranked[-TOP_N:]))][::-1]
    lines.append("\n".join(rank_lines))
    # the budget link
    lines.append(budget_block(conn, lang, level, unit, today))
    lines.append(t["neutral"])
    source = conn.execute("SELECT source FROM ward_history WHERE measure = %s LIMIT 1", (measure,)).fetchone()[0]
    lines.append(t["sources"].format(source=source))
    # show working: every unit
    working = [t["working_head"].format(what=what, measure=measure, year=y or period)]
    for code, name, v, n in sorted(rows, key=lambda r: (r[2] is None, -(r[2] or 0))):
        flag = {"below": t["flag_below"], "above": t["flag_above"]}.get(flags.get(code, ""), "")
        lowmark = "~" if (n is not None and n <= cut and v is not None) else ""
        working.append(t["working_row"].format(name=name, code=code, value=lowmark + _fmt(spec, v), n=n if n is not None else "–",
                                               flag=flag))
    if missing:
        working.append(f"({len(missing)} {what}: no value)")
    specs = [{"kind": "area_map", "measure": measure, "key": key, "year": y, "level": compare, "unit": unit}]
    return AreaAnswer("\n\n".join(x for x in lines if x), True, "\n".join(working), partial=bool(missing), specs=specs,
                      level=compare, unit=unit, measure=measure, year=y)


def budget_block(conn, lang: str, level: str, unit: str, today: date) -> str:
    from app.agent.analysis import lga_projects
    from app.sources.lga_names import name_of
    t = _t(lang)
    if level != "lga":
        return t["budget_state"]
    lga = name_of(unit)
    try:
        res = lga_projects(conn, {"lga": lga, "terms": BUDGET_TERMS})
    except Exception as e:                      # noqa: BLE001 - the link is extra
        log.warning("place: budget link failed: %s", type(e).__name__)
        return ""
    if res is None or not res.found or not res.rows:
        return t["budget_none"].format(year=getattr(res, "year", today.year) or today.year, lga=lga)
    rows = [t["budget_row"].format(name=r.name, amount=f"{r.amount:,.0f}", title=res.titles.get(r.doc_id, r.doc_id), page=r.page)
            for r in res.rows[:6]]
    return t["budget_head"].format(year=res.year, lga=res.subject) + "\n" + "\n".join(rows)
