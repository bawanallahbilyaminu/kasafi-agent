"""The period a question names, and the implementation report that covers it.

The period asked beats the newest report: "Q1-Q2 2026", "the first half of 2026", "by the end of Q2", "January to
June" are the Q2 report's year-to-date column even when a Q3 report exists. "Latest", "current", "now" (and no
period named) mean the newest. The reports are cumulative: the Q2 report covers Q1-Q2.

An answer about a named period reads only that report among the year's implementation reports (the budgets stay
in), so it can't say "used report A" and quote report B.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

_Q = r"(?:q|quarter\s*)"
# (pattern, quarter the period ends with): cumulative, from January
_PERIODS = [
    (r"\bq1\s*(?:-|–|to|and|&)\s*q([1-4])\b", None),                       # Q1-Q2, Q1 to Q3: the later one
    (r"\b(?:first|1st)\s+half\b|\bh1\b|\bhalf[-\s]year\b|\bmid[-\s]year\b|\brabin\s+shekara(?:\s+na\s+farko)?\b", 2),
    (r"\b(?:end\s+of|by|as\s+at|as\s+of|through)\s+(?:the\s+)?q([1-4])\b", None),
    (r"\b(?:end\s+of|by|as\s+at|as\s+of|through)\s+(?:the\s+)?(first|second|third|fourth|1st|2nd|3rd|4th)\s+quarter\b",
     "word"),
    (r"\bjan(?:uary)?\s*(?:-|–|to)\s*mar(?:ch)?\b|\b(?:first|1st)\s+quarter\b|\brubu'?i\s+na\s+farko\b", 1),
    (r"\bjan(?:uary)?\s*(?:-|–|to)\s*jun(?:e)?\b|\b(?:end\s+of|by)\s+june\b", 2),
    (r"\bjan(?:uary)?\s*(?:-|–|to)\s*sep(?:t|tember)?\b|\bnine\s+months\b|\b9\s+months\b|\b(?:end\s+of|by)\s+"
     r"september\b|\b(?:third|3rd)\s+quarter\b", 3),
    (r"\bjan(?:uary)?\s*(?:-|–|to)\s*dec(?:ember)?\b|\b(?:end\s+of|by)\s+december\b|\b(?:fourth|4th)\s+quarter\b", 4),
    (r"\b(?:second|2nd)\s+quarter\b", 2),
    (r"\bq([1-4])\b", None),
]
_WORDS = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3, "fourth": 4, "4th": 4}
LATEST = re.compile(r"(?i)\b(?:latest|most\s+recent|newest|current(?:ly)?|now|to\s+date|so\s+far|yanzu|"
                    r"na\s+baya[-\s]bayan\s+nan|zuwa\s+yanzu)\b")
YEAR = re.compile(r"\b(20[2-3]\d)\b")


@dataclass(frozen=True)
class Period:
    year: int | None             # None: the most recent year with a report for that quarter
    quarter: int                 # the quarter the cumulative period ends with

    def label(self) -> str:
        return f"Q1-Q{self.quarter} {self.year}" if self.quarter > 1 else f"Q1 {self.year}"


def asked_period(*texts: str) -> Period | None:
    """The cumulative period a question names ('Q1-Q2 2026', 'first half of 2025', 'end of Q3'), or None. A
    question saying latest / current / now without naming a period gets None (the newest report is meant)."""
    text = " ".join(t for t in texts if t)
    low = text.lower()
    for pat, q in _PERIODS:
        m = re.search(pat, low)
        if not m:
            continue
        quarter = (int(m.group(1)) if q is None else _WORDS[m.group(1)] if q == "word" else q)
        years = [int(y) for y in YEAR.findall(text)]
        return Period(years[0] if years else None, quarter)
    return None


def report_for(conn, period: Period, today: date | None = None) -> tuple[str, int] | None:
    """(doc_id, year) of the implementation report whose year-to-date figures end with that quarter: the asked
    year, or the most recent year that has one."""
    rows = conn.execute("SELECT doc_id, year FROM perf_items GROUP BY doc_id, year HAVING max(quarter) = %s "
                        "ORDER BY year DESC, doc_id DESC", (period.quarter,)).fetchall()
    for doc, year in rows:
        if period.year is None or year == period.year:
            if today is None or year <= today.year:
                return doc, year
    return None


def other_reports(conn, keep: str, year: int) -> list[str]:
    """The year's other implementation reports: left out of an answer about one period."""
    return [r[0] for r in conn.execute("SELECT DISTINCT doc_id FROM perf_items WHERE year = %s AND doc_id <> %s",
                                       (year, keep)).fetchall()]


def readable_docs(conn, skip: list[str]) -> list[str]:
    """Every document with budget lines except `skip` (the docs filter of the line search)."""
    return [r[0] for r in conn.execute("SELECT DISTINCT doc_id FROM budget_lines WHERE NOT (doc_id = ANY(%s))",
                                       (skip,)).fetchall()]
