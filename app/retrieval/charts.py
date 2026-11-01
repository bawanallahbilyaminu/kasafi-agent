"""Charts on text pages (2 Nov 2026): found locally, read once at index time by a vision model, stored as data.

OCR runs only on pages with no text layer, so a chart on a text page (a bar chart of the causes of maternal deaths
under 'Figure 3' on a page of running text) was invisible: its labels and values are drawn, not text.

1. DETECT (no model, here): on every text page, regions that are an embedded image or a cluster of filled vector
   shapes (bars, pie wedges, plotted lines) of chart size, kept when a caption beside them names a figure, chart or
   graph, or when they hold axis-like numbers in sparse text (a table is dense text in a grid: not a chart).
2. READ (vision model, app/retrieval/chart_read.py): the region's crop -> title, type, units, axis and legend
   labels, every labelled value, period, place, and whether each value is a printed label or estimated from a bar.
3. STORE (migration 0027): one row per chart with its page, region and crop; its printed values join the page's
   searchable text and the section card. Values estimated from bar heights are never used as figures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CAPTION = re.compile(r"(?im)^\s*((?:figure|fig\.?|chart|graph|diagram)\s*[\dIVX]+[\w.-]*)\s*[:.\-–—]?\s*(.{0,160})$")
TABLE_CAPTION = re.compile(r"(?im)^\s*table\s*[\dIVX]+")
NUMBER = re.compile(r"(?<![\w.])\d{1,3}(?:[.,]\d+)?%?(?![\w])")
MIN_AREA, MAX_AREA = 0.03, 0.85     # of the page
MIN_WIDTH = 0.20                    # of the page width
MIN_SHAPES = 6                      # filled vector shapes in a cluster
GAP = 8.0                           # points: shapes this close belong to one drawing


@dataclass
class Region:
    page: int
    box: tuple[float, float, float, float]     # left, bottom, right, top in PDF points
    kind: str                                    # image | form | vector
    caption: str = ""                            # 'Figure 3: Causes of maternal deaths ...'
    label: str = ""                              # 'Figure 3'
    shapes: int = 0
    numbers: int = 0
    reason: str = ""                             # why it counts as a chart


def _area(b) -> float:
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def _union(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def _near(a, b, gap: float = GAP) -> bool:
    return not (a[2] + gap < b[0] or b[2] + gap < a[0] or a[3] + gap < b[1] or b[3] + gap < a[1])


def cluster(boxes: list[tuple]) -> list[tuple[tuple, int]]:
    """Boxes that touch (within GAP) merged into one: (union box, how many)."""
    groups: list[list] = []
    for b in boxes:
        hit = [g for g in groups if _near(g[0], b)]
        if not hit:
            groups.append([b, 1])
            continue
        g0 = hit[0]
        g0[0], g0[1] = _union(g0[0], b), g0[1] + 1
        for g in hit[1:]:                                    # b joined several groups: they are one drawing
            g0[0], g0[1] = _union(g0[0], g[0]), g0[1] + g[1]
            groups.remove(g)
    # one more pass: groups that grew into each other
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if _near(groups[i][0], groups[j][0]):
                    groups[i] = [_union(groups[i][0], groups[j][0]), groups[i][1] + groups[j][1]]
                    groups.pop(j)
                    merged = True
                    break
            if merged:
                break
    return [(g[0], g[1]) for g in groups]


STRIP = 14.0          # points: captions are searched outward from the region in strips this tall
REACH = 6             # strips above and below (about 85 pt)


def _caption_near(textpage, box, h: float, w: float = 10_000.0) -> tuple[str, str, bool]:
    """(caption, label, is_table): the NEAREST 'Figure N ...' line to the region, searching outward from its top
    and bottom edges strip by strip (reports put captions above or below; a caption above may belong to the
    figure before: EmONC's 'Figure 3' is under its chart and 'Figure 2' above it is the previous one's), then
    inside the region's top band. The strips span the page's width: a caption is often set at the margin, not
    under the chart's own edges. A 'Table N' nearer than any figure caption: a table, not a chart."""
    l, b, r, t = box
    strips = [(l - 20, t - 30, r + 20, t + 2)]                    # the region's own top band (a title inside)
    for i in range(REACH):
        strips.append((0, max(0, b - STRIP * (i + 1)), w, b - STRIP * i))       # below, nearest first
        strips.append((0, t + STRIP * i, w, min(h, t + STRIP * (i + 1))))      # above, nearest first
    for band in strips:
        text = textpage.get_text_bounded(*band) or ""
        m = CAPTION.search(text)
        if not m and TABLE_CAPTION.search(text):
            return "", "", True
        if m:
            # the caption may wrap: take the next strip in the same direction too
            nxt = (band[0], band[1] - STRIP, band[2], band[1]) if band[3] <= b + 2 and band != strips[0] else \
                (band[0], band[3], band[2], band[3] + STRIP)
            more = (textpage.get_text_bounded(*nxt) or "").strip()
            tail = f"{m.group(2)} {more}" if more and not CAPTION.search(more) and not TABLE_CAPTION.search(more) \
                else m.group(2)
            cap = re.sub(r"\s+", " ", f"{m.group(1)}: {tail}").strip(" :")
            return cap[:200], re.sub(r"\s+", " ", m.group(1)).strip(), False
    return "", "", False


def detect_page(page, page_no: int) -> list[Region]:
    """Chart regions on one pypdfium2 page."""
    import pypdfium2.raw as c
    w, h = page.get_size()
    page_area = w * h
    images, shapes = [], []
    # top-level objects only: a form object (an Excel or Word chart exported as one drawing) is a candidate as a
    # whole; the shapes inside it are measured in the form's own coordinates, not the page's (2 Nov 2026)
    for o in page.get_objects(max_depth=1):
        try:
            box = o.get_bounds()
        except Exception:          # noqa: BLE001 - an object pdfium can't measure
            continue
        bw, bh = box[2] - box[0], box[3] - box[1]
        if o.type in (c.FPDF_PAGEOBJ_IMAGE, c.FPDF_PAGEOBJ_FORM):
            images.append((box, "image" if o.type == c.FPDF_PAGEOBJ_IMAGE else "form"))
        elif o.type == c.FPDF_PAGEOBJ_PATH and bw > 2 and bh > 2 and _area(box) < 0.5 * page_area:
            shapes.append(box)
    textpage = page.get_textpage()
    candidates: list[tuple[tuple, str, int]] = [(b, kind, 0) for b, kind in images]
    candidates += [(b, "vector", n) for b, n in cluster(shapes) if n >= MIN_SHAPES]
    out: list[Region] = []
    for box, kind, n in candidates:
        frac = _area(box) / page_area
        if not (MIN_AREA <= frac <= MAX_AREA) or (box[2] - box[0]) < MIN_WIDTH * w:
            continue
        caption, label, is_table = _caption_near(textpage, box, h, w)
        if is_table:
            continue
        # a chart has a caption naming a figure, chart or graph (2 Nov 2026: regions found by axis-like numbers
        # alone were all tables with coloured cells, page backgrounds or shaded text boxes)
        if not caption:
            continue
        inside = textpage.get_text_bounded(*box) or ""
        numbers = len(NUMBER.findall(inside))
        out.append(Region(page_no, tuple(round(x, 1) for x in box), kind, caption, label, n, numbers, "caption"))
    # one region per drawing: a caption's image and its vector overlay are the same chart
    kept: list[Region] = []
    for r in sorted(out, key=lambda r: -_area(r.box)):
        if not any(_overlap(r.box, k.box) > 0.6 for k in kept):
            kept.append(r)
    return sorted(kept, key=lambda r: -r.box[3])


def _overlap(a, b) -> float:
    inter = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return _area(inter) / max(1e-6, min(_area(a), _area(b)))


def detect_document(path: Path, text_pages: set[int] | None = None) -> list[Region]:
    """Chart regions on the text pages of a PDF (pages without a text layer go to page OCR, as before)."""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(path))
    out: list[Region] = []
    try:
        for i in range(len(pdf)):
            if text_pages is not None and (i + 1) not in text_pages:
                continue
            page = pdf[i]
            try:
                out += detect_page(page, i + 1)
            finally:
                page.close()
    finally:
        pdf.close()
    return out
