"""What fires an alert, per hazard and LGA, read from the hazard tables (docs/hazard-and-services.md section 9).

- A new official advisory (NEMA, SEMA, State MoH; issued in the last 3 days and still current) covering the LGA,
  or state-wide. Official: sent in quiet hours too.
- Heat: Danger or Extreme danger today or tomorrow, from max(air temperature, NWS heat index), as answers use.
- Dust: US AQI "Hazardous" today, or high for the time of year: at least "Unhealthy" and above the 95th percentile
  of the LGA's daily maxima over the last 30 days (needs 20 days of history; "Very unhealthy" alone is most
  harmattan days, so it never fires on its own).
- Rivers: a river point's forecast (today to 2 days ahead) above the 95th percentile of the same time of year in
  its own history (the seasonal percentile the answers use); a GloFAS model estimate, said as such.
- Outbreaks: a new NCDC situation report (read in the last 7 days) whose Sokoto figures rose from the previous
  report (or a first report with cases), for every LGA (the figures are state-level).

Layers whose data is stale (older than twice the fetch interval) fire nothing. Each candidate carries its own
`key`; a key already sent is never sent again (app/alerts/dispatch.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from app.hazards import read
from app.hazards.categories import label
from app.hazards.official import CURRENT, SOURCE_NAMES, current, period_label, _t
from app.sources.lga_names import PCODES, pcode

LAGOS = timezone(timedelta(hours=1))
ADVISORY_DAYS = 3                 # only advisories issued this recently are "new" (no flood of old ones on day 1)
OUTBREAK_DAYS = 7
OUTBREAK_WEEKS = 4                # an NCDC report about an epi week older than this is a back-report, not news
AIR_HISTORY_DAYS, AIR_MIN_DAYS, AIR_KEEP_DAYS = 30, 20, 120
SEASONAL_PCT = 95
ADVISORY_HAZARDS = {"flood": "flood", "rain": "flood", "heat": "heat", "dust": "dust", "cholera": "outbreak",
                    "csm": "outbreak", "lassa": "outbreak", "measles": "outbreak", "diphtheria": "outbreak"}


@dataclass
class Candidate:
    hazard: str                   # heat | dust | flood | outbreak
    lga_pcode: str
    key: str                      # what fired; never sent twice
    official: bool                # an official warning: quiet hours don't hold it back
    what: dict[str, str]          # the template's {{3}} per language
    source: dict[str, str]        # {{4}} per language


def _stamp(at: datetime | None) -> str:
    return at.astimezone(LAGOS).strftime("%d %b %Y %H:%M") if at else ""


def _when(day: date, today: date, lang: str) -> str:
    if day == today:
        return "yau" if lang == "ha" else "today"
    if day == today + timedelta(days=1):
        return "gobe" if lang == "ha" else "tomorrow"
    return f"ranar {day:%d %b}" if lang == "ha" else f"on {day:%d %b}"


def _lgas(conn) -> list[tuple[int, str, str]]:
    return conn.execute("SELECT p.id, l.name, l.pcode FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode "
                        "WHERE p.kind = 'lga' ORDER BY l.name").fetchall()


def advisories(conn, now: datetime) -> list[Candidate]:
    rows = conn.execute("SELECT id, source, kind, hazard, issued_at, valid_until, lgas, state_wide FROM advisories "
                        "WHERE kind <> 'outlook' AND doc_id IS NULL AND issued_at >= %s ORDER BY issued_at",
                        (now - timedelta(days=ADVISORY_DAYS),)).fetchall()
    out = []
    for aid, source, kind, hazard, issued, until, lgas, state_wide in rows:
        ours = ADVISORY_HAZARDS.get(hazard)
        if not ours or not current(kind, issued, until, now) or kind not in CURRENT:
            continue
        src, day = SOURCE_NAMES.get(source, source), issued.astimezone(LAGOS).strftime("%d %b %Y")
        thing = {"en": _t("en")["names"].get(hazard, {"rain": "heavy rain"}.get(hazard, hazard)).lower(),
                 "ha": _t("ha")["names"].get(hazard, {"flood": "ambaliya", "rain": "ruwan sama mai yawa",
                                                      "heat": "zafin rana", "dust": "ƙura"}.get(hazard, hazard))}
        kind_en, kind_ha = {"alert": ("alert", "Gargaɗi"), "notice": ("notice", "Sanarwa"),
                            "report": ("report", "Rahoto")}[kind]
        what = {"en": f"{src} {thing['en']} {kind_en} issued {day}",
                "ha": f"{kind_ha} game da {thing['ha']} daga {src}, an fitar {day}"}
        source_text = {"en": f"{src}, {day}", "ha": f"{src}, {day}"}
        for code in (sorted(PCODES.values()) if state_wide else lgas):
            out.append(Candidate(ours, code, f"adv:{aid}", True, what, source_text))
    return out


def heat(conn, now: datetime) -> list[Candidate]:
    if read.freshness(conn, "forecast", now).stale:
        return []
    today, out = now.astimezone(LAGOS).date(), []
    for pid, lga, code in _lgas(conn):
        for day in (today, today + timedelta(days=1)):
            h = read.heat_day(conn, pid, lga, day)
            if h is None or h.category not in ("danger", "extreme_danger"):
                continue
            v = f"{h.category_value:.0f}"
            basis = {"en": "air temperature" if h.basis == "air_temperature" else "heat index",
                     "ha": "zafin iska" if h.basis == "air_temperature" else "ma'aunin zafi"}
            out.append(Candidate("heat", code, f"heat:{code}:{day}", False, {
                "en": f"up to {v} °C {_when(day, today, 'en')} ({basis['en']}), {label(h.category, 'en')} on the "
                      f"US National Weather Service heat index scale",
                "ha": f"har zuwa {v} °C {_when(day, today, 'ha')} ({basis['ha']}), matakin {label(h.category, 'ha')} "
                      f"a ma'aunin zafi na NWS"},
                {"en": f"Open-Meteo forecast, {_stamp(h.fetched_at)}", "ha": f"Hasashen Open-Meteo, {_stamp(h.fetched_at)}"}))
            break
    return out


def _p95(values: list[float]) -> float:
    s = sorted(values)
    return s[int(round(SEASONAL_PCT / 100 * (len(s) - 1)))]


def dust(conn, now: datetime) -> list[Candidate]:
    """Records today's highest AQI per LGA (air_daily), then fires on Hazardous or high for the time of year."""
    if read.freshness(conn, "air", now).stale:
        return []
    today, out = now.astimezone(LAGOS).date(), []
    for pid, lga, code in _lgas(conn):
        a = read.air_day(conn, pid, lga, today)
        if a is None:
            continue
        conn.execute("INSERT INTO air_daily (lga_pcode, day, aqi_max) VALUES (%s, %s, %s) ON CONFLICT (lga_pcode, day) "
                     "DO UPDATE SET aqi_max = greatest(air_daily.aqi_max, excluded.aqi_max)", (code, today, a.aqi_max))
        past = [float(r[0]) for r in conn.execute(
            "SELECT aqi_max FROM air_daily WHERE lga_pcode = %s AND day >= %s AND day < %s",
            (code, today - timedelta(days=AIR_HISTORY_DAYS), today))]
        seasonal = len(past) >= AIR_MIN_DAYS and a.aqi_max >= 151 and a.aqi_max > _p95(past)
        if a.category != "hazardous" and not seasonal:
            continue
        v = f"{a.aqi_max:.0f}"
        high = ({"en": f", higher than {SEASONAL_PCT}% of the last {len(past)} days",
                 "ha": f", fiye da kashi {SEASONAL_PCT} na kwanaki {len(past)} da suka gabata"}
                if a.category != "hazardous" else {"en": "", "ha": ""})
        out.append(Candidate("dust", code, f"dust:{code}:{today}", False, {
            "en": f"US AQI up to {v} today (set by {a.aqi_by}), {label(a.category, 'en')}{high['en']}",
            "ha": f"US AQI har zuwa {v} yau ({a.aqi_by}), {label(a.category, 'ha')}{high['ha']}"},
            {"en": f"Open-Meteo Air Quality (Copernicus CAMS), {_stamp(a.fetched_at)}",
             "ha": f"Ingancin iska na Open-Meteo (Copernicus CAMS), {_stamp(a.fetched_at)}"}))
    conn.execute("DELETE FROM air_daily WHERE day < %s", (today - timedelta(days=AIR_KEEP_DAYS),))
    return out


def rivers(conn, now: datetime) -> list[Candidate]:
    if read.freshness(conn, "flood", now).stale:
        return []
    today, best = now.astimezone(LAGOS).date(), {}
    for day in (today + timedelta(days=i) for i in range(3)):
        for r in read.river_days(conn, day):
            code = pcode(r.lga)
            if r.rank > SEASONAL_PCT and code and (code not in best or r.rank > best[code][0].rank):
                best[code] = (r, day)
    out = []
    for code, (r, day) in best.items():
        q, pct = f"{r.discharge:g}", f"{r.rank:.0f}"
        out.append(Candidate("flood", code, f"flood:{r.point}:{day}", False, {
            "en": f"{r.point} forecast at {q} m³/s {_when(day, today, 'en')}, higher than {pct}% of days at this time "
                  f"of year since {r.since.year} (a GloFAS model estimate, not an official warning)",
            "ha": f"ana hasashen {r.point} zai kai {q} m³/s {_when(day, today, 'ha')}, fiye da kashi {pct} na "
                  f"kwanakin wannan lokaci tun {r.since.year} (ƙiyasin samfurin GloFAS, ba gargaɗin hukuma ba)"},
            {"en": f"Open-Meteo Flood API (GloFAS v4), {_stamp(r.fetched_at)}",
             "ha": f"Open-Meteo Flood API (GloFAS v4), {_stamp(r.fetched_at)}"}))
    return out


def _figs(lang: str, s, c, d) -> str:
    f = _t(lang)["fig"]
    return ", ".join(f[k].format(n=n) for k, n in (("suspected", s), ("confirmed", c), ("deaths", d)) if n is not None)


def recent_week(year: int, week: int, now: datetime, weeks: int = OUTBREAK_WEEKS) -> bool:
    """The epi week is within the last `weeks` weeks of now (a back-report the crawl just read is not news)."""
    try:
        start = date.fromisocalendar(year, week, 1)
    except ValueError:
        return False
    return timedelta(0) <= now.astimezone(LAGOS).date() - start <= timedelta(weeks=weeks)


def outbreaks(conn, now: datetime) -> list[Candidate]:
    rows = conn.execute("SELECT disease, year, epi_week, period, suspected, confirmed, deaths FROM outbreak_cases "
                        "WHERE listed AND fetched_at >= %s ORDER BY year, epi_week",
                        (now - timedelta(days=OUTBREAK_DAYS),)).fetchall()
    latest = {}                                  # only each disease's newest report, and only a recent one
    for row in rows:
        if recent_week(row[1], row[2], now):
            latest[row[0]] = row
    out = []
    for disease, year, week, period, s, c, d in latest.values():
        prev = conn.execute("SELECT suspected, confirmed FROM outbreak_cases WHERE disease = %s AND listed AND "
                            "(year, epi_week) < (%s, %s) ORDER BY year DESC, epi_week DESC LIMIT 1",
                            (disease, year, week)).fetchone()
        rose = ((s or 0) > (prev[0] or 0) or (c or 0) > (prev[1] or 0)) if prev else bool(s or c)
        if not rose:
            continue
        what = {lang: (f"NCDC week {week} {year} report: {_t(lang)['names'][disease]} in Sokoto, "
                       f"{_figs(lang, s, c, d)} ({period_label(lang, period, year)})" if lang == "en" else
                       f"rahoton NCDC na mako {week} {year}: {_t(lang)['names'][disease]} a Sokoto, "
                       f"{_figs(lang, s, c, d)} ({period_label(lang, period, year)})") for lang in ("en", "ha")}
        source = {"en": f"NCDC situation report, week {week} {year}",
                  "ha": f"Rahoton halin da ake ciki na NCDC, mako {week} {year}"}
        out += [Candidate("outbreak", code, f"ncdc:{disease}:{year}-{week}", False, what, source)
                for code in sorted(PCODES.values())]
    return out


def all_candidates(conn, now: datetime | None = None) -> list[Candidate]:
    """Every trigger, official advisories first (so they take the day's one alert for a hazard and LGA)."""
    now = now or datetime.now(timezone.utc)
    return advisories(conn, now) + heat(conn, now) + dust(conn, now) + rivers(conn, now) + outbreaks(conn, now)
