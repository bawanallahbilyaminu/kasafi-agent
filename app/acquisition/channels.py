"""Discovery channels: publishers' own document listings and data APIs, tried before web search.

A web-search miss is not proof a document doesn't exist: state and partner sites are poorly indexed. So the
publishers' own listings are read directly (data/source_registry.yaml `discovery_channels`):
  - Sokoto State Bureau of Statistics: its document API (sbs.sk.gov.ng/api/documents, downloads at
    /api/documents/<slug>/download, no .pdf);
  - NBS e-library: one HTML table of every report (name, tags, upload date; downloads at /download/<id>);
  - HDX (CKAN): datasets and their resources, e.g. each DTM round's data, which also tells us the newest round;
  - IOM DTM API v3 (only with DTMAPI_SUBSCRIPTION_KEY): IDP figures by state, with round and reporting date.
Listings are cached for a week (refreshed weekly). Everything they return is untrusted data: titles and
descriptions only help pick a document, which is then fetched through the allowlist and robots.txt as usual.
"""

from __future__ import annotations

import html as htmllib
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.acquisition.find import Candidate
from app.acquisition.policy import Robots

log = logging.getLogger(__name__)

LISTING_TTL_S = 7 * 24 * 3600          # refresh weekly
TIMEOUT = 20
SBS_API = "https://sbs.sk.gov.ng/api/documents"
NBS_LIBRARY = "https://nigerianstat.gov.ng/elibrary"
HDX_SEARCH = "https://data.humdata.org/api/3/action/package_search"
DTM_ADMIN1 = "https://dtmapi.iom.int/v3/displacement/admin1"     # dtmapi 0.2.1 config.IDP_ADMIN_1_API


@dataclass
class Entry:
    title: str
    url: str
    date: str = ""            # ISO date or year
    text: str = ""            # description, category and tags: matched against the question, never quoted
    site: str = ""


_cache: dict[str, tuple[float, list[Entry]]] = {}


def iso_date(text: str) -> str:
    """'Tue Sep 24 2024', '1 October 2026', '2026-09-25T15:21:01Z' -> '2024-09-24' ...; '' if unreadable."""
    text = " ".join(text.split())
    if re.match(r"\d{4}-\d\d-\d\d", text):
        return text[:10]
    for fmt in ("%a %b %d %Y", "%d %B %Y", "%B %d %Y", "%d %b %Y", "%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


async def _listing(key: str, load, http: httpx.AsyncClient) -> list[Entry]:
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < LISTING_TTL_S:
        return hit[1]
    ok, why = await Robots(http).allowed(f"https://{key}/")
    if not ok:
        log.info("listing %s skipped: %s", key, why)
        return []
    try:
        entries = await load(http)
    except (httpx.HTTPError, ValueError, KeyError) as e:
        log.warning("listing %s failed: %s", key, type(e).__name__)
        return hit[1] if hit else []
    _cache[key] = (time.time(), entries)
    log.info("listing %s: %d documents", key, len(entries))
    return entries


async def _sbs(http: httpx.AsyncClient) -> list[Entry]:
    out, page, pages = [], 1, 1
    while page <= pages and page <= 20:
        r = await http.get(SBS_API, params={"page": page, "limit": 50}, timeout=TIMEOUT)
        r.raise_for_status()
        d = r.json()
        pages = int(d.get("pages") or 1)
        for it in d.get("items", []):
            if not it.get("published", True) or not it.get("slug"):
                continue
            out.append(Entry(str(it.get("title", "")), f"{SBS_API}/{it['slug']}/download",
                             str(it.get("createdAt") or it.get("year") or "")[:10],
                             " ".join([str(it.get("description") or "")[:600], str(it.get("category") or ""),
                                       " ".join(map(str, it.get("tags") or []))]), "sbs.sk.gov.ng"))
        page += 1
    return out


_ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
_TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
_READ = re.compile(r"elibrary/read/(\d+)")


def parse_nbs_library(page: str) -> list[Entry]:
    """Rows of the NBS e-library table: name, (hidden) sector, category, sub-category, tags, upload date."""
    out = []
    for row in _ROW.findall(re.sub(r"<!--.*?-->", "", page, flags=re.S)):
        cells = [htmllib.unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in _TD.findall(row)]
        doc = _READ.search(row)
        if not doc or len(cells) < 6:
            continue
        out.append(Entry(cells[0], f"https://nigerianstat.gov.ng/download/{doc.group(1)}", iso_date(cells[5]),
                         " ".join(cells[1:5]), "nigerianstat.gov.ng"))
    return out


async def _nbs(http: httpx.AsyncClient) -> list[Entry]:
    r = await http.get(NBS_LIBRARY, timeout=40)
    r.raise_for_status()
    return parse_nbs_library(r.text)


UNHCR_NIGERIA = "https://data.unhcr.org/en/country/nga"
_UNHCR_DOC = re.compile(r"""href=['"](https://data\.unhcr\.org/en/documents/download/\d+)['"]\s+data-title=["']([^"']+)"""
                        r"""["'].*?Publish date:\s*(?:<b>)?\s*([^&<(]+)""", re.S)


def parse_unhcr_country(page: str) -> list[Entry]:
    """The UNHCR Operational Data Portal's Nigeria page: each document's download link, title and publish date."""
    out, seen = [], set()
    for url, title, published in _UNHCR_DOC.findall(page):
        if url not in seen:
            seen.add(url)
            out.append(Entry(htmllib.unescape(title).strip(), url, iso_date(published), "", "data.unhcr.org"))
    return out


async def _unhcr(http: httpx.AsyncClient) -> list[Entry]:
    r = await http.get(UNHCR_NIGERIA, timeout=40)
    r.raise_for_status()
    return parse_unhcr_country(r.text)


LISTINGS = {"sbs.sk.gov.ng": _sbs, "nigerianstat.gov.ng": _nbs, "data.unhcr.org": _unhcr}

_WORD = re.compile(r"[a-z0-9]{3,}")
_STOP = {"the", "and", "for", "report", "sokoto", "state", "nigeria", "with", "from", "latest", "newest", "data"}


def _words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP}


def best_entries(entries: list[Entry], query: str, top: int = 5) -> list[Entry]:
    """The listed documents sharing the most words with the query (title counts double), newest first on ties."""
    want = _words(query)
    scored = [(2 * len(want & _words(e.title)) + len(want & _words(e.text)), e.date, e) for e in entries
              if len(want & (_words(e.title) | _words(e.text))) >= 2]        # two of its words at least
    return [e for _, _, e in sorted(scored, key=lambda s: (s[0], s[1]), reverse=True)[:top]]


async def catalog_candidates(http: httpx.AsyncClient, query: str, domains: list[str] | None = None,
                             top: int = 5) -> list[Candidate]:
    """Documents from the publishers' own listings (all of them, or those on `domains`) that match the query."""
    out = []
    for site, load in LISTINGS.items():
        if domains is not None and not any(site == d or site.endswith("." + d) or d.endswith(site)
                                           for d in domains):
            continue
        for e in best_entries(await _listing(site, load, http), query, top):
            out.append(Candidate(e.url, e.title, e.text[:300], "catalog", e.date))
    return out


async def hdx_datasets(http: httpx.AsyncClient, query: str, rows: int = 5) -> tuple[list[Candidate], list[str]]:
    """HDX datasets for the query: PDF resources as candidates, and every resource's name and date (the newest
    edition signal, e.g. 'dtm r19 ... 2026-09-04' tells us DTM Round 19 exists)."""
    r = await http.get(HDX_SEARCH, params={"q": query, "rows": rows, "sort": "metadata_modified desc"},
                       timeout=TIMEOUT)
    r.raise_for_status()
    cands, editions = [], []
    for p in r.json().get("result", {}).get("results", []):
        org = (p.get("organization") or {}).get("title", "")
        for res in p.get("resources", [])[:6]:
            name = res.get("name") or res.get("url", "").rsplit("/", 1)[-1]
            when = (res.get("last_modified") or res.get("created") or p.get("metadata_modified") or "")[:10]
            editions.append(f"{p.get('title', '')}: {name} ({when})")
            if str(res.get("format", "")).upper() == "PDF" and res.get("url"):
                cands.append(Candidate(res["url"], f"{p.get('title', '')}: {name}", org, "hdx", when))
    return cands, editions


@dataclass
class DtmFigure:
    value: int
    round: str
    date: str
    admin1: str


def _first(d: dict, *keys: str):
    lower = {k.lower(): v for k, v in d.items()}
    return next((lower[k.lower()] for k in keys if k.lower() in lower and lower[k.lower()] not in (None, "")),
                None)


async def dtm_admin1(http: httpx.AsyncClient, key: str, state: str = "Sokoto") -> DtmFigure | None:
    """The newest DTM IDP figure for a state (API v3). Field names are read defensively: the API's response
    fields aren't documented on the package's pages."""
    r = await http.get(DTM_ADMIN1, params={"CountryName": "Nigeria", "Admin1Name": state},
                       headers={"Ocp-Apim-Subscription-Key": key}, timeout=TIMEOUT)
    r.raise_for_status()
    body = r.json()
    rows = body.get("result") if isinstance(body, dict) else body
    if not isinstance(rows, list) or not rows:
        return None
    rows = [x for x in rows if isinstance(x, dict)]
    rows.sort(key=lambda x: (str(_first(x, "reportingDate", "reporting_date") or ""),
                             int(_first(x, "roundNumber", "round_number") or 0)), reverse=True)
    top = rows[0]
    value = _first(top, "numPresentIdpInd", "numberOfIdps", "idps", "idpCount")
    if value is None:
        return None
    return DtmFigure(int(float(value)), str(_first(top, "roundNumber", "round_number") or ""),
                     str(_first(top, "reportingDate", "reporting_date") or "")[:10],
                     str(_first(top, "admin1Name") or state))
