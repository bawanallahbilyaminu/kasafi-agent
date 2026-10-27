"""Index PDFs into Postgres: one row per page (for citations) plus searchable chunks.

Document text is untrusted data (CLAUDE.md rule 6): it is stored and searched, never executed
or followed. Pages with no text layer are stored with source='none' and need OCR later.
Re-indexing is idempotent: a document whose SHA-256 hasn't changed is skipped.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import psycopg
import pypdfium2 as pdfium

log = logging.getLogger(__name__)

CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200
MIN_PAGE_CHARS = 40   # less than this is treated as "no text layer"


@dataclass
class IndexResult:
    doc_id: str
    status: str          # "indexed" | "unchanged" | "missing" | "failed"
    pages: int = 0
    empty_pages: int = 0
    chunks: int = 0
    detail: str = ""


def normalise_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_file(doc: dict, data_dir: Path) -> Path | None:
    """<id>.pdf, or a local file named after the title (punctuation ignored), as in fetch_seed_docs.py."""
    by_id = data_dir / f"{doc['id']}.pdf"
    if by_id.exists():
        return by_id
    wanted = normalise_name(doc["title"])
    return next((p for p in data_dir.glob("*.pdf") if normalise_name(p.stem) == wanted), None)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 16):
            h.update(chunk)
    return h.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(path: Path) -> list[str]:
    pdf = pdfium.PdfDocument(str(path))
    try:
        return [clean_text(pdf[i].get_textpage().get_text_range()) for i in range(len(pdf))]
    finally:
        pdf.close()


def chunk_page(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split on line boundaries into ~size-char pieces with ~overlap chars repeated between pieces."""
    if len(text) <= size:
        return [text] if text else []
    lines, chunks, cur = text.split("\n"), [], ""
    for line in lines:
        while len(line) > size:                    # a single huge line (rare): hard-split it
            head, line = line[:size], line[size:]
            if cur:
                chunks.append(cur)
            chunks.append(head)
            cur = ""
        if cur and len(cur) + 1 + len(line) > size:
            chunks.append(cur)
            cur = cur[-overlap:].split("\n", 1)[-1] if overlap else ""
        cur = f"{cur}\n{line}" if cur else line
    if cur.strip():
        chunks.append(cur)
    return chunks


def index_document(conn: psycopg.Connection, doc: dict, path: Path, *, force: bool = False) -> IndexResult:
    sha = sha256_file(path)
    if not force:
        row = conn.execute("SELECT sha256 FROM documents WHERE id = %s", (doc["id"],)).fetchone()
        if row and row[0] == sha:
            return IndexResult(doc["id"], "unchanged")
    pages = extract_pages(path)
    empty = sum(len(p) < MIN_PAGE_CHARS for p in pages)
    with conn.transaction():
        conn.execute("DELETE FROM documents WHERE id = %s", (doc["id"],))   # cascades to pages/chunks
        conn.execute(
            """INSERT INTO documents (id, title, category, year, publisher, source_url, acquisition, sha256, page_count)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (doc["id"], doc["title"], doc.get("category"), doc.get("year"), doc.get("publisher"),
             doc.get("source_url"), doc.get("acquisition"), sha, len(pages)),
        )
        n_chunks = 0
        with conn.cursor() as cur:
            with cur.copy("COPY pages (doc_id, page, text, source) FROM STDIN") as cp:
                for i, text in enumerate(pages, start=1):
                    cp.write_row((doc["id"], i, text, "text" if len(text) >= MIN_PAGE_CHARS else "none"))
            with cur.copy("COPY chunks (doc_id, page, idx, text) FROM STDIN") as cp:
                for i, text in enumerate(pages, start=1):
                    if len(text) < MIN_PAGE_CHARS:
                        continue
                    for j, chunk in enumerate(chunk_page(text)):
                        cp.write_row((doc["id"], i, j, chunk))
                        n_chunks += 1
    return IndexResult(doc["id"], "indexed", len(pages), empty, n_chunks)


def index_manifest(conn: psycopg.Connection, manifest_path: Path, *, only: list[str] | None = None,
                   force: bool = False) -> list[IndexResult]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []
    for doc in manifest["documents"]:
        if only and doc["id"] not in only:
            continue
        path = find_file(doc, manifest_path.parent)
        if path is None:
            results.append(IndexResult(doc["id"], "missing", detail="no local PDF"))
            continue
        try:
            results.append(index_document(conn, doc, path, force=force))
        except pdfium.PdfiumError as e:
            results.append(IndexResult(doc["id"], "failed", detail=f"unreadable PDF: {e}"))
    return results
