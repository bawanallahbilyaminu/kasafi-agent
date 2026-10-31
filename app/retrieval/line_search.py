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

import re
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal

import psycopg

from app.retrieval import pool
from app.retrieval.line_meaning import embed_queries
from app.sources.lga_names import city_terms

MAX_TERMS = 10
MAX_LINES = 40          # what the model reads in one go
CANDIDATES = 400        # read from the database before scoring
PER_DOC_NAME = 4        # copies of one line per document (total, personnel, overhead, capital tables)
MEANING_K = 200         # nearest lines per query vector (many are copies of one name)
MEANING_ONLY = 6        # names found by meaning alone that the model reads
PER_TERM = 2            # each term's best distinct names, read before anything else
PER_TERM_PROJECTS = 4   # and the best projects with the term in their own name
RRF_K = 60              # reciprocal-rank fusion constant

_COLS = """l.id, d.title, l.doc_id, l.page, COALESCE(l.table_title, ''), l.name, l.row_text, l.classification,
       COALESCE(d.series, ''), COALESCE(d.edition, ''), COALESCE(l.code, ''), l.context,
       COALESCE(l.spend_kind, '')"""
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
       (SELECT COALESCE(max(w), 0) FROM t WHERE o.own ILIKE '%%' || t.term || '%%') * 4
       + (SELECT COALESCE(max(w), 0) FROM t WHERE l.row_text ILIKE '%%' || t.term || '%%') * 2
       + (SELECT COALESCE(max(w), 0) FROM t WHERE l.tsv @@ plainto_tsquery('english', t.term))
       + (SELECT COALESCE(max(similarity(o.own, t.term) * w), 0) FROM t) * 2
       + (SELECT count(*) FROM t WHERE l.row_text ILIKE '%%' || t.term || '%%') * 0.3 AS score
FROM cand JOIN budget_lines l ON l.id = cand.id JOIN documents d ON d.id = l.doc_id
-- a project line's name carries its agency, item and function after the codes ("Server Upgrade 025300100100 -
-- Min of Lands and Housing ..."): only the words before the codes are its own name, as in short_name()
CROSS JOIN LATERAL (SELECT regexp_replace(l.name, '\\s\\d{8,}\\s*-.*$', '') AS own) o
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
    spend_kind: str = ""       # total / personnel / overhead / capital / revenue ...: the kind its table shows

    def cell(self, column: str) -> Cell | None:
        return next((c for c in self.cells if c.column == column), None)


def _line(r) -> Line:
    return Line(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], score=float(r[13]), code=r[10],
                context=r[11], spend_kind=r[12])


# a kind of spending the question names; its table title often doesn't ("Other Non-Debt Recurrent
# Expenditure" is the overhead table)
_KINDS = (("overhead", r"overhead|running cost|non-debt recurrent|other recurrent"),
          ("personnel", r"personnel|salar(?:y|ies)|wages|emolument"),
          ("capital", r"capital (?:expenditure|budget|spending|allocation)|\bcapex\b"))


def asked_kind(text: str) -> str:
    """The one kind of spending a question names (overhead, personnel, capital), or '' for none or several."""
    kinds = [k for k, pat in _KINDS if re.search(pat, text, re.I)]
    return kinds[0] if len(kinds) == 1 else ""


def names_a_kind(text: str) -> bool:
    """The question names any kind of spending (overhead, personnel, capital). Broader than asked_kind: a bare
    'capital' counts (not 'the capital city'), and the Hausa words, since a kind wrongly seen only keeps a row."""
    return any(re.search(pat, text, re.I) for _, pat in _KINDS) or bool(re.search(
        r"(?i)\bcapital\b(?!\s+(?:city|town|of)\b)|manyan ayyuka|albashi|kuɗin gudanarwa|kudin gudanarwa", text))


def lift_kind(lines: list[Line], kind: str) -> list[Line]:
    """Each line of the asked kind moves up to where its name first ranks: one agency is printed in the total,
    personnel, overhead and capital tables with one name, and only a few copies per document are kept, so the
    asked table's copy must not be the one dropped (m19: Government House's overhead row). No kind asked: the
    total table's copy (all spending) moves up the same way."""
    kind = kind or "total"
    first: dict[str, int] = {}
    for i, x in enumerate(lines):
        first.setdefault(name_key(x), i)
    return [x for _, _, x in sorted(((first[name_key(x)] if x.spend_kind == kind else i,
                                      0 if x.spend_kind == kind else 1, x) for i, x in enumerate(lines)),
                                    key=lambda r: r[:2])]


def _clean(term: str) -> str:
    return " ".join(term.replace("%", " ").replace("_", " ").split())[:80]


_ACRONYM = re.compile(r"\b[A-Z]{2,6}\b")
_MINOR = {"and", "of", "the", "for", "in", "on", "to", "&"}
_initials_cache: dict[str, list[str]] = {}


def initials(name: str) -> str:
    """'Information Communication and Technology - General' -> 'ICT' (the part before ' - ', minor words out)."""
    words = re.findall(r"[A-Za-z]+", name.split(" - ")[0])
    return "".join(w[0] for w in words if w.lower() not in _MINOR).upper()


def acronym_names(conn: psycopg.Connection) -> dict[str, list[str]]:
    """Every printed budget line name by its initials, built once: the budget's own expansion of an acronym."""
    if not _initials_cache:
        for (name,) in conn.execute("SELECT DISTINCT split_part(name, ' - ', 1) FROM budget_lines "
                                    "WHERE length(name) BETWEEN 8 AND 120").fetchall():
            name = re.sub(r"^\d+\s+", "", " ".join(name.split()))          # a leading code is not part of it
            if len(key := initials(name)) >= 2 and name not in _initials_cache.get(key, []):
                _initials_cache.setdefault(key, []).append(name)
    return _initials_cache


def expand_acronyms(conn: psycopg.Connection, terms: list[str], *, room: int = MAX_TERMS, most: int = 2) -> list[str]:
    """Terms with an acronym in them ('ICT and Innovation') get the names the budgets print it as ('Information
    Communication and Technology') when the planner didn't give the expansion itself. They go last (the lowest
    weight), only in the room the planner's terms leave: an initials match can be wrong ('LGA' -> 'Local
    Government Audit'), so it only adds lines to read, never displaces the planner's terms."""
    terms = terms[:room]
    if len(terms) >= room:
        return terms
    names = acronym_names(conn)
    have = " ".join(terms).lower()
    extra = list(dict.fromkeys(n for t in terms for a in _ACRONYM.findall(t)
                               for n in sorted(names.get(a, []), key=len)[:most] if n.lower() not in have))
    return terms + extra[:min(most, room - len(terms))]


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


_CODES = re.compile(r"\s\d{8,}\s*-")


def own_name(x: Line) -> str:
    """A line's own words: a project's name is followed by its codes and their descriptions ("Server Upgrade
    025300100100 - Min of Lands and Housing ..."), which aren't what it is."""
    return _CODES.split(x.name, maxsplit=1)[0]


def named_project(x: Line) -> bool:
    """A project with its own name before its codes: not a heading in capitals ("HOUSING 33312100 - WAMAKKO"),
    a row whose name is only its agency's (the project's words were lost on the page), or the programme table's
    copy, whose name starts with the programme's code and title ("06100126001300 - Housing and Urban Development
    - General Server Upgrade")."""
    own = " ".join(own_name(x).split())
    return (bool(_CODES.search(x.name)) and not own.isupper() and not own[:1].isdigit()
            and own.lower() != " ".join(ministry_of(x).split()).lower())


def cover(lines: list[Line], terms: list[str], per_term: int = PER_TERM,
          per_term_projects: int = PER_TERM_PROJECTS, years: list[int] | None = None) -> list[Line]:
    """Every term's best `per_term` distinct names first (by name, row or code descriptions), and its best
    `per_term_projects` projects named by it, then the lines found by meaning alone (keyword score 0), then the
    rest in order: one broad term printed in many tables can't keep another term's lines out of what the model
    reads, and its summary rows (sector, ministry and item totals, printed in every table and report) can't keep
    out the projects it names ("housing": HOUSING, Ministry of Lands and Housing, ... and "Construction of 500
    Housing Estate at Wajekke"). Several years asked: each year's budget gets its own best names (a 2025 and a
    2026 total of one sector are both read)."""
    first: list[Line] = []
    ids: set[str] = set()
    each_year = [str(y) for y in years or []] if len(years or []) >= 2 else [""]

    def take(t: str, match, most: int) -> None:
        for y in each_year:
            names: set[str] = set()
            for x in lines:
                if len(names) >= most:
                    break
                if x.id not in ids and y in x.doc_id and name_key(x) not in names and match(x, t):
                    first.append(x)
                    ids.add(x.id)
                    names.add(name_key(x))

    for t in (t.lower() for t in terms):
        take(t, lambda x, t: t in f"{x.name} {x.row_text} {x.context}".lower(), per_term)
        take(t, lambda x, t: named_project(x) and t in own_name(x).lower(), per_term_projects)
    first += [x for x in lines if x.score == 0 and x.id not in ids]
    ids |= {x.id for x in first}
    return first + [x for x in lines if x.id not in ids]


def search_lines(conn: psycopg.Connection, terms: list[str], *, year: int | None = None, years: list[int] | None = None,
                 docs: list[str] | None = None, spend: str = "any", limit: int = CANDIDATES,
                 per_doc_name: int = PER_DOC_NAME, question: str | None = None, settings=None) -> list[Line]:
    """Lines matching any term or nearest in meaning to the question and terms, best first, with their cells;
    `spend` is expenditure, revenue or any. With `settings` (a pool), the keyword and vector searches overlap.

    At most `per_doc_name` copies of one line per document (the same agency is printed in many tables), so one
    item can't fill the list the model reads.
    """
    terms = list(dict.fromkeys(t for t in (_clean(t) for t in terms) if len(t) >= 3))
    terms = expand_acronyms(conn, terms)
    have = " ".join(terms).lower()                 # 'Sokoto city' is printed 'Sokoto Metropolis' / 'Township'
    terms += [t for t in city_terms(" ".join([question or "", *terms])) if t.lower() not in have]
    if not terms:
        return []
    years = list(years or []) + ([year] if year else [])
    weights = [max(0.3, 1.0 - 0.15 * i) for i in range(len(terms))]
    params = {"years": years, "docs": docs, "spend": spend if spend in ("expenditure", "revenue") else "any"}
    # the vector search (embedding plus HNSW) on a pooled connection in another thread while the keyword SQL
    # runs here; without a pool (tests, no `settings`) it runs first, as before
    meaning = pool.run_sync(settings, nearest, conn, [question, *terms], years=years, docs=docs,
                            spend=spend) if question else None
    rows = conn.execute(_SQL, {**params, "terms": terms, "weights": weights, "pats": [f"%{t}%" for t in terms],
                               "cap": max(limit, 1) * 4}).fetchall()
    lines = [_line(r) for r in rows]
    lines.sort(key=lambda x: (-x.score, *_newest_first(x)))
    if meaning is not None:
        lines = fuse(lines, meaning.result())
    lines = lift_kind(lines, asked_kind(" ".join([question or "", *terms])))
    kept, copies = [], Counter()
    for x in lines:
        # the whole name: fragment-named project lines differ only in their location at the end
        key = (x.doc_id, " ".join(x.name.lower().split()))
        if copies[key] < per_doc_name:
            copies[key] += 1
            kept.append(x)
    lines = (cover(kept, terms, years=years) if question else kept)[:limit]
    if lines:
        by_id = {x.id: x for x in lines}
        for lid, col, yr, measure, period, amount in conn.execute(
                "SELECT line_id, column_label, year, measure, period, amount_naira FROM budget_rows "
                "WHERE line_id = ANY(%s) ORDER BY id", ([x.id for x in lines],)).fetchall():
            by_id[lid].cells.append(Cell(col, yr, measure, period, Decimal(amount)))
    return lines


# a project the question names: 'Construction of …', 'Rehabilitation of …' (the words up to the end of the clause)
PROJECT_PHRASE = re.compile(r"(?i)\b((?:re)?(?:constr|rehab|renov|complet|provi|suppl|procur|purchas|install|upgrad|"
                            r"expan|establish|drill|equip|fenc|furnish|mainten|erect|electrif|dual|asphalt)\w*\s+"
                            r"(?:and\s+\w+\s+)?of\s+[^?;,.]{4,140})")      # verb prefixes: typos still match


def project_phrases(*texts: str) -> list[str]:
    """The project names a question gives ('Construction of Kalambaina Road' ...), longest first."""
    found = [m.group(1).strip() for t in texts if t for m in PROJECT_PHRASE.finditer(t)]
    found = [re.sub(r"(?i)\s+(?:in|for|during|by)\s+(?:the\s+)?(?:20\d\d|q[1-4]|budget|year)\b.*$", "", p) for p in found]
    return sorted(dict.fromkeys(p for p in found if len(p) >= 12), key=len, reverse=True)


_FUZZY_SQL = """
SELECT """ + _COLS + """, greatest(word_similarity(lower(%(name)s), lower(o.own)),
                                   similarity(lower(o.own), lower(%(name)s))) AS score
FROM budget_lines l JOIN documents d ON d.id = l.doc_id
CROSS JOIN LATERAL (SELECT regexp_replace(l.name, '\\s\\d{8,}\\s*-.*$', '') AS own) o
WHERE (lower(%(name)s) <%% lower(o.own) OR lower(o.own) %% lower(%(name)s)) AND """ + _FILTERS + """
ORDER BY score DESC, l.id
LIMIT %(cap)s
"""


def project_lines(conn: psycopg.Connection, name: str, *, years: list[int] | None = None,
                  docs: list[str] | None = None, limit: int = 12, floor: float = 0.45) -> list[Line]:
    """Lines whose own name matches a project name loosely (pg_trgm word similarity: spelling variants, a word
    left out or added), in the budgets' project lists and the BIRs' capital project tables, best first."""
    rows = conn.execute(_FUZZY_SQL, {"name": name, "years": list(years or []), "docs": docs, "spend": "expenditure",
                                     "cap": limit * 3}).fetchall()
    lines = [_line(r) for r in rows if float(r[13]) >= floor][:limit]
    return _with_cells(conn, lines)


def _with_cells(conn: psycopg.Connection, lines: list[Line]) -> list[Line]:
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
