"""Binding every cited figure to its row (external review, finding 01). The numeric check only shows a figure
occurs somewhere in the cited evidence; this binds each figure in the answer to the row or sentence that holds
it and checks the entity named next to the figure, the year, the unit and the kind (allocation vs spending)
against that row, in code, with no model call.

States (`Attribution.state`):
- "attribution checked": every figure sits in a row naming the entity the answer attributes it to;
- "figures checked": every figure is in the evidence, but a binding could not be established (the answer names
  the entity in Hausa, or names none next to the figure);
- "unsupported": a figure contradicts its row (another entity's figure, another year, another unit, spending
  given as an allocation, a swapped comparison) or is not in the evidence at all.
A contradiction is rejected or corrected (app/agent/answer.py: the answer is composed again with the mismatch
named, then refused); "figures checked" is answerable and said as such in show working and the trace.
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
        "year", "years", "quarter", "performance", "report", "sokoto", "state", "government", "ministry", "office",
        "agency", "commission", "board", "department", "capital", "recurrent", "overhead", "personnel", "which",
        "than", "more", "less", "about", "under", "over", "also", "only", "into", "while", "kasafi", "miliyan",
        "biliyan", "naira", "shekara", "shekarar", "kuɗi", "kudi", "kashe", "ware", "wannan", "yana", "tana"}
_WORD = re.compile(r"[A-Za-zƁɓƊɗƘƙƳƴ'’][A-Za-zƁɓƊɗƘƙƳƴ'’-]{3,}")


@dataclass
class Claim:
    sentence: str
    number: str                       # as written
    value: float
    scaled: bool                      # written with a scale word ("200 million")
    terms: set[str]                   # entity words next to the figure (the segment before it)
    years: set[str]
    kind: str                         # spend | alloc | ''


@dataclass
class Binding:
    claim: Claim
    span: str = ""                    # the evidence row or sentence holding the figure
    found: bool = False
    bound: bool = False               # the entity named next to the figure is in the span
    problem: str = ""                 # entity | year | unit | kind | missing


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
    return {w for w in words if len(w) >= 4 and w not in STOP and not YEAR.fullmatch(w)}


def _kind(text: str) -> str:
    s, a = bool(SPEND.search(text)), bool(ALLOC.search(text))
    return "spend" if s and not a else "alloc" if a and not s else ""


def sentences(text: str) -> list[str]:
    text = re.sub(r"\[\d+\]|\[L\d+\]", " ", text or "")
    parts = re.split(r"(?<=[.;!?])\s+(?=[A-ZƁƊƘƳ•]|\d)|\n+|(?<=\s)•\s*", text)
    return [p.strip(" •-") for p in parts if p and p.strip(" •-")]


def claims_from(text: str) -> list[Claim]:
    """Every figure in the answer with the entity words written just before it (back to the previous figure or
    the sentence start), its years and its kind. Years and page references are not figures."""
    out = []
    for s in sentences(text):
        clean = PAGE_REF.sub(" ", s)
        last = 0
        for m in NUMBER.finditer(clean):
            num, scale = m.group(1), m.group(2)
            digits = num.replace(",", "").replace(".", "")
            if len(digits) < 2 or (YEAR.fullmatch(num) and not scale) or re.fullmatch(r"\d{1,2}", num) and not scale:
                continue
            if clean[m.end():m.end() + 2].strip().startswith("%"):
                continue                                   # a share, not a money figure
            segment = clean[last:m.start()]
            terms = _terms(segment) or _terms(clean)
            out.append(Claim(s, m.group(0).strip(), _value(num, scale), bool(scale), terms, set(YEAR.findall(clean)),
                             _kind(clean)))
            last = m.end()
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


def _kind_at(span: str, claim: Claim) -> str:
    """The kind of the column holding the figure: the label just before it (back to the previous cell or figure),
    else the row's kind, when the row is of one kind."""
    m = _match(span, claim)
    if m is None:
        return _kind(span)
    before = span[:m.start()]
    figures = [x.end() for x in NUMBER.finditer(before) if len(re.sub(r"[^\d]", "", x.group(1))) >= 4]   # not Q1-Q3
    cut = max(before.rfind("|"), max(figures, default=-1))
    label = before[cut + 1:] if cut >= 0 else before
    return _kind(label) or _kind(span)


def _digits_only(span: str, claim: Claim) -> bool:
    """The same digits with another scale ('200 billion' against a 200,000,000.00 row): a unit problem."""
    want = re.sub(r"[^\d]", "", claim.number).lstrip("0").rstrip("0")
    return bool(want) and any(re.sub(r"[^\d]", "", m.group(1)).lstrip("0").rstrip("0") == want
                              and not _holds(m.group(0), claim) for m in NUMBER.finditer(span))


def bind(answer_text: str, evidence, entity_names: list[str] | None = None) -> Attribution:
    """Each figure of the answer against the cited evidence. `entity_names` (the plan's resolved names and codes)
    bind a figure whose sentence names the entity in another language."""
    spans = _spans(evidence)
    names = [n.lower() for n in entity_names or [] if n]
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
        # the entity: the words written next to the figure must be in the row holding it; a contradiction is when
        # those words sit in another row that holds a different figure
        in_span = [(s, h, y) for s, h, y in holding if c.terms and any(t in s.lower() for t in c.terms)
                   or names and any(n in s.lower() for n in names)]
        if in_span:
            b.bound, b.span = True, in_span[0][0]
            s, h, y = in_span[0]
        else:
            b.span = holding[0][0]
            s, h, y = holding[0]
            elsewhere = [x for x, _, _ in spans if c.terms and any(t in x.lower() for t in c.terms) and not _holds(x, c)
                         and NUMBER.search(x)]
            if elsewhere and c.terms:
                b.problem = "entity"
                problems.append(f"entity: {c.number} is in the row '{s[:80]}', not in the row of "
                                f"'{', '.join(sorted(c.terms))[:60]}'")
                bindings.append(b)
                continue
        if c.years:
            near = set(YEAR.findall(s)) | set(YEAR.findall(h)) | ({str(y)} if y else set())
            if near and not c.years & near:
                b.problem = "year"
                problems.append(f"year: {c.number} is given for {'/'.join(sorted(c.years))}, the evidence says "
                                f"{'/'.join(sorted(near))}")
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
        bindings.append(b)
    if any(b.problem for b in bindings):
        state = "unsupported"
    elif bindings and all(b.bound for b in bindings):
        state = "attribution checked"
    else:
        state = "figures checked"
    return Attribution(state, bindings, problems)


STATE_WORDS = {
    "en": {"attribution checked": "Verification: attribution checked ({n} figure(s), each in a row naming what the "
                                  "answer attributes it to).",
           "figures checked": "Verification: figures checked ({n} figure(s) found in the cited pages; the rows could "
                              "not be matched to the names in the answer).",
           "calculation checked": "Verification: calculation checked (the rows and arithmetic were done in code).",
           "unsupported": "Verification: unsupported ({problems})."},
    "ha": {"attribution checked": "Tabbatarwa: an tabbatar da mallakar alƙaluma (alƙaluma {n}, kowanne a layin abin da "
                                  "amsar ta danganta shi da shi).",
           "figures checked": "Tabbatarwa: an duba alƙaluma (an samu alƙaluma {n} a shafukan da aka ambata; ba a iya "
                              "haɗa layukan da sunayen da ke cikin amsar ba).",
           "calculation checked": "Tabbatarwa: an duba lissafi (an yi layuka da lissafin a cikin lambar shirin).",
           "unsupported": "Tabbatarwa: ba a tabbatar ba ({problems})."},
}


def state_line(state: str, lang: str, n: int = 0, problems: list[str] | None = None) -> str:
    w = STATE_WORDS.get(lang, STATE_WORDS["en"])
    return w.get(state, w["figures checked"]).format(n=n, problems="; ".join(problems or [])[:300])
