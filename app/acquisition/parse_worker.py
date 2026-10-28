"""Child process for sandbox.py: read one untrusted PDF, print the result as JSON.

Usage:
    python -E -s -m app.acquisition.parse_worker text <pdf> <max_pages>
    python -E -s -m app.acquisition.parse_worker render <pdf> <out_dir> <page> [<page> ...]
"""

import json
import sys
from pathlib import Path

import pypdfium2 as pdfium

from app.retrieval.indexer import extract_pages
from app.retrieval.ocr import render_page


def main() -> int:
    mode, path = sys.argv[1], Path(sys.argv[2])
    try:
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


if __name__ == "__main__":
    sys.exit(main())
