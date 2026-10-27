"""Full-text search over indexed chunks (Postgres tsvector). Embeddings come in a later slice.

The agent searches in English, translating Hausa questions first, because the documents are
in English. A query first requires all its terms (websearch syntax), then falls back to any
term when too few chunks match. All of this is one round-trip.
"""

from __future__ import annotations

from dataclasses import dataclass

import psycopg


@dataclass
class Hit:
    doc_id: str
    title: str
    year: int | None
    page: int
    text: str
    rank: float


SQL = """
WITH q AS (
    SELECT websearch_to_tsquery('english', %(q)s) AS q_all,
           to_tsquery('english', replace(websearch_to_tsquery('english', %(q)s)::text, ' & ', ' | ')) AS q_any
),
all_terms AS (
    SELECT c.id, ts_rank_cd(c.tsv, q.q_all) + 1.0 AS rank          -- matching every term ranks first
    FROM chunks c, q WHERE c.tsv @@ q.q_all
      AND (%(docs)s::text[] IS NULL OR c.doc_id = ANY(%(docs)s::text[]))
    ORDER BY rank DESC LIMIT %(k)s
),
any_term AS (
    SELECT c.id, ts_rank_cd(c.tsv, q.q_any) AS rank
    FROM chunks c, q WHERE c.tsv @@ q.q_any
      AND (%(docs)s::text[] IS NULL OR c.doc_id = ANY(%(docs)s::text[]))
      AND (SELECT count(*) FROM all_terms) < %(k)s
    ORDER BY rank DESC LIMIT %(k)s
),
best AS (
    SELECT id, max(rank) AS rank FROM (SELECT * FROM all_terms UNION ALL SELECT * FROM any_term) u GROUP BY id
)
SELECT c.doc_id, d.title, d.year, c.page, c.text, b.rank
FROM best b JOIN chunks c ON c.id = b.id JOIN documents d ON d.id = c.doc_id
ORDER BY b.rank DESC LIMIT %(k)s
"""


def search(conn: psycopg.Connection, query: str, *, k: int = 8, doc_ids: list[str] | None = None) -> list[Hit]:
    rows = conn.execute(SQL, {"q": query, "k": k, "docs": doc_ids}).fetchall()
    return [Hit(*r) for r in rows]
