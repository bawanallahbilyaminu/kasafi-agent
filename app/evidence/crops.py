"""Evidence images: a crop of the exact table row each cited figure comes from, sent after the answer.

For each cited figure, best evidence first and at most KASAFI_MAX_IMAGES per answer:
1. LOCATE   In the sandbox (fetched PDFs are untrusted), render the page and find the figure's characters;
            the row is every character on the same line, from the row name to the last column.
2. SEGMENT  SAM 3.1 (Meta Model API) gets the band of the page around the row, with the row as a box prompt,
            and returns the segmented region. If SAM is slow or fails, our own row box is used. A scanned page
            has no character positions, so SAM 3.1 finds the table there instead (concept prompt "table").
3. RENDER   The crop, with the figure highlighted, as a JPEG captioned with the column, document and page.
All of it runs after the text answer has been sent, under one timeout, so a slow crop never delays an answer.
Users can turn the images off ("images off" / "kashe hotuna").
"""

from __future__ import annotations

import asyncio
import io
import logging
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from app.acquisition.sandbox import ParseError, locate_sandboxed
from app.config import Settings
from app.providers.sam import Box, SamError, box_prompt, segment
from app.retrieval.indexer import find_file

log = logging.getLogger(__name__)

SCALE = 4.0           # budget tables use 6-7 pt type: 4x makes it legible on a phone
CONTEXT_ROWS = 1.5    # rows of context shown above and below the cited row
SAM_TIMEOUT = 15.0
MAX_WIDTH = 1600
MAX_SAM_SIDE = 2000   # scanned pages go to SAM at most this big
PAGE_WORD = {"ha": "shafi", "en": "page"}
_FIGURE = re.compile(r"-?\d[\d,]*(?:\.\d+)?%?")


@dataclass
class CropRequest:
    n: int              # evidence number, as in the answer's citations
    doc_id: str
    title: str
    page: int
    figure: str
    label: str = ""     # the column the figure is in, from the labelled row ("2025 Approved Budget")

    def caption(self, lang: str) -> str:
        head = f"{self.label}: {self.figure}" if self.label else self.figure
        return f"{head}\n[{self.n}] {self.title}, {PAGE_WORD.get(lang, 'page')} {self.page}"


def _is_figure(s: str) -> bool:
    """An amount or a rate worth showing: "11,255,447,389.16", "67.8%". A year ("2025") is not."""
    digits = re.sub(r"\D", "", s)
    return ("," in s and len(digits) >= 4) or ("." in s and len(digits) >= 2)


def plan_crops(answer, max_images: int = 2) -> list[CropRequest]:
    """One crop per cited page, best evidence first: the first figure of the answer found in that evidence."""
    figures = [f for f in _FIGURE.findall(re.sub(r"\[\d+\]", " ", getattr(answer, "exact", "") or "")) if _is_figure(f)]
    out, seen = [], set()
    for e in getattr(answer, "cited", None) or []:
        if (e.doc_id, e.page) in seen:
            continue
        figure = next((f for f in figures if re.search(rf"(?<![\d,.]){re.escape(f.lstrip('-'))}(?![\d,])", e.text)), None)
        if not figure:
            continue
        m = re.search(rf"([^|:\n]{{3,80}}): -?{re.escape(figure.lstrip('-'))}(?![\d,])", e.text)
        out.append(CropRequest(e.n, e.doc_id, e.title, e.page, figure, m.group(1).strip() if m else ""))
        seen.add((e.doc_id, e.page))
        if len(out) >= max_images:
            break
    return out


def pdf_path(doc_id: str, title: str, settings: Settings) -> Path | None:
    for p in (Path(settings.kasafi_pdf_dir) / f"{doc_id}.pdf", Path(settings.kasafi_fetch_dir) / f"{doc_id}.pdf",
              Path("data") / f"{doc_id}.pdf"):
        if p.exists():
            return p
    return find_file({"id": doc_id, "title": title}, Path("data")) if Path("data").is_dir() else None


def _jpeg(img: Image.Image, quality: int = 85) -> bytes:
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _highlight(img: Image.Image, box: list[int]) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle([box[0] - 4, box[1] - 3, box[2] + 4, box[3] + 3], fill=(255, 221, 0, 90),
                                      outline=(230, 120, 0, 255), width=3)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


async def _row_crop(img: Image.Image, row: list[int], hit: list[int], settings: Settings) -> tuple[Image.Image, bool]:
    x1, y1, x2, y2 = row
    rh = max(y2 - y1, 8)
    top, bottom = max(0, int(y1 - 4 * rh)), min(img.height, int(y2 + 4 * rh))
    band = img.crop((0, top, img.width, bottom))
    box, used_sam = [x1, y1, x2, y2], False
    try:
        buf = io.BytesIO()
        band.save(buf, format="JPEG", quality=88)
        found = await segment(buf.getvalue(), box_prompt(x1, y1 - top, x2, y2 - top, band.width, band.height),
                              settings=settings, timeout=SAM_TIMEOUT)
        b = next((b for b in found if b.obj == 1), None)
        # Accept SAM's region when it is the row (not the whole table): about the row's height, at least its width.
        if b and (b.y2 - b.y1) <= 2.5 * rh and (b.x2 - b.x1) >= 0.6 * (x2 - x1):
            box = [min(x1, b.x1), min(y1, b.y1 + top), max(x2, b.x2), max(y2, b.y2 + top)]
            used_sam = True
    except (SamError, OSError, asyncio.TimeoutError, ValueError) as e:
        log.info("SAM row refinement skipped: %s", type(e).__name__)
    pad = int(CONTEXT_ROWS * rh * 1.6)
    crop = (max(0, box[0] - 24), max(0, box[1] - pad), min(img.width, box[2] + 24), min(img.height, box[3] + pad))
    shown = _highlight(img, hit).crop(crop)
    return shown, used_sam


async def _table_crop(img: Image.Image, settings: Settings) -> Image.Image | None:
    """Scanned page: SAM 3.1 finds the tables; the biggest one is the evidence."""
    small = img.copy()
    small.thumbnail((MAX_SAM_SIDE, MAX_SAM_SIDE))
    buf = io.BytesIO()
    small.save(buf, format="JPEG", quality=85)
    boxes: list[Box] = await segment(buf.getvalue(), "table", settings=settings, timeout=SAM_TIMEOUT)
    if not boxes:
        return None
    b = max(boxes, key=lambda b: b.area)
    k = img.width / small.width
    return img.crop((int(b.x1 * k), int(b.y1 * k), int(b.x2 * k) + 1, int(b.y2 * k) + 1))


async def make_crop(req: CropRequest, settings: Settings) -> bytes | None:
    path = pdf_path(req.doc_id, req.title, settings)
    if path is None:
        log.info("no PDF for %s: no evidence image", req.doc_id)
        return None
    work = Path(tempfile.mkdtemp(prefix="kasafi-crop-"))
    try:
        loc = await locate_sandboxed(path, req.page, req.figure, work / "page.jpg", SCALE)
        with Image.open(loc["image"]) as page:
            page.load()
            if loc.get("row"):
                shown, used_sam = await _row_crop(page, loc["row"], loc["hit"], settings)
                log.info("evidence crop %s p%d: row%s", req.doc_id, req.page, " (SAM 3.1)" if used_sam else "")
                return _jpeg(shown)
            table = await _table_crop(page, settings)
            log.info("evidence crop %s p%d: %s", req.doc_id, req.page, "table (SAM 3.1)" if table else "none")
            return _jpeg(table) if table else None
    except (ParseError, SamError, OSError, KeyError, ValueError, asyncio.TimeoutError) as e:
        log.info("evidence crop failed for %s p%d: %s", req.doc_id, req.page, type(e).__name__)
        return None
    finally:
        shutil.rmtree(work, ignore_errors=True)
