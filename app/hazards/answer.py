"""Hazard answers (docs/hazard-and-services.md sections 4 and 10): the planner capabilities weather_forecast,
air_quality, river_flood and fire_detections, answered in code from hazard_values for an LGA, a point or the whole
state, for today, tomorrow or the next 3 days.

Every figure names its scale and source and the time it was fetched. A layer whose last fetch is too old says how
old; one with no data for the day asked says it isn't available now. River figures are a model forecast against the
point's own history, never an official flood warning. "What should we watch out for?" leads with what is in season.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

from app.hazards import categories as cat
from app.hazards import read
from app.sources.lga_names import name_of, pcode

LAYERS = ("heat", "rain", "air", "flood", "fires")
# the planner's measures (app/agent/need.MEASURES) for each layer
MEASURE_LAYERS = {"heat": "heat", "temperature": "heat", "humidity": "heat", "uv_index": "heat", "wind": "heat",
                  "rain": "rain", "air_quality": "air", "dust": "air", "river_discharge": "flood",
                  "fire_detections": "fires", "hazard_overview": "overview"}
WORDS = {
    "heat": r"heat|hot|temperature|feels? like|uv\b|sunburn|zafi|zafin rana|ɗumi|dumi|rana mai tsanani",
    "rain": r"\brain|rainfall|storm|downpour|wet\b|ruwan sama|ruwa zai|hadari\b|guguwa",
    "air": r"dust|harmattan|haze|air quality|pollution|pm ?10|pm ?2\.?5|ƙura|kura\b|hazo|iska mai|bushewar iska",
    "flood": r"flood|river|discharge|overflow|ambaliya|kogi|kogin|ruwa ya cika",
    "fires": r"\bfires?\b|burning|bush ?fire|smoke|gobara|wuta|ƙone|kone|hayaƙi|hayaki",
    "overview": r"watch out|look out|be careful|what should (?:i|we) (?:expect|watch|look)|any (?:hazards?|danger)|"
                r"weather (?:risks?|hazards?)|me (?:za|ya kamata) (?:mu|in|a|ka) kula|abin da (?:za|ya kamata) "
                r"(?:mu|a) kula|haɗarin yanayi|hadarin yanayi",
}
# money asked about: the budget tools answer ("the budget for flood control", "kuɗin yaƙi da ambaliya")
MONEY = re.compile(r"(?i)\b(?:budget\w*|allocat\w*|spent|spend\w*|naira|₦|kasafi\w*|kuɗi|kudi|ware|kashe)\b")
# in season, by month (section 4 notes): harmattan dust Nov-Feb, heat Mar-May, rains and floods Jun-Oct
SEASON = {1: ("air", "heat"), 2: ("air", "heat"), 3: ("heat", "air"), 4: ("heat",), 5: ("heat", "rain"),
          6: ("rain", "flood"), 7: ("rain", "flood"), 8: ("flood", "rain"), 9: ("flood", "rain"),
          10: ("flood", "rain"), 11: ("air",), 12: ("air",)}


def layers_asked(question: str, measures: list[str] | None = None) -> list[str]:
    """The hazard layers a question asks about (its words and the planner's measures), or [] (a budget question
    about floods is a budget question). 'overview' alone means every layer, in season first."""
    if MONEY.search(question or ""):
        return []
    found = [layer for layer, pat in WORDS.items() if re.search(rf"(?i){pat}", question or "")]
    found += [MEASURE_LAYERS[m] for m in measures or [] if m in MEASURE_LAYERS]
    return list(dict.fromkeys(found))


def days_asked(question: str, today: date) -> list[date]:
    q = (question or "").lower()
    if re.search(r"next (?:3|three|few) days|coming days|this week|kwana uku|'yan kwanaki|wannan mako|mako mai zuwa", q):
        return [today + timedelta(days=i) for i in range(3)]
    if re.search(r"tomorrow|\bgobe\b", q):
        return [today + timedelta(days=1)]
    return [today]


W = {
    "en": {"heat": "🌡️ *Heat*", "rain": "🌧️ *Rain*", "air": "🌫️ *Dust and air*", "flood": "🌊 *Rivers*",
           "fires": "🔥 *Fires*",
           "where_state": "Sokoto State", "where_lga": "{lga} LGA", "today": "today", "tomorrow": "tomorrow",
           "heat_line": "{day}: up to {t:.0f} °C, feels like {f:.0f} °C; heat index up to {hi:.0f} °C: *{cat}* "
                        "(US National Weather Service heat index). UV index up to {uv:.0f}. Wind up to {w:.0f} km/h, "
                        "gusts {g:.0f} km/h.",
           "heat_state": "{day}: hottest in {lga}, heat index up to {hi:.0f} °C: *{cat}* (US National Weather "
                         "Service heat index); up to {t:.0f} °C there. {n} of 23 LGAs at Danger or above.",
           "rain_line": "{day}: {mm:.1f} mm expected, heaviest {peak:.1f} mm/h (*{cls}*, WMO rainfall intensity "
                        "classes); chance of rain up to {p:.0f}%.",
           "rain_none": "{day}: no rain expected (chance up to {p:.0f}%).",
           "rain_state": "{day}: most rain in {lga}, {mm:.1f} mm; {n} of 23 LGAs expect rain.",
           "air_line": "{day}: PM10 averaging {pm10:.0f} µg/m³ (WHO 24-hour guideline: 45), PM2.5 {pm25:.0f} µg/m³ "
                       "(guideline: 15), dust {dust:.0f} µg/m³; US AQI up to {aqi:.0f}: *{cat}*.",
           "air_state": "{day}: dustiest in {lga}, PM10 averaging {pm10:.0f} µg/m³ (WHO 24-hour guideline: 45); "
                        "US AQI up to {aqi:.0f}: *{cat}*.",
           "river_line": "{point} ({lga} LGA), {day}: {q:.0f} m³/s, higher than {rank:.0f}% of days since {since}.",
           "river_note": "River figures are a GloFAS model forecast compared with each point's own history, not "
                         "an official flood warning.",
           "fire_line": "Satellite heat detections (could be bush, farm or other fires) in the last 24 hours: {n} "
                        "in {where}{most}.",
           "fire_most": " (most in {lgas})", "fire_none": "No satellite heat detections in {where} in the last "
                                                          "24 hours.",
           "fire_off": "Fire detections aren't switched on (no NASA FIRMS key).",
           "stale": "⚠️ This is the latest {what} data, from {h:.0f} hours ago: newer data couldn't be fetched.",
           "unavailable": "{what} data isn't available now.",
           "no_day": "{what}: no forecast for {day} yet.",
           "sources": "Sources", "fetched": "fetched {when}", "forecast_note": "These are model forecasts, not "
           "official warnings.",
           "season": "In season now: {layers}.", "season_names": {"heat": "heat", "rain": "rain", "air":
                                                                  "harmattan dust", "flood": "river floods",
                                                                  "fires": "fires"},
           "what": {"heat": "Weather forecast", "rain": "Rain forecast", "air": "Air quality", "flood": "River",
                    "fires": "Fire detection"}},
    "ha": {"heat": "🌡️ *Zafin rana*", "rain": "🌧️ *Ruwan sama*", "air": "🌫️ *Ƙura da iska*", "flood": "🌊 *Koguna*",
           "fires": "🔥 *Gobara*",
           "where_state": "Jihar Sokoto", "where_lga": "Ƙaramar Hukumar {lga}", "today": "yau", "tomorrow": "gobe",
           "heat_line": "{day}: har zuwa {t:.0f} °C, ana jin kamar {f:.0f} °C; ma'aunin zafi har zuwa {hi:.0f} °C: "
                        "*{cat}* (ma'aunin zafi na US National Weather Service). Ma'aunin UV har zuwa {uv:.0f}. Iska "
                        "har zuwa {w:.0f} km/h, guguwa {g:.0f} km/h.",
           "heat_state": "{day}: inda ya fi zafi shi ne {lga}, ma'aunin zafi har zuwa {hi:.0f} °C: *{cat}* "
                         "(ma'aunin zafi na US National Weather Service); har zuwa {t:.0f} °C a can. Ƙananan hukumomi "
                         "{n} cikin 23 suna matakin Haɗari ko sama.",
           "rain_line": "{day}: ana sa ran {mm:.1f} mm, mafi yawa {peak:.1f} mm a awa (*{cls}*, rabe-raben ruwan "
                        "sama na WMO); yiwuwar ruwan sama har zuwa {p:.0f}%.",
           "rain_none": "{day}: ba a sa ran ruwan sama ba (yiwuwa har zuwa {p:.0f}%).",
           "rain_state": "{day}: inda za a fi samun ruwa shi ne {lga}, {mm:.1f} mm; ƙananan hukumomi {n} cikin 23 "
                         "suna sa ran ruwa.",
           "air_line": "{day}: matsakaicin PM10 {pm10:.0f} µg/m³ (iyakar WHO ta awa 24: 45), PM2.5 {pm25:.0f} "
                       "µg/m³ (iyaka: 15), ƙura {dust:.0f} µg/m³; US AQI har zuwa {aqi:.0f}: *{cat}*.",
           "air_state": "{day}: inda ƙura ta fi yawa shi ne {lga}, matsakaicin PM10 {pm10:.0f} µg/m³ (iyakar WHO "
                        "ta awa 24: 45); US AQI har zuwa {aqi:.0f}: *{cat}*.",
           "river_line": "{point} (Ƙaramar Hukumar {lga}), {day}: {q:.0f} m³/s, sama da kashi {rank:.0f}% na "
                         "kwanakin tun {since}.",
           "river_note": "Alƙaluman koguna hasashen GloFAS ne idan aka kwatanta da tarihin kowane wuri, ba "
                         "gargaɗin ambaliya na hukuma ba.",
           "fire_line": "Alamun zafi da tauraron ɗan adam ya gano (na iya zama gobarar daji, gona ko wata) a awa 24 "
                        "da suka wuce: {n} a {where}{most}.",
           "fire_most": " (mafi yawa a {lgas})", "fire_none": "Babu alamun zafi da tauraron ɗan adam ya gano a "
                                                              "{where} a awa 24 da suka wuce.",
           "fire_off": "Ba a kunna gano gobara ba (babu maɓallin NASA FIRMS).",
           "stale": "⚠️ Wannan su ne bayanan {what} mafi sabo, na awa {h:.0f} da suka wuce: ba a iya samo sababbi "
                    "ba.",
           "unavailable": "Bayanan {what} ba su samu yanzu ba.",
           "no_day": "{what}: babu hasashe na {day} tukuna.",
           "sources": "Madogara", "fetched": "an samo {when}", "forecast_note": "Waɗannan hasashen samfuri ne, ba "
           "gargaɗin hukuma ba.",
           "season": "Lokacin da ake ciki: {layers}.", "season_names": {"heat": "zafi", "rain": "ruwan sama",
                                                                         "air": "ƙurar hunturu", "flood":
                                                                         "ambaliyar koguna", "fires": "gobara"},
           "what": {"heat": "hasashen yanayi", "rain": "hasashen ruwan sama", "air": "ingancin iska",
                    "flood": "koguna", "fires": "gano gobara"}},
}
LAYER_OF_SOURCE = {"heat": "forecast", "rain": "forecast", "air": "air", "flood": "flood", "fires": "fires"}


@dataclass
class HazardAnswer:
    text: str
    layers: list[str]
    where: read.Where
    found: bool


def _day_label(d: date, today: date, lang: str) -> str:
    w = W.get(lang, W["en"])
    if d == today:
        return w["today"].capitalize()
    if d == today + timedelta(days=1):
        return w["tomorrow"].capitalize()
    return d.strftime("%a %d %b")


def where_for(entities: list, place: dict | None) -> read.Where:
    """An LGA the question names; else the user's point or LGA on file ('here'); else the whole state."""
    for e in entities or []:
        if getattr(e, "type", "") == "lga" and (code := pcode(e.resolved or e.name)):
            return read.Where("lga", code, name_of(code))
    if place and place.get("lat") is not None:
        return read.Where("point", place.get("lga_pcode", ""), place.get("lga", ""), place["lat"], place["lon"])
    if place and place.get("lga_pcode"):
        return read.Where("lga", place["lga_pcode"], name_of(place["lga_pcode"]))
    return read.Where("state")


def hazard_answer(conn, question: str, lang: str, layers: list[str], where: read.Where, today: date,
                  settings=None) -> HazardAnswer:
    w = W.get(lang, W["en"])
    days = days_asked(question, today)
    if "overview" in layers or not layers:
        season = SEASON[today.month]
        layers = list(dict.fromkeys([*season, *[x for x in LAYERS if x not in season]]))
        intro = [w["season"].format(layers=", ".join(w["season_names"][x] for x in season))]
    else:
        intro = []
    place = w["where_state"] if where.kind == "state" else w["where_lga"].format(lga=where.lga)
    out, found, used = [f"📍 {place}"] + intro, False, {}
    pids = read.point_ids(conn, where)
    for layer in [x for x in layers if x in LAYERS]:
        src = LAYER_OF_SOURCE[layer]
        fresh = read.freshness(conn, src)
        if layer == "fires" and settings is not None and getattr(settings, "firms_map_key", None) is None:
            out += ["", w["fires"], w["fire_off"]]
            continue
        if not fresh.available:
            out += ["", w[layer], w["unavailable"].format(what=w["what"][layer])]
            continue
        lines = _layer_lines(conn, layer, lang, where, pids, days, today)
        if not lines:
            out += ["", w[layer], w["no_day"].format(what=w["what"][layer], day=_day_label(days[0], today, lang))]
            continue
        found = True
        out += ["", w[layer], *lines]
        if fresh.stale:
            out.append(w["stale"].format(what=w["what"][layer], h=fresh.hours_old))
        used[src] = fresh.fetched_at
    if "flood" in layers and found:
        out += ["", w["river_note"]]
    if used:
        if any(s in used for s in ("forecast", "air", "flood")):
            out += ["", w["forecast_note"]]
        out.append(f"📄 *{w['sources']}:* " + "; ".join(
            f"{read.source_of(s)}, {w['fetched'].format(when=at.astimezone(read.LAGOS).strftime('%d %b %H:%M'))}"
            for s, at in used.items()))
    return HazardAnswer("\n".join(out), layers, where, found)


def _layer_lines(conn, layer: str, lang: str, where: read.Where, pids: list, days: list[date], today: date) -> list[str]:
    w = W.get(lang, W["en"])
    out = []
    if layer in ("heat", "rain"):
        for d in days:
            rows = [r for pid, lga in pids if (r := read.heat_day(conn, pid, lga, d))]
            if not rows:
                continue
            label = _day_label(d, today, lang)
            if where.kind == "state":
                if layer == "heat":
                    top = max(rows, key=lambda r: r.heat_index_max)
                    n = sum(1 for r in rows if r.category in ("danger", "extreme_danger"))
                    out.append(w["heat_state"].format(day=label, lga=top.lga, hi=top.heat_index_max,
                                                      cat=cat.label(top.category, lang), t=top.temp_max, n=n))
                else:
                    top = max(rows, key=lambda r: r.rain_mm)
                    n = sum(1 for r in rows if r.rain_mm >= 0.1)
                    out.append(w["rain_state"].format(day=label, lga=top.lga, mm=top.rain_mm, n=n)
                               if top.rain_mm >= 0.1 else w["rain_none"].format(day=label, p=top.rain_prob_max))
                continue
            r = rows[0]
            if layer == "heat":
                out.append(w["heat_line"].format(day=label, t=r.temp_max, f=r.feels_max, hi=r.heat_index_max,
                                                 cat=cat.label(r.category, lang), uv=r.uv_max, w=r.wind_max,
                                                 g=r.gust_max))
            elif r.rain_mm >= 0.1:
                out.append(w["rain_line"].format(day=label, mm=r.rain_mm, peak=r.rain_peak_mm_h,
                                                 cls=cat.label(r.rain_class, lang), p=r.rain_prob_max))
            else:
                out.append(w["rain_none"].format(day=label, p=r.rain_prob_max))
    elif layer == "air":
        for d in days:
            rows = [r for pid, lga in pids if (r := read.air_day(conn, pid, lga, d))]
            if not rows:
                continue
            label = _day_label(d, today, lang)
            if where.kind == "state":
                top = max(rows, key=lambda r: r.pm10_mean)
                out.append(w["air_state"].format(day=label, lga=top.lga, pm10=top.pm10_mean, aqi=top.aqi_max,
                                                 cat=cat.label(top.category, lang)))
            else:
                r = rows[0]
                out.append(w["air_line"].format(day=label, pm10=r.pm10_mean, pm25=r.pm2_5_mean, dust=r.dust_mean,
                                                aqi=r.aqi_max, cat=cat.label(r.category, lang)))
    elif layer == "flood":
        lga = where.lga_pcode if where.kind == "lga" else ""
        for d in days:
            rows = read.river_days(conn, d, lga) or (read.river_days(conn, d) if lga else [])
            out += [w["river_line"].format(point=r.point, lga=r.lga, day=_day_label(d, today, lang), q=r.discharge,
                                           rank=r.rank, since=r.since.year) for r in rows]
    elif layer == "fires":
        lga = where.lga_pcode if where.kind == "lga" else ""
        counts = read.fire_counts(conn, 24, lga)
        place = w["where_state"] if not lga else where.lga
        n = sum(c.count for c in counts)
        if not n:
            return [w["fire_none"].format(where=place)]
        most = w["fire_most"].format(lgas=", ".join(f"{c.lga} {c.count}" for c in counts[:3])) if not lga else ""
        out.append(w["fire_line"].format(n=n, where=place, most=most))
    return out
