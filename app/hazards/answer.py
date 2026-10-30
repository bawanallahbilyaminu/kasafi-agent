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
from app.hazards.official import official_lines
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
           "pin_fallback": "Forecast for {lga} LGA (none for your exact spot yet):",
           "heat_line": "{day}: up to {t:.0f} °C, feels like {f:.0f} °C, heat index up to {hi:.0f} °C: *{cat}* "
                        "(US National Weather Service heat index categories, by the {basis}). UV index up to {uv:.0f}. "
                        "Wind up to {w:.0f} km/h, gusts {g:.0f} km/h.",
           "heat_state": "{day}: hottest in {lga}, up to {t:.0f} °C, heat index up to {hi:.0f} °C: *{cat}* (US "
                         "National Weather Service heat index categories, by the {basis}). {danger}",
           "basis": {"air_temperature": "air temperature, which in dry air is above the heat index",
                     "heat_index": "heat index"},
           "danger_none": "No LGA is at Danger level or above.", "danger_one": "1 LGA is at Danger level or above.",
           "danger_n": "{n} of 23 LGAs are at Danger level or above.",
           "rain_line": "{day}: {mm:.1f} mm expected, heaviest {peak:.1f} mm/h (*{cls}*, WMO rainfall intensity "
                        "classes); chance of rain up to {p:.0f}%.",
           "rain_none": "{day}: no rain expected (chance up to {p:.0f}%).", "rain_dry": "{day}: no rain expected.",
           "rain_state": "{day}: most rain in {lga}, {mm:.1f} mm; {n} of 23 LGAs expect rain.",
           "air_line": "{day}: US AQI up to {aqi:.0f}, set by {by}: *{cat}*. PM10 averaging {pm10:.0f} µg/m³ (WHO "
                       "24-hour guideline: 45), PM2.5 averaging {pm25:.0f} µg/m³ (WHO 24-hour guideline: 15), dust "
                       "{dust:.0f} µg/m³.",
           "air_state": "{day}: worst air in {lga}, US AQI up to {aqi:.0f}, set by {by}: *{cat}*. There, PM10 "
                        "averaging {pm10:.0f} µg/m³ (WHO 24-hour guideline: 45), PM2.5 averaging {pm25:.0f} µg/m³ "
                        "(WHO 24-hour guideline: 15).",
           "river_line": "{point} ({lga} LGA), {day}: {q} m³/s, *{level}* for {period} ({where_in}).",
           "rank_mid": "higher than {rank:.0f}% of {period} days since {since}",
           "rank_low": "the lowest for {period} since {since}", "rank_high": "the highest for {period} since {since}",
           "rank_near_low": "lower than all but {k} of {n} {period} days since {since}",
           "rank_near_high": "higher than all but {k} of {n} {period} days since {since}",
           "dam": " Model estimate; releases from {dam} not included.",
           "levels": {"low": "low", "normal": "normal", "high": "high", "very_high": "very high"},
           "parts": {"early": "early", "mid": "mid", "late": "late"},
           "months": ("January", "February", "March", "April", "May", "June", "July", "August", "September",
                      "October", "November", "December"),
           "river_note": "River figures are a GloFAS model forecast compared with the same time of year in each "
                         "point's own history, not an official flood warning.",
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
           "ranked": "Most severe now first (each on its own scale).",
           "season": "In season now: {layers}.", "season_names": {"heat": "heat", "rain": "rain", "air":
                                                                  "harmattan dust", "flood": "river floods",
                                                                  "fires": "fires"},
           "what": {"heat": "Weather forecast", "rain": "Rain forecast", "air": "Air quality", "flood": "River",
                    "fires": "Fire detection"}},
    "ha": {"heat": "🌡️ *Zafin rana*", "rain": "🌧️ *Ruwan sama*", "air": "🌫️ *Ƙura da iska*", "flood": "🌊 *Koguna*",
           "fires": "🔥 *Gobara*",
           "where_state": "Jihar Sokoto", "where_lga": "Ƙaramar Hukumar {lga}", "today": "yau", "tomorrow": "gobe",
           "pin_fallback": "Hasashen Ƙaramar Hukumar {lga} (babu na daidai inda kake tukuna):",
           "heat_line": "{day}: har zuwa {t:.0f} °C, ana jin kamar {f:.0f} °C, ma'aunin zafi har zuwa {hi:.0f} °C: "
                        "*{cat}* (matakan ma'aunin zafi na US National Weather Service, bisa {basis}). Ma'aunin UV "
                        "har zuwa {uv:.0f}. Iska har zuwa {w:.0f} km/h, guguwa {g:.0f} km/h.",
           "heat_state": "{day}: inda ya fi zafi shi ne {lga}, har zuwa {t:.0f} °C, ma'aunin zafi har zuwa {hi:.0f} "
                         "°C: *{cat}* (matakan ma'aunin zafi na US National Weather Service, bisa {basis}). {danger}",
           "basis": {"air_temperature": "zafin iska, wanda a busasshiyar iska ya fi ma'aunin zafi",
                     "heat_index": "ma'aunin zafi"},
           "danger_none": "Babu ƙaramar hukumar da ke matakin Haɗari ko sama.",
           "danger_one": "Ƙaramar hukuma 1 ce ke matakin Haɗari ko sama.",
           "danger_n": "Ƙananan hukumomi {n} cikin 23 suna matakin Haɗari ko sama.",
           "rain_line": "{day}: ana sa ran {mm:.1f} mm, mafi yawa {peak:.1f} mm a awa (*{cls}*, rabe-raben ruwan "
                        "sama na WMO); yiwuwar ruwan sama har zuwa {p:.0f}%.",
           "rain_none": "{day}: ba a sa ran ruwan sama ba (yiwuwa har zuwa {p:.0f}%).",
           "rain_dry": "{day}: ba a sa ran ruwan sama ba.",
           "rain_state": "{day}: inda za a fi samun ruwa shi ne {lga}, {mm:.1f} mm; ƙananan hukumomi {n} cikin 23 "
                         "suna sa ran ruwa.",
           "air_line": "{day}: US AQI har zuwa {aqi:.0f}, saboda {by}: *{cat}*. Matsakaicin PM10 {pm10:.0f} µg/m³ "
                       "(iyakar WHO ta awa 24: 45), matsakaicin PM2.5 {pm25:.0f} µg/m³ (iyakar WHO ta awa 24: 15), "
                       "ƙura {dust:.0f} µg/m³.",
           "air_state": "{day}: iska ta fi muni a {lga}, US AQI har zuwa {aqi:.0f}, saboda {by}: *{cat}*. A can, "
                        "matsakaicin PM10 {pm10:.0f} µg/m³ (iyakar WHO ta awa 24: 45), matsakaicin PM2.5 {pm25:.0f} "
                        "µg/m³ (iyakar WHO ta awa 24: 15).",
           "river_line": "{point} (Ƙaramar Hukumar {lga}), {day}: {q} m³/s, *{level}* a {period} ({where_in}).",
           "rank_mid": "sama da kashi {rank:.0f}% na kwanakin {period} tun {since}",
           "rank_low": "mafi ƙaranci a {period} tun {since}", "rank_high": "mafi yawa a {period} tun {since}",
           "rank_near_low": "ƙasa da duka sai {k} cikin kwanaki {n} na {period} tun {since}",
           "rank_near_high": "sama da duka sai {k} cikin kwanaki {n} na {period} tun {since}",
           "dam": " Ƙiyasin samfuri ne; ba a haɗa da ruwan da ake sakowa daga {dam} ba.",
           "levels": {"low": "ƙasa da yadda aka saba", "normal": "kamar yadda aka saba", "high": "sama da yadda "
                      "aka saba", "very_high": "sama sosai da yadda aka saba"},
           "parts": {"early": "farkon", "mid": "tsakiyar", "late": "ƙarshen"},
           "months": ("Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba",
                      "Oktoba", "Nuwamba", "Disamba"),
           "river_note": "Alƙaluman koguna hasashen GloFAS ne idan aka kwatanta da wannan lokaci na shekara a "
                         "tarihin kowane wuri, ba gargaɗin ambaliya na hukuma ba.",
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
           "ranked": "Mafi tsanani yanzu na farko (kowanne bisa ma'auninsa).",
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
    pids = read.point_ids(conn, where)
    if "overview" in layers or not layers:
        # the most severe now first (each layer's own category); what is in season breaks ties
        season = SEASON[today.month]
        order = {x: i for i, x in enumerate([*season, *[x for x in LAYERS if x not in season]])}
        layers = sorted(LAYERS, key=lambda x: (-severity(conn, x, where, pids, days[0]), order[x]))
        intro = [w["ranked"], w["season"].format(layers=", ".join(w["season_names"][x] for x in season))]
    else:
        intro = []
    place = w["where_state"] if where.kind == "state" else w["where_lga"].format(lga=where.lga)
    out, found, used = [f"📍 {place}"] + intro, False, {}
    if conn is not None and (official := official_lines(conn, lang, layers, where)):
        out += ["", *official]                  # official warnings first, verbatim; the model forecasts follow
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
        if not lines and where.kind == "point" and where.lga_pcode:
            # the pin's own spot has no data yet (the grid fetch hasn't run): its LGA's forecast, said as such
            lga = read.Where("lga", where.lga_pcode, where.lga or name_of(where.lga_pcode))
            if lines := _layer_lines(conn, layer, lang, lga, read.point_ids(conn, lga), days, today):
                lines = [w["pin_fallback"].format(lga=lga.lga), *lines]
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


HEAT_RANK = {"below": 0, "caution": 1, "extreme_caution": 2, "danger": 3, "extreme_danger": 4}
AIR_RANK = {"good": 0, "moderate": 1, "unhealthy_sensitive": 2, "unhealthy": 3, "very_unhealthy": 4, "hazardous": 5}
RAIN_RANK = {"none": 0, "light": 1, "moderate": 2, "heavy": 3, "violent": 4}
FLOOD_RANK = {"low": 0, "normal": 0, "high": 2, "very_high": 4}


def severity(conn, layer: str, where: read.Where, pids: list, day: date) -> int:
    """How severe a layer is now, on its own category (0 nothing notable ... 4-5 the worst); -1 without data.
    Fires have no official scale: detections in the last 24 hours, ranked only for ordering (an LGA: 1-4 low,
    5-19 moderate, 20 or more high; the state: three times that)."""
    if layer in ("heat", "rain"):
        rows = [r for pid, lga in pids if (r := read.heat_day(conn, pid, lga, day))]
        if not rows:
            return -1
        return max(HEAT_RANK[r.category] if layer == "heat" else RAIN_RANK[r.rain_class] for r in rows)
    if layer == "air":
        rows = [r for pid, lga in pids if (r := read.air_day(conn, pid, lga, day))]
        return max((AIR_RANK[r.category] for r in rows), default=-1)
    if layer == "flood":
        rows = read.river_days(conn, day, where.lga_pcode if where.kind == "lga" else "") or read.river_days(conn, day)
        return max((FLOOD_RANK[r.level] for r in rows), default=-1)
    if layer == "fires":
        n = sum(c.count for c in read.fire_counts(conn, 24, where.lga_pcode if where.kind == "lga" else ""))
        scale = 1 if where.kind == "lga" else 3
        return 0 if n == 0 else 1 if n < 5 * scale else 2 if n < 20 * scale else 3
    return -1


def discharge(q: float) -> str:
    """m3/s as printed: a decimal below 10 (2.4, not 2), whole numbers above (1,976)."""
    return f"{q:.1f}" if q < 10 else f"{q:,.0f}"


def _dry(w: dict, label: str, prob: float) -> str:
    return w["rain_none"].format(day=label, p=prob) if prob >= 1 else w["rain_dry"].format(day=label)


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
                    top = max(rows, key=lambda r: r.category_value)
                    n = sum(1 for r in rows if r.category in ("danger", "extreme_danger"))
                    danger = w["danger_none"] if n == 0 else w["danger_one"] if n == 1 else w["danger_n"].format(n=n)
                    out.append(w["heat_state"].format(day=label, lga=top.lga, hi=top.heat_index_max,
                                                      cat=cat.label(top.category, lang), t=top.temp_max,
                                                      basis=w["basis"][top.basis], danger=danger))
                else:
                    top = max(rows, key=lambda r: r.rain_mm)
                    n = sum(1 for r in rows if r.rain_mm >= 0.1)
                    out.append(w["rain_state"].format(day=label, lga=top.lga, mm=top.rain_mm, n=n)
                               if top.rain_mm >= 0.1 else _dry(w, label, max(r.rain_prob_max for r in rows)))
                continue
            r = rows[0]
            if layer == "heat":
                out.append(w["heat_line"].format(day=label, t=r.temp_max, f=r.feels_max, hi=r.heat_index_max,
                                                 cat=cat.label(r.category, lang), uv=r.uv_max, w=r.wind_max,
                                                 g=r.gust_max, basis=w["basis"][r.basis]))
            elif r.rain_mm >= 0.1:
                out.append(w["rain_line"].format(day=label, mm=r.rain_mm, peak=r.rain_peak_mm_h,
                                                 cls=cat.label(r.rain_class, lang), p=r.rain_prob_max))
            else:
                out.append(_dry(w, label, r.rain_prob_max))
    elif layer == "air":
        for d in days:
            rows = [r for pid, lga in pids if (r := read.air_day(conn, pid, lga, d))]
            if not rows:
                continue
            label = _day_label(d, today, lang)
            if where.kind == "state":
                top = max(rows, key=lambda r: (r.aqi_max, r.pm10_mean))   # the AQI sets the category shown
                out.append(w["air_state"].format(day=label, lga=top.lga, pm10=top.pm10_mean, pm25=top.pm2_5_mean,
                                                 aqi=top.aqi_max, by=top.aqi_by, cat=cat.label(top.category, lang)))
            else:
                r = rows[0]
                out.append(w["air_line"].format(day=label, pm10=r.pm10_mean, pm25=r.pm2_5_mean, dust=r.dust_mean,
                                                aqi=r.aqi_max, by=r.aqi_by, cat=cat.label(r.category, lang)))
    elif layer == "flood":
        lga = where.lga_pcode if where.kind == "lga" else ""
        for d in days:
            rows = read.river_days(conn, d, lga) or (read.river_days(conn, d) if lga else [])
            for r in rows:
                period = f"{w['parts'][r.period[0]]} {w['months'][r.period[1] - 1]}"
                # 'the lowest' only below every day compared with; near the edges, how many days are beyond it
                key, k = (("rank_low", 0) if r.n and r.below == 0 else ("rank_high", 0) if r.n and r.above == 0
                          else ("rank_near_low", r.below) if r.rank < 1 else ("rank_near_high", r.above)
                          if r.rank > 99 else ("rank_mid", 0))
                out.append(w["river_line"].format(point=r.point, lga=r.lga, day=_day_label(d, today, lang),
                                                  q=discharge(r.discharge), level=w["levels"][r.level], period=period,
                                                  where_in=w[key].format(rank=r.rank, period=period, k=k, n=r.n,
                                                                         since=r.since.year))
                           + (w["dam"].format(dam=r.dam) if r.dam else ""))
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
