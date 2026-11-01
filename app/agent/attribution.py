"""Binding every cited figure to its row (external review, finding 01; follow-up review, finding 1). The numeric
check only shows a figure occurs somewhere in the cited evidence; this binds each figure in the answer to the row
or sentence that holds it and checks, in code with no model call, the claim's identity against that row:

- entity: every distinguishing word written next to the figure is in the row, and the row is the only one those
  words can mean ('Education' with a Basic and a Higher Education row binds neither; one shared word never
  binds). Plan names and Hausa aliases bind per entity: a name of another entity in the plan does not;
- year: the year of the figure's own column (the cell label: '2026 Approved Budget: 200,000,000.00'), else the
  row's or the header's single year, else the document's; a row, header or document with several years and no
  label on the cell leaves the year unbound (a 2026 budget prints 2025 columns too);
- period: Q1, Q2, Q1–Q3 ('by Q3', 'first nine months', 'zuwa kwata ta uku'), half year: the column's period
  against the claim's, as separate periods;
- unit (the scale word) and kind (allocation vs spending) against the column.

Survey and statistics tables (MICS, NDHS, the MPI, the labour force survey: the row is a geography or a
sub-population, the columns are indicators, the year is the survey's) are bound by geography instead: the figure's
row must be the geography the answer gives it (the Sokoto row, not the national 'Total' or the North West zone),
the indicator words must be on the page, the survey year must be the year the answer states, and a sub-population
the answer names (children 12–23 months) must be the row's or the table's. Percent figures count on these tables.
A figure given for Sokoto that sits in the Total row is a contradiction; a figure whose geography the answer
doesn't state is "figures checked", never a refusal.

States (`Attribution.state`):
- "attribution checked": every figure is bound on entity, and on year and period where the answer states them;
- "figures checked": every figure is in the evidence, but a complete binding could not be established (the row
  can't settle the year or the entity, or the answer names the entity in words the row doesn't use);
- "unsupported": a figure contradicts its row (another entity's figure, another year's or period's column,
  another unit, spending given as an allocation, a swapped comparison) or is not in the evidence at all.
A contradiction is composed again with the mismatch named, then refused (app/agent/answer.py); "figures checked"
is answerable and said as such in show working and the trace.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

NUMBER = re.compile(r"(?<![\d.])(\d(?:[\d,]*\d)?(?:\.\d+)?)(?:\s*(trillion|billion|million|thousand|biliyan|miliyan|dubu|bn|m|k)\b)?",
                    re.IGNORECASE)
SCALE = {"trillion": 1e12, "billion": 1e9, "bn": 1e9, "biliyan": 1e9, "million": 1e6, "m": 1e6, "miliyan": 1e6,
         "thousand": 1e3, "k": 1e3, "dubu": 1e3}
YEAR = re.compile(r"\b(?:19|20)\d\d\b")
PAGE_REF = re.compile(r"(?i)\b(?:pages?|shafi(?:\s+na)?|p\.)\s*\d{1,4}\b")
SPEND = re.compile(r"(?i)\b(?:spent|spending|actual\w*|expenditure\s+to\s+date|performance|disbursed|utili[sz]ed|"
                   r"year\s+to\s+date|ytd|kashe\w*|aka\s+kashe)\b")
ALLOC = re.compile(r"(?i)\b(?:allocat\w*|approved|budgeted|appropriat\w*|aka\s+ware|an\s+ware|amince\w*)\b")
STOP = {"the", "this", "that", "with", "from", "were", "was", "for", "and", "its", "has", "had", "have", "been",
        "total", "budget", "budgets", "allocation", "allocations", "allocated", "approved", "revised", "spent",
        "spending", "actual", "amount", "amounts", "figure", "figures", "million", "billion", "thousand", "naira",
        "year", "years", "quarter", "quarters", "performance", "report", "sokoto", "state", "government", "ministry",
        "office", "agency", "commission", "board", "department", "capital", "recurrent", "overhead", "personnel",
        "which", "than", "more", "less", "about", "under", "over", "also", "only", "into", "while", "kasafi",
        "miliyan", "biliyan", "naira", "shekara", "shekarar", "kuɗi", "kudi", "kashe", "ware", "wannan", "yana",
        "tana", "expenditure", "got", "received", "receive", "gets", "given", "first", "second", "third", "fourth",
        "nine", "months", "half", "ma'aikatar", "ma’aikatar", "hukumar", "samu", "kwata", "zuwa", "watanni",
        "tara", "farko", "biyu", "huɗu", "hudu", "whose", "their", "there", "where", "what", "much", "many"}
_WORD = re.compile(r"[A-Za-zƁɓƊɗƘƙƳƴ'’][A-Za-zƁɓƊɗƘƙƳƴ'’-]{3,}")
# Hausa words for the sector an entity names, to the English the tables print (the plan's names are per entity)
HAUSA = {"lafiya": "health", "ilimi": "education", "ilimin": "education", "firamare": "basic", "noma": "agriculture",
         "aikin": "agriculture", "ruwa": "water", "muhalli": "environment", "ayyuka": "works", "matasa": "youth",
         "wasanni": "sports", "kasuwanci": "commerce", "shari'a": "justice", "addini": "religious",
         "zurfi": "higher", "gidaje": "housing", "sufuri": "transport", "mata": "women"}
_ORD = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3, "fourth": 4, "4th": 4,
        "farko": 1, "biyu": 2, "uku": 3, "huɗu": 4, "hudu": 4}
_PERIOD = re.compile(
    r"(?i)(?P<upto>\b(?:by|to|through|as\s+at|as\s+of|up\s+to|until|zuwa|at)\s+(?:the\s+)?(?:end\s+(?:of\s+)?(?:the\s+)?)?)?"
    r"(?:\bQ(?P<a>[1-4])(?:\s*(?:-|–|to|zuwa)\s*Q?(?P<b>[1-4]))?\b"
    r"|\b(?P<ord>first|1st|second|2nd|third|3rd|fourth|4th)\s+quarter\b"
    r"|\bkwata\s+ta\s+(?P<hord>farko|biyu|uku|huɗu|hudu)\b"
    r"|\b(?P<h1>first\s+half|H1|half[-\s]year|rabin\s+shekara)\b"
    r"|\b(?P<nine>(?:first\s+)?nine\s+months|January\s*(?:-|–|to)\s*September|watanni\s+tara)\b)"
    r"(?P<tail>\s+(?:(?:19|20)\d\d\s+)?(?:report|BIR|budget\s+implementation|implementation\s+report|rahoto))?")


_REPORT_NAME = re.compile(r"(?i)\b(?:report|BIR|bulletin|rahoto\w*)\s+Q[1-4](?:\s*[-–]\s*Q?[1-4])?(?:\s+(?:19|20)\d\d)?")


def periods(text: str) -> set[tuple[int, int]]:
    """The quarter ranges a text states, as (first, last): 'Q1' (1, 1), 'Q1-Q3' and 'by Q3' (1, 3), 'first half'
    (1, 2), 'nine months' (1, 3), Hausa 'kwata ta uku' (3, 3) and 'zuwa kwata ta uku' (1, 3). A report's name
    ('the Q3 2025 report') is not a period of a figure."""
    out = set()
    text = _REPORT_NAME.sub(" ", text or "")
    for m in _PERIOD.finditer(text or ""):
        if m.group("tail"):
            continue
        if m.group("h1"):
            out.add((1, 2))
            continue
        if m.group("nine"):
            out.add((1, 3))
            continue
        if m.group("a"):
            a, b = int(m.group("a")), int(m.group("b") or m.group("a"))
        else:
            a = b = _ORD[(m.group("ord") or m.group("hord")).lower()]
        out.add((1, b) if m.group("upto") and a == b else (min(a, b), max(a, b)))
    return out


@dataclass
class Claim:
    sentence: str
    number: str                       # as written
    value: float
    scaled: bool                      # written with a scale word ("200 million")
    terms: set[str]                   # entity words next to the figure (the segment before it)
    years: set[str]                   # the years written next to the figure, else in the sentence
    kind: str                         # spend | alloc | ''
    periods: set[tuple[int, int]] = field(default_factory=set)
    segment: str = ""                 # the words written next to the figure
    percent: bool = False             # written with % (a survey indicator; a budget share is not bound)
    window: str = ""                  # the text from the previous figure to the next one


@dataclass
class Binding:
    claim: Claim
    span: str = ""                    # the evidence row or sentence holding the figure
    found: bool = False
    bound: bool = False               # entity, year and period all settled by the row
    problem: str = ""                 # entity | year | period | unit | kind | missing


@dataclass
class Attribution:
    state: str                        # attribution checked | figures checked | unsupported
    bindings: list[Binding] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.state != "unsupported"

    def feedback(self) -> str:
        """What to tell the model on a retry."""
        return "; ".join(self.problems[:4])


def _value(num: str, scale: str | None) -> float:
    v = float(num.replace(",", ""))
    return v * SCALE[scale.lower()] if scale else v


def _terms(text: str) -> set[str]:
    words = (re.sub(r"['’]s$", "", w.lower()).strip("'’-") for w in _WORD.findall(text))     # Health's -> health
    out = set()
    for w in words:
        w = HAUSA.get(w, w)
        if len(w) >= 4 and w not in STOP and not YEAR.fullmatch(w):
            out.add(w)
    return out


def _kind(text: str) -> str:
    s, a = bool(SPEND.search(text)), bool(ALLOC.search(text))
    return "spend" if s and not a else "alloc" if a and not s else ""


def sentences(text: str) -> list[str]:
    """The answer's sentences and items: a citation mark followed by a capital ends one ('… 42.8 [1] National …':
    the items of an answer run together with spaces)."""
    text = re.sub(r"(?:\[\d+\]|\[L\d+\])\s+(?=[A-ZƁƊƘƳ•])", ". ", text or "")
    text = re.sub(r"\[\d+\]|\[L\d+\]", " ", text)
    parts = re.split(r"(?<=[.;!?])\s+(?=[A-ZƁƊƘƳ•]|\d)|\n+|(?<=\s)•\s*", text)
    return [p.strip(" •-") for p in parts if p and p.strip(" •-")]


_PER = re.compile(r"(?i)\b(?:per|a\s+kowane|kowane|cikin)\s*$")


def _figures(text: str) -> list[re.Match]:
    """The figures of a text: not years, page numbers, quarter digits, short counts or a rate's base ('per 1,000
    live births'). A figure written with % is kept (survey indicators); the binding skips it when no survey table
    is cited."""
    out = []
    for m in NUMBER.finditer(text):
        num, scale = m.group(1), m.group(2)
        digits = num.replace(",", "").replace(".", "")
        if _PER.search(text[:m.start()]):
            continue
        if _is_percent(text, m) and len(digits) >= 1 and not YEAR.fullmatch(num):
            out.append(m)                              # '23%': a survey indicator
            continue
        if len(digits) < 2 or (YEAR.fullmatch(num) and not scale) or re.fullmatch(r"\d{1,2}", num) and not scale:
            continue
        out.append(m)
    return out


def _is_percent(text: str, m: re.Match) -> bool:
    return text[m.end():m.end() + 2].strip().startswith("%") or \
        bool(re.match(r"(?i)\s*(?:percent|per\s+cent|kashi)", text[m.end():m.end() + 12]))


def claims_from(text: str) -> list[Claim]:
    """Every figure in the answer with the entity words written just before it (back to the previous figure or
    the sentence start), its years and periods (written next to it, else in the sentence) and its kind."""
    out = []
    for s in sentences(text):
        clean = PAGE_REF.sub(" ", s)
        figs = _figures(clean)
        for i, m in enumerate(figs):
            last = figs[i - 1].end() if i else 0
            nxt = figs[i + 1].start() if i + 1 < len(figs) else len(clean)
            segment = clean[last:m.start()]
            window = clean[last:nxt]
            terms = _terms(segment) or _terms(clean)
            years = set(YEAR.findall(window)) or set(YEAR.findall(clean))
            per = periods(window) or periods(clean)
            out.append(Claim(s, m.group(0).strip(), _value(m.group(1), m.group(2)), bool(m.group(2)), terms, years,
                             _kind(clean), per, segment, _is_percent(clean, m), window))
    return out


# --- table kinds: budget rows, survey tables, running text ---------------------------------------------------------

BUDGET_TITLE = re.compile(r"(?i)\b(?:budget|appropriation|implementation\s+report|expenditure|financial\s+statement|"
                          r"audited|mtef|fiscal|accountability|revenue|kasafi)\b")
SURVEY_TITLE = re.compile(r"(?i)\b(?:survey|mics|ndhs|dhs|index|statistics|labour\s+force|poverty|census|assessment|"
                          r"bulletin|situation\s+report|cpi|displacement|tracking|matrix|profil\w*|monitoring)\b")


def kind_of(title: str) -> str:
    """budget | survey | text, from the document's title."""
    t = title or ""
    if BUDGET_TITLE.search(t):
        return "budget"
    if SURVEY_TITLE.search(t):
        return "survey"
    return "text"


ZONES = {"north west": "zone:nw", "north-west": "zone:nw", "northwest": "zone:nw", "north east": "zone:ne",
         "north-east": "zone:ne", "north central": "zone:nc", "north-central": "zone:nc", "south west": "zone:sw",
         "south-west": "zone:sw", "south east": "zone:se", "south-east": "zone:se", "south south": "zone:ss",
         "south-south": "zone:ss", "arewa maso yamma": "zone:nw", "arewa maso gabas": "zone:ne",
         "arewa ta tsakiya": "zone:nc"}
STATES = ("abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue", "borno", "cross river", "delta",
          "ebonyi", "edo", "ekiti", "enugu", "gombe", "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi", "kogi",
          "kwara", "lagos", "nasarawa", "niger", "ogun", "ondo", "osun", "oyo", "plateau", "rivers", "taraba",
          "yobe", "zamfara", "fct", "abuja")
NATIONAL = re.compile(r"(?i)\b(?:nigeria(?:'s|’s)?|national(?:ly)?|nationwide|country-?wide|the\s+country|"
                      r"all\s+of\s+nigeria|ƙasa\s+baki\s+ɗaya|kasa\s+baki\s+daya|faɗin\s+ƙasa|fadin\s+kasa|"
                      r"najeriya|na\s+ƙasa|na\s+kasa|ƙasa\s+gaba\s+ɗaya|gaba\s+ɗayan\s+ƙasa|matsakaicin\s+ƙasa|"
                      r"ƙasar\s+najeriya|kasar\s+najeriya)\b")
SOKOTO = re.compile(r"(?i)\bsokoto\b(?!\s+(?:north|south|ta\s+arewa|ta\s+kudu))|\bjihar\b|\bthe\s+state\b")
AGE = re.compile(r"(?i)\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(?:months?|years?|watanni|shekaru)?\b|"
                 r"\bunder[-\s]?(?:age\s+|the\s+age\s+of\s+)?(?:5|five)\b|\b(?:ƙasa|kasa)\s+da\s+shekar\w*\s+(?:5|biyar)\b")


def geo_of(text: str) -> set[str]:
    """The geographies a claim names: sokoto, national, a zone, urban/rural, another state."""
    low = (text or "").lower()
    out = set()
    if SOKOTO.search(text or ""):
        out.add("sokoto")
    if NATIONAL.search(text or ""):
        out.add("national")
    for z, key in ZONES.items():
        if re.search(rf"\b{re.escape(z)}\b", low):
            out.add(key)
    for st in STATES:
        if re.search(rf"\b{re.escape(st)}\b", low):
            out.add(f"state:{st}")
    if re.search(r"\burban\b|\bbirni\b", low):
        out.add("urban")
    if re.search(r"\brural\b|\bƙauye\b|\bkauye\b", low):
        out.add("rural")
    return out


_CONNECT = re.compile(r"(?i),|;|\(|\)|\band\b|\bbut\b|\bagainst\b|\bcompared\b|\bwhile\b|\bvs\.?\b|\bversus\b|"
                      r"\bwhereas\b|\bda\b|\bamma\b|\bidan\s+aka\s+kwatanta\b")


_CONTINUES = re.compile(r"(?i)^\s*(?:%|percent|per\s+cent)?\s*(?:nationally|statewide|state-wide|in|for|among|of|across|"
                        r"at|within|a|na|ga|daga|cikin|wa)\b")


def claim_geography(c: Claim) -> set[str]:
    """The place a figure is given for: the words just before it, back to the last connector ('In Sokoto 22.5%',
    'and in North West 47.4%'); else the words just after it up to the next connector ('57.3% nationally'); else
    the sentence when it names one place only. Several places and no cue: not settled, never a contradiction."""
    before = _CONNECT.split(c.segment)[-1]
    if geo := geo_of(before):
        return geo
    after = c.window[len(c.segment):]
    after = re.sub(r"^\s*[\d.,]+%?", "", after)                 # the figure itself
    after_part = _CONNECT.split(after)[0]
    # '22.5% of children under 5 in Sokoto had…', '57.3% nationally': the words after the figure belong to it only
    # when they continue its phrase; a new item starting with a capital ('42.8 National stunted …') does not
    if _CONTINUES.match(after_part) and len(after_part.split()) <= 12 and (geo := geo_of(after_part)):
        return geo
    in_sentence = geo_of(c.sentence)
    return in_sentence if len(in_sentence) == 1 else set()


def claim_age_groups(c: Claim) -> set[str]:
    """The age group a figure is given for, like its geography: the words just before it back to the last
    connector, else just after it, else the sentence when it names one age group only (a sentence giving the
    12-23 months vaccination figure and the under-5 registration figure assigns neither to the other)."""
    before = _CONNECT.split(c.segment)[-1]
    if ages := _ages(before):
        return ages
    after = re.sub(r"^\s*[\d.,]+%?", "", c.window[len(c.segment):])
    after_part = _CONNECT.split(after)[0]
    if _CONTINUES.match(after_part) and len(after_part.split()) <= 12 and (ages := _ages(after_part)):
        return ages
    in_sentence = _ages(c.sentence)
    return in_sentence if len(in_sentence) == 1 else set()


def _survey_label(span: str) -> str:
    """A survey row's label: the words before its first figure ('Sokoto', 'North West', 'Total', '12-23')."""
    m = re.match(r"\s*([^\d(]*?)(?=\s*[\d(]|$)", span)
    return (m.group(1) if m else span).strip(" :|")


def row_geo(label: str) -> str:
    """The geography a survey row is for, or '' for a sub-population row ('Male', '12-23', 'Poorest')."""
    low = label.lower().strip()
    if not low:
        return ""
    if low.startswith("sokoto"):
        return "sokoto"
    if low.startswith(("total", "nigeria", "national", "all")):
        return "national"
    for z, key in ZONES.items():
        if low.startswith(z):
            return key
    for st in STATES:
        if low.startswith(st):
            return f"state:{st}"
    if low.startswith("urban"):
        return "urban"
    if low.startswith("rural"):
        return "rural"
    return ""


def _ages(text: str) -> set[str]:
    """Age groups as '12-23' or 'under5', whatever the unit words."""
    return {f"{m.group(1)}-{m.group(2)}" if m.group(1) else "under5" for m in AGE.finditer(text or "")}


GEO_TERMS = {"sokoto", "nigeria", "national", "nationally", "nationwide", "state", "states", "zone", "zones", "north",
             "south", "east", "west", "central", "urban", "rural", "children", "women", "people", "figure", "figures",
             "share", "percent", "percentage", "rate", "overall", "najeriya", "jihar", "ƙasa", "kasa", "yankin",
             "arewa", "kudu", "gabas", "yamma", "birni", "ƙauye", "kauye"} | {s for s in ()}
GEO_WORDS = {"national": "the national (Total) figure", "sokoto": "the Sokoto figure", "zone:nw": "the North West figure",
             "zone:ne": "the North East figure", "zone:nc": "the North Central figure", "zone:sw": "the South West figure",
             "zone:se": "the South East figure", "zone:ss": "the South South figure", "urban": "the urban figure",
             "rural": "the rural figure"}


INDICATOR_SYNONYMS = {"stunt": ["height-for-age", "stunting"], "waste": ["weight-for-height", "wasting"],
                      "under": ["weight-for-age", "underweight"], "vacci": ["immuni", "vaccin"], "immun": ["vaccin", "immuni"],
                      "regis": ["regist"], "liter": ["litera"], "anaem": ["anaem", "anem"], "anemi": ["anaem", "anem"],
                      "morta": ["mortal", "death"], "death": ["mortal", "death"], "anten": ["antenatal", "anc"],
                      "contr": ["contracept", "family planning", "demand"], "unmet": ["unmet", "demand"],
                      "poore": ["wealth", "quintile"], "wealt": ["wealth", "quintile"], "insec": ["insecur"],
                      "hunge": ["insecur", "hunger"], "skill": ["skilled", "assistance"], "deliv": ["deliver"],
                      "fully": ["basic antigens", "all antigens", "fully"], "rigak": ["vaccin", "immuni"],
                      "rajis": ["regist"], "koriy": ["height-for-age", "stunting"], "karat": ["litera"]}


def _indicator_on_pages(words: set[str], texts: list[str]) -> bool:
    """A word of the claim (its 5-letter stem, or a synonym the tables use: 'stunted' is 'Height-for-age') on any
    cited survey page, the table's start page included."""
    low = " ".join(texts).lower()
    for w in words:
        stem = w[:5]
        if stem in low:
            return True
        if any(syn in low for syn in INDICATOR_SYNONYMS.get(stem, [])):
            return True
    return False


def _survey(c: Claim, holding: list, spans: list | None = None) -> tuple[str, str, object]:
    """('bound' | 'unknown' | 'contradiction', the problem text, the span): a survey figure against the geography,
    indicator, year and sub-population the answer gives it."""
    claim_geo = claim_geography(c)
    # 'under 5' is the population of most child tables, never a contradiction; a range (12-23 months) is checked
    claim_ages = claim_age_groups(c) - {"under5"}
    rows = [(x, row_geo(_survey_label(x[0]))) for x in holding]
    # a national table's rows are indicators, not places ('No vaccinations 0.3 17.7 17.8'): they are the national
    # figures when the page is the survey's national table ('Nigeria MICS, 2021' in its header, no 'State' rows)
    if "national" in claim_geo:
        rows = [(x, g or ("national" if "nigeria" in x[1].lower() and not re.search(r"(?m)^\s*State\s*$", x[4])
                          else g)) for x, g in rows]
    # with an age group named, the pages printing it come first ('12-23 months' in the title)
    if claim_ages:
        rows.sort(key=lambda r: not (claim_ages & _ages(r[0][4])))
        holding = [x for x, _ in rows]
    pick = None
    if claim_geo:
        fit = [x for x, g in rows if g in claim_geo]
        if not fit:
            geos = {g for _, g in rows if g}
            if geos:
                g = sorted(geos)[0]
                what = GEO_WORDS.get(g, f"the {g.split(':')[-1].title()} figure")
                return ("contradiction", f"geography: {c.number} is {what} in the row '{_survey_label(holding[0][0])}', "
                                         f"given for {'/'.join(sorted(claim_geo))}", holding[0])
            # sub-population rows only: every row an age group, none the answer's, is a contradiction
            row_ages = [_ages(_survey_label(x[0])) for x in holding]
            if claim_ages and all(row_ages) and not any(claim_ages & a for a in row_ages):
                return ("contradiction", f"subpopulation: {c.number} is the row '{_survey_label(holding[0][0])}', given "
                                         f"for {', '.join(sorted(claim_ages))}", holding[0])
            return ("unknown", "", holding[0])
        pick = fit[0]
    else:
        pick = holding[0]
    span, header, year, kind, full = pick
    # the survey year: the year the answer gives the figure must be the survey's (or printed on the page)
    if c.years and year and str(year) not in c.years and not any(y in full for y in c.years):
        return ("contradiction", f"year: {c.number} is from the {year} survey, given for {'/'.join(sorted(c.years))}", pick)
    # an age group the answer names must be on the page, when every page holding the figure prints age groups
    if claim_ages:
        page_ages = _ages(full)
        if page_ages and not claim_ages & page_ages and all(_ages(x[4]) for x in holding):
            return ("contradiction", f"subpopulation: {c.number} is for {', '.join(sorted(page_ages))[:40]}, given for "
                                     f"{', '.join(sorted(claim_ages))}", pick)
    if not claim_geo:
        return ("unknown", "", pick)
    # the indicator: a word of the claim on the cited survey pages (the table's title or column headers, on the page
    # the table starts on when the figure is on a continuation page); geography words don't count
    words = {w for w in c.terms if w not in GEO_TERMS}
    texts = list(dict.fromkeys([full] + [x[4] for x in (spans or []) if x[3] == "survey"]))
    if words and not _indicator_on_pages(words, texts):
        return ("unknown", "", pick)
    return ("bound", "", pick)


def _spans(evidence) -> list[tuple[str, str, int | None, str, str]]:
    """(span, header, document year, table kind, the whole item text) for every row or sentence of every cited
    evidence item."""
    out = []
    for e in evidence:
        header = (e.text or "")[:300]
        kind = kind_of(getattr(e, "title", "") or "")
        for line in re.split(r"\n+|(?<=[.;])\s+(?=[A-Z])", e.text or ""):
            if line.strip():
                out.append((line.strip(), header, e.year, kind, e.text or ""))
    return out


def _is_money(m: re.Match) -> bool:
    num = m.group(1)
    return bool(m.group(2)) or ("," in num or "." in num) and len(re.sub(r"[^\d]", "", num)) >= 4


def _matches(span: str, claim: Claim) -> list[re.Match]:
    """Every match of the claim's figure in the span. A percent written without decimals ('57%') matches the
    table's '57.3'."""
    tol = max(0.005, 0.0005 * abs(claim.value))
    if claim.percent and "." not in claim.number:
        tol = 0.55
    out = []
    for m in NUMBER.finditer(span):
        try:
            v = _value(m.group(1), m.group(2))
        except ValueError:
            continue
        if abs(v - claim.value) <= tol:
            out.append(m)
    return out


def _match(span: str, claim: Claim):
    """The first match of the claim's figure in the span, or None."""
    ms = _matches(span, claim)
    return ms[0] if ms else None


def _holds(span: str, claim: Claim) -> bool:
    return _match(span, claim) is not None


def _cells(span: str, claim: Claim) -> list[str]:
    """The labels of every column holding the figure: the text just before each match, back to the previous cell
    ('|') or money figure (years, codes and quarter digits are part of the label). A row can print one amount in
    two columns (the 2027 and 2028 out-year estimates)."""
    out = []
    for m in _matches(span, claim):
        before = span[:m.start()]
        figures = [x.end() for x in NUMBER.finditer(before) if _is_money(x)]
        cut = max(before.rfind("|"), max(figures, default=-1))
        out.append(before[cut + 1:] if cut >= 0 else before)
    return out


def _cell(span: str, claim: Claim) -> str:
    cells = _cells(span, claim)
    return cells[0] if cells else ""


def _label(span: str) -> str:
    """The row's own label: up to its first cell, colon or money figure ('Ministry of Basic Education')."""
    cut = len(span)
    for sep in ("|", ":"):
        i = span.find(sep)
        if i >= 0:
            cut = min(cut, i)
    money = [m.start() for m in NUMBER.finditer(span) if _is_money(m)]
    if money:
        cut = min(cut, money[0])
    return span[:cut]


def _kind_at(span: str, claim: Claim) -> str:
    """The kinds of the columns holding the figure: the claim's own kind when any column has it, else the first
    column's, else the row's kind when the row is of one kind."""
    kinds = [_kind(c) for c in _cells(span, claim)]
    if claim.kind in kinds:
        return claim.kind
    return next((k for k in kinds if k), "") or _kind(span)


def _digits_only(span: str, claim: Claim) -> bool:
    """The same digits with another scale ('200 billion' against a 200,000,000.00 row): a unit problem."""
    want = re.sub(r"[^\d]", "", claim.number).lstrip("0").rstrip("0")
    return bool(want) and any(re.sub(r"[^\d]", "", m.group(1)).lstrip("0").rstrip("0") == want
                              and not _holds(m.group(0), claim) for m in NUMBER.finditer(span))


def _groups(entity_names) -> list[list[str]]:
    """The plan's names per entity: a flat list is one entity; a list of lists is one list per entity."""
    if not entity_names:
        return []
    if all(isinstance(x, str) for x in entity_names):
        return [[x.lower() for x in entity_names if x]]
    return [[x.lower() for x in g if x] for g in entity_names if any(g)]


def _names_in(text: str, name: str) -> bool:
    """A name is in a text when all of its distinguishing words are (or it is a code written in full)."""
    low = text.lower()
    if re.fullmatch(r"[\d\s]+", name):
        return name.strip() in low
    words = _terms(name)
    return bool(words) and all(w in _terms(low) or w in low for w in words)


def _tabular(span: str) -> bool:
    """A table row (cells, two money figures, or a short label before one figure: 'Ministry of Basic Education
    allocation: 100,000,000.00'), where another entity's words beside a figure contradict; a running-text
    sentence ('The Primary Healthcare subsector was allocated a total of ₦7,210,210,444.94 in the 2026 …') naming
    the entity does not: its next sentence holds the spending figure without repeating the name."""
    if "|" in span or len([m for m in NUMBER.finditer(span) if _is_money(m)]) >= 2:
        return True
    return bool(_is_money_span(span)) and len(_label(span).split()) <= 8


def _is_money_span(span: str) -> bool:
    return any(_is_money(m) for m in NUMBER.finditer(span))


def _entity(c: Claim, spans, groups) -> tuple[str, list]:
    """('bound' | 'ambiguous' | 'contradiction' | 'unknown', the rows holding the figure that the claim's words
    or its entity's names fit)."""
    holding = [x for x in spans if _holds(x[0], c)]
    fits = [x for x in holding if c.terms and c.terms <= _terms(x[0])]
    # the plan's names bind per entity: the group the claim's own words name, or the only one in the plan
    mine = [g for g in groups if any(_names_in(c.segment or c.sentence, n) for n in g)] or (groups if len(groups) == 1 else [])
    by_name = [x for x in holding if any(_names_in(x[0], n) for g in mine for n in g)]
    if fits:
        # one shared word never binds: a row with more distinguishing words than the claim ('Basic Education')
        # binds only when no other row of the evidence also fits the claim's words with another label
        rows = [x for x in fits if _terms(_label(x[0])) <= c.terms]
        others = {frozenset(_terms(_label(x[0]))) for x in spans if c.terms <= _terms(x[0]) and NUMBER.search(x[0])}
        if rows or len(others) <= 1:
            return "bound", rows or fits
        return ("bound", by_name) if by_name else ("ambiguous", fits)
    if by_name:
        return "bound", by_name
    if c.terms:
        # a contradiction: the claim's words name another row (all of them in it) that holds a different figure
        elsewhere = [x[0] for x in spans if c.terms <= _terms(x[0]) and not _holds(x[0], c) and NUMBER.search(x[0])
                     and _tabular(x[0])]
        if elsewhere and not any(c.terms & _terms(x[0]) == c.terms for x in holding):
            return "contradiction", holding
        if mine:
            named = [x[0] for x in spans if any(_names_in(x[0], n) for g in mine for n in g) and not _holds(x[0], c)
                     and _tabular(x[0])]
            if named:
                return "contradiction", holding
    elif mine:
        named = [x[0] for x in spans if any(_names_in(x[0], n) for g in mine for n in g) and not _holds(x[0], c)
                 and _tabular(x[0])]
        if named:
            return "contradiction", holding
    return "unknown", holding


def _years_of(span: str, header: str, doc_year: int | None, c: Claim) -> tuple[set[str], bool]:
    """(the years of the figure's columns, settled?): the cell labels' years (a column whose year the answer names
    settles it); else the row's single year; else the header's single year; else the document's. Several years
    with no label on the cell: not settled."""
    cells = [set(YEAR.findall(x)) for x in _cells(span, c)]
    cells = [x for x in cells if x]
    if cells:
        fit = [x for x in cells if x & c.years]
        return (fit[0] if fit else set().union(*cells)), True
    row = set(YEAR.findall(span))
    if len(row) == 1:
        return row, True
    if len(row) > 1:
        return row, False
    head = set(YEAR.findall(header))
    if len(head) == 1:
        return head, True
    if len(head) > 1:
        return head, False
    return ({str(doc_year)}, True) if doc_year else (set(), False)


def _periods_of(span: str, header: str, c: Claim) -> tuple[set[tuple[int, int]], bool]:
    cells = [periods(x) for x in _cells(span, c)]
    cells = [x for x in cells if x]
    if cells:
        fit = [x for x in cells if x & c.periods]
        return (fit[0] if fit else set().union(*cells)), True
    row = periods(span)
    if len(row) == 1:
        return row, True
    if len(row) > 1:
        return row, False
    head = periods(header)
    return (head, len(head) == 1) if head else (set(), True)


def bind(answer_text: str, evidence, entity_names=None) -> Attribution:
    """Each figure of the answer against the cited evidence. `entity_names`: the plan's names per entity (a list
    of lists: resolved name, the words the question used, the code), or a flat list for one entity."""
    spans = _spans(evidence)
    groups = _groups(entity_names)
    bindings: list[Binding] = []
    problems: list[str] = []
    any_survey = any(x[3] == "survey" for x in spans)
    for c in claims_from(answer_text):
        if c.percent and not any_survey:
            continue                                   # a budget share: not a figure of a row
        b = Binding(c)
        holding = [x for x in spans if _holds(x[0], c)]
        if not holding:
            if any(_digits_only(x[0], c) for x in spans):
                b.problem = "unit"
                problems.append(f"unit: {c.number} is written with another scale than the evidence row")
            else:
                b.problem = "missing"
                problems.append(f"missing: {c.number} is not in the cited evidence")
            bindings.append(b)
            continue
        b.found = True
        survey_rows = [x for x in holding if x[3] == "survey"]
        if survey_rows and len(survey_rows) == len(holding) or (survey_rows and not c.terms):
            how, why, pick = _survey(c, survey_rows, spans)
            b.span = pick[0]
            if how == "contradiction":
                b.problem = why.split(":")[0]
                problems.append(why)
            b.bound = how == "bound"
            bindings.append(b)
            continue
        how, rows = _entity(c, spans, groups)
        if how == "contradiction":
            s = rows[0][0]
            b.span, b.problem = s, "entity"
            problems.append(f"entity: {c.number} is in the row '{s[:80]}', not in the row of "
                            f"'{', '.join(sorted(c.terms))[:60] or 'the entity named'}'")
            bindings.append(b)
            continue
        s, h, y = (rows or holding)[0][:3]
        b.span = s
        entity_ok = how == "bound"
        # the year of the figure's own column
        years, settled_year = _years_of(s, h, y, c)
        if c.years and years and settled_year and not c.years & years:
            b.problem = "year"
            problems.append(f"year: {c.number} is given for {'/'.join(sorted(c.years))}, its column is for "
                            f"{'/'.join(sorted(years))}")
            bindings.append(b)
            continue
        # the period of the figure's column: Q1 and Q1–Q3 are different periods
        pers, settled_period = _periods_of(s, h, c)
        cell_kinds = [_kind(x) for x in _cells(s, c)]
        if c.periods and pers and settled_period and not c.periods & pers and "alloc" not in cell_kinds \
                and c.kind != "alloc":
            def show(p):
                return f"Q{p[0]}" if p[0] == p[1] else f"Q{p[0]}-Q{p[1]}"
            b.problem = "period"
            problems.append(f"period: {c.number} is given for {', '.join(show(p) for p in sorted(c.periods))}, its "
                            f"column is for {', '.join(show(p) for p in sorted(pers))}")
            bindings.append(b)
            continue
        if c.kind:
            row_kind = _kind_at(s, c) or _kind(h)
            if row_kind and row_kind != c.kind:
                b.problem = "kind"
                problems.append(f"kind: {c.number} is {'spending' if row_kind == 'spend' else 'an allocation'} in the "
                                f"row, given as {'spending' if c.kind == 'spend' else 'an allocation'}")
                bindings.append(b)
                continue
        b.bound = (entity_ok and (not c.years or settled_year and bool(years))
                   and (not c.periods or settled_period and bool(pers)))
        bindings.append(b)
    if any(b.problem for b in bindings):
        state = "unsupported"
    elif bindings and all(b.bound for b in bindings):
        state = "attribution checked"
    else:
        state = "figures checked"
    return Attribution(state, bindings, problems)


STATE_WORDS = {
    "en": {"attribution checked": "Verification: attribution checked ({n} figure(s), each in its own row and column: "
                                  "the entity, year and period the answer gives it).",
           "figures checked": "Verification: figures checked ({n} figure(s) found in the cited pages; which row, year "
                              "or period each belongs to could not be fully established).",
           "calculation checked": "Verification: calculation checked (the rows and arithmetic were done in code).",
           "unsupported": "Verification: unsupported ({problems})."},
    "ha": {"attribution checked": "Tabbatarwa: an tabbatar da mallakar alƙaluma (alƙaluma {n}, kowanne a layinsa da "
                                  "ginshiƙinsa: abin, shekara da lokacin da amsar ta ba shi).",
           "figures checked": "Tabbatarwa: an duba alƙaluma (an samu alƙaluma {n} a shafukan da aka ambata; ba a iya "
                              "tabbatar da layi, shekara ko lokacin kowanne gaba ɗaya ba).",
           "calculation checked": "Tabbatarwa: an duba lissafi (an yi layuka da lissafin a cikin lambar shirin).",
           "unsupported": "Tabbatarwa: ba a tabbatar ba ({problems})."},
}


def state_line(state: str, lang: str, n: int = 0, problems: list[str] | None = None) -> str:
    w = STATE_WORDS.get(lang, STATE_WORDS["en"])
    return w.get(state, w["figures checked"]).format(n=n, problems="; ".join(problems or [])[:300])
