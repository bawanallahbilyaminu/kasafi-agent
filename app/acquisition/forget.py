"""Admin: forget a document (remove it from the index and delete its stored PDF), e.g. to reset the
live-fetch demo before recording.

    python -m app.acquisition.forget bir-2025-q3                  # shows what would be removed
    python -m app.acquisition.forget bir-2025-q3 --yes --reason "demo reset"

On the server (the api container has the app, the database settings and the /data volume):
    ssh vps docker exec kasafi-agent-api python -m app.acquisition.forget bir-2025-q3 [--yes --reason "..."]

Only documents Kasafi fetched itself (acquisition = fetched) are removed, unless --seed is given:
a seed document only comes back with deploy/deploy.sh --sync-index. Every removal is appended to
<KASAFI_FETCH_DIR>/forgotten.jsonl with its provenance, so the record survives the deletion.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

from app.config import Settings, get_settings


def describe(conn: psycopg.Connection, doc_id: str) -> dict | None:
    row = conn.execute(
        "SELECT id, title, acquisition, status, source_url, final_url, sha256, fetched_at, indexed_at, page_count, "
        "(SELECT count(*) FROM chunks WHERE doc_id = d.id) FROM documents d WHERE id = %s", (doc_id,)).fetchone()
    if not row:
        return None
    keys = ("id", "title", "acquisition", "status", "source_url", "final_url", "sha256", "fetched_at", "indexed_at",
            "pages", "chunks")
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in zip(keys, row)}


def forget(conn: psycopg.Connection, doc_id: str, settings: Settings, *, reason: str, allow_seed: bool = False,
           dry_run: bool = True) -> dict:
    doc = describe(conn, doc_id)
    if doc is None:
        raise SystemExit(f"no document with id {doc_id!r}")
    if doc["acquisition"] not in ("fetched", "scheduled") and not allow_seed:
        raise SystemExit(f"{doc_id} is a seed document ({doc['acquisition']}); add --seed to remove it anyway "
                         "(it only comes back with deploy/deploy.sh --sync-index)")
    fetch_dir = Path(settings.kasafi_fetch_dir)
    pdf = fetch_dir / f"{doc_id}.pdf"
    record = {"forgotten_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "reason": reason,
              "file": str(pdf) if pdf.exists() else None, **doc}
    if dry_run:
        return record
    with conn.transaction():
        conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))   # cascades to pages and chunks
    pdf.unlink(missing_ok=True)
    fetch_dir.mkdir(parents=True, exist_ok=True)
    with (fetch_dir / "forgotten.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Remove a document from the index and delete its stored PDF.")
    ap.add_argument("doc_id")
    ap.add_argument("--yes", action="store_true", help="really remove it (without this, only show what would go)")
    ap.add_argument("--reason", default="", help='why, for the log, e.g. "demo reset"')
    ap.add_argument("--seed", action="store_true", help="also allow removing a seed (non-fetched) document")
    args = ap.parse_args(argv)
    settings = get_settings()
    with psycopg.connect(settings.db_url(), connect_timeout=10) as conn:
        rec = forget(conn, args.doc_id, settings, reason=args.reason, allow_seed=args.seed, dry_run=not args.yes)
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    if args.yes:
        print(f"removed {args.doc_id}: {rec['pages']} pages, {rec['chunks']} chunks"
              + (f", file {rec['file']}" if rec["file"] else ", no stored file") + "; logged to forgotten.jsonl")
    else:
        print(f"DRY RUN: nothing removed. Add --yes to remove {args.doc_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
