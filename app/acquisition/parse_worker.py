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

from app.retrieval.indexer import extract_pages, image_table_pages
from app.retrieval.ocr import render_page


def main() -> int:
    mode, path = sys.argv[1], Path(sys.argv[2])
    try:
        if mode == "unzip":
            print(json.dumps(unzip_pdf(path, Path(sys.argv[3]), int(sys.argv[4]))))
            return 0
        if mode == "evidence":
            print(json.dumps(locate_and_render(path, int(sys.argv[3]), sys.argv[4], Path(sys.argv[5]), float(sys.argv[6]))))
            return 0
        if mode == "text":
            max_pages = int(sys.argv[3])
            n = len(pdfium.PdfDocument(str(path)))
            if n > max_pages:
                print(json.dumps({"error": f"too many pages ({n} > {max_pages})"}))
                return 0
            print(json.dumps({"pages": extract_pages(path), "image_pages": sorted(image_table_pages(path))}))
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


def locate_and_render(path: Path, page_no: int, figure: str, out: Path, scale: float) -> dict:
    """Evidence crops: render one page to a JPEG and find a figure's characters and its whole row, in pixels.

    The row is every character whose vertical centre lies on the figure's line, from the row name to the
    last column. Pages without a text layer (scanned) return no row; the caller segments the table instead.
    """
    pdf = pdfium.PdfDocument(str(path))
    if not 1 <= page_no <= len(pdf):
        return {"error": f"no page {page_no}"}
    page = pdf[page_no - 1]
    w, h = page.get_size()
    img = page.render(scale=scale).to_pil().convert("RGB")
    img.save(out, format="JPEG", quality=88)
    result = {"image": str(out), "w": img.width, "h": img.height, "hit": None, "row": None}

    def px(left: float, bottom: float, right: float, top: float) -> list[int]:
        return [int(left * scale), int((h - top) * scale), int(right * scale) + 1, int((h - bottom) * scale) + 1]

    textpage = page.get_textpage()
    needle = figure.lstrip("-")
    found = textpage.search(needle, match_case=True).get_next() if needle else None
    if not found:
        return result
    start, count = found
    boxes = [textpage.get_charbox(i) for i in range(start, start + count)]
    left, bottom = min(b[0] for b in boxes), min(b[1] for b in boxes)
    right, top = max(b[2] for b in boxes), max(b[3] for b in boxes)
    result["hit"] = px(left, bottom, right, top)
    row_l, row_r = left, right
    for i in range(textpage.count_chars()):
        cl, cb, cr, ct = textpage.get_charbox(i)
        if cr - cl > 0 and bottom <= (cb + ct) / 2 <= top:
            row_l, row_r = min(row_l, cl), max(row_r, cr)
    result["row"] = px(row_l, bottom, row_r, top)
    return result


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
