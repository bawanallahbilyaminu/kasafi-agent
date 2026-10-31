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
LAYER_HAZARDS = {"heat": ("heat",), "rain": ("rain", "dry_spell", "flood"), "air": ("dust",), "flood": ("flood",),
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
# a warning asked about: the hazard answer (official warnings first, then the outlook for these months)
WARNING = re.compile(r"(?i)\b(?:warn\w*|alerts?|advisor\w*|gargaɗ\w*|gargad\w*|faɗakarw\w*|fadakarw\w*|sanarw\w*)\b")
# a disease named with these words asks about cases ('any meningitis now?'), not coverage or budgets
CASE_WORDS = re.compile(r"(?i)\b(?:cases?|outbreaks?|now|currently|this (?:week|month|year)|any|deaths?|died|"
                        r"suspected|confirmed|spread|yanzu|akwai|ɓarke|barke|bulla|mutu)\b")
LIBRARY = {"flood": r"(?i)annual flood outlook", "climate": r"(?i)seasonal climate prediction"}
MONEY = re.compile(r"(?i)\b(?:budget\w*|allocat\w*|spent|spend\w*|naira|₦|kasafi\w*|kuɗi|kudi|ware|kashe)\b")

T = {
    "en": {"head": "⚠️ *Official warnings*", "model_head": "*Model forecasts (not official):*",
           "line": "{src}, issued {date}: “{text}”", "expired": "{src}, issued {date} (*expired*): “{text}”",
           "none": "No active alert from NEMA, the Sokoto State Government (SEMA) or the Ministry of Health for "
                   "{place} as of {when}.",
           "stale_none": "Last checked {ago} ({when}); no alert from NEMA, the Sokoto State Government (SEMA) or "
                         "the Ministry of Health for {place} then.",
           "unchecked": "Kasafi has no successful check of NEMA, SEMA or Ministry of Health alerts yet, so it can't "
                        "say whether one is active.",
           "today": "{t} today", "yesterday": "yesterday {t}", "days_ago": "{n} days ago", "day_ago": "a day ago",
           "place_state": "Sokoto State", "place_lga": "{lga} LGA",
           "names": {"cholera": "Cholera", "csm": "Meningitis (CSM)", "lassa": "Lassa fever", "measles": "Measles",
                     "diphtheria": "Diphtheria"},
           "out_head": "🦠 *Disease outbreaks in Sokoto (NCDC situation reports)*",
           "row": "*{name}*: NCDC report for epi week {week} {year} ({date}): Sokoto {figs} ({period}).",
           "fig": {"suspected": "{n:,} suspected", "confirmed": "{n:,} confirmed", "deaths": "{n:,} deaths"},
           "fig_none": {"suspected": "suspected not reported", "confirmed": "confirmed not reported",
                        "deaths": "deaths not reported"},
           "periods": {"since": "totals since week {w} {y}", "weeks": "totals for weeks {a}-{b} of {y}",
                       "months": "totals for {m1}-{m2} {y}", "week": "week {w} only",
                       "printed": "period in the report: “{p}”"},
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
           "outlook_head": {"flood": "🌊 *Official flood outlook*", "climate": "🌦️ *Official seasonal prediction*"},
           "doc_line": "{src}, {title}, page {page} (about {covers}; issued {issued}){mark}: “{text}”",
           "expired_mark": " (*expired*)",
           "outlook_now": "📘 *Official outlooks for these months (seasonal, not warnings):*",
           "issued": "issued", "item": "• {covers}, page {page}{table}: “{text}”",
           "lga_more": "{n} more statements are for single LGAs (onset, season end, rainfall, dry spells): ask for "
                       "your LGA.",
           "outlook_note": "Quoted as printed; where the prediction's tables and its text differ, both are shown. "
                           "A later update replaces the original only for the months it covers."},
    "ha": {"head": "⚠️ *Gargaɗin hukuma*", "model_head": "*Hasashen samfuri (ba na hukuma ba):*",
           "line": "{src}, an fitar {date}: “{text}”", "expired": "{src}, an fitar {date} (*wa'adinsa ya ƙare*): "
                                                               "“{text}”",
           "none": "Babu gargaɗi mai aiki daga NEMA, Gwamnatin Jihar Sokoto (SEMA) ko Ma'aikatar Lafiya ga {place} "
                   "har zuwa {when}.",
           "stale_none": "An duba ƙarshe {ago} ({when}); babu gargaɗi daga NEMA, Gwamnatin Jihar Sokoto (SEMA) ko "
                         "Ma'aikatar Lafiya ga {place} a lokacin.",
           "unchecked": "Kasafi bai yi nasarar duba gargaɗin NEMA, SEMA ko Ma'aikatar Lafiya ba tukuna, don haka ba "
                        "zai iya cewa akwai ko babu ba.",
           "today": "{t} yau", "yesterday": "jiya {t}", "days_ago": "kwanaki {n} da suka wuce",
           "day_ago": "kwana ɗaya da ya wuce",
           "place_state": "Jihar Sokoto", "place_lga": "Ƙaramar Hukumar {lga}",
           "names": {"cholera": "Kwalara", "csm": "Sankarau (CSM)", "lassa": "Zazzaɓin Lassa", "measles": "Ƙyanda",
                     "diphtheria": "Mashaƙo (diphtheria)"},
           "out_head": "🦠 *Ɓarkewar cututtuka a Sokoto (rahotannin NCDC)*",
           "row": "*{name}*: rahoton NCDC na makon epi {week} {year} ({date}): Sokoto {figs} ({period}).",
           "fig": {"suspected": "{n:,} da ake zargi", "confirmed": "{n:,} da aka tabbatar", "deaths": "{n:,} sun mutu"},
           "fig_none": {"suspected": "ba a ba da adadin da ake zargi ba", "confirmed": "ba a ba da adadin da aka "
                        "tabbatar ba", "deaths": "ba a ba da adadin mace-mace ba"},
           "periods": {"since": "jimilla tun makon {w} {y}", "weeks": "jimilla na makonni {a}-{b} na {y}",
                       "months": "jimilla na {m1}-{m2} {y}", "week": "makon {w} kawai",
                       "printed": "lokacin a rahoton: “{p}”"},
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
                            "climate": "🌦️ *Hasashen damina na hukuma*"},
           "doc_line": "{src}, {title}, shafi {page} (game da {covers}; an fitar {issued}){mark}: “{text}”",
           "expired_mark": " (*wa'adinsa ya ƙare*)",
           "outlook_now": "📘 *Hasashen hukuma na waɗannan watanni (na lokaci, ba gargaɗi ba):*",
           "issued": "an fitar", "item": "• {covers}, shafi {page}{table}: “{text}”",
           "lga_more": "Akwai ƙarin bayanai {n} na ƙananan hukumomi ɗaya-ɗaya (farkon damina, ƙarshenta, yawan "
                       "ruwa, lokutan fari): tambayi ƙaramar hukumarka.",
           "outlook_note": "An kawo su yadda aka buga; inda teburorin hasashen da rubutunsa suka bambanta, an nuna "
                           "duka biyun. Sabon bayani yana maye gurbin na farko ne kawai a watannin da ya shafa."},
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


@dataclass
class Adv:
    source: str
    kind: str
    issued_at: datetime
    valid_until: datetime | None
    text: str
    url: str
    lgas: list
    state_wide: bool
    doc_id: str | None = None           # an outlook from a library document, cited by page and the months it covers
    page: int | None = None
    covers: str | None = None
    issued_label: str | None = None
    title: str = ""


def advisories_for(conn, hazards: tuple[str, ...] | list[str], where: read.Where, now: datetime | None = None,
                   undated_outlooks: bool = False) -> tuple[list[Adv], Adv | None]:
    """(current advisories, the newest expired one of the last 90 days or None) for these hazards and the place: an
    LGA's own first, then the state-wide ones; for the state, all of them. A document's outlook counts as current
    only within its stated months (valid_until); one without them only when `undated_outlooks` (the outlook answer:
    'what did NiMet predict' asks about the whole season)."""
    now = now or datetime.now(timezone.utc)
    rows = [Adv(*r) for r in conn.execute(
        "SELECT source, kind, issued_at, valid_until, text, url, lgas, state_wide, doc_id, page, covers, "
        "issued_label, title FROM advisories WHERE hazard = ANY(%s) AND issued_at >= %s ORDER BY issued_at DESC",
        (list(hazards), now - timedelta(days=400))).fetchall()]
    here = [a for a in rows if where.kind == "state" or not where.lga_pcode or a.state_wide
            or where.lga_pcode in (a.lgas or [])]
    here.sort(key=lambda a: not (where.lga_pcode and where.lga_pcode in (a.lgas or [])))     # stable: own LGA first
    usable = [a for a in here if not (a.doc_id and a.valid_until is None and not undated_outlooks)]
    live = [a for a in usable if current(a.kind, a.issued_at, a.valid_until, now)]
    gone = next((a for a in usable if not current(a.kind, a.issued_at, a.valid_until, now)
                 and now - (a.valid_until or a.issued_at) <= SHOW_EXPIRED), None)
    return live, gone


def quote(lang: str, a: Adv, expired: bool = False) -> str:
    """An advisory verbatim: a post with its issue date and link; a document's outlook with its title, page, the
    months it covers and its issue date as printed."""
    t = _t(lang)
    src = SOURCE_NAMES.get(a.source, a.source)
    if a.doc_id:
        return t["doc_line"].format(src=src, title=a.title, page=a.page, covers=a.covers, issued=a.issued_label,
                                    text=a.text, mark=t["expired_mark"] if expired else "")
    return t["expired" if expired else "line"].format(src=src, date=_date(a.issued_at), text=a.text) + f"\n{a.url}"


def checked_status(lang: str, checked: datetime, place: str, now: datetime | None = None) -> str:
    """'No active alert ... as of 06:00 today' when the crawl last succeeded within 24 hours; otherwise when it last
    did ('Last checked 2 days ago (29 Oct); no alert then'). Never 'none' without a successful check."""
    t = _t(lang)
    now = now or datetime.now(timezone.utc)
    at, today = checked.astimezone(read.LAGOS), now.astimezone(read.LAGOS).date()
    clock = at.strftime("%H:%M")
    if now - checked <= timedelta(hours=24):
        when = t["today"].format(t=clock) if at.date() == today else t["yesterday"].format(t=clock)
        return t["none"].format(place=place, when=when)
    days = (today - at.date()).days
    ago = t["day_ago"] if days <= 1 else t["days_ago"].format(n=days)
    return t["stale_none"].format(place=place, ago=ago, when=at.strftime("%d %b"))


def official_lines(conn, lang: str, layers: list[str], where: read.Where, now: datetime | None = None) -> list[str]:
    """The 'Official warnings' section that leads a hazard answer (warnings, then the official outlooks for the
    current months), or [] when the question has no hazard."""
    t = _t(lang)
    hazards = tuple(dict.fromkeys(h for x in layers for h in LAYER_HAZARDS.get(x, ())))
    if not hazards:
        return []
    checked = last_checked(conn)
    live, gone = advisories_for(conn, hazards, where, now)
    warnings = [a for a in live if a.kind != "outlook"]
    outlooks = [a for a in live if a.kind == "outlook"]
    out = [t["head"]]
    if checked is None:
        out.append(t["unchecked"])
    else:
        out += [quote(lang, a) for a in warnings[:3]]
        if not warnings and gone and gone.kind != "outlook":
            out.append(quote(lang, gone, expired=True))
        if not warnings:
            out.append(checked_status(lang, checked, _place(lang, where), now))
    if outlooks:
        out += ["", t["outlook_now"], *[quote(lang, a) for a in outlooks[:3]]]
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
    if WARNING.search(q) and not outlook_asked(q):   # 'is there a flood warning?': warnings first, outlook after
        return ""
    which = outlook_asked(q) or ("flood" if "flood_outlook" in measures else
                                 "climate" if "seasonal_outlook" in measures else "")
    return f"outlook_{which}" if which else ""


_SINCE = re.compile(r"(?i)(?:epi[- ]?week|week|wk)\s*(\d{1,2})\s*,?\s*(20\d\d)\s*,?\s*[-–]")
_WEEKS = re.compile(r"(?i)(?:week|wk)s?\s*(\d{1,2})\s*[-–]\s*(?:week\s*)?(\d{1,2})\b")
_MONTHS = re.compile(r"(?i)\b(jan\w*|feb\w*|mar\w*|apr\w*|may|jun\w*|jul\w*|aug\w*|sep\w*|oct\w*|nov\w*|dec\w*)\s+"
                     r"(?:to|-|–)\s+(\w+)\s+(20\d\d)")
_WEEK = re.compile(r"(?i)^\s*(?:epi[- ]?)?week\s*(\d{1,2})\s*$")


def period_label(lang: str, period: str, year: int) -> str:
    """What a report's figures cover, in plain words: 'totals since week 19 2022', 'totals for weeks 1-40 of 2026',
    'totals for January-September 2026'; anything else quoted as printed."""
    p, t = period or "", _t(lang)["periods"]
    if m := _SINCE.search(p):
        return t["since"].format(w=int(m.group(1)), y=m.group(2))
    if m := _MONTHS.search(p):
        return t["months"].format(m1=m.group(1).capitalize(), m2=m.group(2).capitalize(), y=m.group(3))
    if m := _WEEKS.search(p):
        return t["weeks"].format(a=int(m.group(1)), b=int(m.group(2)), y=year)
    if m := _WEEK.match(p):
        return t["week"].format(w=int(m.group(1)))
    return t["printed"].format(p=p)


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
            figs = [t["fig"][k].format(n=v) if v is not None else t["fig_none"][k]   # a blank cell is never 0
                    for k, v in (("suspected", sus), ("confirmed", conf), ("deaths", deaths))]
            out.append(t["row"].format(name=name, week=week, year=year, date=when, period=period_label(lang, period, year),
                                       figs=", ".join(figs)))
            sources.append(t["src_row"].format(name=name, week=week, year=year, page=page))
        if rdate and (weeks := (today - rdate).days // 7) >= 8:
            checked = last_checked(conn, "ncdc")
            out.append(t["old"].format(name=name, weeks=weeks, when=_date(checked) if checked else _date(today)))
        live, _ = advisories_for(conn, (d,), read.Where("state"))
        out += [t["guidance"].format(src=SOURCE_NAMES.get(a.source, a.source), date=_date(a.issued_at), text=a.text)
                for a in live[:1] if a.source in ("sokoto_moh", "ncdc_sitreps")]
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


OUTLOOK_HAZARDS = {"flood": ("flood",), "climate": ("rain", "dry_spell", "heat", "dust")}
MOST_LINES = 12


def page_ranges(pages: list[int]) -> str:
    """'p. 12–16, 106' from [12, 13, 14, 15, 16, 106]."""
    ps = sorted(set(pages))
    if not ps:
        return ""
    runs, start = [], ps[0]
    for a, b in zip(ps, ps[1:] + [None]):
        if b != a + 1:
            runs.append(f"{start}–{a}" if a != start else f"{a}")
            start = b
    return "p. " + ", ".join(runs)


HEAT_WORDS = re.compile(r"(?i)temperat|heat|\bhot\b|harmattan|dust|zafi|ɗumi|dumi|hunturu|ƙura|kura\b")


def outlook_answer(conn, which: str, lang: str, where: read.Where, now: datetime | None = None,
                   question: str = "") -> OfficialAnswer | None:
    """This year's official outlooks for the place, every statement with its document, page and the months it
    covers (an update covers other months than the original prediction), oldest document first; the months
    already past are kept ('what did NiMet predict' asks about the season). For the state, statements about one
    LGA are counted, not listed. None when nothing is loaded but the document is in the library (the document
    path answers it); otherwise says it isn't available."""
    t = _t(lang)
    now = now or datetime.now(timezone.utc)
    hazards = OUTLOOK_HAZARDS[which]
    if which == "climate" and question:          # the rainy season unless temperature or dust is asked about too
        hazards = tuple(h for h in hazards if h not in ("heat", "dust") or HEAT_WORDS.search(question))
    rows = [Adv(*r) for r in conn.execute(
        "SELECT source, kind, issued_at, valid_until, text, url, lgas, state_wide, doc_id, page, covers, "
        "issued_label, title FROM advisories WHERE kind = 'outlook' AND hazard = ANY(%s) AND "
        "extract(year FROM issued_at) = %s ORDER BY issued_at, page", (list(hazards), now.year)).fetchall()]
    if where.kind == "state" or not where.lga_pcode:
        own, single = [a for a in rows if a.state_wide or not a.lgas], [a for a in rows if a.lgas and not a.state_wide]
    else:
        own = [a for a in rows if where.lga_pcode in (a.lgas or [])] + [a for a in rows if a.state_wide]
        single = []
    if own:
        out = [t["outlook_head"][which] + f" — {_place(lang, where)}"]
        for doc in dict.fromkeys(a.doc_id or a.source for a in own):
            items = [a for a in own if (a.doc_id or a.source) == doc][:MOST_LINES]
            first = items[0]
            out += ["", f"*{SOURCE_NAMES.get(first.source, first.source)}, {first.title.split(',')[0]}* "
                        f"({t['issued']} {first.issued_label or _date(first.issued_at)})"]
            out += [t["item"].format(covers=a.covers or "", page=a.page, text=a.text,
                                     table=f" ({a.title.split(', ', 1)[1]})" if "Table" in a.title else "")
                    for a in items]
        if single:
            out += ["", t["lga_more"].format(n=len(single))]
        out += ["", "📄 " + "; ".join(f"{SOURCE_NAMES.get(a.source, a.source)}, {a.title.split(',')[0]} "
                                      f"{page_ranges([x.page for x in own if (x.doc_id or x.source) == d and x.page])}"
                                      for d, a in {(a.doc_id or a.source): a for a in own}.items())]
        if any("Table" in a.title for a in own) and any("Table" not in a.title for a in own):
            out += ["", t["outlook_note"]]       # a table row next to the text's own figures: both shown
        return OfficialAnswer("\n".join(out), "outlook", True)
    if in_library(conn, which):
        return None
    return OfficialAnswer("\n".join([t["outlook_head"][which], t["outlook_none"][which], "", t["outlook_alt"][which]]),
                          "outlook", False)
