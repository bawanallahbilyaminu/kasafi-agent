"""The entity, level and period check on every budget answer, in code (no model call).

The planner's need says what was asked: an agency or unit (with its budget code once resolved), a level (a unit
inside a ministry, or the ministry with its agencies) and a period (a year, or a cumulative quarter). The rows the
answer actually used say what was given: a line answer's selected rows (code, document, year, period), or the
codes and documents in a page answer's cited evidence. A mismatch means the answer is about something else than
asked, and the answer is redone once with the mismatch named; what still doesn't match is said plainly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CODE = re.compile(r"\b(\d{12})\b")
REPORT = re.compile(r"^(?:bir|bpr)-(\d{4})-q(\d)$")
WORDS = {
    "en": {"entity": "The rows found are for {got}, not {asked}.",
           "level": "The row found is {got}, not {asked} on its own.",
           "period": "The figures found are for {got}, not {asked}.",
           "redo": "Use exactly {what}; if it isn't in the documents, say so."},
    "ha": {"entity": "Layukan da aka samu na {got} ne, ba na {asked} ba.",
           "level": "Layin da aka samu {got} ne, ba {asked} kaɗai ba.",
           "period": "Alƙaluman da aka samu na {got} ne, ba na {asked} ba.",
           "redo": "Use exactly {what}; if it isn't in the documents, say so."},
}


@dataclass
class Mismatch:
    kind: str            # entity | level | period
    asked: str
    got: str


@dataclass
class Used:
    """What an answer's rows are about."""
    codes: set[str]
    docs: set[str]
    years: set[int]
    quarters: set[int]   # the quarter a cumulative actual figure ends with (from its period 'q1_q2' or the report)


def used_rows(a) -> Used:
    """From a line answer's selections, else from the cited evidence (codes in the text; the report a figure is
    from gives its quarter)."""
    codes, docs, years, quarters = set(), set(), set(), set()
    res = getattr(a, "lines", None)
    if res is not None and res.selections:
        for s in res.selections:
            if s.line.code:
                codes.add(s.line.code)
            docs.add(s.line.doc_id)
            if s.cell.year:
                years.add(int(s.cell.year))
            if s.cell.measure == "actual":
                if m := re.search(r"q1_q(\d)", s.cell.period or ""):
                    quarters.add(int(m.group(1)))
                elif m := REPORT.match(s.line.doc_id):
                    quarters.add(int(m.group(2)))
        return Used(codes, docs, years, quarters)
    for e in getattr(a, "cited", None) or []:
        docs.add(e.doc_id)
        codes.update(CODE.findall(e.text or ""))
        if m := REPORT.match(e.doc_id):
            years.add(int(m.group(1)))
            quarters.add(int(m.group(2)))
    return Used(codes, docs, years, quarters)


def _asked_agencies(plan) -> list:
    return [e for e in (plan.need.entities if plan.need else []) if e.type in ("mda", "sub_agency") and e.code]


def check(plan, question: str, a, period=None, years: list[int] | None = None) -> list[Mismatch]:
    """Mismatches between what was asked and the rows used; [] when everything matches or nothing is checkable.
    `period` is app.agent.periods.asked_period(...); `years` the years the question names."""
    out: list[Mismatch] = []
    used = used_rows(a)
    if not (used.codes or used.docs):
        return out
    for e in _asked_agencies(plan):
        if not used.codes:
            continue                             # a page answer without codes: nothing to compare
        own = e.code in used.codes
        parent = e.code[:4] + "00000000"
        inside = any(c.startswith(e.code[:4]) for c in used.codes)
        if not own and not inside:
            got = ", ".join(sorted(used.codes)[:2])
            out.append(Mismatch("entity", f"{e.resolved or e.name} ({e.code})", f"code {got}"))
        elif not own and e.type == "sub_agency" and parent in used.codes and not getattr(a, "partial", False):
            out.append(Mismatch("level", f"{e.resolved or e.name} ({e.code})",
                                f"the ministry total ({parent})"))
    if period is not None and used.quarters and period.quarter not in used.quarters:
        got = ", ".join(f"Q1-Q{q}" if q > 1 else "Q1" for q in sorted(used.quarters))
        out.append(Mismatch("period", period.label() if period.year else f"Q1-Q{period.quarter}", got))
    elif period is not None and period.year and used.years and period.year not in used.years:
        out.append(Mismatch("period", period.label(), ", ".join(str(y) for y in sorted(used.years))))
    elif period is None and years and len(set(years)) == 1 and used.years and set(years).isdisjoint(used.years):
        out.append(Mismatch("period", str(years[0]), ", ".join(str(y) for y in sorted(used.years))))
    return out


def redo_hint(mismatches: list[Mismatch]) -> str:
    what = "; ".join(f"{m.kind}: {m.asked} (not {m.got})" for m in mismatches)
    return WORDS["en"]["redo"].format(what=what)


def note(mismatches: list[Mismatch], lang: str) -> str:
    w = WORDS.get(lang, WORDS["en"])
    return " ".join(w[m.kind].format(asked=m.asked, got=m.got) for m in mismatches)


def focus_terms(mismatches: list[Mismatch], plan) -> list[str]:
    """Search terms for the missing part: the asked agency's printed name and code, the period's report words."""
    terms: list[str] = []
    for m in mismatches:
        if m.kind in ("entity", "level"):
            terms += [re.sub(r"\s*\(\d{12}\)$", "", m.asked)] + CODE.findall(m.asked)
        else:
            terms.append(m.asked)
    return list(dict.fromkeys(t for t in terms if t))
