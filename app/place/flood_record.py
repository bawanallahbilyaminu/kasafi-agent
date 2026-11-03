"""Flood answers for a ward, an LGA or the state over the whole record, written in code (docs/place-history.md §16).

Sources, in this order:
1. Copernicus GFM (app/place/gfm.py), 2015→: the seasons with floodwater seen, the largest (its biggest single pass
   and the land under water at some point that season), and where: farmland, the river floodplain, other land.
2. UNOSAT's event maps (2022, 2024): quoted next to the radar figure with the reason they differ, never averaged.
3. GFM's exclusion mask: the share of the area radar can't judge, said every time.
4. JRC Global Surface Water 1984–2020: the floodplain, land the river covers in some years.
5. Kasafi's own Sentinel-1 radar (s1_flood_share): the check.
The flood season is a radar measure: the MODIS season rule (planner.headline_year) never applies to it.
"""

from __future__ import annotations

from datetime import date

from app.place.area import STATE

MIN_HA = 2.0                  # under this, a season counts as no floodwater seen (half a 200 m cell)
CHECK_SHARE = 0.005           # our radar: a season counts when over 0.5% of normally dry farmland
SEASON_END = (10, 31)         # a season's floods are in by the end of October (the passes run to November)
MEASURES = ("gfm_union_ha", "gfm_max_ha", "gfm_max_doy", "gfm_crop_ha", "gfm_plain_ha", "gfm_excluded_share",
            "unosat_ha", "s1_flood_share")

T = {
    "en": {
        "head_ward": "*Flooding: {ward} ward{likely}, {lga} LGA* — experimental",
        "head_area": "*Flooding: {area}* — experimental",
        "scope": "Your pin is in {ward} ward{likely} of {lga} LGA, so this answer is about that ward.",
        "none": "No floodwater was seen in {name} on any satellite radar pass in the rainy seasons {first}–{last} "
                "(Copernicus GFM: {n} seasons, {p} passes).",
        "some": "Satellite radar saw floodwater in {name} in {k} of the {n} rainy seasons {first}–{last}: {years}. "
                "The largest was in {big}: about {max} on its biggest pass ({day}), and {union} under water at some "
                "point that season ({where}).",
        "some_one": "Satellite radar saw floodwater in {name} in 1 of the {n} rainy seasons {first}–{last}: {big}, "
                    "about {max} on its biggest pass ({day}) and {union} under water at some point ({where}).",
        "year_none": "No floodwater was seen on {name}'s land in {year} on any of its {p} radar passes.",
        "year_some": "In {year}, radar saw about {max} of {name} under water on its biggest pass ({day}), and {union} "
                     "at some point in the season ({where}).",
        "year_missing": "No radar season is on file for {year}; the record runs {first}–{last}.",
        "so_far": " ({year} so far)",
        "where_crop": "{ha} on farmland", "where_plain": "{ha} in the river floodplain", "where_other": "{ha} on other land",
        "compare": "In {year}, radar passes saw {g}; UNOSAT's event map of {period}, built from several days and "
                   "sensors, shows {u}. They measure differently; the larger is closer to what people experienced.",
        "g_none": "no floodwater", "g_some": "{ha} under water at some point", "g_nodata": "nothing (no passes on file)",
        "excluded": "Radar can't judge {pct} of {name} (about {ha}: built-up land, dense trees and dry sandy ground, "
                    "where radar can't tell water from land), so floods there aren't counted. It can't see water "
                    "between buildings: for built-up parts, flood reports are the source.",
        "plain_some": "The river floodplain: water covered {plain} of {name} in some years between 1984 and 2020, and "
                      "{often} in half the years or more (JRC Global Surface Water). Water there is partly the river's "
                      "normal rise.",
        "plain_none": "No part of {name} was under water in any year from 1984 to 2020 in JRC's long-term water record.",
        "check_agree": "Kasafi's own radar check (Sentinel-1, {first}–{last}) agrees: no season with floodwater on "
                       "more than 0.5% of normally dry farmland.",
        "check_some": "Kasafi's own radar check (Sentinel-1, normally dry farmland only) found floodwater in {years}; "
                      "the most in {y} ({pct} of that farmland).",
        "lga_context": "{lga} LGA as a whole: floodwater in {k} of {n} seasons; the largest in {y} ({union} under "
                       "water at some point).",
        "lga_context_none": "{lga} LGA as a whole: no floodwater seen in {n} seasons.",
        "map_note": "The map shows each {unit}'s share of land under water at some point in {year}.",
        "unit": {"ward": "ward", "lga": "LGA"},
        "neutral": "Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work. "
                   "This is information only, not an official flood warning.",
        "sources": "Sources: Copernicus Global Flood Monitoring ({attribution}); UNOSAT satellite-detected water "
                   "extents (HDX); JRC Global Surface Water; Copernicus Sentinel-1 RTC (Kasafi's check); boundaries "
                   "GRID3 wards and OCHA COD-AB LGAs.",
        "working": "Per season ({unit}): passes, land under water at some point, biggest pass, farmland / floodplain, "
                   "share radar can't judge, UNOSAT, Kasafi's radar check on normally dry farmland.",
        "working_row": "{y}: {p} passes; {union}; biggest {max}{day}; {crop} / {plain}; excluded {ex}; UNOSAT {u}; "
                       "check {s1}",
        "ha": "{v} ha", "and": " and ", "state": "Sokoto State", "lga": "{lga} LGA",
        "area_lga": "{lga} LGA", "area_state": "Sokoto State",
    },
    "ha": {
        "head_ward": "*Ambaliya: gundumar {ward}{likely}, Ƙaramar Hukumar {lga}* — na gwaji",
        "head_area": "*Ambaliya: {area}* — na gwaji",
        "scope": "Wurinku yana gundumar {ward}{likely} ta Ƙaramar Hukumar {lga}, saboda haka wannan amsa ta wannan gunduma ce.",
        "none": "Ba a ga ruwan ambaliya a {name} ba a kowane hoton radar na tauraron ɗan adam a daminun {first}–{last} "
                "(Copernicus GFM: damina {n}, hotuna {p}).",
        "some": "Radar ta tauraron ɗan adam ta ga ruwan ambaliya a {name} a damina {k} cikin {n} na {first}–{last}: "
                "{years}. Mafi girma ita ce ta {big}: kusan {max} a hotonta mafi girma ({day}), kuma {union} ya kasance "
                "ƙarƙashin ruwa a wani lokaci a daminar ({where}).",
        "some_one": "Radar ta tauraron ɗan adam ta ga ruwan ambaliya a {name} a damina 1 cikin {n} na {first}–{last}: "
                    "{big}, kusan {max} a hotonta mafi girma ({day}), da {union} ƙarƙashin ruwa a wani lokaci ({where}).",
        "year_none": "Ba a ga ruwan ambaliya a ƙasar {name} ba a {year} a ɗaya daga cikin hotunan radar {p}.",
        "year_some": "A {year}, radar ta ga kusan {max} na {name} ƙarƙashin ruwa a hotonta mafi girma ({day}), da {union} "
                     "a wani lokaci a daminar ({where}).",
        "year_missing": "Babu daminar radar ta {year} a cikin bayanai; tarihin ya kama daga {first} zuwa {last}.",
        "so_far": " ({year} har zuwa yanzu)",
        "where_crop": "{ha} a gonaki", "where_plain": "{ha} a fadamar kogi", "where_other": "{ha} a sauran ƙasa",
        "compare": "A {year}, hotunan radar sun ga {g}; taswirar UNOSAT ta {period}, wadda aka haɗa daga kwanaki da "
                   "na'urori da dama, ta nuna {u}. Suna aunawa ta hanyoyi daban-daban; mafi girma ya fi kusa da abin da "
                   "mutane suka fuskanta.",
        "g_none": "babu ruwan ambaliya", "g_some": "{ha} ƙarƙashin ruwa a wani lokaci",
        "g_nodata": "babu komai (babu hotunan radar a bayanai)",
        "excluded": "Radar ba za ta iya tantance kashi {pct} na {name} ba (kusan {ha}: wuraren gine-gine, bishiyoyi "
                    "masu yawa da busasshiyar ƙasa mai yashi, inda radar ba ta bambance ruwa da ƙasa), saboda haka ba a "
                    "ƙidaya ambaliya a can. Ba ta ganin ruwa tsakanin gine-gine: ga wuraren gine-gine, rahotannin "
                    "ambaliya ne madogara.",
        "plain_some": "Fadamar kogi: ruwa ya rufe {plain} na {name} a wasu shekaru tsakanin 1984 da 2020, da {often} a "
                      "rabin shekarun ko fiye (JRC Global Surface Water). Ruwa a can wani ɓangare ne na hawan kogin da "
                      "aka saba.",
        "plain_none": "Babu wani ɓangare na {name} da ruwa ya rufe a kowace shekara daga 1984 zuwa 2020 a tarihin ruwa "
                      "na JRC.",
        "check_agree": "Binciken radar na Kasafi (Sentinel-1, {first}–{last}) ya yarda: babu daminar da ruwan ambaliya "
                       "ya rufe fiye da kashi 0.5% na gonakin da a kullum suke bushe.",
        "check_some": "Binciken radar na Kasafi (Sentinel-1, gonakin da a kullum suke bushe kawai) ya ga ruwan ambaliya "
                      "a {years}; mafi yawa a {y} (kashi {pct} na gonakin).",
        "lga_context": "Ƙaramar Hukumar {lga} gaba ɗaya: an ga ruwan ambaliya a damina {k} cikin {n}; mafi girma a {y} "
                       "({union} ƙarƙashin ruwa a wani lokaci).",
        "lga_context_none": "Ƙaramar Hukumar {lga} gaba ɗaya: ba a ga ruwan ambaliya ba a damina {n}.",
        "map_note": "Taswirar tana nuna kashin ƙasar kowace {unit} da ruwa ya rufe a wani lokaci a {year}.",
        "unit": {"ward": "gunduma", "lga": "ƙaramar hukuma"},
        "neutral": "Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai "
                   "ko aikin kowa. Wannan bayani ne kawai, ba gargaɗin ambaliya na hukuma ba.",
        "sources": "Madogara: Copernicus Global Flood Monitoring ({attribution}); taswirorin ruwa na UNOSAT (HDX); JRC "
                   "Global Surface Water; Copernicus Sentinel-1 RTC (binciken Kasafi); iyakoki: gundumomin GRID3 da "
                   "ƙananan hukumomin OCHA COD-AB.",
        "working": "Kowace damina ({unit}): hotuna, ƙasar da ruwa ya rufe a wani lokaci, hoto mafi girma, gonaki / "
                   "fadama, kashin da radar ba ta iya tantancewa, UNOSAT, binciken radar na Kasafi.",
        "working_row": "{y}: hotuna {p}; {union}; mafi girma {max}{day}; {crop} / {plain}; ba a tantance ba {ex}; "
                       "UNOSAT {u}; bincike {s1}",
        "ha": "hekta {v}", "and": " da ", "state": "Jihar Sokoto", "lga": "Ƙaramar Hukumar {lga}",
        "area_lga": "Ƙaramar Hukumar {lga}", "area_state": "Jihar Sokoto",
    },
}


def _t(lang: str) -> dict:
    return T["ha" if lang == "ha" else "en"]


def ha_text(v: float | None, lang: str) -> str:
    v = float(v or 0.0)
    n = round(v, -1) if v >= 100 else round(v)
    return _t(lang)["ha"].format(v=f"{n:,.0f}")


def loaded(conn) -> bool:
    return conn.execute("SELECT 1 FROM ward_history WHERE measure = 'gfm_union_ha' AND value IS NOT NULL LIMIT 1"
                        ).fetchone() is not None


def record(conn, level: str, unit: str) -> dict[int, dict[str, tuple[float | None, int | None]]]:
    """year -> {measure: (value, n_obs)} for the flood measures; only seasons with radar passes."""
    out: dict[int, dict] = {}
    for m, y, v, n in conn.execute("SELECT measure, year, value, n_obs FROM ward_history WHERE level = %s AND unit = %s "
                                   "AND year > 0 AND measure = ANY(%s)", (level, unit, list(MEASURES))).fetchall():
        out.setdefault(int(y), {})[m] = (None if v is None else float(v), n)
    return dict(sorted(out.items()))


def static(conn, level: str, unit: str) -> dict[str, float]:
    return {m: float(v) for m, v in conn.execute(
        "SELECT measure, value FROM ward_history WHERE level = %s AND unit = %s AND year = 0 AND measure = ANY(%s) AND "
        "value IS NOT NULL", (level, unit, ["land_ha", "jrc_plain_ha", "jrc_often_ha"])).fetchall()}


def _v(r: dict, m: str) -> float:
    return float((r.get(m) or (None, None))[0] or 0.0)


def seasons(rec: dict) -> list[int]:
    return [y for y, r in rec.items() if (r.get("gfm_union_ha", (None, 0))[1] or 0) > 0 and r["gfm_union_ha"][0] is not None]


def flooded(rec: dict) -> list[int]:
    return [y for y in seasons(rec) if _v(rec[y], "gfm_union_ha") >= MIN_HA]


def complete(year: int, today: date) -> bool:
    return date(year, *SEASON_END) < today


def where_text(r: dict, lang: str) -> str:
    t = _t(lang)
    union, crop, plain = _v(r, "gfm_union_ha"), _v(r, "gfm_crop_ha"), _v(r, "gfm_plain_ha")
    other = max(0.0, union - crop - plain)
    parts = [t[k].format(ha=ha_text(v, lang)) for k, v in (("where_crop", crop), ("where_plain", plain),
                                                            ("where_other", other)) if v >= MIN_HA / 2]
    return ", ".join(parts) or t["where_other"].format(ha=ha_text(union, lang))


def day_text(r: dict, year: int, lang: str) -> str:
    from app.place.planner import doy_text
    doy = (r.get("gfm_max_doy") or (None, None))[0]
    return f"{doy_text(int(doy), year, lang)} {year}" if doy else str(year)


def record_line(rec: dict, name: str, lang: str, today: date) -> str:
    t = _t(lang)
    ys = seasons(rec)
    if not ys:
        return ""
    passes = sum(int(rec[y]["gfm_union_ha"][1] or 0) for y in ys)
    first, last_txt = ys[0], ys[-1]
    last = last_txt
    wet = flooded(rec)
    so_far = "" if complete(last, today) else t["so_far"].format(year=last)
    if not wet:
        return t["none"].format(name=name, first=first, last=last_txt, n=len(ys), p=passes) + so_far
    big = max(wet, key=lambda y: _v(rec[y], "gfm_union_ha"))
    r = rec[big]
    key = "some_one" if len(wet) == 1 else "some"
    return t[key].format(name=name, k=len(wet), n=len(ys), first=first, last=last_txt, years=", ".join(map(str, wet)),
                         big=big, max=ha_text(_v(r, "gfm_max_ha"), lang), day=day_text(r, big, lang),
                         union=ha_text(_v(r, "gfm_union_ha"), lang), where=where_text(r, lang)) + so_far


def year_line(rec: dict, name: str, year: int, lang: str) -> str:
    t = _t(lang)
    ys = seasons(rec)
    if year not in ys:
        return t["year_missing"].format(year=year, first=ys[0], last=ys[-1]) if ys else ""
    r = rec[year]
    if _v(r, "gfm_union_ha") < MIN_HA:
        return t["year_none"].format(name=name, year=year, p=int(r["gfm_union_ha"][1] or 0))
    return t["year_some"].format(year=year, name=name, max=ha_text(_v(r, "gfm_max_ha"), lang), day=day_text(r, year, lang),
                                 union=ha_text(_v(r, "gfm_union_ha"), lang), where=where_text(r, lang))


def compare_lines(rec: dict, lang: str, years: list[int] | None = None) -> list[str]:
    """Radar and UNOSAT side by side for the map years, with the reason they differ; never averaged."""
    from app.place.planner import map_period
    t = _t(lang)
    out = []
    for y in sorted(rec):
        if years is not None and y not in years:
            continue
        r = rec[y]
        if "unosat_ha" not in r or r["unosat_ha"][0] is None:
            continue
        u, g = _v(r, "unosat_ha"), _v(r, "gfm_union_ha")
        if u < MIN_HA and g < MIN_HA:
            continue
        if y not in seasons(rec):                    # no radar season on file: never 'radar saw no floodwater'
            gt = t["g_nodata"]
        else:
            gt = t["g_none"] if g < MIN_HA else t["g_some"].format(ha=ha_text(g, lang))
        ut = t["g_none"] if u < MIN_HA else ha_text(u, lang)
        out.append(t["compare"].format(year=y, g=gt, period=map_period(y, lang), u=ut))
    return out


def excluded_line(rec: dict, st: dict, name: str, lang: str) -> str:
    ys = seasons(rec)
    if not ys:
        return ""
    share = _v(rec[ys[-1]], "gfm_excluded_share")
    if share < 0.01:
        return ""
    land = st.get("land_ha", 0.0)
    return _t(lang)["excluded"].format(pct=f"{share:.0%}", name=name, ha=ha_text(share * land, lang))


def plain_line(st: dict, name: str, lang: str) -> str:
    t = _t(lang)
    plain, often = st.get("jrc_plain_ha"), st.get("jrc_often_ha", 0.0)
    if plain is None:
        return ""
    if plain < MIN_HA:
        return t["plain_none"].format(name=name)
    return t["plain_some"].format(plain=ha_text(plain, lang), name=name, often=ha_text(often, lang))


def check_line(rec: dict, lang: str) -> str:
    t = _t(lang)
    s1 = {y: r["s1_flood_share"][0] for y, r in rec.items() if r.get("s1_flood_share") and r["s1_flood_share"][0] is not None}
    if not s1:
        return ""
    wet = [y for y, v in s1.items() if v > CHECK_SHARE]
    if not wet:
        return t["check_agree"].format(first=min(s1), last=max(s1))
    y = max(wet, key=lambda k: s1[k])
    return t["check_some"].format(years=", ".join(map(str, wet)), y=y, pct=f"{s1[y]:.1%}")


def context_line(conn, lga_pcode: str, lga: str, lang: str) -> str:
    t = _t(lang)
    rec = record(conn, "lga", lga_pcode)
    ys, wet = seasons(rec), flooded(rec)
    if not ys:
        return ""
    if not wet:
        return t["lga_context_none"].format(lga=lga, n=len(ys))
    big = max(wet, key=lambda y: _v(rec[y], "gfm_union_ha"))
    return t["lga_context"].format(lga=lga, k=len(wet), n=len(ys), y=big, union=ha_text(_v(rec[big], "gfm_union_ha"), lang))


def working(rec: dict, unit_name: str, lang: str) -> list[str]:
    t = _t(lang)
    out = [t["working"].format(unit=unit_name)]
    for y, r in rec.items():
        if y not in seasons(rec) and (r.get("unosat_ha") or (None, None))[0] is None:
            continue
        doy = (r.get("gfm_max_doy") or (None, None))[0]
        s1 = (r.get("s1_flood_share") or (None, None))[0]
        u = (r.get("unosat_ha") or (None, None))[0]
        out.append(t["working_row"].format(
            y=y, p=int((r.get("gfm_union_ha") or (0, 0))[1] or 0), union=ha_text(_v(r, "gfm_union_ha"), lang),
            max=ha_text(_v(r, "gfm_max_ha"), lang), day=f" ({day_text(r, y, lang)})" if doy else "",
            crop=ha_text(_v(r, "gfm_crop_ha"), lang), plain=ha_text(_v(r, "gfm_plain_ha"), lang),
            ex=f"{_v(r, 'gfm_excluded_share'):.0%}", u="–" if u is None else ha_text(u, lang),
            s1="–" if s1 is None else f"{s1:.1%}"))
    return out


def map_year(rec: dict, year: int | None, today: date) -> int | None:
    """The map's year: the one asked, else the unit's largest flood season, else the latest complete season."""
    ys = seasons(rec)
    if year is not None:                 # a year asked: that year or nothing, never another year's ranking
        return year if year in ys else None
    wet = flooded(rec)
    if wet:
        return max(wet, key=lambda y: _v(rec[y], "gfm_union_ha"))
    done = [y for y in ys if complete(y, today)]
    return done[-1] if done else (ys[-1] if ys else None)


def attribution_years(rec: dict) -> list[int]:
    return seasons(rec)


def unit_lines(conn, rec: dict, st: dict, name: str, lang: str, today: date, year: int | None) -> list[str]:
    """The record (or the year asked), the radar/UNOSAT comparison, the share radar can't judge, the floodplain and
    our radar check, in that order."""
    lines = [year_line(rec, name, year, lang)] if year else []
    lines.append(record_line(rec, name, lang, today))
    lines += compare_lines(rec, lang, [year] if year else None)
    lines.append(excluded_line(rec, st, name, lang))
    lines.append(plain_line(st, name, lang))
    lines.append(check_line(rec, lang))
    return [x for x in lines if x]


def ward_flood_answer(conn, lang: str, wardcode: str, ward: str, lga_pcode: str, lga: str, likely: str,
                      today: date, year: int | None, budget: str):
    """(text, working, specs, year shown on the map) for 'my ward' flood questions."""
    from app.place.gfm import attribution
    t = _t(lang)
    rec = record(conn, "ward", wardcode)
    st = static(conn, "ward", wardcode)
    lines = [t["head_ward"].format(ward=ward, likely=likely, lga=lga), t["scope"].format(ward=ward, likely=likely, lga=lga)]
    lines += unit_lines(conn, rec, st, ward, lang, today, year)
    lines.append(context_line(conn, lga_pcode, lga, lang))
    my = map_year(record(conn, "lga", lga_pcode), year, today)
    if my:
        lines.append(t["map_note"].format(year=my, unit=t["unit"]["ward"]))
    lines += [budget, t["neutral"], t["sources"].format(attribution=attribution(attribution_years(rec)))]
    specs = [{"kind": "area_map", "measure": "gfm_union_share", "key": "gfm", "year": my, "level": "ward",
              "unit": lga_pcode, "highlight": wardcode}] if my else []
    return "\n\n".join(x for x in lines if x), "\n".join(working(rec, ward, lang)), specs, my or 0


def area_flood_lines(conn, lang: str, level: str, unit: str, today: date, year: int | None) -> tuple[list[str], list[str], int | None]:
    """The LGA's or the state's own record lines (before the ward/LGA ranking), working lines and the ranking year."""
    from app.sources.lga_names import name_of
    t = _t(lang)
    lvl = "lga" if level == "lga" else "state"
    code = unit if level == "lga" else STATE
    name = t["lga"].format(lga=name_of(unit)) if level == "lga" else t["state"]
    rec = record(conn, lvl, code)
    st = static(conn, lvl, code)
    return unit_lines(conn, rec, st, name, lang, today, year), working(rec, name, lang), map_year(rec, year, today)
