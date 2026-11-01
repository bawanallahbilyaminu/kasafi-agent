"""The library-wide search: every indexed document is a candidate for every question (1 Nov 2026).

A newly indexed plan (the Sokoto Health Resource Optimization Plan) was never read for three questions it answers:
the planner chose budgets for one, and for the other two the 320-page EmONC assessment filled every keyword slot.
So every path also runs this search over ALL documents. It works in two steps, because a long mixed chunk
(~1,400 characters) dilutes the one sentence that answers, and thousands of short budget-table chunks look alike
to the local meaning model (similarity ~0.80-0.84 for any budget-flavoured question):

1. Documents. Three lists rank documents by their best chunk: meaning search over running-text chunks only (the
   question's vector against each chunk's, bge-small run locally; migration 0025), keyword search with the
   question and the planner's queries (60 deep, so one long report can't fill the list), and the question's own
   rare multi-word phrases ('drug revolving fund': printed in a handful of chunks). The lists are fused by
   reciprocal rank. Budget tables (budgets, implementation reports) take part only when money is asked: the
   planned search already reads them, and they crowd out the plans and reports this search exists for.
2. Pages. Inside each candidate document, its pages are ranked by the question's words (length-normalised full
   text rank), and the best two are returned.

A candidate is *strong* when two lists put the document in their top five, or it prints one of the question's rare
phrases: those are read even when the plan chose other documents. Nothing here excludes a document; callers may
prefer their planned ones.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import psycopg

from app.retrieval.search import Hit, search

log = logging.getLogger(__name__)

DOCS = 4                       # candidate documents
PAGES_PER_DOC = 2
RRF_K = 5                      # reciprocal-rank constant over document ranks: the first places count most
TOP = 5                        # a list that puts a document in its first TOP places "agrees" on it
RARE = 30                      # a phrase printed in at most this many chunks is distinctive
TABLE_CATEGORIES = ("budget", "budget_performance")
CARD_WEIGHT = 0.5              # the card list's weight beside meaning (1.2), keywords (1.0) and phrases (1.5)
PROSE = "(length(c.text) - length(replace(c.text, ' | ', ''))) / 3 <= 2"
VEC_SQL = f"""
SELECT c.doc_id, c.page, c.idx FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE c.embedding IS NOT NULL AND {PROSE}
  AND (%(skip)s::text[] IS NULL OR NOT c.doc_id = ANY(%(skip)s::text[]))
  AND (%(tables)s OR d.category IS NULL OR NOT d.category = ANY(%(table_cats)s::text[]))
ORDER BY c.embedding <=> %(v)s::vector LIMIT 200
"""
PHRASE_SQL = """
SELECT c.doc_id, c.page, c.idx FROM chunks c
WHERE c.tsv @@ phraseto_tsquery('english', %(q)s) LIMIT 200
"""
PAGE_SQL = """
WITH q AS (SELECT to_tsquery('english', replace(websearch_to_tsquery('english', %(q)s)::text, ' & ', ' | ')) AS q)
SELECT p.page, ts_rank_cd(to_tsvector('english', p.text), q.q, 1 | 32) AS r
FROM pages p, q WHERE p.doc_id = %(d)s AND to_tsvector('english', p.text) @@ q.q ORDER BY r DESC, p.page LIMIT %(k)s
"""

# words that make a phrase generic: every document prints them
_STOP = {"the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "by", "with", "at", "from", "is", "are", "was",
         "were", "be", "been", "has", "have", "had", "how", "what", "which", "who", "when", "where", "why", "much",
         "many", "did", "does", "do", "that", "this", "these", "those", "its", "it", "their", "there", "as", "into",
         "according", "about", "any", "all", "some", "per", "than", "then", "more", "most", "less", "share", "number",
         "amount", "total", "plan", "planned", "plans", "sokoto", "state", "states", "nigeria", "government", "year",
         "years", "figure", "figures", "data", "show", "shows", "say", "says", "report", "document", "documents",
         "kasafi", "please", "tell", "me", "us", "give", "list", "can", "could", "would", "should", "will", "met",
         "paid", "raise", "budget", "spending", "out"}
_TOKEN = re.compile(r"[A-Za-z][A-Za-z'’-]+")
_GENERIC = re.compile(r"(?i)\b(?:sokoto(?:['’]s)?|state(?:['’]s)?|nigeria(?:['’]s)?|government)\b")


@dataclass
class LibHit:
    hit: Hit                                            # the document's page (idx: its best chunk, if known)
    score: float = 0.0                                  # the document's fused score
    via: set[str] = field(default_factory=set)        # the lists that ranked the document: meaning | keyword | phrase
    agree: int = 0                                      # how many lists put the document in their first TOP places
    rare: list[str] = field(default_factory=list)     # the question's rare phrases the document prints

    @property
    def strong(self) -> bool:
        """A candidate that should be read even when the plan chose other documents."""
        return self.agree >= 2 or bool(self.rare)


def distinctive_phrases(text: str, most: int = 8) -> list[str]:
    """The question's multi-word phrases of content words (2-3 words in a row, none generic), longest first:
    'How many primary health centres met the minimum staffing requirements in the drug revolving fund readiness
    assessment?' -> 'drug revolving fund', 'minimum staffing requirements', 'primary health centres', ..."""
    words = [w.strip("'’-").lower() for w in _TOKEN.findall(text or "")]
    runs, cur = [], []
    for w in words:
        if w in _STOP or len(w) < 3:
            if len(cur) >= 2:
                runs.append(cur)
            cur = []
        else:
            cur.append(w)
    if len(cur) >= 2:
        runs.append(cur)
    out: list[str] = []
    for run in runs:
        for n in (3, 2):
            for i in range(len(run) - n + 1):
                out.append(" ".join(run[i:i + n]))
    return list(dict.fromkeys(out))[:most]


def _vector(text: str) -> str | None:
    from app.retrieval.line_meaning import embed_queries
    v = embed_queries([text])
    return v[0] if v else None


def has_vectors(conn: psycopg.Connection) -> bool:
    try:
        return bool(conn.execute("SELECT 1 FROM chunks WHERE embedding IS NOT NULL LIMIT 1").fetchone())
    except Exception:              # noqa: BLE001 - before migration 0025
        conn.rollback()
        return False


def _doc_order(rows) -> list[str]:
    return list(dict.fromkeys(r[0] for r in rows))


def library_search(conn: psycopg.Connection, question: str, queries: list[str] | None = None, *, k: int = 8,
                   skip_docs: list[str] | None = None, tables: bool = False, vectors: bool = True,
                   docs: int = DOCS) -> list[LibHit]:
    """The library's best documents for a question and their best pages (PAGES_PER_DOC each), best first.
    `tables`: budget tables take part (a money question)."""
    qs = [q for q in dict.fromkeys([question, *(queries or [])]) if q and q.strip()]
    if not qs:
        return []
    skip = set(skip_docs or [])
    cats = dict(conn.execute("SELECT id, category FROM documents").fetchall())
    allowed = {d for d, c in cats.items() if d not in skip and (tables or c not in TABLE_CATEGORIES)}
    lists: dict[str, list[str]] = {}                 # list name -> documents in rank order
    best_chunk: dict[str, tuple[int, int]] = {}      # document -> (page, idx) of its best chunk in any list
    v = _vector(" ".join(qs[:2])) if vectors and has_vectors(conn) else None
    if v:
        rows = conn.execute(VEC_SQL, {"v": v, "skip": list(skip) or None, "tables": tables,
                                      "table_cats": list(TABLE_CATEGORIES)}).fetchall()
        lists["meaning"] = [d for d in _doc_order(rows) if d in allowed]
        for d, p, i in rows:
            best_chunk.setdefault(d, (p, i))
    # document and section cards (app/retrieval/cards.py): what each document is about, its places, years and
    # measures; a boost list like the others (never excludes), and a matching section's pages are read first
    from app.retrieval.cards import card_matches
    matches = [m for m in card_matches(conn, qs[0], v) if m.doc_id in allowed or (tables and m.doc_id not in skip)]
    if matches:
        lists["card"] = [m.doc_id for m in matches]
    section_pages = {m.doc_id: m.pages for m in matches if m.pages}
    keyword: dict[str, int] = {}
    for q in qs:
        q = _GENERIC.sub(" ", q).strip()        # 'Sokoto', 'State': every document prints them; they rank nothing
        if not q:
            continue
        for rank, h in enumerate(search(conn, q, k=60)):
            if h.doc_id in allowed:
                keyword[h.doc_id] = min(keyword.get(h.doc_id, rank), rank)
                best_chunk.setdefault(h.doc_id, (h.page, h.idx))
    lists["keyword"] = sorted(keyword, key=keyword.get)
    rare: dict[str, list[str]] = {}
    for ph in distinctive_phrases(" ".join(qs[:2])):
        rows = conn.execute(PHRASE_SQL, {"q": ph}).fetchall()
        if not rows or len(rows) > RARE:
            continue
        for d, p, i in rows:
            if d in allowed and ph not in rare.setdefault(d, []):
                rare[d].append(ph)
                best_chunk.setdefault(d, (p, i))
    lists["phrase"] = sorted(rare, key=lambda d: -len(rare[d]))
    scores: dict[str, float] = {}
    via: dict[str, set[str]] = {}
    agree: dict[str, int] = {}
    for name, order in lists.items():
        # cards boost; they never decide alone: with every document carded, a full-weight card list buried a
        # document whose card isn't built yet (a fresh fetch, its card still in the background)
        weight = {"phrase": 1.5, "meaning": 1.2, "card": CARD_WEIGHT}.get(name, 1.0)
        for rank, d in enumerate(order):
            scores[d] = scores.get(d, 0.0) + weight / (RRF_K + rank + 1)
            via.setdefault(d, set()).add(name)
            if rank < TOP:
                agree[d] = agree.get(d, 0) + 1
    chosen = sorted(scores, key=lambda d: -scores[d])[:docs]
    words = qs[0]                    # the question's own words rank its pages; the planner's queries are a fallback
    titles = dict(conn.execute("SELECT id, title FROM documents WHERE id = ANY(%s)", (chosen,)).fetchall()) \
        if chosen else {}
    years = dict(conn.execute("SELECT id, year FROM documents WHERE id = ANY(%s)", (chosen,)).fetchall()) \
        if chosen else {}
    out: list[LibHit] = []
    for d in chosen:
        # the document's best pages by the question's words, plus the best page of its matching section card
        pages = [r[0] for r in conn.execute(PAGE_SQL, {"q": words, "d": d, "k": PAGES_PER_DOC}).fetchall()]
        if d in section_pages:
            lo, hi = min(section_pages[d]), max(section_pages[d])
            sec = [r[0] for r in conn.execute(PAGE_SQL.replace("ORDER BY", "AND p.page BETWEEN %(lo)s AND %(hi)s ORDER BY"),
                                              {"q": words, "d": d, "k": 1, "lo": lo, "hi": hi}).fetchall()] or [lo]
            pages += [p for p in sec if p not in pages]
        if not pages and len(qs) > 1:
            pages = [r[0] for r in conn.execute(PAGE_SQL, {"q": " ".join(qs[1:]), "d": d,
                                                           "k": PAGES_PER_DOC}).fetchall()]
        if not pages and d in best_chunk:
            pages = [best_chunk[d][0]]
        for p in pages:
            idx = best_chunk[d][1] if best_chunk.get(d, (None,))[0] == p else 0
            text = (conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = %s", (d, p)).fetchone() or [""])[0]
            out.append(LibHit(Hit(d, titles.get(d, ""), years.get(d), p, text[:1200], scores[d], idx), scores[d],
                              via.get(d, set()), agree.get(d, 0), rare.get(d, [])))
    return out[:k]


def embed_chunks(conn: psycopg.Connection, doc_id: str | None = None, *, batch: int = 256, progress=None) -> int:
    """Fill the missing chunk vectors of one document (or all), committing each batch so a long backfill resumes."""
    from app.retrieval.line_meaning import embed_texts
    done = 0
    while True:
        rows = conn.execute("SELECT id, text FROM chunks WHERE (%(d)s::text IS NULL OR doc_id = %(d)s) "
                            "AND embedding IS NULL ORDER BY id LIMIT %(b)s", {"d": doc_id, "b": batch}).fetchall()
        if not rows:
            return done
        vecs = embed_texts([t[:2000] for _, t in rows])
        with conn.transaction():
            with conn.cursor() as cur:
                cur.executemany("UPDATE chunks SET embedding = %s::vector WHERE id = %s",
                                [(v, i) for (i, _), v in zip(rows, vecs)])
        done += len(rows)
        if progress:
            progress(done)


if __name__ == "__main__":  # python -m app.retrieval.library_search [doc_id]: fill missing chunk vectors
    import sys
    import time

    from app.config import get_settings

    logging.basicConfig(level=logging.INFO)
    t = time.time()
    with psycopg.connect(get_settings().db_url(), autocommit=True) as c:      # each batch commits: resumable
        total = c.execute("SELECT count(*) FROM chunks WHERE embedding IS NULL").fetchone()[0]
        n = embed_chunks(c, sys.argv[1] if len(sys.argv) > 1 else None, batch=64,
                         progress=lambda d: print(f"  {d}/{total} chunks ({time.time() - t:.0f}s)", flush=True))
    print(f"{n} chunks embedded in {time.time() - t:.0f}s")
