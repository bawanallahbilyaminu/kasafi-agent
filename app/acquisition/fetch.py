"""Download one PDF from an allowlisted site, safely.

Every hop (the URL and each redirect target) must pass the allowlist and robots.txt. The
download is streamed with a size limit, must start with %PDF- and end with %%EOF, and must
match its Content-Length. Some publishers (NBS) ship a report as a ZIP holding the PDF: a ZIP is
accepted too and unpacked later, inside the sandbox. The file's SHA-256 is recorded for provenance.
"""

from __future__ import annotations

import hashlib
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.acquisition.policy import USER_AGENT, Robots, host_allowed

MAX_BYTES = 60 * 1024 * 1024     # live fetches run while a user waits; seed documents can be bigger
MAX_REDIRECTS = 5
TIMEOUT = httpx.Timeout(60.0, connect=15.0)


class FetchError(Exception):
    pass


@dataclass
class Downloaded:
    path: Path
    sha256: str
    bytes: int
    url: str            # the URL we were asked to fetch
    final_url: str      # after redirects
    fetched_at: str     # ISO 8601, UTC
    kind: str = "pdf"   # pdf | zip


async def check_url(url: str, robots: Robots) -> None:
    if not host_allowed(url):
        raise FetchError(f"not https on an allowlisted domain: {url}")
    ok, why = await robots.allowed(url)
    if not ok:
        raise FetchError(f"{why}: {url}")


LANDING_BYTES = 2 * 1024 * 1024
_HREF = re.compile(r"""href\s*=\s*["']([^"'#]+)["']""", re.I)
_DOC_LINK = re.compile(r"(?i)\.pdf(?:$|\?)|/download(?:/|$|\?)|/documents?/download/")


def document_link(html: str, page_url: str) -> str | None:
    """The first link on a landing page to a document on the same site: a .pdf, or a download address
    (NBS /download/<id>, UNHCR /documents/download/<id>, /api/documents/<slug>/download) without one."""
    host = urllib.parse.urlsplit(page_url).hostname
    for href in _HREF.findall(html):
        link = urllib.parse.urljoin(page_url, href.strip())
        if urllib.parse.urlsplit(link).hostname == host and _DOC_LINK.search(link) and link != page_url:
            return link
    return None


async def download_pdf(url: str, dest: Path, http: httpx.AsyncClient, robots: Robots,
                       max_bytes: int = MAX_BYTES) -> Downloaded:
    """The file is accepted by what it is (PDF or ZIP bytes; the address often has no .pdf). A landing page (HTML)
    is followed one hop to the same site's document link; every hop passes the allowlist and robots.txt."""
    current, hopped = url, False
    for _ in range(MAX_REDIRECTS + 2):
        await check_url(current, robots)
        async with http.stream("GET", current, headers={"User-Agent": USER_AGENT,
                                                        "Accept": "application/pdf, application/zip, */*;q=0.5"},
                               follow_redirects=False, timeout=TIMEOUT) as resp:
            if resp.is_redirect:
                current = urllib.parse.urljoin(current, resp.headers.get("location", ""))
                continue
            if resp.status_code != 200:
                raise FetchError(f"HTTP {resp.status_code}")
            if "html" in resp.headers.get("content-type", "").lower():
                if hopped:
                    raise FetchError("a landing page, not a document")
                html = b""
                async for chunk in resp.aiter_bytes(64 * 1024):
                    html += chunk
                    if len(html) > LANDING_BYTES:
                        break
                link = document_link(html.decode("utf-8", "replace"), current)
                if not link:
                    raise FetchError("a landing page with no document link on its own site")
                current, hopped = link, True
                continue
            return await _save(resp, url, current, dest, max_bytes)
    raise FetchError("too many redirects")


async def _save(resp: httpx.Response, url: str, final_url: str, dest: Path, max_bytes: int) -> Downloaded:
    length = resp.headers.get("content-length")
    if length and length.isdigit() and int(length) > max_bytes:
        raise FetchError(f"too large ({int(length)} bytes > {max_bytes})")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    sha, size, tail, first, kind = hashlib.sha256(), 0, b"", True, "pdf"
    try:
        with tmp.open("wb") as f:
            async for chunk in resp.aiter_bytes(64 * 1024):
                if first:
                    if chunk.startswith(b"PK\x03\x04"):
                        kind = "zip"
                    elif not chunk.startswith(b"%PDF-"):
                        raise FetchError(f"not a PDF (Content-Type: {resp.headers.get('content-type')})")
                first = False
                size += len(chunk)
                if size > max_bytes:
                    raise FetchError(f"too large (> {max_bytes} bytes)")
                sha.update(chunk)
                f.write(chunk)
                tail = (tail + chunk)[-2048:]
        if size == 0:
            raise FetchError("empty response")
        if length and length.isdigit() and size != int(length):
            raise FetchError(f"truncated: got {size} of {int(length)} bytes")
        if kind == "pdf" and b"%%EOF" not in tail:
            raise FetchError("truncated: no %%EOF at end of file")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return Downloaded(dest, sha.hexdigest(), size, url, final_url,
                      datetime.now(timezone.utc).isoformat(timespec="seconds"), kind)
