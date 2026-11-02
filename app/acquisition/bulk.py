"""Bulk import of a publisher's public documents (2 Nov 2026; first site: mof.sk.gov.ng).

Public side only: the WordPress REST media listing (/wp-json/wp/v2/media, public, no login) and the site's own
sitemap pages' links to files on the same site. Never WordPress admin credentials. robots.txt is honoured and
requests are spaced (DELAY_S). Files go through the usual path (app/acquisition/library.fetch_and_index):
allowlist, size limits, sandboxed parse, the confirm step's exclusions, personal-data pages withheld.

1. DISCOVERY: every PDF, Word or zip file listed; spreadsheets and images are reported, not ingested.
2. CLASSES (from the title and file name): budgets and amendments, BIRs, citizens' budgets, MTEF/MTSS, plans and
   policies, financial statements and audits, other; excluded by title (attacks, conflict, banditry, security
   operations, partisan political material; a budget's security lines are fine); possible personal data (lists
   of beneficiaries, nominal rolls: ingested with those pages withheld).
3. DEDUPE before download: a URL the library holds; the same file uploaded twice on the site (the same name
   with WordPress's '-1' suffix, or the same title and size); a library document with the same series and
   edition (a likely duplicate: confirmed by text when downloaded; a different text is flagged as a possible
   newer version and not ingested). After download: the same bytes (fetch_and_index), or near-identical text
   (word shingles of the first pages against every library document).
4. INGEST in class order, newest first, Muse Spark Open on Baseten only; resumable (a state file); the running
   cost is checked before each document and the run stops past the cap.
"""

from __future__ import annotations

import asyncio
import html
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import httpx
import psycopg

from app.acquisition.policy import USER_AGENT, Robots, host_allowed

DELAY_S = 1.0
DOC_MIMES = {"application/pdf": "pdf", "application/zip": "zip", "application/x-zip-compressed": "zip",
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
             "application/msword": "doc", "application/rtf": "rtf",
             "application/vnd.oasis.opendocument.text": "odt"}
DOC_EXT = re.compile(r"(?i)\.(pdf|docx?|zip|odt|rtf)(?:$|\?)")
SHEET = re.compile(r"(?i)spreadsheet|excel|\.xlsx?$|\.csv$")

CLASSES = [   # (class, title pattern), in ingest order; the first match wins
    ("excluded", r"bandit|insurgen|kidnap|\battacks?\b|terror|militar|security\s+operation|armed\s+conflict|"
                 r"\bconflict\b|campaign|manifesto|political\s+part|\bAPC\b|\bPDP\b|election|rally"),
    # the budget process's paperwork and the debt office's acknowledgements: not budgets, read last
    ("other", r"invitation|attendance|minutes?\b|minute\s+of|town\s*hall|deliberation|speech|acknowledg|"
              r"ackwonleg|submission|call\s*circular|callcircular|meeting|debt\s+and\s+liabilities"),
    ("bir", r"\bBIR\d?\b|\bBPR\d?\b|budget\s+(?:implementation|performance)|implementation\s+report|"
            r"performance\s+report|\bQ[1-4]\b.*\b(?:report|budget)"),
    ("citizens", r"citizen"),
    ("mtef", r"MTEF|MTSS|fiscal\s+strategy|medium[\s-]+term|\bFSP\b|economic\s+and\s+fiscal\s+update|\bEFU\b"),
    ("budget", r"budget|appropriation|supplementary|estimates?\b"),
    ("plans", r"plan\b|policy|strateg|framework|agenda|roadmap|blueprint|vision"),
    ("accounts", r"financial\s+statement|audit|accounts?\b|auditor"),
]
ORDER = ["budget", "bir", "citizens", "mtef", "plans", "accounts", "other"]
LABEL = {"budget": "budgets and amendments", "bir": "budget implementation reports", "citizens": "citizens' budgets",
         "mtef": "MTEF / MTSS / fiscal strategy", "plans": "plans and policies",
         "accounts": "financial statements and audits", "other": "other documents",
         "excluded": "excluded by title (conflict, security operations, partisan)"}
PERSONAL_TITLE = re.compile(r"(?i)beneficiar|nominal|payroll|pay\s*roll|list\s+of\s+(?:names|staff|successful|"
                            r"pensioners|beneficiar)|successful\s+candidates|shortlist|pensioners|attendance|"
                            r"verification\s+(?:list|exercise)|staff\s+list|teaching[\s_-]+staff|gratuit|posting")


@dataclass
class Item:
    url: str
    title: str
    kind: str                    # pdf | docx | zip | ...
    date: str = ""               # upload date (the media listing)
    size: int = 0
    found_by: str = "media"      # media | page
    cls: str = "other"
    personal_title: bool = False
    year: int | None = None
    series: str | None = None
    edition: str | None = None
    dedupe: str = ""             # why it isn't ingested: 'known URL <id>', 'site copy of <url>', 'same edition as <id>'
    status: str = "new"          # new | duplicate | excluded | indexed | known | skipped | failed | flagged
    doc_id: str = ""
    detail: str = ""
    cost: float = 0.0


def classify(title: str, url: str) -> str:
    text = f"{title} {unquote(Path(urlparse(url).path).stem).replace('-', ' ').replace('_', ' ')}"
    return next((c for c, rx in CLASSES if re.search(rx, text, re.I)), "other")


def edition_of(title: str, url: str, cls: str) -> tuple[str | None, str | None, int | None]:
    """(series, edition, year) from a title like 'Sokoto State 2026 Q3 BIR' or '2026 Approved Budget'."""
    text = f"{title} {unquote(Path(urlparse(url).path).stem)}".replace("_", " ").replace("-", " ")
    years = [int(y) for y in re.findall(r"\b(20[0-4]\d)\b", text)]
    year = years[0] if years else None
    q = re.search(r"(?i)\b(?:Q|quarter\s*)([1-4])\b|\b([1-4])(?:st|nd|rd|th)\s+quarter", text)
    if cls == "bir" and year and q:
        return "sokoto_bir", f"{year}-Q{q.group(1) or q.group(2)}", year
    # the approved budget book only: an appropriation law is its own document (the library keeps both)
    if cls == "budget" and year and re.search(r"(?i)approved", text) and \
            not re.search(r"(?i)amend|supplementary|revised|proposal|citizen|appropriation|\blaw\b", text):
        return "sokoto_budget", str(year), year
    return None, None, year


def _site_key(url: str) -> str:
    """The uploaded file's name without WordPress's duplicate suffix ('report-1.pdf' -> 'report')."""
    stem = unquote(Path(urlparse(url).path).stem).lower()
    return re.sub(r"-\d$", "", stem)            # '-1', '-2'; never '-26' (a year or quarter in the name)


# --- discovery ----------------------------------------------------------------------------------------------------

async def _get(http: httpx.AsyncClient, robots: Robots, url: str) -> httpx.Response | None:
    if not host_allowed(url) or not (await robots.allowed(url))[0]:
        return None
    await asyncio.sleep(DELAY_S)
    try:
        return await http.get(url, timeout=30)
    except httpx.HTTPError:
        return None


async def list_media(http: httpx.AsyncClient, robots: Robots, site: str) -> tuple[list[Item], list[dict]]:
    """Every file in the public media listing: (documents, other files [spreadsheets, images, ...])."""
    docs, others, page = [], [], 1
    while True:
        r = await _get(http, robots, f"https://{site}/wp-json/wp/v2/media?per_page=100&page={page}"
                                     f"&_fields=id,date,title,source_url,mime_type,media_details")
        if r is None or r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        for m in batch:
            url, mime = m.get("source_url") or "", m.get("mime_type") or ""
            title = html.unescape((m.get("title") or {}).get("rendered") or "")
            size = int((m.get("media_details") or {}).get("filesize") or 0)
            if mime in DOC_MIMES:
                docs.append(Item(url, title, DOC_MIMES[mime], m.get("date") or "", size))
            elif not mime.startswith("image/"):
                others.append({"url": url, "title": title, "mime": mime})
        if page >= int(r.headers.get("X-WP-TotalPages") or page):
            break
        page += 1
    return docs, others


async def sitemap_links(http: httpx.AsyncClient, robots: Robots, site: str, most_pages: int = 400) -> list[Item]:
    """Files linked from the site's own pages (its sitemap), on the same site: uploads the media listing misses."""
    r = await _get(http, robots, f"https://{site}/wp-sitemap.xml")
    if r is None or r.status_code != 200:
        return []
    maps = [m for m in re.findall(r"<loc>([^<]+)</loc>", r.text) if re.search(r"posts-(?:post|page|project)", m)]
    pages: list[str] = []
    for m in maps:
        if (r := await _get(http, robots, m)) is not None and r.status_code == 200:
            pages += re.findall(r"<loc>([^<]+)</loc>", r.text)
    out: dict[str, Item] = {}
    for p in pages[:most_pages]:
        r = await _get(http, robots, p)
        if r is None or r.status_code != 200:
            continue
        for href, text in re.findall(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text):
            url = urljoin(p, html.unescape(href))
            if DOC_EXT.search(url) and urlparse(url).hostname == site and url not in out:
                label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(text))).strip()
                out[url] = Item(url, label or unquote(Path(urlparse(url).path).stem),
                                DOC_EXT.search(url).group(1).lower(), found_by="page")
    return list(out.values())


# --- classes and dedupe -------------------------------------------------------------------------------------------

def plan(conn: psycopg.Connection, items: list[Item]) -> list[Item]:
    """Classes, editions and the dedupe before download; the order to ingest in."""
    known = {}
    for doc_id, a, b in conn.execute("SELECT id, source_url, final_url FROM documents").fetchall():
        for u in (a, b):
            if u:
                known[u] = doc_id
    editions = {(s, e): d for d, s, e in conn.execute(
        "SELECT id, series, edition FROM documents WHERE series IS NOT NULL AND edition IS NOT NULL").fetchall()}
    seen: dict[str, Item] = {}
    by_url: dict[str, Item] = {}
    for it in items:
        if it.url in by_url:                        # listed by both the media listing and a page
            continue
        by_url[it.url] = it
        it.cls = classify(it.title, it.url)
        it.personal_title = bool(PERSONAL_TITLE.search(f"{it.title} {it.url}"))
        it.series, it.edition, it.year = edition_of(it.title, it.url, it.cls)
        if it.cls == "excluded":
            it.status, it.dedupe = "excluded", "title names conflict, security operations or partisan material"
        elif it.url in known:
            it.status, it.dedupe, it.doc_id = "duplicate", f"known URL ({known[it.url]})", known[it.url]
        elif (key := _site_key(it.url)) in seen and (not it.size or not seen[key].size or
                                                     abs(it.size - seen[key].size) <= 0.02 * it.size):
            it.status, it.dedupe = "duplicate", f"site copy of {seen[key].url}"
        elif it.series and (it.series, it.edition) in editions:
            # the same edition is in the library: checked by its text when downloaded (a different text is flagged)
            it.dedupe = f"same edition as {editions[(it.series, it.edition)]}"
            it.doc_id = editions[(it.series, it.edition)]
        seen.setdefault(_site_key(it.url), it)
    out = list(by_url.values())
    # class order, then newest first inside a class: by year, then upload date (descending)
    out.sort(key=lambda x: (ORDER.index(x.cls) if x.cls in ORDER else len(ORDER), -(x.year or 0),
                            "".join(chr(255 - ord(ch)) for ch in x.date)))
    return out


def report(items: list[Item], others: list[dict]) -> str:
    """The discovery and dedupe report: counts per class, what is new, what is skipped and why."""
    lines = ["| Class | Listed | New | Duplicates | Same edition (text check) | Possible personal data |",
             "|---|---|---|---|---|---|"]
    for cls in ORDER + ["excluded"]:
        mine = [i for i in items if i.cls == cls]
        if not mine:
            continue
        lines.append(f"| {LABEL[cls]} | {len(mine)} | {sum(i.status == 'new' and not i.dedupe for i in mine)} | "
                     f"{sum(i.status == 'duplicate' for i in mine)} | "
                     f"{sum(i.status == 'new' and bool(i.dedupe) for i in mine)} | "
                     f"{sum(i.personal_title for i in mine)} |")
    lines.append(f"\nNot ingested (not documents Kasafi reads): {len(others)} files "
                 f"({', '.join(sorted({o['mime'] for o in others})) or 'none'}).")
    return "\n".join(lines)


# --- near-duplicate text --------------------------------------------------------------------------------------------

def shingles(text: str, n: int = 5) -> set[int]:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {hash(" ".join(words[i:i + n])) for i in range(max(0, len(words) - n + 1))}


def library_fingerprints(conn: psycopg.Connection, pages: int = 4) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    for doc_id, text in conn.execute("SELECT doc_id, string_agg(text, ' ' ORDER BY page) FROM pages "
                                     "WHERE page <= %s GROUP BY doc_id", (pages,)).fetchall():
        out[doc_id] = shingles(text)
    return out


def near_duplicate(pages: list[str], prints: dict[str, set[int]], floor: float = 0.8) -> tuple[str, float]:
    """The library document whose first pages share most of this one's word shingles (Jaccard), if any."""
    mine = shingles(" ".join(pages[:4]))
    if len(mine) < 50:
        return "", 0.0
    best, score = "", 0.0
    for doc_id, theirs in prints.items():
        if theirs:
            j = len(mine & theirs) / len(mine | theirs)
            if j > score:
                best, score = doc_id, j
    return (best, score) if score >= floor else ("", score)


# --- state ----------------------------------------------------------------------------------------------------------

def save_state(path: Path, items: list[Item], others: list[dict], spent: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"items": [asdict(i) for i in items], "others": others, "spent": spent,
                                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=1), encoding="utf-8")


def load_state(path: Path) -> tuple[list[Item], list[dict], float] | None:
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    return [Item(**i) for i in d["items"]], d.get("others") or [], float(d.get("spent") or 0.0)


def client_headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT}
