"""Charts on text pages, built once per document at index time (2 Nov 2026; migration 0027).

For each chart region found in the sandbox (app/retrieval/charts.py), the crop goes once to the vision model (Muse
Spark Open on Baseten: it reads images; never Muse Spark on Meta, whose credits are for live answers). What it read
is stored as a row in `charts`, and, for a chart with values, added to the page: its text joins the page's
searchable chunks (with a vector) and the page text, and its title joins the measures of the section card that
covers the page. A region already read is never read again (cached by document, page and box).

Honesty: only values printed on the chart (data labels) appear as figures, marked "(read from a chart label)";
values the model estimated from bar heights or slice sizes appear only as an order, never as numbers.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import tempfile
from pathlib import Path

import psycopg

from app.config import Settings, get_settings
from app.retrieval.chart_read import ChartData, as_json, chart_text, read_chart, snap_labels

log = logging.getLogger(__name__)

CONCURRENT = 4
CHUNK_BASE = 1000            # idx of a page's chart chunks: after its text chunks


def vision_client(settings: Settings):
    from app.providers.baseten import BasetenClient
    if settings.baseten_api_key is None:
        raise RuntimeError("charts need BASETEN_API_KEY (Muse Spark Open on Baseten reads images)")
    return BasetenClient(settings)


def store_chart(conn: psycopg.Connection, doc_id: str, region: dict, d: ChartData, crop: bytes, model: str) -> str:
    """The chart's row, and its text added to the page (chunks, page text) and to the section card. Returns the
    text added ('' for a region that isn't a chart or has no values)."""
    from app.retrieval.line_meaning import embed_texts
    text = chart_text(region.get("label", ""), region["page"], d) if d.is_chart and d.values else ""
    with conn.transaction():
        conn.execute("INSERT INTO charts (doc_id, page, box, region_kind, label, caption, is_chart, chart_type, data, "
                     "value_source, text, crop, model) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                     "ON CONFLICT (doc_id, page, box) DO NOTHING",
                     (doc_id, region["page"], json.dumps(list(region["box"])), region.get("kind", ""),
                      region.get("label", ""), region.get("caption", ""), d.is_chart, d.chart_type, as_json(d),
                      d.value_source if d.is_chart else "", text, crop, model))
        if not text:
            return ""
        n = conn.execute("SELECT count(*) FROM chunks WHERE doc_id = %s AND page = %s AND idx >= %s",
                         (doc_id, region["page"], CHUNK_BASE)).fetchone()[0]
        try:
            vec = embed_texts([text])[0]
        except Exception:          # noqa: BLE001 - keyword search still finds it
            vec = None
        conn.execute("INSERT INTO chunks (doc_id, page, idx, text, embedding) VALUES (%s, %s, %s, %s, %s::vector)",
                     (doc_id, region["page"], CHUNK_BASE + n, text, vec))
        marker = text.splitlines()[0]
        conn.execute("UPDATE pages SET text = text || %s WHERE doc_id = %s AND page = %s AND position(%s in text) = 0",
                     ("\n\n" + text, doc_id, region["page"], marker))
        conn.execute("UPDATE section_cards SET measures = measures || %s::jsonb WHERE doc_id = %s AND "
                     "%s BETWEEN page_from AND page_to AND NOT measures @> %s::jsonb",
                     (json.dumps([f"{d.title or region.get('label', '')} (chart)"[:160]]), doc_id, region["page"],
                      json.dumps([f"{d.title or region.get('label', '')} (chart)"[:160]])))
    return text


async def build_charts(conn: psycopg.Connection, doc_id: str, settings: Settings | None = None, client=None,
                       path: Path | None = None) -> dict:
    """Read every new chart region of a document once. Returns counts: regions, read, charts, values printed."""
    from app.acquisition.sandbox import charts_sandboxed
    from app.evidence.crops import pdf_path
    s = settings or get_settings()
    row = conn.execute("SELECT title FROM documents WHERE id = %s", (doc_id,)).fetchone()
    if not row:
        return {}
    path = path or pdf_path(doc_id, row[0], s)
    if path is None:
        return {"regions": 0, "note": "no PDF"}
    text_pages = {p for (p,) in conn.execute("SELECT page FROM pages WHERE doc_id = %s AND source = 'text'",
                                             (doc_id,)).fetchall()}
    work = Path(tempfile.mkdtemp(prefix="kasafi-charts-"))
    own = client is None
    client = client or vision_client(s)
    counts = {"regions": 0, "read": 0, "charts": 0, "printed": 0}
    try:
        regions = await charts_sandboxed(path, text_pages, work)
        counts["regions"] = len(regions)
        done = {(p, json.dumps(b)) for p, b in conn.execute(
            "SELECT page, box FROM charts WHERE doc_id = %s", (doc_id,)).fetchall()}
        todo = [r for r in regions if (r["page"], json.dumps(list(r["box"]))) not in done]
        gate = asyncio.Semaphore(CONCURRENT)

        async def one(r: dict) -> tuple[dict, ChartData, bytes]:
            crop = Path(r["crop"]).read_bytes()
            async with gate:
                try:
                    d = await read_chart(client, crop)
                except Exception as e:      # noqa: BLE001 - one chart must not stop the document
                    log.warning("%s p%d: chart read failed: %s", doc_id, r["page"], type(e).__name__)
                    return r, None, crop
            return r, d, crop
        for r, d, crop in await asyncio.gather(*(one(r) for r in todo)):
            if d is None:
                continue
            page_text = (conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = %s",
                                      (doc_id, r["page"])).fetchone() or [""])[0]
            d = snap_labels(d, page_text, r.get("caption", ""))
            store_chart(conn, doc_id, r, d, crop, s.baseten_model)
            counts["read"] += 1
            counts["charts"] += d.is_chart
            counts["printed"] += len(d.printed)
    finally:
        if own:
            await client.aclose()
        shutil.rmtree(work, ignore_errors=True)
    return counts


async def build_charts_later(doc_id: str, settings: Settings | None = None) -> None:
    """After indexing: the document's charts, then its cards (so the cards see the charts). Never raises."""
    s = settings or get_settings()
    if s.baseten_api_key is None:
        log.info("%s: no charts or cards (BASETEN_API_KEY not set)", doc_id)
        return
    try:
        with psycopg.connect(s.db_url(), autocommit=True) as conn:
            log.info("%s: charts %s", doc_id, await build_charts(conn, doc_id, s))
    except Exception as e:          # noqa: BLE001
        log.warning("%s: chart build failed: %s", doc_id, e)
    from app.retrieval.cards import build_card_later
    await build_card_later(doc_id, s)


def chart_crop(conn: psycopg.Connection, doc_id: str, page: int, figure: str) -> bytes | None:
    """The stored crop of the chart on this page that prints this figure as a label (evidence image), or None."""
    try:
        rows = conn.execute("SELECT data, crop FROM charts WHERE doc_id = %s AND page = %s AND crop IS NOT NULL",
                            (doc_id, page)).fetchall()
    except Exception:              # noqa: BLE001 - before migration 0027
        conn.rollback()
        return None
    want = figure.replace(",", "").rstrip("%")
    for data, crop in rows:
        for v in (data or {}).get("values", []):
            if v.get("printed") and str(v.get("value", "")).replace(",", "").rstrip("%") == want:
                return bytes(crop)
    return None
