"""Load the official outlooks in data/official_outlooks.yaml (NIHSA AFO 2026, NiMet SCP 2026 and its update) into the
advisories table, after checking every quote and table cell against the indexed page text. One missing quote or
cell and nothing is written. Run after the documents are indexed and OCR'd (scripts/index_docs.py,
scripts/ocr_pages.py), locally and on the server.

    uv run python scripts/official_outlooks.py [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402
import yaml  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.sources.lga_names import pcode  # noqa: E402

SPEC = ROOT / "data" / "official_outlooks.yaml"


def norm(text: str) -> str:
    return " ".join((text or "").split())


def _ts(d) -> datetime | None:
    if d is None:
        return None
    d = d if isinstance(d, date) else date.fromisoformat(str(d))
    return datetime.combine(d, time(23, 59), tzinfo=timezone.utc)


def table_rows(page_texts: list[str], state: str, n: int) -> list[tuple[str, list[str]]]:
    """(location, n cells) for the state's block of a 'State | Location | n columns' table spread over pages: the
    row whose first cell is the state, then the rows under it, until the next state's row. Rows are told apart by
    their cell count, not their pipes, since OCR prints them either way: 'Sokoto | Gudu North | ...' and
    '| Bodinga | ...' (no state cell), or '| Sokoto | Gudu North | ...' and '| | Illela | ...' (an empty one)."""
    rows, inside = [], False
    for text in page_texts:
        for line in text.splitlines():
            line = line.strip()
            if "|" not in line:
                continue
            body = line[1:] if line.startswith("|") else line
            cells = [c.strip() for c in (body[:-1] if body.endswith("|") else body).split("|")]
            if len(cells) == n + 2 and cells[0]:                    # a state's first row
                if cells[0].lower() == state.lower():
                    inside = True
                    rows.append((cells[1], cells[2:]))
                elif inside:
                    return rows
            elif inside and len(cells) == n + 2:                    # under the state, its cell left empty
                rows.append((cells[1], cells[2:]))
            elif inside and len(cells) == n + 1:                    # under the state, no state cell
                rows.append((cells[0], cells[1:]))
    return rows


def build(conn, spec: dict) -> tuple[list[dict], list[str]]:
    """The advisory rows, and the problems (a quote or cell not on its page)."""
    docs, out, problems = spec["documents"], [], []
    page = {}
    for doc in docs:
        page.update({(doc, p): t or "" for p, t in conn.execute(
            "SELECT page, text FROM pages WHERE doc_id = %s", (doc,)).fetchall()})

    def row(item: dict, text: str, pg: int, lgas: list[str], state_wide: bool, title: str) -> dict:
        d = docs[item["doc"]]
        return {"source": d["source"], "title": title[:300], "kind": "outlook", "hazard": item["hazard"],
                "issued_at": _ts(d["issued_at"]), "valid_until": _ts(item.get("valid_until")), "lgas": lgas,
                "state_wide": state_wide, "text": text, "url": d.get("url") or "", "doc_id": item["doc"],
                "page": pg, "covers": item["covers"], "issued_label": str(d["issued_label"]),
                "key": f"{item['doc']}:p{pg}:{hashlib.sha1(text.encode()).hexdigest()[:10]}"}

    for q in spec.get("quotes", []):
        if norm(q["text"]) not in norm(page.get((q["doc"], q["page"]), "")):
            problems.append(f"{q['doc']} p{q['page']}: quote not on the page: {q['text'][:70]}")
            continue
        lgas = [c for n in q.get("lgas", []) if (c := pcode(n))]
        if len(lgas) != len(q.get("lgas", [])):
            problems.append(f"{q['doc']} p{q['page']}: an LGA name didn't resolve: {q.get('lgas')}")
        out.append(row(q, q["text"], q["page"], lgas, q.get("state_wide", not lgas), q["title"]))

    for t in spec.get("tables", []):
        texts = [page.get((t["doc"], p), "") for p in t["pages"]]
        found = table_rows(texts, t["state"], len(t["columns"]))
        if not found:
            problems.append(f"{t['doc']} p{t['pages']}: no {t['state']} rows")
        for location, cells in found:
            if len(cells) != len(t["columns"]):
                problems.append(f"{t['doc']} {location}: {len(cells)} cells for {len(t['columns'])} columns")
                continue
            hits = [(p, ln) for p, x in zip(t["pages"], texts) for ln in x.splitlines()
                    if location in ln and all(c in ln for c in cells)]
            where = hits[0][0] if hits else t["pages"][0]
            if not hits:
                problems.append(f"{t['doc']} p{where} {location}: a cell isn't on the row")
                continue
            code = pcode(location)
            text = f"{location}: " + "; ".join(f"{col}: {c}" for col, c in zip(t["columns"], cells))
            out.append(row(t, text, where, [code] if code else [], False, t["title"]))
    return out, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    with psycopg.connect(get_settings().db_url()) as conn:
        rows, problems = build(conn, spec)
        for r in rows:
            print(f"{r['doc_id']:22} p{r['page']:<4} {r['hazard']:9} {r['covers']:32} "
                  f"{','.join(r['lgas']) or ('state' if r['state_wide'] else '-'):12} {r['text'][:90]}")
        if problems:
            print("\nNOT LOADED:", *problems, sep="\n  ")
            return 1
        if args.dry_run:
            print(f"\n{len(rows)} rows checked (dry run)")
            return 0
        with conn.transaction():
            conn.execute("DELETE FROM advisories WHERE doc_id = ANY(%s)", (list(spec["documents"]),))
            for r in rows:
                conn.execute(
                    "INSERT INTO advisories (source, title, kind, hazard, issued_at, valid_until, lgas, state_wide, "
                    "text, url, key, doc_id, page, covers, issued_label) VALUES (%(source)s, %(title)s, %(kind)s, "
                    "%(hazard)s, %(issued_at)s, %(valid_until)s, %(lgas)s, %(state_wide)s, %(text)s, %(url)s, "
                    "%(key)s, %(doc_id)s, %(page)s, %(covers)s, %(issued_label)s)", r)
        print(f"\n{len(rows)} official outlook rows loaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
