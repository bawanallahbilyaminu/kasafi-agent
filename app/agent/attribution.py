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

NUMBER = re.compile(r"(?<![\d.])(\d[\d,]*(?:\.\d+)?)(?:\s*(trillion|billion|million|thousand|biliyan|miliyan|dubu|bn|m|k)\b)?",
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
    r"(?i)(?P<upto>\b(?:by|to|through|as\s+at|as\s+of|up\s+to|until|zuwa)\s+(?:the\s+(?:end\s+of\s+(?:the\s+)?)?)?)?"
    r"(?:\bQ(?P<a>[1-4])(?:\s*(?:-|–|to|zuwa)\s*Q?(?P<b>[1-4]))?\b"
    r"|\b(?P<ord>first|1st|second|2nd|third|3rd|fourth|4th)\s+quarter\b"
    r"|\bkwata\s+ta\s+(?P<hord>farko|biyu|uku|huɗu|hudu)\b"
    r"|\b(?P<h1>first\s+half|H1|half[-\s]year|rabin\s+shekara)\b"
    r"|\b(?P<nine>(?:first\s+)?nine\s+months|January\s*(?:-|–|to)\s*September|watanni\s+tara)\b)"
    r"(?P<tail>\s+(?:(?:19|20)\d\d\s+)?(?:report|BIR|budget\s+implementation|implementation\s+report|rahoto))?")


def periods(text: str) -> set[tuple[int, int]]:
    """The quarter ranges a text states, as (first, last): 'Q1' (1, 1), 'Q1-Q3' and 'by Q3' (1, 3), 'first half'
    (1, 2), 'nine months' (1, 3), Hausa 'kwata ta uku' (3, 3) and 'zuwa kwata ta uku' (1, 3). A report's name
    ('the Q3 2025 report') is not a period of a figure."""
    out = set()
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
    text = re.sub(r"\[\d+\]|\[L\d+\]", " ", text or "")
    parts = re.split(r"(?<=[.;!?])\s+(?=[A-ZƁƊƘƳ•]|\d)|\n+|(?<=\s)•\s*", text)
    return [p.strip(" •-") for p in parts if p and p.strip(" •-")]


def _figures(text: str) -> list[re.Match]:
    """The money figures of a text: not years, page numbers, quarter digits or short counts."""
    out = []
    for m in NUMBER.finditer(text):
        num, scale = m.group(1), m.group(2)
        digits = num.replace(",", "").replace(".", "")
        if len(digits) < 2 or (YEAR.fullmatch(num) and not scale) or re.fullmatch(r"\d{1,2}", num) and not scale:
            continue
        if text[m.end():m.end() + 2].strip().startswith("%"):
            continue                                   # a share, not a money figure
        out.append(m)
    return out


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
                             _kind(clean), per, segment))
    return out


def _spans(evidence) -> list[tuple[str, str, int | None]]:
    """(span, header, document year) for every row or sentence of every cited evidence item."""
    out = []
    for e in evidence:
        header = (e.text or "")[:300]
        for line in re.split(r"\n+|(?<=[.;])\s+(?=[A-Z])", e.text or ""):
            if line.strip():
                out.append((line.strip(), header, e.year))
    return out


def _is_money(m: re.Match) -> bool:
    num = m.group(1)
    return bool(m.group(2)) or ("," in num or "." in num) and len(re.sub(r"[^\d]", "", num)) >= 4


def _match(span: str, claim: Claim):
    """The match of the claim's figure in the span, or None."""
    for m in NUMBER.finditer(span):
        try:
            v = _value(m.group(1), m.group(2))
        except ValueError:
            continue
        if abs(v - claim.value) <= max(0.005, 0.0005 * abs(claim.value)):
            return m
    return None


def _holds(span: str, claim: Claim) -> bool:
    return _match(span, claim) is not None


def _cell(span: str, claim: Claim) -> str:
    """The label of the column holding the figure: the text just before it, back to the previous cell ('|') or
    money figure (years, codes and quarter digits are part of the label)."""
    m = _match(span, claim)
    if m is None:
        return ""
    before = span[:m.start()]
    figures = [x.end() for x in NUMBER.finditer(before) if _is_money(x)]
    cut = max(before.rfind("|"), max(figures, default=-1))
    return before[cut + 1:] if cut >= 0 else before


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
    """The kind of the column holding the figure, else the row's kind when the row is of one kind."""
    return _kind(_cell(span, claim)) or _kind(span)


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
        others = {frozenset(_terms(_label(s))) for s, _, _ in spans if c.terms <= _terms(s) and NUMBER.search(s)}
        if rows or len(others) <= 1:
            return "bound", rows or fits
        return ("bound", by_name) if by_name else ("ambiguous", fits)
    if by_name:
        return "bound", by_name
    if c.terms:
        # a contradiction: the claim's words name another row (all of them in it) that holds a different figure
        elsewhere = [s for s, _, _ in spans if c.terms <= _terms(s) and not _holds(s, c) and NUMBER.search(s)]
        if elsewhere and not any(c.terms & _terms(s) == c.terms for s, _, _ in holding):
            return "contradiction", holding
        if mine:
            named = [s for s, _, _ in spans if any(_names_in(s, n) for g in mine for n in g) and not _holds(s, c)]
            if named:
                return "contradiction", holding
    elif mine:
        named = [s for s, _, _ in spans if any(_names_in(s, n) for g in mine for n in g) and not _holds(s, c)]
        if named:
            return "contradiction", holding
    return "unknown", holding


def _years_of(span: str, header: str, doc_year: int | None, c: Claim) -> tuple[set[str], bool]:
    """(the years of the figure's column, settled?): the cell label's years; else the row's single year; else the
    header's single year; else the document's. Several years with no label on the cell: not settled."""
    cell = set(YEAR.findall(_cell(span, c)))
    if cell:
        return cell, True
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
    cell = periods(_cell(span, c))
    if cell:
        return cell, True
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
    for c in claims_from(answer_text):
        b = Binding(c)
        holding = [(s, h, y) for s, h, y in spans if _holds(s, c)]
        if not holding:
            if any(_digits_only(s, c) for s, _, _ in spans):
                b.problem = "unit"
                problems.append(f"unit: {c.number} is written with another scale than the evidence row")
            else:
                b.problem = "missing"
                problems.append(f"missing: {c.number} is not in the cited evidence")
            bindings.append(b)
            continue
        b.found = True
        how, rows = _entity(c, spans, groups)
        if how == "contradiction":
            s = rows[0][0]
            b.span, b.problem = s, "entity"
            problems.append(f"entity: {c.number} is in the row '{s[:80]}', not in the row of "
                            f"'{', '.join(sorted(c.terms))[:60] or 'the entity named'}'")
            bindings.append(b)
            continue
        s, h, y = (rows or holding)[0]
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
        if c.periods and pers and settled_period and not c.periods & pers:
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
