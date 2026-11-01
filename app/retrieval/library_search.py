"""The library-wide search: every indexed document is a candidate for every question (1 Nov 2026).

A newly indexed plan (the Sokoto Health Resource Optimization Plan) was never read for three questions it answers:
the planner chose budgets for one, and for the other two the 320-page EmONC assessment filled every keyword slot.
So every path also runs this search over ALL documents and merges its best hits:

- keyword search with the question and the planner's queries (Postgres full text), each unscoped;
- meaning search: the question's vector against every chunk's vector (bge-small, run locally; migration 0025);
- distinctive phrases: the question's multi-word phrases ('drug revolving fund', 'minimum staffing requirements')
  matched as phrases; a chunk that prints two or more of them ranks first: an exact match must be found if it exists.

The lists are fused by reciprocal rank, and at most PER_DOC hits come from one document, so one long report can't
take every place. Ranking may prefer the planned documents (the caller's choice); nothing here excludes any.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import psycopg

from app.retrieval.search import Hit, search

log = logging.getLogger(__name__)

PER_DOC = 2
RRF_K = 20                     # reciprocal-rank constant: small, so the first places of each list count most
STRONG_SIM = 0.72              # a chunk this close in meaning (cosine) is a strong candidate on its own
VEC_SQL = """
SELECT c.doc_id, d.title, d.year, c.page, c.text, 1 - (c.embedding <=> %(v)s::vector) AS sim, c.idx
FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE c.embedding IS NOT NULL AND (%(skip)s::text[] IS NULL OR NOT c.doc_id = ANY(%(skip)s::text[]))
ORDER BY c.embedding <=> %(v)s::vector LIMIT %(k)s
"""
PHRASE_SQL = """
SELECT c.doc_id, d.title, d.year, c.page, c.text, 1.0, c.idx
FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE c.tsv @@ phraseto_tsquery('english', %(q)s)
  AND (%(skip)s::text[] IS NULL OR NOT c.doc_id = ANY(%(skip)s::text[]))
LIMIT %(k)s
"""

# words that make a phrase generic: every document prints them
_STOP = {"the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "by", "with", "at", "from", "is", "are", "was",
         "were", "be", "been", "has", "have", "had", "how", "what", "which", "who", "when", "where", "why", "much",
         "many", "did", "does", "do", "that", "this", "these", "those", "its", "it", "their", "there", "as", "into",
         "according", "about", "any", "all", "some", "per", "than", "then", "more", "most", "less", "share", "number",
         "amount", "total", "plan", "planned", "plans", "sokoto", "state", "states", "nigeria", "government", "year",
         "years", "figure", "figures", "data", "show", "shows", "say", "says", "report", "document", "documents",
         "kasafi", "please", "tell", "me", "us", "give", "list", "can", "could", "would", "should", "will", "met",
         "paid", "raise", "budget", "spending"}
_TOKEN = re.compile(r"[A-Za-z][A-Za-z'’-]+")


@dataclass
class LibHit:
    hit: Hit
    score: float = 0.0
    via: set[str] = field(default_factory=set)        # keyword | meaning | phrase
    phrases: int = 0                                    # distinct distinctive phrases the chunk prints
    sim: float = 0.0                                    # cosine similarity to the question

    @property
    def strong(self) -> bool:
        """A candidate that should be read even when the plan chose other documents."""
        return self.phrases >= 2 or self.sim >= STRONG_SIM or (self.phrases >= 1 and len(self.via) >= 2)


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


def library_search(conn: psycopg.Connection, question: str, queries: list[str] | None = None, *, k: int = 8,
                   per_doc: int = PER_DOC, skip_docs: list[str] | None = None, vectors: bool = True) -> list[LibHit]:
    """The best chunks of the whole library for a question, at most `per_doc` from one document, best first."""
    qs = [q for q in dict.fromkeys([question, *(queries or [])]) if q and q.strip()]
    skip = list(skip_docs) if skip_docs else None
    lists: list[tuple[str, list[Hit], float]] = []           # (via, hits in rank order, weight)
    for q in qs:
        hits = [h for h in search(conn, q, k=12) if not skip or h.doc_id not in skip]
        lists.append(("keyword", hits, 1.0))
    sims: dict[tuple[str, int, int], float] = {}
    if vectors and has_vectors(conn) and (v := _vector(" ".join(qs[:2]))):
        rows = conn.execute(VEC_SQL, {"v": v, "k": 24, "skip": skip}).fetchall()
        hits = [Hit(*r) for r in rows]
        sims = {(h.doc_id, h.page, h.idx): float(h.rank) for h in hits}
        lists.append(("meaning", hits, 1.2))
    phrase_count: dict[tuple[str, int, int], int] = {}
    phrase_hit: dict[tuple[str, int, int], Hit] = {}
    for ph in distinctive_phrases(" ".join(qs[:2])):
        for r in conn.execute(PHRASE_SQL, {"q": ph, "k": 40, "skip": skip}).fetchall():
            h = Hit(*r)
            key = (h.doc_id, h.page, h.idx)
            phrase_count[key] = phrase_count.get(key, 0) + 1
            phrase_hit[key] = h
    if phrase_count:
        ranked = sorted(phrase_count, key=lambda x: -phrase_count[x])
        lists.append(("phrase", [phrase_hit[x] for x in ranked], 1.5))
    fused: dict[tuple[str, int, int], LibHit] = {}
    for via, hits, weight in lists:
        for rank, h in enumerate(hits):
            key = (h.doc_id, h.page, h.idx)
            lh = fused.setdefault(key, LibHit(h))
            lh.score += weight / (RRF_K + rank + 1)
            lh.via.add(via)
    for key, lh in fused.items():
        lh.phrases = phrase_count.get(key, 0)
        lh.sim = sims.get(key, 0.0)
        lh.score += 0.05 * max(0, lh.phrases - 1)            # each further phrase printed together: an exact match
    out, per = [], {}
    for lh in sorted(fused.values(), key=lambda x: -x.score):
        d = lh.hit.doc_id
        if per.get(d, 0) >= per_doc:
            continue
        per[d] = per.get(d, 0) + 1
        out.append(lh)
        if len(out) >= k:
            break
    return out


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
        n = embed_chunks(c, sys.argv[1] if len(sys.argv) > 1 else None,
                         progress=lambda d: print(f"  {d}/{total} chunks ({time.time() - t:.0f}s)", flush=True))
    print(f"{n} chunks embedded in {time.time() - t:.0f}s")
