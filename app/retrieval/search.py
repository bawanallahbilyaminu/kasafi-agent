"""Full-text search over indexed chunks (Postgres tsvector). Embeddings come in a later slice.

The agent searches in English, translating Hausa questions first, because the documents are
in English. A query first requires all its terms (websearch syntax), then falls back to any
term when too few chunks match. All of this is one round-trip.
"""

from __future__ import annotations

import re
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
    idx: int = 0          # chunk position on its page, for fetching neighbours


SQL = """
WITH q AS (
    SELECT websearch_to_tsquery('english', %(q)s) AS q_all,
           to_tsquery('english', replace(websearch_to_tsquery('english', %(q)s)::text, ' & ', ' | ')) AS q_any
),
all_terms AS (
    SELECT c.id, ts_rank_cd(c.tsv, q.q_all) + 1.0 AS rank          -- matching every term ranks first
    FROM chunks c, q WHERE c.tsv @@ q.q_all
      AND (%(docs)s::text[] IS NULL OR c.doc_id = ANY(%(docs)s::text[]))
      AND (NOT %(key_rows)s OR (c.text LIKE '%% | %%'
           AND length(c.text) - length(replace(c.text, chr(10), '')) <= 1))
      AND (NOT %(prose)s OR (c.text ~ %(sentences)s AND c.text ~ %(ends)s
           AND regexp_replace(c.text, '^\\[Table:[^\\n]*\\n', '') !~ '\\.{6,}'
           AND (length(c.text) - length(replace(c.text, ' | ', ''))) / 3 <= 2))
    ORDER BY rank DESC LIMIT %(k)s
),
any_term AS (
    SELECT c.id, ts_rank_cd(c.tsv, q.q_any) AS rank
    FROM chunks c, q WHERE c.tsv @@ q.q_any
      AND (%(docs)s::text[] IS NULL OR c.doc_id = ANY(%(docs)s::text[]))
      AND (NOT %(key_rows)s OR (c.text LIKE '%% | %%'
           AND length(c.text) - length(replace(c.text, chr(10), '')) <= 1))
      AND (NOT %(prose)s OR (c.text ~ %(sentences)s AND c.text ~ %(ends)s
           AND regexp_replace(c.text, '^\\[Table:[^\\n]*\\n', '') !~ '\\.{6,}'
           AND (length(c.text) - length(replace(c.text, ' | ', ''))) / 3 <= 2))
      AND (SELECT count(*) FROM all_terms) < %(k)s
    ORDER BY rank DESC LIMIT %(k)s
),
best AS (
    SELECT id, max(rank) AS rank FROM (SELECT * FROM all_terms UNION ALL SELECT * FROM any_term) u GROUP BY id
)
SELECT c.doc_id, d.title, d.year, c.page, c.text, b.rank, c.idx
FROM best b JOIN chunks c ON c.id = b.id JOIN documents d ON d.id = c.doc_id
ORDER BY b.rank DESC LIMIT %(k)s
"""


PHRASE_SQL = """
SELECT c.doc_id, d.title, d.year, c.page, c.text, ts_rank_cd(c.tsv, phraseto_tsquery('english', %(q)s)) AS rank, c.idx
FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE c.tsv @@ phraseto_tsquery('english', %(q)s)
  AND c.text ~ '(N|₦)\\s?[0-9][0-9,.]{2,}|[0-9]{1,3},[0-9]{3}'     -- an amount, not a year or a chart axis
  AND (%(docs)s::text[] IS NULL OR c.doc_id = ANY(%(docs)s::text[]))
ORDER BY rank DESC LIMIT %(k)s
"""


# Everyday words for indicators that surveys print under their technical names: NDHS Table 11.1 heads Sokoto's
# 42.8% stunting "Height-for-age1 ... below -2 SD" and never says "stunted", so a question's words alone can't reach
# it. The printed name 'or' its first word: a footnote mark glued to it ("age1") breaks the full name's match.
PRINTED_AS = (
    (re.compile(r"(?i)\bstunt\w*"), "height-for-age or height"),
    (re.compile(r"(?i)\bwast(?:ed|ing)\b"), "weight-for-height or weight"),
    (re.compile(r"(?i)\bunderweight\b"), "weight-for-age or weight"),
)


def printed_names(query: str) -> list[str]:
    """The printed names of the indicators a query names in everyday words ('stunted' -> 'height-for-age')."""
    return [printed.split(" or ")[0] for pat, printed in PRINTED_AS if pat.search(query or "")]


def printed_query(query: str) -> str:
    """The query with each everyday indicator word replaced by the name surveys print, or '' when none."""
    out = query
    for pat, printed in PRINTED_AS:
        out = pat.sub(printed, out)
    return out if out != query else ""


# running text: six lower-case words in a row and at least two sentence ends (a BIR's narrative sits under the
# table title the indexer carries over, so '[Table:' can't tell prose from a table; a long programme name in a
# table row can look like six words, so the sentence ends decide); dotted leaders mark a table of contents
SENTENCES = r"(?:[a-z]+ ){5}[a-z]+"       # any six lower-case words in a row ('was allocated a total of the')
SENTENCE_ENDS = r"[a-z0-9%)]\.\s+[A-Z].*[a-z0-9%)]\.(\s|$)"


def is_prose(text: str) -> bool:
    """The same test in Python (the eval generator picks narrative paragraphs with it). The carried-over
    '[Table: …]' title line is left out of the leaders test: a narrative page's title can come from a contents
    line ('Table 30: … 58')."""
    body = re.sub(r"^\[Table:[^\n]*\n", "", text)
    return bool(re.search(SENTENCES, body) and re.search(SENTENCE_ENDS, body, re.S) and not re.search(r"\.{6,}", body)
                and body.count(" | ") <= 2)


def search(conn: psycopg.Connection, query: str, *, k: int = 8, doc_ids: list[str] | None = None,
           key_rows: bool = False, prose: bool = False) -> list[Hit]:
    """key_rows=True searches only labelled single-row chunks ("[Table: ...]" + one table row): exact facts
    such as a ministry's total, which keyword ranking over whole pages tends to bury. A query naming an indicator
    in everyday words also runs with its printed name, and the best hits of both are kept. prose=True searches only
    running text (no table rows): a report's narrative, for what it explains, corrects or notes."""
    rows = conn.execute(SQL, {"q": query, "k": k, "docs": doc_ids, "key_rows": key_rows, "prose": prose, "sentences": SENTENCES, "ends": SENTENCE_ENDS}).fetchall()
    if alt := printed_query(query):
        seen = {(r[0], r[3], r[6]) for r in rows}
        more = [r for r in conn.execute(SQL, {"q": alt, "k": k, "docs": doc_ids, "key_rows": key_rows, "prose": prose, "sentences": SENTENCES, "ends": SENTENCE_ENDS}).fetchall()
                if (r[0], r[3], r[6]) not in seen]
        rows = sorted(rows + more, key=lambda r: -r[5])[:k]
    return [Hit(*r) for r in rows]


def phrase_search(conn: psycopg.Connection, phrase: str, *, k: int = 2, doc_ids: list[str] | None = None) -> list[Hit]:
    """Chunks that print this exact phrase (as words in order) and a figure: a key term as the document names it
    ("Debt Stock - Sokoto State Debt Stock ... N104,450 million in 2022"), which pages that only say "debt" a
    lot (charts, ratio tables) outrank in keyword search."""
    rows = conn.execute(PHRASE_SQL, {"q": phrase, "k": k, "docs": doc_ids}).fetchall()
    return [Hit(*r) for r in rows]
