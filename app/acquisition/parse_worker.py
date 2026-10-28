"""Child process for sandbox.py: read one untrusted PDF, print the result as JSON.

Usage:
    python -E -s -m app.acquisition.parse_worker text <pdf> <max_pages>
    python -E -s -m app.acquisition.parse_worker render <pdf> <out_dir> <page> [<page> ...]
    python -E -s -m app.acquisition.parse_worker unzip <zip> <out_pdf> <max_bytes>
"""

import json
import sys
import zipfile
from pathlib import Path

import pypdfium2 as pdfium

from app.retrieval.indexer import extract_pages
from app.retrieval.ocr import render_page


def main() -> int:
    mode, path = sys.argv[1], Path(sys.argv[2])
    try:
        if mode == "unzip":
            print(json.dumps(unzip_pdf(path, Path(sys.argv[3]), int(sys.argv[4]))))
            return 0
        if mode == "text":
            max_pages = int(sys.argv[3])
            n = len(pdfium.PdfDocument(str(path)))
            if n > max_pages:
                print(json.dumps({"error": f"too many pages ({n} > {max_pages})"}))
                return 0
            print(json.dumps({"pages": extract_pages(path)}))
        else:   # render: one JPEG per page, for OCR
            out_dir, pages = Path(sys.argv[3]), [int(p) for p in sys.argv[4:]]
            pdf = pdfium.PdfDocument(str(path))
            files = {}
            for p in pages:
                f = out_dir / f"p{p}.jpg"
                f.write_bytes(render_page(pdf, p - 1))
                files[p] = str(f)
            print(json.dumps({"files": files}))
    except pdfium.PdfiumError as e:
        print(json.dumps({"error": f"unreadable PDF: {e}"}))
    return 0


MAX_ENTRIES = 50


def unzip_pdf(path: Path, out: Path, max_bytes: int) -> dict:
    """Extract the largest PDF from a ZIP, with zip-bomb limits (entry count, declared and actual size)."""
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile as e:
        return {"error": f"bad zip: {e}"}
    infos = z.infolist()
    if len(infos) > MAX_ENTRIES:
        return {"error": f"zip has too many entries ({len(infos)})"}
    pdfs = [i for i in infos if i.filename.lower().endswith(".pdf") and not i.is_dir()]
    if not pdfs:
        return {"error": "zip has no PDF"}
    best = max(pdfs, key=lambda i: i.file_size)
    if best.file_size > max_bytes:
        return {"error": f"PDF in zip too large ({best.file_size} bytes)"}
    written = 0
    with z.open(best) as src, out.open("wb") as dst:
        while chunk := src.read(1 << 16):
            written += len(chunk)
            if written > max_bytes:          # the declared size can lie
                break
            dst.write(chunk)
    if written > max_bytes:
        out.unlink(missing_ok=True)
        return {"error": "PDF in zip larger than declared"}
    with out.open("rb") as f:
        head = f.read(5)
    if not head.startswith(b"%PDF-"):
        out.unlink(missing_ok=True)
        return {"error": "file in zip is not a PDF"}
    return {"pdf": str(out), "name": Path(best.filename).name}


if __name__ == "__main__":
    sys.exit(main())
