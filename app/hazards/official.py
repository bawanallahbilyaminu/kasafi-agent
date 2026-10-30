"""Official sources in answers (docs/hazard-and-services.md section 5): the planner capabilities advisories,
flood_outlook_official and outbreaks_ncdc.

- Advisories lead every hazard answer: the current official warnings for the place and hazard, quoted verbatim with
  their issue date; an expired one is dropped, except the newest of the last 90 days, marked expired. The model
  forecasts follow, labelled as such (app/hazards/answer.py).
- Outbreaks: Sokoto's figures from NCDC's newest situation report per disease, with its epi week and the period the
  figures cover. The only guidance quoted is official guidance (a current notice from the Ministry of Health or
  NCDC); otherwise the reply refers to a health worker. No other health advice (CLAUDE.md rule 5).
- Official outlooks (NIHSA Annual Flood Outlook, NiMet Seasonal Climate Prediction): an outlook in the advisories
  table, or the document in the library (then the document path answers it, with its pages); otherwise the reply
  says it isn't available, never a forecast passed off as the outlook.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from app.hazards import read

SOURCE_NAMES = {"nema_alerts": "NEMA", "sokoto_sema": "Sokoto State Government (SEMA)",
                "sokoto_moh": "Sokoto State Ministry of Health", "nihsa_afo": "NIHSA", "nimet_scp": "NiMet",
                "ncdc_sitreps": "NCDC"}
# the advisory hazards each forecast layer leads with
LAYER_HAZARDS = {"heat": ("heat",), "rain": ("rain", "flood"), "air": ("dust",), "flood": ("flood",),
                 "fires": ("fire",)}
CURRENT = {"alert": timedelta(days=10), "notice": timedelta(days=21), "report": timedelta(days=14)}
SHOW_EXPIRED = timedelta(days=90)
DISEASES = ("cholera", "csm", "lassa", "measles", "diphtheria")
DISEASE_WORDS = {"cholera": r"cholera|kwalara|gastroenteritis|amai da gudawa",
                 "csm": r"meningitis|\bcsm\b|sankarau",
                 "lassa": r"lassa", "measles": r"measles|kyanda|ƙyanda",
                 "diphtheria": r"diphtheria|mashaƙo|mashako"}
OUTBREAK = re.compile(r"(?i)\boutbreaks?\b|epidemic|disease cases|ɓarkewar cuta|barkewar cuta|annoba")
OUTLOOK = {"flood": re.compile(r"(?i)flood outlook|\bafo\b|annual flood|flood risk (?:map|class|level)s?|"
                               r"nihsa|hasashen ambaliya"),
           "climate": re.compile(r"(?i)seasonal climate|\bscp\b|nimet.{0,40}(?:predict|season|outlook)|"
                                 r"rainy season|onset|cessation|hasashen damina|farkon damina|ƙarshen damina|"
                                 r"karshen damina")}
# a disease named with these words asks about cases ('any meningitis now?'), not coverage or budgets
CASE_WORDS = re.compile(r"(?i)\b(?:cases?|outbreaks?|now|currently|this (?:week|month|year)|any|deaths?|died|"
                        r"suspected|confirmed|spread|yanzu|akwai|ɓarke|barke|bulla|mutu)\b")
LIBRARY = {"flood": r"(?i)annual flood outlook", "climate": r"(?i)seasonal climate prediction"}
MONEY = re.compile(r"(?i)\b(?:budget\w*|allocat\w*|spent|spend\w*|naira|₦|kasafi\w*|kuɗi|kudi|ware|kashe)\b")

T = {
    "en": {"head": "⚠️ *Official warnings*", "model_head": "*Model forecasts (not official):*",
           "line": "{src}, issued {date}: “{text}”", "expired": "{src}, issued {date} (*expired*): “{text}”",
           "none": "No current official warning for {place} from NEMA, the Sokoto State Government (SEMA) or the "
                   "Ministry of Health (checked {when}).",
           "unchecked": "Official warnings haven't been checked yet.",
           "place_state": "Sokoto State", "place_lga": "{lga} LGA",
           "names": {"cholera": "Cholera", "csm": "Meningitis (CSM)", "lassa": "Lassa fever", "measles": "Measles",
                     "diphtheria": "Diphtheria"},
           "out_head": "🦠 *Disease outbreaks in Sokoto (NCDC situation reports)*",
           "row": "*{name}*: NCDC report for epi week {week} {year} ({date}): Sokoto {figs} (period in the report: "
                  "“{period}”).",
           "fig": {"suspected": "{n:,} suspected", "confirmed": "{n:,} confirmed", "deaths": "{n:,} deaths"},
           "no_figs": "listed, without figures",
           "not_listed": "*{name}*: Sokoto isn't listed in NCDC's report for epi week {week} {year} ({date}).",
           "none_read": "*{name}*: no NCDC report read yet.",
           "old": "NCDC hasn't published a newer {name} report (checked {when}); this one is {weeks} weeks old, so it "
                  "doesn't show the situation now.",
           "guidance": "Official guidance, {src}, issued {date}: “{text}”",
           "health_worker": "For symptoms, prevention or treatment, please see a health worker.",
           "src_row": "NCDC {name} situation report, epi week {week} {year}, page {page}",
           "sources": "Sources",
           "outlook_none": {"flood": "NIHSA's 2026 Annual Flood Outlook (the LGA flood-risk classes) isn't available "
                                     "to Kasafi yet: NIHSA's site doesn't offer the file to automated access.",
                            "climate": "NiMet's 2026 Seasonal Climate Prediction isn't available to Kasafi yet: "
                                       "NiMet's site blocks automated access and the prediction's files are no "
                                       "longer online."},
           "outlook_alt": {"flood": "Kasafi can give the GloFAS river forecast instead (a model, not the outlook): "
                                    "ask “Is the Rima high near Goronyo?”",
                           "climate": "Kasafi can give the rain forecast for the next 3 days instead (a model, not "
                                      "NiMet's prediction)."},
           "outlook_head": {"flood": "🌊 *Official flood outlook*", "climate": "🌦️ *Official seasonal prediction*"}},
    "ha": {"head": "⚠️ *Gargaɗin hukuma*", "model_head": "*Hasashen samfuri (ba na hukuma ba):*",
           "line": "{src}, an fitar {date}: “{text}”", "expired": "{src}, an fitar {date} (*wa'adinsa ya ƙare*): "
                                                               "“{text}”",
           "none": "Babu gargaɗin hukuma na yanzu ga {place} daga NEMA, Gwamnatin Jihar Sokoto (SEMA) ko "
                   "Ma'aikatar Lafiya (an duba {when}).",
           "unchecked": "Ba a duba gargaɗin hukuma ba tukuna.",
           "place_state": "Jihar Sokoto", "place_lga": "Ƙaramar Hukumar {lga}",
           "names": {"cholera": "Kwalara", "csm": "Sankarau (CSM)", "lassa": "Zazzaɓin Lassa", "measles": "Ƙyanda",
                     "diphtheria": "Mashaƙo (diphtheria)"},
           "out_head": "🦠 *Ɓarkewar cututtuka a Sokoto (rahotannin NCDC)*",
           "row": "*{name}*: rahoton NCDC na makon epi {week} {year} ({date}): Sokoto {figs} (lokacin a rahoton: "
                  "“{period}”).",
           "fig": {"suspected": "{n:,} da ake zargi", "confirmed": "{n:,} da aka tabbatar", "deaths": "{n:,} sun mutu"},
           "no_figs": "an lissafa, ba alƙaluma",
           "not_listed": "*{name}*: ba a lissafa Sokoto a rahoton NCDC na makon epi {week} {year} ({date}) ba.",
           "none_read": "*{name}*: ba a karanta rahoton NCDC ba tukuna.",
           "old": "NCDC bai fitar da sabon rahoton {name} ba (an duba {when}); wannan ya yi makonni {weeks}, don haka "
                  "bai nuna halin da ake ciki yanzu ba.",
           "guidance": "Shawarar hukuma, {src}, an fitar {date}: “{text}”",
           "health_worker": "Don alamomi, kariya ko magani, don Allah a ga ma'aikacin lafiya.",
           "src_row": "Rahoton NCDC na {name}, makon epi {week} {year}, shafi {page}",
           "sources": "Madogara",
           "outlook_none": {"flood": "Hasashen Ambaliya na Shekara-shekara na NIHSA na 2026 (matakan haɗarin "
                                     "ambaliya na ƙananan hukumomi) bai samu ga Kasafi ba tukuna: shafin NIHSA ba ya "
                                     "ba da fayil ɗin ga shiga ta na'ura.",
                            "climate": "Hasashen Yanayi na Damina na NiMet na 2026 bai samu ga Kasafi ba tukuna: "
                                       "shafin NiMet yana hana shiga ta na'ura kuma fayilolin hasashen ba su kan "
                                       "intanet yanzu."},
           "outlook_alt": {"flood": "Kasafi zai iya ba da hasashen koguna na GloFAS maimakon haka (samfuri ne, ba "
                                    "hasashen hukuma ba): tambayi “Kogin Rima ya cika kusa da Goronyo?”",
                           "climate": "Kasafi zai iya ba da hasashen ruwan sama na kwana uku maimakon haka (samfuri "
                                      "ne, ba hasashen NiMet ba)."},
           "outlook_head": {"flood": "🌊 *Hasashen ambaliya na hukuma*",
                            "climate": "🌦️ *Hasashen damina na hukuma*"}},
}


@dataclass
class OfficialAnswer:
    text: str
    kind: str                   # outbreaks | outlook
    found: bool


def _t(lang: str) -> dict:
    return T.get(lang, T["en"])


def _date(d) -> str:
    return (d.astimezone(read.LAGOS) if isinstance(d, datetime) else d).strftime("%d %b %Y")


def _place(lang: str, where: read.Where) -> str:
    t = _t(lang)
    return t["place_state"] if where.kind == "state" or not where.lga else t["place_lga"].format(lga=where.lga)


def last_checked(conn, layer: str = "advisories") -> datetime | None:
    row = conn.execute("SELECT max(started_at) FROM hazard_fetch WHERE layer = %s AND ok", (layer,)).fetchone()
    return row[0] if row else None


def current(kind: str, issued: datetime, valid_until: datetime | None, now: datetime) -> bool:
    """A stated end date decides; else an alert counts for 10 days, a notice 21, an outlook to the end of its year."""
    if valid_until is not None:
        return now <= valid_until
    if kind == "outlook":
        return issued.year == now.year
    return now - issued <= CURRENT.get(kind, CURRENT["alert"])


def advisories_for(conn, hazards: tuple[str, ...] | list[str], where: read.Where, now: datetime | None = None
                   ) -> tuple[list, tuple | None]:
    """(current advisories, the newest expired one of the last 90 days or None) for these hazards and the place: an
    LGA's own and the state-wide ones; for the state, all of them. Rows: (source, kind, issued_at, valid_until,
    text, url)."""
    now = now or datetime.now(timezone.utc)
    rows = conn.execute(
        "SELECT source, kind, issued_at, valid_until, text, url, lgas, state_wide FROM advisories "
        "WHERE hazard = ANY(%s) AND issued_at >= %s ORDER BY issued_at DESC",
        (list(hazards), now - timedelta(days=400))).fetchall()
    here = [r for r in rows if where.kind == "state" or not where.lga_pcode or r[7] or where.lga_pcode in (r[6] or [])]
    live = [r[:6] for r in here if current(r[1], r[2], r[3], now)]
    gone = next((r[:6] for r in here if not current(r[1], r[2], r[3], now) and now - r[2] <= SHOW_EXPIRED), None)
    return live, gone


def official_lines(conn, lang: str, layers: list[str], where: read.Where, now: datetime | None = None) -> list[str]:
    """The 'Official warnings' section that leads a hazard answer, or [] when it has nothing to add."""
    t = _t(lang)
    hazards = tuple(dict.fromkeys(h for x in layers for h in LAYER_HAZARDS.get(x, ())))
    if not hazards:
        return []
    checked = last_checked(conn)
    if checked is None:
        return [t["head"], t["unchecked"]]
    live, gone = advisories_for(conn, hazards, where, now)
    out = [t["head"]]
    out += [t["line"].format(src=SOURCE_NAMES.get(s, s), date=_date(i), text=x) + f"\n{u}"
            for s, _k, i, _v, x, u in live[:3]]
    if not live and gone:
        s, _k, i, _v, x, u = gone
        out.append(t["expired"].format(src=SOURCE_NAMES.get(s, s), date=_date(i), text=x) + f"\n{u}")
    if not live:
        out.append(t["none"].format(place=_place(lang, where),
                                    when=checked.astimezone(read.LAGOS).strftime("%d %b %H:%M")))
    return out + ["", t["model_head"]]


# --- outbreaks -------------------------------------------------------------------------------------------------

def diseases_asked(question: str) -> list[str]:
    """The diseases a question names; 'any outbreak?' alone means all five; [] when it names none."""
    named = [d for d, pat in DISEASE_WORDS.items() if re.search(rf"(?i){pat}", question or "")]
    return named or (list(DISEASES) if OUTBREAK.search(question or "") else [])


def route(question: str, measures: list[str] | None = None) -> str:
    """'outbreaks', 'outlook_flood', 'outlook_climate' or '' (a budget question about cholera is a budget one)."""
    q, measures = question or "", measures or []
    if MONEY.search(q):
        return ""
    if "outbreak_cases" in measures or (diseases_asked(q) and (CASE_WORDS.search(q) or OUTBREAK.search(q))):
        return "outbreaks"
    which = outlook_asked(q) or ("flood" if "flood_outlook" in measures else
                                 "climate" if "seasonal_outlook" in measures else "")
    return f"outlook_{which}" if which else ""


def outbreak_answer(conn, question: str, lang: str, today: date) -> OfficialAnswer:
    t = _t(lang)
    out, sources, found = [t["out_head"]], [], False
    for d in diseases_asked(question) or list(DISEASES):
        name = t["names"][d]
        row = conn.execute(
            "SELECT year, epi_week, report_date, period, suspected, confirmed, deaths, listed, page, fetched_at "
            "FROM outbreak_cases WHERE disease = %s ORDER BY year DESC, epi_week DESC LIMIT 1", (d,)).fetchone()
        if row is None:
            out.append(t["none_read"].format(name=name))
            continue
        year, week, rdate, period, sus, conf, deaths, listed, page, _ = row
        when = _date(rdate) if rdate else str(year)
        found = True
        if not listed:
            out.append(t["not_listed"].format(name=name, week=week, year=year, date=when))
        else:
            figs = [t["fig"][k].format(n=v) for k, v in (("suspected", sus), ("confirmed", conf), ("deaths", deaths))
                    if v is not None]
            out.append(t["row"].format(name=name, week=week, year=year, date=when, period=period,
                                       figs=", ".join(figs) or t["no_figs"]))
            sources.append(t["src_row"].format(name=name, week=week, year=year, page=page))
        if rdate and (weeks := (today - rdate).days // 7) >= 8:
            checked = last_checked(conn, "ncdc")
            out.append(t["old"].format(name=name, weeks=weeks, when=_date(checked) if checked else _date(today)))
        live, _ = advisories_for(conn, (d,), read.Where("state"))
        out += [t["guidance"].format(src=SOURCE_NAMES.get(s, s), date=_date(i), text=x)
                for s, _k, i, _v, x, _u in live[:1] if s in ("sokoto_moh", "ncdc_sitreps")]
    out += ["", t["health_worker"]]
    if sources:
        out.append(f"📄 *{t['sources']}:* " + "; ".join(sources))
    return OfficialAnswer("\n".join(out), "outbreaks", found)


# --- official outlooks -----------------------------------------------------------------------------------------

def outlook_asked(question: str) -> str:
    """'flood' (NIHSA's Annual Flood Outlook) or 'climate' (NiMet's Seasonal Climate Prediction), or ''."""
    if MONEY.search(question or ""):
        return ""
    return next((k for k, pat in OUTLOOK.items() if pat.search(question or "")), "")


def in_library(conn, which: str) -> bool:
    return conn.execute("SELECT 1 FROM documents WHERE title ~* %s LIMIT 1",
                        (LIBRARY[which].removeprefix("(?i)"),)).fetchone() is not None


def outlook_answer(conn, which: str, lang: str, where: read.Where, now: datetime | None = None
                   ) -> OfficialAnswer | None:
    """An official outlook from the advisories table; None when the document is in the library (the document path
    answers it, with its pages); otherwise says it isn't available."""
    t = _t(lang)
    hazards = ("flood",) if which == "flood" else ("rain", "heat", "dust")
    live, _ = advisories_for(conn, hazards, where, now)
    outlooks = [r for r in live if r[1] == "outlook"]
    if outlooks:
        out = [t["outlook_head"][which]] + [t["line"].format(src=SOURCE_NAMES.get(s, s), date=_date(i), text=x)
                                            + f"\n{u}" for s, _k, i, _v, x, u in outlooks[:2]]
        return OfficialAnswer("\n".join(out), "outlook", True)
    if in_library(conn, which):
        return None
    return OfficialAnswer("\n".join([t["outlook_head"][which], t["outlook_none"][which], "", t["outlook_alt"][which]]),
                          "outlook", False)
