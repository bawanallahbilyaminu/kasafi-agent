"""Recurring reports and their editions: what "the latest" means on a given day.

A question about the latest / most recent / current figure must be answered from the newest
edition that exists, not the newest one we happen to have. Each recurring series has a release
pattern (CPI monthly, about mid-month for the previous month; implementation reports quarterly;
budgets and audited statements yearly). From today's date we compute the newest edition that
should be out, then look for it, one period further back at a time (at most MAX_STEPS):
  1. our library, but only the exact edition (documents.series / documents.edition);
  2. the publisher's own listing page, where one is registered (NBS lists every CPI edition
     in its microdata catalog; web search indexes them months late);
  3. otherwise web search for that edition (find_and_fetch).
An older edition in the library never answers a "latest" question before newer ones were tried.

Edition keys sort as strings in time order: "2026-09" (monthly), "2026-Q3" (quarterly), "2026" (yearly).
"""

from __future__ import annotations

import calendar
import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, timedelta

import httpx
import psycopg

from app.acquisition.policy import USER_AGENT, Robots, host_allowed

log = logging.getLogger(__name__)

MAX_STEPS = 6
LISTING_TTL_S = 6 * 3600

MONTHS_EN = list(calendar.month_name)[1:]
MONTHS_HA = ["Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba", "Oktoba",
             "Nuwamba", "Disamba"]


@dataclass(frozen=True)
class Series:
    key: str
    name: str
    frequency: str              # monthly | quarterly | yearly
    lag_days: int               # release = period end (or start) + lag_days
    search: str                 # web-search description, with {edition} (an English label)
    anchor: str = "end"         # yearly budgets are released around the START of their year
    listing: str = ""           # publisher page that lists every edition (parsed by `parser`)
    parser: str = ""


SERIES: dict[str, Series] = {s.key: s for s in [
    Series("nbs_cpi", "NBS CPI and Inflation Report", "monthly", 15,
           "NBS Nigeria Consumer Price Index (CPI) and Inflation Report {edition}",
           listing="https://microdata.nigerianstat.gov.ng/index.php/catalog/154/related-materials",
           parser="nbs_catalog"),
    Series("sokoto_bir", "Sokoto State Budget Implementation Report", "quarterly", 21,
           "Sokoto State Budget Implementation Report {edition}"),
    Series("sokoto_budget", "Sokoto State Approved Budget", "yearly", 15,
           "Sokoto State {edition} Approved Budget", anchor="start"),
    Series("sokoto_audited_fs", "Sokoto State Audited Financial Statements", "yearly", 200,
           "Sokoto State {edition} Audited Financial Statements Accountant-General's Report"),
]}

_KEY = {"monthly": re.compile(r"^\d{4}-(0[1-9]|1[0-2])$"), "quarterly": re.compile(r"^\d{4}-Q[1-4]$"),
        "yearly": re.compile(r"^\d{4}$")}


def valid_edition(key: str | None) -> bool:
    return bool(key) and any(p.match(key) for p in _KEY.values())


def generic_series(name: str, frequency: str) -> Series:
    """A recurring report we have no registry entry for (the planner names it)."""
    lag = {"monthly": 20, "quarterly": 30, "yearly": 60}.get(frequency, 30)
    freq = frequency if frequency in _KEY else "yearly"
    return Series("other", name, freq, lag, name + " {edition}")


# --- edition arithmetic ------------------------------------------------------------------------

def _period(series: Series, key: str) -> tuple[date, date]:
    if series.frequency == "monthly":
        y, m = map(int, key.split("-"))
        return date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])
    if series.frequency == "quarterly":
        y, q = int(key[:4]), int(key[-1])
        return date(y, 3 * q - 2, 1), date(y, 3 * q, calendar.monthrange(y, 3 * q)[1])
    y = int(key)
    return date(y, 1, 1), date(y, 12, 31)


def release_date(series: Series, key: str) -> date:
    start, end = _period(series, key)
    return (start if series.anchor == "start" else end) + timedelta(days=series.lag_days)


def _previous(series: Series, key: str) -> str:
    if series.frequency == "monthly":
        y, m = map(int, key.split("-"))
        return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"
    if series.frequency == "quarterly":
        y, q = int(key[:4]), int(key[-1])
        return f"{y - 1}-Q4" if q == 1 else f"{y}-Q{q - 1}"
    return str(int(key) - 1)


def current_key(series: Series, today: date) -> str:
    if series.frequency == "monthly":
        return f"{today.year}-{today.month:02d}"
    if series.frequency == "quarterly":
        return f"{today.year}-Q{(today.month - 1) // 3 + 1}"
    return str(today.year + 1)          # next year's budget can come out before the year starts


def editions_back(series: Series, today: date, n: int = MAX_STEPS) -> list[str]:
    """The n newest editions that should be out by `today`, newest first."""
    key = current_key(series, today)
    while release_date(series, key) > today:
        key = _previous(series, key)
    out = [key]
    while len(out) < n:
        out.append(_previous(series, out[-1]))
    return out


def label(key: str, lang: str = "en") -> str:
    if _KEY["monthly"].match(key):
        y, m = map(int, key.split("-"))
        return f"{(MONTHS_HA if lang == 'ha' else MONTHS_EN)[m - 1]} {y}"
    if _KEY["quarterly"].match(key):
        return f"Q{key[-1]} {key[:4]}"
    return key


def month_label(d: date, lang: str = "en") -> str:
    return f"{(MONTHS_HA if lang == 'ha' else MONTHS_EN)[d.month - 1]} {d.year}"


# --- publisher listings ------------------------------------------------------------------------

_MONTH_NUM = {m.lower(): i for i, m in enumerate(MONTHS_EN, 1)}
_listing_cache: dict[str, tuple[float, dict[str, str]]] = {}


def parse_nbs_catalog(html: str, page_url: str) -> dict[str, str]:
    """NBS microdata catalog: '<span ... id="1440"> September 2026 CPI Report </span>' -> download/1440.

    'CPI Tables' entries are spreadsheets and are skipped.
    """
    base = page_url.split("/related")[0]
    out: dict[str, str] = {}
    for rid, text in re.findall(r'id="(\d+)">(?:\s*<i[^>]*></i>)*\s*([^<]+?)\s*</span>', html):
        m = re.match(r"(?i)^([a-z]+)\s+(\d{4})\s+CPI\s+Report\b", text.strip())
        if m and m.group(1).lower() in _MONTH_NUM:
            key = f"{m.group(2)}-{_MONTH_NUM[m.group(1).lower()]:02d}"
            out.setdefault(key, f"{base}/download/{rid}")
    return out


PARSERS: dict[str, Callable[[str, str], dict[str, str]]] = {"nbs_catalog": parse_nbs_catalog}


async def fetch_listing(series: Series, http: httpx.AsyncClient, robots: Robots) -> dict[str, str] | None:
    """edition key -> download URL from the publisher's listing page; None if it can't be read."""
    if not series.listing or series.parser not in PARSERS:
        return None
    cached = _listing_cache.get(series.key)
    if cached and time.monotonic() - cached[0] < LISTING_TTL_S:
        return cached[1]
    if not host_allowed(series.listing) or not (await robots.allowed(series.listing))[0]:
        log.info("listing for %s not fetchable (allowlist/robots)", series.key)
        return None
    try:
        r = await http.get(series.listing, headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=60)
        r.raise_for_status()
    except httpx.HTTPError as e:
        log.warning("listing for %s failed: %s", series.key, type(e).__name__)
        return None
    found = {k: u for k, u in PARSERS[series.parser](r.text, series.listing).items() if host_allowed(u)}
    _listing_cache[series.key] = (time.monotonic(), found)
    log.info("listing for %s: %d editions, newest %s", series.key, len(found), max(found, default="-"))
    return found


# --- the library -------------------------------------------------------------------------------

def local_edition(conn: psycopg.Connection, series: str, edition: str) -> str | None:
    row = conn.execute("SELECT id FROM documents WHERE series = %s AND edition = %s ORDER BY indexed_at DESC LIMIT 1",
                       (series, edition)).fetchone()
    return row[0] if row else None


def newest_local(conn: psycopg.Connection, series: str, before: str | None = None) -> tuple[str, str] | None:
    row = conn.execute("SELECT id, edition FROM documents WHERE series = %s AND edition IS NOT NULL "
                       "AND (%s::text IS NULL OR edition < %s) ORDER BY edition DESC LIMIT 1",
                       (series, before, before)).fetchone()
    return (row[0], row[1]) if row else None


def doc_edition(conn: psycopg.Connection, doc_id: str) -> tuple[str | None, str | None]:
    row = conn.execute("SELECT series, edition FROM documents WHERE id = %s", (doc_id,)).fetchone()
    return (row[0], row[1]) if row else (None, None)


def series_doc_ids(conn: psycopg.Connection, series: str) -> set[str]:
    return {r[0] for r in conn.execute("SELECT id FROM documents WHERE series = %s", (series,)).fetchall()}


@dataclass
class Latest:
    series: Series
    expected: str                      # the newest edition that should be out today
    doc_id: str | None = None
    edition: str | None = None         # the edition we're answering from
    status: str = "not_found"          # newest | older | none_newer | not_found
    tried: list[str] = field(default_factory=list)    # editions looked for online and not found
    fetched: bool = False
    acquired: object = None                           # library.Acquired, when the edition was fetched now

    @property
    def is_newest(self) -> bool:
        return self.edition == self.expected


Acquire = Callable[..., Awaitable]     # find_and_fetch / fetch_and_index (app/acquisition/library.py)


async def find_latest(conn: psycopg.Connection, series: Series, today: date, *, find_fn: Acquire, fetch_fn: Acquire,
                      newer_than: str | None = None, notify: Callable[[str], Awaitable[None]] | None = None,
                      notify_text: str = "", http: httpx.AsyncClient | None = None,
                      max_steps: int = MAX_STEPS) -> Latest:
    """Find the newest edition of `series`, newest first. `newer_than`: only editions after that one (recheck)."""
    editions = editions_back(series, today, max_steps)
    if newer_than:
        editions = [e for e in editions if e > newer_than]
    res = Latest(series, editions[0] if editions else (newer_than or ""))
    own = http is None
    http = http or httpx.AsyncClient(headers={"User-Agent": USER_AGENT})
    robots = Robots(http)
    listing: dict[str, str] | None = None
    listing_tried = False
    try:
        for key in editions:
            if doc := local_edition(conn, series.key, key):
                res.doc_id, res.edition = doc, key
                break
            if notify and not res.tried:
                await notify(notify_text)
            res.tried.append(key)
            description = series.search.format(edition=label(key))
            if not listing_tried:
                listing_tried = True
                listing = await fetch_listing(series, http, robots)
            if listing is not None:                  # the publisher's list is authoritative
                if key not in listing:
                    continue
                acq = await fetch_fn(conn, listing[key], description, http=http, robots=robots,
                                     series=series.key, edition=key)
            else:
                acq = await find_fn(conn, description, http=http, series=series.key, edition=key, check_local=False)
            log.info("latest %s %s: %s %s", series.key, key, acq.status, acq.detail[:100])
            if acq.doc_id:
                res.doc_id, res.edition, res.fetched, res.acquired = acq.doc_id, key, acq.status == "indexed", acq
                break
    finally:
        if own:
            await http.aclose()
    if res.doc_id:
        res.status = "newest" if res.edition == res.expected else "older"
        if newer_than:
            res.status = "newer_found"
        return res
    if newer_than:
        res.status = "none_newer"
        return res
    if older := newest_local(conn, series.key, before=editions[-1] if editions else None):
        res.doc_id, res.edition, res.status = older[0], older[1], "older"
    return res
