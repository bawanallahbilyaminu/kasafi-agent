"""Wide search over every extracted budget line (projects, economic items, agencies, ministries, functions).

The planner gives several search terms per question: synonyms, abbreviations, spelling variants, English
equivalents of Hausa words ("BHCPF", "Basic Health Care Provision Fund", "counterpart", "immunisation").
A line matches on any term, by
  - keyword: the term appears in the printed row (name, codes, location),
  - stemmed full text: "immunization" also finds "immunisation programme",
  - trigram similarity on the line's name: spelling variants such as "BHCPF" / "BHCBF".
Lines are scored by how many terms they match and how, then returned with their document, page, table
title, a row id and every labelled cell, for the model to read and the code to verify.
(An embedding model would add meaning search; until one is hosted, meaning comes from the planner's terms.)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal

import psycopg

MAX_TERMS = 10
MAX_LINES = 40          # what the model reads in one go
CANDIDATES = 400        # read from the database before scoring

_SQL = """
SELECT l.id, d.title, l.doc_id, l.page, COALESCE(l.table_title, ''), l.name, l.row_text, l.classification,
       COALESCE(d.series, ''), COALESCE(d.edition, ''),
       (SELECT count(*) FROM unnest(%(pats)s::text[]) p WHERE l.row_text ILIKE p) AS kw,
       (SELECT count(*) FROM unnest(%(terms)s::text[]) t WHERE l.tsv @@ plainto_tsquery('english', t)) AS ft,
       (SELECT COALESCE(max(similarity(l.name, t)), 0) FROM unnest(%(terms)s::text[]) t) AS sim
FROM budget_lines l JOIN documents d ON d.id = l.doc_id
WHERE (l.row_text ILIKE ANY(%(pats)s)
       OR EXISTS (SELECT 1 FROM unnest(%(terms)s::text[]) t WHERE l.tsv @@ plainto_tsquery('english', t))
       OR EXISTS (SELECT 1 FROM unnest(%(terms)s::text[]) t WHERE l.name %% t))
  AND (%(year)s::int IS NULL OR EXISTS (SELECT 1 FROM budget_rows b WHERE b.line_id = l.id AND b.year = %(year)s))
  AND (%(docs)s::text[] IS NULL OR l.doc_id = ANY(%(docs)s))
LIMIT %(cap)s
"""


@dataclass
class Cell:
    column: str
    year: int | None
    measure: str
    period: str
    amount: Decimal


@dataclass
class Line:
    id: str
    title: str             # document title
    doc_id: str
    page: int
    table_title: str
    name: str
    row_text: str
    classification: str
    series: str
    edition: str
    score: float
    cells: list[Cell] = field(default_factory=list)

    def cell(self, column: str) -> Cell | None:
        return next((c for c in self.cells if c.column == column), None)


def _clean(term: str) -> str:
    return " ".join(term.replace("%", " ").replace("_", " ").split())[:80]


def search_lines(conn: psycopg.Connection, terms: list[str], *, year: int | None = None,
                 docs: list[str] | None = None, limit: int = CANDIDATES) -> list[Line]:
    """All lines matching any term, best first, with their cells. Up to `limit` lines."""
    terms = list(dict.fromkeys(t for t in (_clean(t) for t in terms) if len(t) >= 3))[:MAX_TERMS]
    if not terms:
        return []
    rows = conn.execute(_SQL, {"terms": terms, "pats": [f"%{t}%" for t in terms], "year": year, "docs": docs,
                               "cap": max(limit, 1) * 3}).fetchall()
    lines = [Line(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9],
                  score=3.0 * r[10] + 2.0 * r[11] + float(r[12])) for r in rows]
    lines.sort(key=lambda x: (-x.score, x.edition and -int(x.edition[:4]) if x.edition[:4].isdigit() else 0, x.page))
    lines = lines[:limit]
    if lines:
        by_id = {x.id: x for x in lines}
        for lid, col, yr, measure, period, amount in conn.execute(
                "SELECT line_id, column_label, year, measure, period, amount_naira FROM budget_rows "
                "WHERE line_id = ANY(%s) ORDER BY id", ([x.id for x in lines],)).fetchall():
            by_id[lid].cells.append(Cell(col, yr, measure, period, Decimal(amount)))
    return lines


def ministry_of(line: Line) -> str:
    """The agency a project line belongs to ('052100100100 - Ministry of Health'), or the line's own name."""
    import re
    m = re.search(r"\d{12}\s*-\s*([A-Za-z][^|\d]{2,60}?)\s+\d{6,}", line.row_text)
    return (m.group(1) if m else line.name).strip()


def groups(lines: list[Line], top: int = 3) -> list[tuple[str, int]]:
    """The main agencies among many hits, for a short 'which one?' question."""
    return Counter(ministry_of(x) for x in lines).most_common(top)
