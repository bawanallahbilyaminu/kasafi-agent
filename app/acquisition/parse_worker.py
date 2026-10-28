"""Child process for sandbox.py: extract page text from one PDF and print it as JSON.

Usage: python -E -s -m app.acquisition.parse_worker <pdf> <max_pages>
"""

import json
import sys
from pathlib import Path

import pypdfium2 as pdfium

from app.retrieval.indexer import extract_pages


def main() -> int:
    path, max_pages = Path(sys.argv[1]), int(sys.argv[2])
    try:
        n = len(pdfium.PdfDocument(str(path)))
        if n > max_pages:
            print(json.dumps({"error": f"too many pages ({n} > {max_pages})"}))
            return 0
        print(json.dumps({"pages": extract_pages(path)}))
    except pdfium.PdfiumError as e:
        print(json.dumps({"error": f"unreadable PDF: {e}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
