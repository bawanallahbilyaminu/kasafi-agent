"""Bulk import of a publisher's public documents into the dev library (app/acquisition/bulk.py).

    KASAFI_BATCH_PROVIDER=baseten python scripts/bulk_import.py --site mof.sk.gov.ng --discover
    KASAFI_BATCH_PROVIDER=baseten python scripts/bulk_import.py --site mof.sk.gov.ng --ingest --max-usd 8

--discover lists the site (public media listing and its pages' links), classifies and dedupes, saves the plan to
data/bulk/<site>.json and prints the report. --ingest indexes the new documents in class order (budgets, BIRs,
citizens' budgets, MTEF/MTSS, plans and policies, financial statements and audits, the rest), every model call on
Muse Spark Open (the confirm step, charts, cards); it stops before a document once the run's spend passes
--max-usd, and resumes where it stopped. Then deploy/deploy.sh --sync-index and --sync-pdfs.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx  # noqa: E402
import psycopg  # noqa: E402

from app import usage  # noqa: E402
from app.acquisition import bulk, library  # noqa: E402
from app.acquisition.policy import Robots  # noqa: E402
from app.config import get_settings  # noqa: E402


def say(text: str) -> None:
    print(text, flush=True)


async def discover(site: str, state: Path, only: str = "", pages: bool = True) -> None:
    s = get_settings()
    async with httpx.AsyncClient(headers=bulk.client_headers(), follow_redirects=True) as http:
        robots = Robots(http)
        say(f"listing https://{site}/wp-json/wp/v2/media (public) ...")
        docs, others = await bulk.list_media(http, robots, site)
        say(f"  {len(docs)} document files, {len(others)} other files")
        linked = []
        if pages:
            say("reading the sitemap's pages for links to files ...")
            linked = await bulk.sitemap_links(http, robots, site)
            say(f"  {len(linked)} linked files")
    found = docs + linked
    if only:                                   # one topic from a large site: the titles (or file names) matching
        import re
        found = [i for i in found if re.search(only, f"{i.title} {i.url}", re.I)]
        say(f"  {len(found)} match '{only}'")
    with psycopg.connect(s.db_url()) as conn:
        items = bulk.plan(conn, found)
    bulk.save_state(state, items, others, 0.0)
    say(bulk.report(items, others))


async def discover_reliefweb(topic: str, since: str, until: str, state: Path) -> None:
    """ReliefWeb's reports on Sokoto and the topic (its v2 API, the approved appname from the settings, never
    printed), through the same plan, dedupe and report as a site."""
    s = get_settings()
    if not s.reliefweb_appname:
        sys.exit("RELIEFWEB_APPNAME is not set")
    async with httpx.AsyncClient(headers=bulk.client_headers(), follow_redirects=True) as http:
        items, left = await bulk.reliefweb_items(http, s.reliefweb_appname, topic, since, until)
    say(f"ReliefWeb: {len(items)} reports to plan, {len(left)} left out")
    for x in left:
        say(f"  left out: {x['date']} {x['title'][:90]} ({x['why']})")
    with psycopg.connect(s.db_url()) as conn:
        items = bulk.plan(conn, items)
    others = [{"mime": f"left out: {x['why']}", **x} for x in left]
    bulk.save_state(state, items, others, 0.0)
    say(bulk.report(items, others))


async def ingest(state: Path, max_usd: float, limit: int | None, retry: bool = False,
                 classes: set[str] | None = None) -> None:
    s = get_settings()
    if s.kasafi_batch_provider.lower() not in ("baseten", "fireworks"):
        sys.exit("set KASAFI_BATCH_PROVIDER=baseten: the import runs on Muse Spark Open only")
    loaded = bulk.load_state(state)
    if not loaded:
        sys.exit(f"no plan at {state}: run --discover first")
    items, others, spent_before = loaded
    from app.providers.fireworks import BatchModel
    client = BatchModel(s)
    if retry:                                     # failed ones tried again (after a fix), in their place in the order
        for i in items:
            if i.status == "failed":
                i.status, i.detail = "new", ""
    todo = [i for i in items if i.status == "new" and (not classes or i.cls in classes)][:limit]
    say(f"{len(todo)} documents to ingest; spent so far ${spent_before:.2f}; cap ${max_usd:.2f}")
    with psycopg.connect(s.db_url()) as conn:
        prints = bulk.library_fingerprints(conn)
        async with httpx.AsyncClient(headers=bulk.client_headers(), follow_redirects=True) as http:
            robots = Robots(http)
            for n, it in enumerate(todo, 1):
                spent = spent_before + usage.total_dollars(s)
                if spent >= max_usd:
                    say(f"STOP: ${spent:.2f} spent, past the ${max_usd:.2f} cap; {len(todo) - n + 1} left")
                    break
                flagged: dict[str, str] = {}

                def screen(pages, it=it, flagged=flagged):
                    doc, j = bulk.near_duplicate(pages, prints)
                    if doc:
                        return f"near-duplicate of {doc} (text overlap {j:.2f})"
                    if it.dedupe.startswith("same edition"):
                        flagged["why"] = f"possible newer version of {it.doc_id} (same edition, text overlap " \
                                         f"{j:.2f})"
                        return flagged["why"]
                    return ""
                before = usage.total_dollars(s)
                await asyncio.sleep(bulk.DELAY_S)
                try:
                    got = await library.fetch_and_index(conn, it.url, it.title, settings=s, client=client, http=http,
                                                        robots=robots, acquisition="imported", screen=screen,
                                                        ocr_head=True)
                except Exception as e:  # noqa: BLE001 - one file must not stop the run
                    conn.rollback()
                    got = library.Acquired("failed", url=it.url, detail=f"{type(e).__name__}: {e}"[:300])
                # its OCR (Muse Spark Open in a batch run), charts and cards, before the next document
                while pending := list(library._background) + list(library._CARD_TASKS):
                    await asyncio.gather(*pending, return_exceptions=True)
                it.cost = usage.total_dollars(s) - before
                it.doc_id = got.doc_id or it.doc_id
                it.detail = got.detail
                it.status = {"indexed": "indexed", "known": "duplicate", "skipped": "flagged" if flagged else
                             "duplicate"}.get(got.status, "excluded" if "excluded content" in got.detail else
                                              "flagged" if got.detail.startswith("held for review") else "failed")
                if got.status == "known" and conn.execute(          # this import's own earlier, interrupted run
                        "SELECT 1 FROM documents WHERE id = %s AND acquisition = 'imported' AND source_url = %s",
                        (got.doc_id, it.url)).fetchone():
                    it.status, got.detail = "indexed", ""
                    if not conn.execute("SELECT 1 FROM doc_cards WHERE doc_id = %s", (got.doc_id,)).fetchone():
                        from app.retrieval.chart_build import build_charts_later
                        await build_charts_later(got.doc_id, s)
                if it.status == "duplicate" and not it.dedupe:
                    it.dedupe = got.detail or f"same file as {got.doc_id}"
                if got.status == "indexed":
                    rows = conn.execute("SELECT string_agg(text, ' ' ORDER BY page) FROM pages WHERE doc_id = %s "
                                        "AND page <= 4", (got.doc_id,)).fetchone()
                    prints[got.doc_id] = bulk.shingles(rows[0] if rows else "")
                say(f"[{n}/{len(todo)}] {bulk.LABEL.get(it.cls, it.cls)}: {it.title[:70]} -> {it.status}"
                    f"{' ' + it.doc_id if it.doc_id else ''}{' (' + it.detail[:90] + ')' if it.detail else ''}"
                    f" ${it.cost:.3f} | total ${spent_before + usage.total_dollars(s):.2f}")
                bulk.save_state(state, items, others, spent_before + usage.total_dollars(s))   # resumable
    bulk.save_state(state, items, others, spent_before + usage.total_dollars(s))
    await client.aclose()


def replan(state: Path) -> None:
    """The saved listing classified and deduped again (after a rule change), without reading the site again."""
    loaded = bulk.load_state(state)
    if not loaded:
        sys.exit(f"no plan at {state}")
    items, others, spent = loaded
    fresh = [bulk.Item(i.url, i.title, i.kind, i.date, i.size, i.found_by) for i in items if i.status in
             ("new", "duplicate", "excluded")]
    done = [i for i in items if i.status not in ("new", "duplicate", "excluded")]
    with psycopg.connect(get_settings().db_url()) as conn:
        items = done + bulk.plan(conn, fresh)
    bulk.save_state(state, items, others, spent)
    say(bulk.report(items, others))


def summary(state: Path) -> None:
    loaded = bulk.load_state(state)
    if not loaded:
        sys.exit(f"no plan at {state}")
    items, others, spent = loaded
    s = get_settings()
    say(bulk.report(items, others))
    for status in ("indexed", "duplicate", "flagged", "excluded", "skipped", "failed", "new"):
        mine = [i for i in items if i.status == status]
        if mine:
            say(f"\n{status.upper()} ({len(mine)}):")
            for i in mine:
                why = (i.dedupe or i.detail)[:120]
                say(f"  - {i.title[:80]} [{bulk.LABEL.get(i.cls, i.cls)}]{' -> ' + i.doc_id if i.doc_id else ''}"
                    f"{': ' + why if why else ''}")
    with psycopg.connect(s.db_url()) as conn:
        ids = [i.doc_id for i in items if i.status == "indexed"]
        rows = conn.execute("SELECT doc_id, count(*), string_agg(DISTINCT reason, '; ') FROM withheld_pages "
                            "WHERE doc_id = ANY(%s) GROUP BY doc_id", (ids,)).fetchall() if ids else []
    say(f"\nWITHHELD PAGES (personal data): {len(rows)} documents")
    for doc_id, n, why in rows:
        say(f"  - {doc_id}: {n} pages ({why})")
    say(f"\nSPENT ${spent:.2f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="mof.sk.gov.ng")
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--replan", action="store_true")
    ap.add_argument("--max-usd", type=float, default=8.0)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--retry", action="store_true", help="try the failed documents again")
    ap.add_argument("--classes", help="only these classes, e.g. budget,bir,citizens,mtef,plans,accounts")
    ap.add_argument("--reliefweb", metavar="TOPIC", help="discover ReliefWeb reports on Sokoto and the topic "
                                                          "(e.g. 'flood floods flooding') instead of a site")
    ap.add_argument("--only", help="discover only files whose title or name matches this pattern (e.g. 'flood')")
    ap.add_argument("--media-only", action="store_true", help="the public media listing only (no sitemap crawl)")
    ap.add_argument("--since", default="2018-01-01")
    ap.add_argument("--until", default="2025-12-31")
    a = ap.parse_args()
    name = f"reliefweb-sokoto-{a.reliefweb.split()[0]}" if a.reliefweb else a.site
    state = ROOT / "data" / "bulk" / f"{name}.json"
    if a.discover and a.reliefweb:
        asyncio.run(discover_reliefweb(a.reliefweb, a.since, a.until, state))
    elif a.discover:
        asyncio.run(discover(a.site, state, a.only or "", pages=not a.media_only))
    if a.replan:
        replan(state)
    if a.ingest:
        asyncio.run(ingest(state, a.max_usd, a.limit, a.retry,
                           set(a.classes.split(",")) if a.classes else None))
    if a.summary:
        summary(state)
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
