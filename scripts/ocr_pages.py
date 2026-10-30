"""OCR every indexed page with no text layer (pages.source = 'none') using Muse Spark vision.

Each page is saved as soon as it's done (source='ocr' plus searchable chunks), so a re-run only
picks up what's left. A blank page is saved as source='ocr' with empty text, so it isn't retried.
Run it locally, where the PDFs are, then copy the index with: deploy/deploy.sh --sync-index

Usage:  uv run python scripts/ocr_pages.py [--only ID ...] [--limit N] [--concurrency 4]
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402
import pypdfium2 as pdfium  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.providers.chat import ProviderError  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402
from app.retrieval.indexer import accounting_negatives, find_file, ocr_page_chunks  # noqa: E402
from app.retrieval.ocr import ocr_image, render_page  # noqa: E402


def save_page(conn: psycopg.Connection, doc_id: str, page: int, text: str) -> int:
    text = accounting_negatives(text)
    chunks = ocr_page_chunks(text)
    with conn.transaction():
        conn.execute("UPDATE pages SET text = %s, source = 'ocr' WHERE doc_id = %s AND page = %s", (text, doc_id, page))
        conn.execute("DELETE FROM chunks WHERE doc_id = %s AND page = %s", (doc_id, page))
        for i, chunk in enumerate(chunks):
            conn.execute("INSERT INTO chunks (doc_id, page, idx, text) VALUES (%s, %s, %s, %s)", (doc_id, page, i, chunk))
    return len(chunks)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", metavar="ID")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--pdf-dir", type=Path, default=ROOT / "data",
                    help="where the PDFs are (the server: /data/pdfs, named <id>.pdf)")
    args = ap.parse_args()
    s = get_settings()
    manifest = {d["id"]: d for d in json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))["documents"]}

    with psycopg.connect(s.db_url(), connect_timeout=10, autocommit=True) as conn:
        todo = conn.execute("SELECT doc_id, page FROM pages WHERE source = 'none' ORDER BY doc_id, page").fetchall()
        todo = [(d, p) for d, p in todo if not args.only or d in args.only]
        if args.limit:
            todo = todo[: args.limit]
        print(f"{len(todo)} pages to OCR")
        pdfs: dict[str, pdfium.PdfDocument] = {}
        sem = asyncio.Semaphore(args.concurrency)
        done = failed = blank = 0
        t0 = time.perf_counter()

        async with MetaClient(s, timeout=240) as client:
            async def one(doc_id: str, page: int) -> None:
                nonlocal done, failed, blank
                if doc_id not in pdfs:
                    path = find_file(manifest[doc_id], args.pdf_dir)
                    pdfs[doc_id] = pdfium.PdfDocument(str(path))
                jpeg = render_page(pdfs[doc_id], page - 1)
                async with sem:
                    try:
                        text = await ocr_image(client, jpeg, model=s.meta_model)
                    except ProviderError as e:
                        failed += 1
                        print(f"  ✗ {doc_id} p{page}: {e}")
                        return
                n = save_page(conn, doc_id, page, text)
                done += 1
                blank += not text
                print(f"  ✓ {doc_id} p{page}: {len(text)} chars, {n} chunks  [{done + failed}/{len(todo)}]", flush=True)

            await asyncio.gather(*(one(d, p) for d, p in todo))

        left = conn.execute("SELECT count(*) FROM pages WHERE source = 'none'").fetchone()[0]
    print(f"\nOCR'd {done} pages ({blank} blank), {failed} failed, {left} still without text "
          f"({time.perf_counter() - t0:.0f}s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
