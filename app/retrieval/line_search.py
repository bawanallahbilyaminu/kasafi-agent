"""Wide search over every extracted budget line (projects, economic items, agencies, ministries, functions).

The planner gives several search terms per question: synonyms, abbreviations, spelling variants, English
equivalents of Hausa words ("BHCPF", "Basic Health Care Provision Fund", "counterpart", "immunisation").
A line matches on any term, by
  - keyword: the term appears in the printed row (name, codes, location),
  - stemmed full text: "immunization" also finds "immunisation programme",
  - trigram similarity on the line's name: spelling variants such as "BHCPF" / "BHCBF",
  - meaning: the nearest line vectors to the question's and the terms' (app/retrieval/line_meaning.py), so
    "assistive devices" finds "Trycle bicycle for disable".
Keyword hits are scored by how many terms they match and how; the keyword and meaning rankings are fused by
reciprocal rank. Lines are returned with their document, page, table title, a row id and every labelled cell,
for the model to read and the code to verify.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal

import psycopg

from app.retrieval.line_meaning import embed_queries

MAX_TERMS = 10
MAX_LINES = 40          # what the model reads in one go
CANDIDATES = 400        # read from the database before scoring
PER_DOC_NAME = 4        # copies of one line per document (total, personnel, overhead, capital tables)
MEANING_K = 200         # nearest lines per query vector (many are copies of one name)
MEANING_ONLY = 6        # names found by meaning alone that the model reads
PER_TERM = 2            # each term's best distinct names, read before anything else
RRF_K = 60              # reciprocal-rank fusion constant

_COLS = """l.id, d.title, l.doc_id, l.page, COALESCE(l.table_title, ''), l.name, l.row_text, l.classification,
       COALESCE(d.series, ''), COALESCE(d.edition, ''), COALESCE(l.code, ''), l.context"""
_FILTERS = """(cardinality(%(years)s::int[]) = 0
       OR EXISTS (SELECT 1 FROM budget_rows b WHERE b.line_id = l.id AND b.year = ANY(%(years)s)))
  AND (%(docs)s::text[] IS NULL OR l.doc_id = ANY(%(docs)s))
  AND (%(spend)s = 'any' OR (%(spend)s = 'revenue') = (l.spend_kind = 'revenue'))"""

# Terms come most specific first; earlier terms weigh more. Ordered in SQL, so a broad term can't crowd out the
# lines that match the core term before scoring.
_SQL = """
WITH t AS (SELECT * FROM unnest(%(terms)s::text[], %(weights)s::float8[]) WITH ORDINALITY AS t(term, w, i)),
-- the candidate lines, by three lookups the indexes serve (an OR of them scanned every line and computed a
-- trigram similarity per line and term: 1-1.7 s; this is 0.25-0.8 s for the same lines and scores)
cand AS (
    SELECT l.id FROM budget_lines l WHERE l.row_text ILIKE ANY(%(pats)s)
    UNION SELECT l.id FROM budget_lines l, t WHERE l.tsv @@ plainto_tsquery('english', t.term)
    UNION SELECT l.id FROM budget_lines l, t WHERE l.name %% t.term
)
SELECT """ + _COLS + """,
       -- the best single match counts: in the line's own name most, elsewhere in the row (codes, function and
       -- location columns of a project) less; more matched terms add only a little
       (SELECT COALESCE(max(w), 0) FROM t WHERE l.name ILIKE '%%' || t.term || '%%') * 4
       + (SELECT COALESCE(max(w), 0) FROM t WHERE l.row_text ILIKE '%%' || t.term || '%%') * 2
       + (SELECT COALESCE(max(w), 0) FROM t WHERE l.tsv @@ plainto_tsquery('english', t.term))
       + (SELECT COALESCE(max(similarity(l.name, t.term) * w), 0) FROM t) * 2
       + (SELECT count(*) FROM t WHERE l.row_text ILIKE '%%' || t.term || '%%') * 0.3 AS score
FROM cand JOIN budget_lines l ON l.id = cand.id JOIN documents d ON d.id = l.doc_id
WHERE """ + _FILTERS + """
ORDER BY score DESC, l.id
LIMIT %(cap)s
"""

# HNSW index (migration 0008) with iterative scans: the index keeps scanning until `k` lines pass the filters
# (a plain HNSW scan filters after the fact and lost lines). relaxed_order is re-sorted by distance here.
_ITERATIVE = ("SELECT set_config('hnsw.iterative_scan', 'relaxed_order', false), "
              "set_config('hnsw.ef_search', '400', false)")
_MEANING_SQL = """
WITH n AS MATERIALIZED (
    SELECT """ + _COLS + """, 0.0, l.embedding <=> %(v)s::vector AS dist
    FROM budget_lines l JOIN documents d ON d.id = l.doc_id
    WHERE l.embedding IS NOT NULL AND """ + _FILTERS + """
    ORDER BY l.embedding <=> %(v)s::vector
    LIMIT %(k)s
)
SELECT * FROM n ORDER BY dist
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
    code: str = ""             # the administrative / economic code printed on the line, if any
    context: str = ""          # its codes' standard descriptions (app/retrieval/line_meaning.py)

    def cell(self, column: str) -> Cell | None:
        return next((c for c in self.cells if c.column == column), None)


def _line(r) -> Line:
    return Line(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], score=float(r[12]), code=r[10],
                context=r[11])


def _clean(term: str) -> str:
    return " ".join(term.replace("%", " ").replace("_", " ").split())[:80]


def _newest_first(x: Line) -> tuple:
    return (-int(x.edition[:4]) if x.edition[:4].isdigit() else 0, x.page)


def name_key(x: Line) -> str:
    return " ".join(x.name.lower().split())


def fuse(keyword: list[Line], meaning: list[list[Line]], *, window: int = MAX_LINES,
         meaning_only: int = MEANING_ONLY) -> list[Line]:
    """The keyword ranking, lifted by meaning: reciprocal-rank fusion of a line's keyword rank and (at half weight)
    its name's best rank for any query vector. Ranks count distinct names, because one name is printed in many
    tables; only the best vector counts, so many terms can't outvote the keywords. The best `meaning_only` names
    that no keyword found get one line each inside the first `window` lines the model reads."""
    mrank: dict[str, int] = {}
    first: dict[str, Line] = {}
    for ranked in meaning:
        names = list(dict.fromkeys(name_key(x) for x in ranked))
        for rank, n in enumerate(names):
            mrank[n] = min(mrank.get(n, rank), rank)
        for x in ranked:
            first.setdefault(name_key(x), x)

    def rrf(rank: int, x: Line) -> float:
        m = mrank.get(name_key(x))
        return 1 / (RRF_K + rank + 1) + (0.5 / (RRF_K + m + 1) if m is not None else 0.0)

    score = {x.id: rrf(r, x) for r, x in enumerate(keyword)}
    fused = sorted(keyword, key=lambda x: (-score[x.id], *_newest_first(x)))
    found = {name_key(x) for x in keyword}
    extra = [first[n] for n in sorted(mrank, key=mrank.get) if n not in found][:meaning_only]
    at = max(0, min(len(fused), window - len(extra)))
    return fused[:at] + extra + fused[at:]


def nearest(conn: psycopg.Connection, texts: list[str], *, years: list[int] | None = None,
            docs: list[str] | None = None, spend: str = "any", k: int = MEANING_K) -> list[list[Line]]:
    """For each text, the lines nearest in meaning, best first (no cells)."""
    params = {"years": list(years or []), "docs": docs,
              "spend": spend if spend in ("expenditure", "revenue") else "any", "k": k}
    vectors = embed_queries(texts)
    if not vectors or len(vectors) != len([t for t in texts if t and t.strip()]):
        return [[] for _ in texts]
    conn.execute(_ITERATIVE)
    return [[_line(r) for r in conn.execute(_MEANING_SQL, {**params, "v": v})] for v in vectors]


def cover(lines: list[Line], terms: list[str], per_term: int = PER_TERM) -> list[Line]:
    """Every term's best `per_term` distinct names first (by name, row or code descriptions), then the lines found
    by meaning alone (keyword score 0), then the rest in order: one broad term printed in many tables can't keep
    another term's lines out of what the model reads."""
    first: list[Line] = []
    ids: set[str] = set()
    for t in (t.lower() for t in terms):
        names: set[str] = set()
        for x in lines:
            if len(names) >= per_term:
                break
            if x.id not in ids and name_key(x) not in names and t in f"{x.name} {x.row_text} {x.context}".lower():
                first.append(x)
                ids.add(x.id)
                names.add(name_key(x))
    first += [x for x in lines if x.score == 0 and x.id not in ids]
    ids |= {x.id for x in first}
    return first + [x for x in lines if x.id not in ids]


def search_lines(conn: psycopg.Connection, terms: list[str], *, year: int | None = None, years: list[int] | None = None,
                 docs: list[str] | None = None, spend: str = "any", limit: int = CANDIDATES,
                 per_doc_name: int = PER_DOC_NAME, question: str | None = None) -> list[Line]:
    """Lines matching any term or nearest in meaning to the question and terms, best first, with their cells;
    `spend` is expenditure, revenue or any.

    At most `per_doc_name` copies of one line per document (the same agency is printed in many tables), so one
    item can't fill the list the model reads.
    """
    terms = list(dict.fromkeys(t for t in (_clean(t) for t in terms) if len(t) >= 3))[:MAX_TERMS]
    if not terms:
        return []
    years = list(years or []) + ([year] if year else [])
    weights = [max(0.3, 1.0 - 0.15 * i) for i in range(len(terms))]
    params = {"years": years, "docs": docs, "spend": spend if spend in ("expenditure", "revenue") else "any"}
    rows = conn.execute(_SQL, {**params, "terms": terms, "weights": weights, "pats": [f"%{t}%" for t in terms],
                               "cap": max(limit, 1) * 4}).fetchall()
    lines = [_line(r) for r in rows]
    lines.sort(key=lambda x: (-x.score, *_newest_first(x)))
    if question:
        lines = fuse(lines, nearest(conn, [question, *terms], years=years, docs=docs, spend=spend))
    kept, copies = [], Counter()
    for x in lines:
        # the whole name: fragment-named project lines differ only in their location at the end
        key = (x.doc_id, " ".join(x.name.lower().split()))
        if copies[key] < per_doc_name:
            copies[key] += 1
            kept.append(x)
    lines = (cover(kept, terms) if question else kept)[:limit]
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
