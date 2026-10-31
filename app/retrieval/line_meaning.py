"""What a budget line is, beyond its printed name: code descriptions and a meaning vector.

Project rows often print only a fragment of the project's name ("Ministry of Health 23010122 - PURCHASE OF HEALTH /
MEDICAL EQUIPMENT ... 33312100 - WAMAKKO") or a name in its own words ("Trycle bicycle for disable"). Two things make
them findable by what they are:

- context: the standard descriptions of the line's economic, function, programme and administrative codes and of their
  parent categories (economic 23010104 -> 230101 -> 2301 -> 23; function 71012 -> 7101 -> 710; an agency -> its
  ministry and sector), all read from the documents' own classification tables, never written by hand;
- embedding: a vector of the name and context from a small local English model (the documents are English, and
  questions are translated to English before search), so "assistive devices" can match "tricycle for disabled".
"""

from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from functools import lru_cache

import psycopg

log = logging.getLogger(__name__)

MODEL = "BAAI/bge-small-en-v1.5"
DIM = 384

# "23010104 - PURCHASE MOTOR CYCLES": a code and the description printed after it, up to the next code
_PAIR = re.compile(r"\b(\d{5,12})\s+-\s+(.+?)(?=\s+\d{5,12}\s+-\s|$)")
_KIND_OF_TITLE = [("economic", "economic"), ("function", "function"), ("administrative", "admin"),
                  ("programme", "programme"), ("by mda", "admin")]
_PARENTS = {"economic": (6, 4, 2), "function": (4, 3), "programme": (4, 2)}


def label(row_text: str) -> str:
    """The printed name part of a row (before the first labelled cell)."""
    return row_text.split(" | ", 1)[0].strip()


def kind_of_code(code: str) -> str | None:
    """The code family, from its shape: 12-digit agencies, 8-digit economic items (333xxxxx are places),
    function codes starting with 7."""
    if len(code) == 12:
        return "admin"
    if len(code) == 8:
        return None if code.startswith("333") else "economic"
    if code.startswith("7") and 3 <= len(code) <= 5:
        return "function"
    return None


def kind_of_table(title: str) -> str | None:
    t = title.lower()
    return next((k for word, k in _KIND_OF_TITLE if word in t), None)


def kind_in_table(title: str, code: str) -> str | None:
    """The family of a classification-table row's own code, when its shape fits the table (an administrative
    table also prints 8-digit revenue codes; a mis-titled table may print programme codes)."""
    kind = kind_of_table(title)
    if not code.isdigit() or kind is None:
        return None
    if kind == "admin":
        return "admin" if len(code) == 12 else kind_of_code(code)
    if kind == "economic":
        return kind if code[0] in "1234" and len(code) in (2, 4, 6, 8) else None
    if kind == "function":
        return kind if code.startswith("7") and 3 <= len(code) <= 5 else None
    return kind if len(code) in (2, 4, 6) else None


def parents(kind: str, code: str) -> list[str]:
    """Parent codes, nearest first."""
    if kind == "admin":
        # 052102600100 (an agency) -> 050000000000 (its sector); the digits in between don't reliably name a ministry
        return [p for p in (code[:2] + "0" * 10,) if p != code]
    return [code[:n] for n in _PARENTS.get(kind, ()) if n < len(code)]


def build_names(rows: list[tuple[str, str, str, str]]) -> dict[str, dict[str, str]]:
    """{kind: {code: description}} from (table_title, code, name, row_text) of every line: classification-table
    rows give their own code and name; project rows give the code - description pairs they print."""
    seen: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for title, code, name, row_text in rows:
        kind = kind_in_table(title or "", code or "")
        if kind and not re.search(r"\d{5,}", name):
            seen[kind][code][" ".join(name.split())] += 1
        for c, desc in _PAIR.findall(label(row_text)):
            k = kind_of_code(c)
            if k and not re.search(r"\d{5,}", desc):
                seen[k][c][" ".join(desc.split())] += 1
    return {k: {c: n.most_common(1)[0][0] for c, n in codes.items()} for k, codes in seen.items()}


def codes_on(table_title: str, code: str, row_text: str) -> list[tuple[str, str]]:
    """(kind, code) for every code printed on a line: the pairs in its name, and its own code in a classification
    table."""
    out = [(k, c) for c, _ in _PAIR.findall(label(row_text)) if (k := kind_of_code(c))]
    kind = kind_in_table(table_title or "", code or "")
    if kind and (kind, code) not in out:
        out.append((kind, code))
    return out


def context_of(table_title: str, code: str, row_text: str, names: dict[str, dict[str, str]],
               depth: int | None = None) -> str:
    """The descriptions of a line's codes and of their parents that the printed row doesn't already say;
    `depth` keeps only the nearest parents (broad ones such as 'CAPITAL EXPENDITURE' make every line alike)."""
    printed = label(row_text).lower()
    out: list[str] = []
    for kind, c in codes_on(table_title, code, row_text):
        book = names.get(kind, {})
        for p in [c, *parents(kind, c)][:None if depth is None else depth + 1]:
            d = book.get(p)
            if d and d.lower() not in printed and d not in out:
                out.append(d)
    return "; ".join(out)


def meaning_text(row_text: str, context: str) -> str:
    """What is embedded: the printed name without its codes, then the context."""
    name = re.sub(r"\b\d{5,12}\b\s*-?\s*", " ", label(row_text))
    return " ".join(f"{name}. {context}".split())[:500]


_model_lock = __import__("threading").Lock()


@lru_cache(maxsize=1)
def _model():
    from fastembed import TextEmbedding
    return TextEmbedding(MODEL)


def model():
    """The embedding model, loaded once even when several search threads ask for it at the same moment."""
    with _model_lock:
        return _model()


def _literal(v) -> str:
    return "[" + ",".join(f"{x:.5f}" for x in v) + "]"


def embed_texts(texts: list[str]) -> list[str]:
    """Passage vectors as pgvector literals."""
    return [_literal(v) for v in model().embed(texts, batch_size=32)]   # small batches: the API runs in 1 GB


def embed_queries(texts: list[str]) -> list[str]:
    """Query vectors as pgvector literals; [] if the model can't load (search then runs on keywords alone)."""
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return []
    try:
        return [_literal(v) for v in model().query_embed(texts)]
    except Exception as e:  # model files missing or unreadable: never take search down with it
        log.warning("meaning search off: %s", e)
        return []


def enrich(conn: psycopg.Connection, doc_id: str | None = None, *, embed: bool = True) -> int:
    """Fill context (and embeddings) for one document's lines, or every line when doc_id is None."""
    names = build_names(conn.execute("SELECT table_title, code, name, row_text FROM budget_lines").fetchall())
    lines = conn.execute("SELECT id, COALESCE(table_title, ''), COALESCE(code, ''), row_text FROM budget_lines "
                         "WHERE %(d)s::text IS NULL OR doc_id = %(d)s", {"d": doc_id}).fetchall()
    if not lines:
        return 0
    contexts = [context_of(t, c, r, names) for _, t, c, r in lines]
    texts = [meaning_text(r, context_of(t, c, r, names, depth=1)) for _, t, c, r in lines]
    vectors: dict[str, str] = {}
    if embed:
        unique = list(dict.fromkeys(texts))
        vectors = dict(zip(unique, embed_texts(unique)))
    with conn.transaction():
        conn.execute("CREATE TEMP TABLE line_meaning (id TEXT, context TEXT, embedding TEXT) ON COMMIT DROP")
        with conn.cursor() as cur, cur.copy("COPY line_meaning (id, context, embedding) FROM STDIN") as cp:
            for (lid, *_), ctx, text in zip(lines, contexts, texts):
                cp.write_row((lid, ctx, vectors.get(text)))
        conn.execute("UPDATE budget_lines l SET context = m.context, "
                     "embedding = COALESCE(m.embedding::vector, l.embedding) FROM line_meaning m WHERE l.id = m.id")
    return len(lines)


if __name__ == "__main__":  # python -m app.retrieval.line_meaning: (re)fill every line
    import sys
    import time

    from app.config import get_settings

    logging.basicConfig(level=logging.INFO)
    t = time.time()
    with psycopg.connect(get_settings().db_url()) as c:
        n = enrich(c, sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"{n} lines enriched in {time.time() - t:.0f}s")
