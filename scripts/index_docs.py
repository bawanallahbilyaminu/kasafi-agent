"""Index the seed documents in data/manifest.json into the database.

Usage:  uv run python scripts/index_docs.py [--only ID ...] [--force]
Runs `alembic upgrade head` first if needed (alembic.ini at the repo root).
"""

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.retrieval.indexer import index_manifest  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", metavar="ID")
    ap.add_argument("--force", action="store_true", help="re-index even if the file is unchanged")
    ap.add_argument("--pdf-dir", type=Path, help="where the PDFs are (the server: /data/pdfs, named <id>.pdf)")
    args = ap.parse_args()
    t0 = time.perf_counter()
    with psycopg.connect(get_settings().db_url(), connect_timeout=10) as conn:
        results = index_manifest(conn, ROOT / "data/manifest.json", only=args.only, force=args.force,
                                 pdf_dir=args.pdf_dir)
        totals = conn.execute("SELECT count(*), (SELECT count(*) FROM pages), (SELECT count(*) FROM chunks), "
                              "(SELECT count(*) FROM pages WHERE source = 'none') FROM documents").fetchone()
    print(f"{'document':<34} {'status':<10} {'pages':>5} {'empty':>5} {'chunks':>6}  detail")
    for r in results:
        print(f"{r.doc_id:<34} {r.status:<10} {r.pages:>5} {r.empty_pages:>5} {r.chunks:>6}  {r.detail}")
    print(f"\nin database: {totals[0]} documents, {totals[1]} pages, {totals[2]} chunks, "
          f"{totals[3]} pages need OCR  ({time.perf_counter() - t0:.0f}s)")
    return 1 if any(r.status in ("failed", "missing") for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
