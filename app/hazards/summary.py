"""The executive summary that leads every hazard answer, written in code from the same data as the details (no model:
nothing can be invented, nothing repeated). Two or three sentences in the user's language:

1. What it means in plain words: the category, with its meaning quoted from the scale's owner and credited (US EPA
   for the AQI categories, the US National Weather Service for heat index categories; in Hausa, Kasafi's
   translation, said as such). Never Kasafi's own health advice.
2. What drives it and how it compares: the pollutant that sets the AQI with PM2.5 / PM10 as multiples of the WHO
   24-hour guideline (not raw numbers); air temperature vs heat index; tomorrow against the day asked; where the
   LGA stands among the 23 when it is near either end.
3. The official warning status, in one clause.

The details that follow carry the figures, once; the summary never repeats a sentence of them
(tests/test_hazard_summary.py).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.hazards import categories as cat
from app.hazards import read

EPA = {   # US EPA, AirNow "AQI Basics": what each AQI category means
    "good": "Air quality is satisfactory, and air pollution poses little or no risk",
    "moderate": "Air quality is acceptable. However, there may be a risk for some people, particularly those who "
                "are unusually sensitive to air pollution",
    "unhealthy_sensitive": "Members of sensitive groups may experience health effects. The general public is less "
                           "likely to be affected",
    "unhealthy": "Some members of the general public may experience health effects; members of sensitive groups "
                 "may experience more serious health effects",
    "very_unhealthy": "Health alert: The risk of health effects is increased for everyone",
    "hazardous": "Health warning of emergency conditions: everyone is more likely to be affected",
}
EPA_HA = {
    "good": "Ingancin iska yana da gamsarwa, kuma gurɓacewar iska ba ta da haɗari ko kuma kaɗan ne",
    "moderate": "Ingancin iska abin karɓa ne. Sai dai akwai yiwuwar haɗari ga wasu mutane, musamman waɗanda gurɓatacciyar "
                "iska ke shafa fiye da kima",
    "unhealthy_sensitive": "Mutane masu rauni na iya fuskantar illa ga lafiya. Ba a cika tsammanin sauran jama'a za "
                           "su shafu ba",
    "unhealthy": "Wasu daga cikin jama'a na iya fuskantar illa ga lafiya; masu rauni na iya fuskantar illa mafi "
                 "tsanani",
    "very_unhealthy": "Faɗakarwar lafiya: haɗarin illa ga lafiya ya ƙaru ga kowa",
    "hazardous": "Gargaɗin lafiya na yanayin gaggawa: kowa zai fi yiwuwa ya shafu",
}
NWS = {   # US National Weather Service heat index chart: what each category means
    "caution": "Fatigue possible with prolonged exposure and/or physical activity",
    "extreme_caution": "Sunstroke, muscle cramps, and/or heat exhaustion possible with prolonged exposure and/or "
                       "physical activity",
    "danger": "Sunstroke, muscle cramps, and/or heat exhaustion likely. Heatstroke possible with prolonged exposure "
              "and/or physical activity",
    "extreme_danger": "Heat stroke highly likely",
}
NWS_HA = {
    "caution": "Gajiya na iya faruwa idan aka daɗe a cikin zafin da/ko aka yi aiki",
    "extreme_caution": "Bugun rana, murɗewar tsoka da/ko gajiyar zafi na iya faruwa idan aka daɗe a ciki da/ko aka "
                       "yi aiki",
    "danger": "Bugun rana, murɗewar tsoka da/ko gajiyar zafi suna da yiwuwa. Bugun zafi na iya faruwa idan aka daɗe "
              "a ciki da/ko aka yi aiki",
    "extreme_danger": "Bugun zafi yana da matuƙar yiwuwa",
}
WHO = {"pm2_5": 15.0, "pm10": 45.0}            # µg/m³, WHO 2021 24-hour guidelines

W = {
    "en": {
        "place_state": "Sokoto State", "place_lga": "{lga} LGA", "today": "today", "tomorrow": "tomorrow",
        "place_named": "{place} ({lga} LGA)",
        "air": "Air quality in {place} {day} is *{cat}* on the US AQI, which the US EPA describes as “{meaning}”.",
        "air_state": "Across Sokoto State {day}, air quality is mostly *{cat}* ({n} of 23 LGAs), which the US EPA "
                     "describes as “{meaning}”; it is worst in {worst} (*{wcat}*).",
        "air_driver": {"PM2.5": "Fine particles (PM2.5) set the AQI", "PM10": "Coarse dust (PM10) sets the AQI"},
        "air_mult": "{driver}{there}: {mult}",
        "there": " there",
        "both": "PM2.5 is about {a} times and PM10 about {b} times the WHO daily guideline",
        "one": "{name} is about {x} times the WHO daily guideline, {other} within it",
        "neither": "PM2.5 and PM10 are within the WHO daily guidelines",
        "heat": "Heat in {place} {day} reaches *{cat}* on the US National Weather Service heat index scale, which "
                "the NWS describes as “{meaning}”.",
        "heat_below": "Heat in {place} {day} stays below the US National Weather Service heat index Caution level.",
        "heat_state": "Across Sokoto State {day}, heat reaches *{cat}* at worst (in {worst}), which the US National "
                      "Weather Service describes as “{meaning}”; {n} of 23 LGAs are at Danger or above.",
        "heat_driver": {"air_temperature": "It comes from the air temperature itself (the air is too dry for "
                                           "humidity to add to it)",
                        "heat_index": "It comes from heat and humidity together"},
        "rain": "{place} expects *{cls}* rain {day} (WMO rainfall intensity class).",
        "rain_none": "{place} expects no rain {day}.",
        "rain_state": "{n} of 23 LGAs expect rain {day}, the most in {worst} (*{cls}*, WMO rainfall intensity "
                      "class).",
        "rain_state_none": "No LGA in Sokoto State expects rain {day}.",
        "river": "By the GloFAS model, the {point} is *{level}* for {period}.",
        "river_none": "There is no river forecast for {place} {day}.",
        "fires": "Satellites detected {n} heat sources (could be bush, farm or other fires) in {place} in the last "
                 "24 hours.",
        "fires_none": "Satellites detected no heat sources (fires) in {place} in the last 24 hours.",
        "trend": {"air": {"up": "{other} looks worse{cat}", "down": "{other} looks better{cat}",
                          "same": "{other} looks similar"},
                  "heat": {"up": "{other} is hotter{cat}", "down": "{other} is cooler{cat}",
                           "same": "{other} is about the same"}},
        "trend_cat": " (*{cat}*)",
        "hotter_today": "today", "rank_top": "{place} is among the 5 worst of the 23 LGAs",
        "rank_low": "{place} is among the 5 least affected of the 23 LGAs",
        "status_none": "No official warning is in force from NEMA, SEMA or the Ministry of Health (checked {when}).",
        "status_stale": "No official warning was in force when NEMA, SEMA and Ministry of Health alerts were last "
                        "checked ({when}).",
        "status_unchecked": "Kasafi hasn't yet been able to check NEMA, SEMA or Ministry of Health alerts.",
        "status_live": "An official {src} warning is in force (issued {date}), quoted below.",
        "when_today": "{t} today", "when_yesterday": "yesterday {t}",
        "levels": {"low": "low", "normal": "normal", "high": "high", "very_high": "very high"},
        "parts": {"early": "early", "mid": "mid", "late": "late"},
        "months": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                   "November", "December"),
    },
    "ha": {
        "place_state": "Jihar Sokoto", "place_lga": "Ƙaramar Hukumar {lga}", "today": "yau", "tomorrow": "gobe",
        "place_named": "{place} (Ƙaramar Hukumar {lga})",
        "air": "Ingancin iska a {place} {day} *{cat}* ne a ma'aunin US AQI; US EPA ta bayyana shi da “{meaning}” "
               "(fassarar Kasafi).",
        "air_state": "A faɗin Jihar Sokoto {day}, ingancin iska galibi *{cat}* ne (ƙananan hukumomi {n} cikin 23); "
                     "US EPA ta bayyana shi da “{meaning}” (fassarar Kasafi); ya fi muni a {worst} (*{wcat}*).",
        "air_driver": {"PM2.5": "Ƙananan ƙwayoyi (PM2.5) ne suka ƙayyade AQI", "PM10": "Ƙura (PM10) ce ta ƙayyade AQI"},
        "air_mult": "{driver}{there}: {mult}",
        "there": " a can",
        "both": "PM2.5 ya kai kusan ninki {a}, PM10 kuma kusan ninki {b} na iyakar WHO ta yini",
        "one": "{name} ya kai kusan ninki {x} na iyakar WHO ta yini, {other} kuma yana cikin iyakar",
        "neither": "PM2.5 da PM10 suna cikin iyakokin WHO na yini",
        "heat": "Zafi a {place} {day} ya kai *{cat}* a ma'aunin zafi na US National Weather Service; NWS ta "
                "bayyana shi da “{meaning}” (fassarar Kasafi).",
        "heat_below": "Zafi a {place} {day} bai kai matakin 'A kula' na ma'aunin zafi na US National Weather Service "
                      "ba.",
        "heat_state": "A faɗin Jihar Sokoto {day}, zafi ya kai *{cat}* a inda ya fi (a {worst}); NWS ta bayyana shi "
                      "da “{meaning}” (fassarar Kasafi); ƙananan hukumomi {n} cikin 23 suna matakin Haɗari ko sama.",
        "heat_driver": {"air_temperature": "Zafin iskar kanta ne ya kawo shi (iskar ta bushe sosai da danshi ba zai "
                                           "ƙara masa ba)",
                        "heat_index": "Zafi da danshi tare ne suka kawo shi"},
        "rain": "Ana sa ran ruwan sama *{cls}* a {place} {day} (rabe-raben WMO).",
        "rain_none": "Ba a sa ran ruwan sama a {place} {day} ba.",
        "rain_state": "Ƙananan hukumomi {n} cikin 23 suna sa ran ruwan sama {day}, mafi yawa a {worst} (*{cls}*, "
                      "rabe-raben WMO).",
        "rain_state_none": "Babu ƙaramar hukuma a Jihar Sokoto da ke sa ran ruwan sama {day}.",
        "river": "A samfurin GloFAS, {point} yana *{level}* a {period}.",
        "river_none": "Babu hasashen koguna na {place} {day}.",
        "fires": "Tauraron ɗan adam ya gano alamun zafi {n} (na iya zama gobarar daji, gona ko wata) a {place} a awa "
                 "24 da suka wuce.",
        "fires_none": "Tauraron ɗan adam bai gano alamun zafi (gobara) a {place} a awa 24 da suka wuce ba.",
        "trend": {"air": {"up": "{other} zai fi muni{cat}", "down": "{other} zai fi kyau{cat}",
                          "same": "{other} zai yi kama da haka"},
                  "heat": {"up": "{other} ya fi zafi{cat}", "down": "{other} bai kai haka zafi ba{cat}",
                           "same": "{other} kusan haka yake"}},
        "trend_cat": " (*{cat}*)",
        "hotter_today": "yau", "rank_top": "{place} na cikin 5 mafi muni a cikin ƙananan hukumomi 23",
        "rank_low": "{place} na cikin 5 da abin ya fi sauƙi a cikin ƙananan hukumomi 23",
        "status_none": "Babu gargaɗin hukuma mai aiki daga NEMA, SEMA ko Ma'aikatar Lafiya (an duba {when}).",
        "status_stale": "Babu gargaɗin hukuma mai aiki lokacin da aka duba gargaɗin NEMA, SEMA da Ma'aikatar Lafiya "
                        "na ƙarshe ({when}).",
        "status_unchecked": "Kasafi bai samu damar duba gargaɗin NEMA, SEMA ko Ma'aikatar Lafiya ba tukuna.",
        "status_live": "Akwai gargaɗin hukuma daga {src} mai aiki (an fitar {date}); an kawo shi a ƙasa.",
        "when_today": "{t} yau", "when_yesterday": "jiya {t}",
        "levels": {"low": "ƙasa da yadda aka saba", "normal": "kamar yadda aka saba", "high": "sama da yadda aka saba",
                   "very_high": "sama sosai da yadda aka saba"},
        "parts": {"early": "farkon", "mid": "tsakiyar", "late": "ƙarshen"},
        "months": ("Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba", "Oktoba",
                   "Nuwamba", "Disamba"),
    },
}
RANK = {"air": {"good": 0, "moderate": 1, "unhealthy_sensitive": 2, "unhealthy": 3, "very_unhealthy": 4,
                "hazardous": 5},
        "heat": {"below": 0, "caution": 1, "extreme_caution": 2, "danger": 3, "extreme_danger": 4}}


def _w(lang: str) -> dict:
    return W.get(lang, W["en"])


def _day(d: date, today: date, lang: str) -> str:
    w = _w(lang)
    return w["today"] if d == today else w["tomorrow"] if d == today + timedelta(days=1) else d.strftime("%a %d %b")


def _x(m: float) -> str:
    return f"{m:.1f}" if m < 2 else f"{m:.0f}"


def multiples(pm25: float, pm10: float, lang: str) -> str:
    """PM2.5 and PM10 as multiples of the WHO 24-hour guidelines, not raw numbers."""
    w = _w(lang)
    a, b = pm25 / WHO["pm2_5"], pm10 / WHO["pm10"]
    if a > 1 and b > 1:
        return w["both"].format(a=_x(a), b=_x(b))
    if a > 1 or b > 1:
        return w["one"].format(name="PM2.5" if a > 1 else "PM10", x=_x(max(a, b)), other="PM10" if a > 1 else "PM2.5")
    return w["neither"]


def _trend(lang: str, layer: str, now_cat: str, now_v: float, other_cat: str, other_v: float, other: str) -> str:
    """The other day against the one asked: by category first, then a 15% (air) or 1.5 °C (heat) change; the
    other day's category is named only when it differs."""
    w, r = _w(lang), RANK[layer]
    step = 0.15 * now_v if layer == "air" else 1.5
    key = ("up" if r[other_cat] > r[now_cat] else "down" if r[other_cat] < r[now_cat]
           else "up" if other_v - now_v > step else "down" if now_v - other_v > step else "same")
    named = w["trend_cat"].format(cat=cat.label(other_cat, lang)) if other_cat != now_cat else ""
    return w["trend"][layer][key].format(other=other, cat=named)


def _rank(lang: str, place: str, value: float, all_values: list[float]) -> str:
    if len(all_values) < 10:
        return ""
    higher = sum(1 for v in all_values if v > value)
    lower = sum(1 for v in all_values if v < value)
    w = _w(lang)
    return (w["rank_top"].format(place=place) if higher < 5 else w["rank_low"].format(place=place) if lower < 5
            else "")


def _clause_join(first: str, rest: list[str]) -> str:
    """'A; b; c.' from a leading clause and the extra clauses (empty ones dropped; they start in lower case or
    with a name)."""
    return "; ".join([first, *[r for r in rest if r]]) + "."


def _air(conn, lang, where, pids, day, today, place) -> list[str]:
    w = _w(lang)
    state = read.point_ids(conn, read.Where("state"))
    every = [r for pid, lga in state if (r := read.air_day(conn, pid, lga, day))]
    other_day = day + timedelta(days=1) if day == today else today
    if where.kind == "state":
        if not every:
            return []
        common = max(set(r.category for r in every), key=lambda c: sum(1 for r in every if r.category == c))
        worst = max(every, key=lambda r: r.aqi_max)
        s1 = w["air_state"].format(day=_day(day, today, lang), cat=cat.label(common, lang),
                                   n=sum(1 for r in every if r.category == common), meaning=_meaning("air", common, lang),
                                   worst=worst.lga, wcat=cat.label(worst.category, lang))
        r, there = worst, w["there"]
        others = [o for pid, lga in state if lga == worst.lga and (o := read.air_day(conn, pid, lga, other_day))]
        rank = ""
    else:
        rows = [r for pid, lga in pids if (r := read.air_day(conn, pid, lga, day))]
        if not rows:
            return []
        r, there = rows[0], ""
        s1 = w["air"].format(place=place, day=_day(day, today, lang), cat=cat.label(r.category, lang),
                             meaning=_meaning("air", r.category, lang))
        others = [o for pid, lga in pids if (o := read.air_day(conn, pid, lga, other_day))]
        rank = _rank(lang, place, r.aqi_max, [x.aqi_max for x in every]) if where.kind != "state" else ""
    mult = w["air_mult"].format(driver=w["air_driver"].get(r.aqi_by, w["air_driver"]["PM10"]), there=there,
                                mult=multiples(r.pm2_5_mean, r.pm10_mean, lang))
    trend = _trend(lang, "air", r.category, r.aqi_max, others[0].category, others[0].aqi_max,
                   _day(other_day, today, lang)) if others else ""
    return [s1, _clause_join(mult, [trend, rank])]


def _heat(conn, lang, where, pids, day, today, place) -> list[str]:
    w = _w(lang)
    state = read.point_ids(conn, read.Where("state"))
    every = [r for pid, lga in state if (r := read.heat_day(conn, pid, lga, day))]
    other_day = day + timedelta(days=1) if day == today else today
    if where.kind == "state":
        if not every:
            return []
        worst = max(every, key=lambda r: r.category_value)
        n = sum(1 for r in every if r.category in ("danger", "extreme_danger"))
        if worst.category == "below":
            return [w["heat_below"].format(place=place, day=_day(day, today, lang))]
        s1 = w["heat_state"].format(day=_day(day, today, lang), cat=cat.label(worst.category, lang), worst=worst.lga,
                                    meaning=_meaning("heat", worst.category, lang), n=n)
        r = worst
        others = [o for pid, lga in state if lga == worst.lga and (o := read.heat_day(conn, pid, lga, other_day))]
        rank = ""
    else:
        rows = [r for pid, lga in pids if (r := read.heat_day(conn, pid, lga, day))]
        if not rows:
            return []
        r = rows[0]
        if r.category == "below":
            s1 = w["heat_below"].format(place=place, day=_day(day, today, lang))
        else:
            s1 = w["heat"].format(place=place, day=_day(day, today, lang), cat=cat.label(r.category, lang),
                                  meaning=_meaning("heat", r.category, lang))
        others = [o for pid, lga in pids if (o := read.heat_day(conn, pid, lga, other_day))]
        rank = _rank(lang, place, r.category_value, [x.category_value for x in every])
    trend = _trend(lang, "heat", r.category, r.category_value, others[0].category, others[0].category_value,
                   _day(other_day, today, lang)) if others else ""
    return [s1, _clause_join(w["heat_driver"][r.basis], [trend, rank])]


def _rain(conn, lang, where, pids, day, today, place) -> list[str]:
    w = _w(lang)
    if where.kind == "state":
        every = [r for pid, lga in read.point_ids(conn, where) if (r := read.heat_day(conn, pid, lga, day))]
        wet = [r for r in every if r.rain_mm >= 0.1]
        if not every:
            return []
        if not wet:
            return [w["rain_state_none"].format(day=_day(day, today, lang))]
        worst = max(wet, key=lambda r: r.rain_mm)
        return [w["rain_state"].format(n=len(wet), day=_day(day, today, lang), worst=worst.lga,
                                       cls=cat.label(worst.rain_class, lang))]
    rows = [r for pid, lga in pids if (r := read.heat_day(conn, pid, lga, day))]
    if not rows:
        return []
    r = rows[0]
    if r.rain_mm < 0.1:
        return [w["rain_none"].format(place=place, day=_day(day, today, lang))]
    return [w["rain"].format(place=place, day=_day(day, today, lang), cls=cat.label(r.rain_class, lang))]


def _river(conn, lang, where, day, today, place) -> list[str]:
    w = _w(lang)
    rows = read.river_days(conn, day, where.lga_pcode if where.kind == "lga" else "") or read.river_days(conn, day)
    if not rows:
        return [w["river_none"].format(place=place, day=_day(day, today, lang))]
    top = max(rows, key=lambda r: r.rank)
    period = f"{w['parts'][top.period[0]]} {w['months'][top.period[1] - 1]}"
    return [w["river"].format(point=top.point, level=w["levels"][top.level], period=period)]


def _fires(conn, lang, where, place) -> list[str]:
    w = _w(lang)
    counts = read.fire_counts(conn, 24, where.lga_pcode if where.kind == "lga" else "")
    n = sum(c.count for c in counts)
    return [w["fires"].format(n=n, place=place) if n else w["fires_none"].format(place=place)]


def _meaning(layer: str, category: str, lang: str) -> str:
    table = (EPA_HA if lang == "ha" else EPA) if layer == "air" else (NWS_HA if lang == "ha" else NWS)
    return table.get(category, "")


def status(conn, lang: str, layers: list[str], where: read.Where, now: datetime | None = None) -> str:
    """The official warning status in one sentence: a warning in force (quoted in the details), or none as of
    the last successful check, or that no check has succeeded yet."""
    from app.hazards import official
    w, now = _w(lang), now or datetime.now(timezone.utc)
    hazards = tuple(dict.fromkeys(h for x in layers for h in official.LAYER_HAZARDS.get(x, ())))
    if not hazards:
        return ""
    live, _ = official.advisories_for(conn, hazards, where, now)
    warnings = [a for a in live if a.kind != "outlook"]
    if warnings:
        a = warnings[0]
        return w["status_live"].format(src=official.SOURCE_NAMES.get(a.source, a.source),
                                       date=a.issued_at.astimezone(read.LAGOS).strftime("%d %b"))
    checked = official.last_checked(conn)
    if checked is None:
        return w["status_unchecked"]
    at = checked.astimezone(read.LAGOS)
    if now - checked > timedelta(hours=24):
        return w["status_stale"].format(when=at.strftime("%d %b %H:%M"))
    clock = at.strftime("%H:%M")
    when = (w["when_today"] if at.date() == now.astimezone(read.LAGOS).date() else w["when_yesterday"]).format(t=clock)
    return w["status_none"].format(when=when)


def hazard_summary(conn, lang: str, layers: list[str], where: read.Where, day: date, today: date,
                   now: datetime | None = None) -> str:
    """2-3 sentences for the first layer (the asked or most severe one), then the official status; '' without
    data."""
    from app.sources.lga_names import name_of
    w = _w(lang)
    lga = where.lga or name_of(where.lga_pcode)
    place = (w["place_state"] if where.kind == "state" else
             w["place_named"].format(place=where.name, lga=lga) if where.name else w["place_lga"].format(lga=lga))
    pids = read.point_ids(conn, where)
    layer = next((x for x in layers if x in ("air", "heat", "rain", "flood", "fires")), "")
    body = {"air": lambda: _air(conn, lang, where, pids, day, today, place),
            "heat": lambda: _heat(conn, lang, where, pids, day, today, place),
            "rain": lambda: _rain(conn, lang, where, pids, day, today, place),
            "flood": lambda: _river(conn, lang, where, day, today, place),
            "fires": lambda: _fires(conn, lang, where, place)}.get(layer, lambda: [])()
    if not body:
        return ""
    return " ".join([*body, status(conn, lang, layers, where, now)]).strip()
