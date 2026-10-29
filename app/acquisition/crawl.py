"""Crawled libraries: publishers whose own document listing we read directly and index in full, weekly.

The registry's `catalog_crawl` channels (data/source_registry.yaml) are state libraries that search engines
index poorly, such as the Sokoto State Bureau of Statistics (sbs.sk.gov.ng). Every week their listing is read
and each document we don't have yet is fetched and indexed through the usual path (allowlist, robots.txt, size
limits, sandboxed parse, the confirm step's exclusions). The daily fetch limit still applies.
"""

from __future__ import annotations

import asyncio
import logging

import httpx
import psycopg

from app.acquisition import channels
from app.acquisition.library import fetch_and_index, fetches_today
from app.acquisition.policy import USER_AGENT, Robots
from app.acquisition.registry import _host, registry
from app.config import Settings
from app.providers.meta import MetaClient

log = logging.getLogger(__name__)

WEEK_S = 7 * 24 * 3600
FIRST_DELAY_S = 120


def crawled_sites() -> list[str]:
    return [_host(c.site) for c in registry().channels.values() if c.type == "catalog_crawl" and c.site]


async def crawl_once(conn: psycopg.Connection, settings: Settings, http: httpx.AsyncClient,
                     client) -> list[tuple[str, str]]:
    """Index every listed document we don't have yet; returns (url, outcome) for each new one."""
    out = []
    robots = Robots(http)
    for site in crawled_sites():
        load = channels.LISTINGS.get(site)
        if load is None:
            continue
        channels._cache.pop(site, None)                  # a fresh listing every week
        for e in await channels._listing(site, load, http):
            known = conn.execute("SELECT 1 FROM documents WHERE source_url = %s OR final_url = %s",
                                 (e.url, e.url)).fetchone()
            if known:
                continue
            if fetches_today(conn) >= settings.kasafi_fetches_per_day:
                out.append((e.url, "daily fetch limit"))
                break
            acq = await fetch_and_index(conn, e.url, f"{e.title} ({site})", settings=settings, client=client,
                                        http=http, robots=robots)
            out.append((e.url, acq.doc_id or acq.detail or acq.status))
    log.info("crawled libraries: %d new documents %s", len(out), out[:5])
    return out


async def crawl_weekly(settings: Settings) -> None:
    """Started with the app: the first crawl after a short delay, then once a week. Never crashes the app."""
    await asyncio.sleep(FIRST_DELAY_S)
    while True:
        try:
            with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
                async with MetaClient(settings) as client, \
                        httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as http:
                    await crawl_once(conn, settings, http, client)
                    conn.commit()
        except Exception as e:
            log.warning("library crawl failed: %s", type(e).__name__)
        await asyncio.sleep(WEEK_S)
