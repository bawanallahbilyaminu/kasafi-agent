"""Planetary Computer STAC: the scenes covering a point, and signed read URLs for their assets.

No key is needed: the catalogue is open and the data token (a SAS token per collection, good for about an
hour) is issued to anonymous callers, rate-limited. PC_SDK_SUBSCRIPTION_KEY, when set, is sent and raises the
limit (a free Planetary Computer account). Everything here is synchronous (it runs in worker threads).
"""

from __future__ import annotations

import contextvars
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence
from urllib.parse import unquote

import httpx

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token"
TIMEOUT = 30.0
PAGE = 500

S2 = "sentinel-2-l2a"
JRC = "jrc-gsw"
WORLDCOVER = "esa-worldcover"
MODIS_VI = "modis-13Q1-061"

_tokens: dict[str, tuple[str, float]] = {}
_lock = threading.Lock()


def _headers() -> dict[str, str]:
    key = os.environ.get("PC_SDK_SUBSCRIPTION_KEY", "")
    return {"Ocp-Apim-Subscription-Key": key} if key else {}


# --- a busy service is tried again (traces 682, 683, 5 Nov 2026) ------------------------------------------------------
# The data API answers 3-6% of requests with '504 upstream request timeout' after 15 s on a busy evening, and now and
# then a read hangs or a reply can't be read. A second try almost always works (23 of 24). One such request among the
# ~400 of a new pin used to fail the whole job and lose everything fetched.

class Busy(Exception):
    """The service didn't serve this just now (a 5xx, a 429, a timeout, a reply that can't be read): worth trying again.
    Its message never carries a URL: a URL can hold the pin."""


class Refused(Exception):
    """The service refused the request itself (a 4xx): trying again won't help."""


BUSY = (Busy, httpx.TransportError, OSError, json.JSONDecodeError)     # OSError: rasterio can't read a broken reply
BUSY_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})
TRY_WAITS_S = (0.0, 2.0, 6.0)                  # one request tried on its own (a search, a token, one small window)
ROUND_WORKERS = (4, 2)                         # the requests that failed go again, fewer side by side
ROUND_WAITS_S = (3.0, 10.0)


class Until:
    """How long a job may go on, and a stop for a job that was withdrawn. Worker threads can't be cancelled: they ask."""

    def __init__(self, seconds: float) -> None:
        self.at = time.monotonic() + seconds
        self.stopped = False

    def left(self) -> float:
        return 0.0 if self.stopped else self.at - time.monotonic()

    def over(self) -> bool:
        return self.left() <= 0

    def stop(self) -> None:
        self.stopped = True


# the running job's limit; asyncio.to_thread carries it into the job's thread
time_limit: contextvars.ContextVar[Until | None] = contextvars.ContextVar("place_time_limit", default=None)


def read_json(send: Callable[[], httpx.Response]):
    """The JSON of a request, tried up to three times. Busy after that; Refused on a 4xx."""
    last: Exception | None = None
    for wait in TRY_WAITS_S:
        if wait:
            time.sleep(wait)
        try:
            r = send()
            if r.status_code in BUSY_STATUS:
                raise Busy(f"HTTP {r.status_code}")
            if r.status_code >= 400:
                raise Refused(f"HTTP {r.status_code}")
            return r.json()
        except BUSY as e:
            last = e
    raise Busy(_named(last)) from last


def patient_get(client: httpx.Client, url: str, **kw) -> httpx.Response:
    """A GET tried up to three times; the response when the service served it (any status but a busy one)."""
    last: Exception | None = None
    for wait in TRY_WAITS_S:
        if wait:
            time.sleep(wait)
        try:
            r = client.get(url, **kw)
            if r.status_code in BUSY_STATUS:
                raise Busy(f"HTTP {r.status_code}")
            return r
        except BUSY as e:
            last = e
    raise Busy(_named(last)) from last


def _named(e: Exception | None) -> str:
    return str(e) if isinstance(e, Busy) else type(e).__name__


def each(fn: Callable, items: Sequence, workers: int) -> tuple[dict[int, object], list[int]]:
    """fn(item) for each item, side by side. What failed because the service was busy goes again in smaller rounds.
    Returns ({index: result}, the indexes still failing). A service that fails nearly everything isn't asked the rest
    of a round: the job's own waiting (app/place/answer.py) takes over, without hundreds of requests that can't work."""
    until = time_limit.get()
    results: dict[int, object] = {}
    todo = list(range(len(items)))
    for n, wait in zip((workers, *ROUND_WORKERS), (0.0, *ROUND_WAITS_S)):
        if not todo or (until is not None and until.over()):
            break
        if wait:
            time.sleep(wait)
        lock = threading.Lock()
        asked, refused = [0], [0]

        def one(i: int, n: int = n, lock: threading.Lock = lock, asked: list = asked, refused: list = refused):
            with lock:
                if (until is not None and until.over()) or (refused[0] >= n * 3 and refused[0] > 0.8 * asked[0]):
                    return i, False, None
            try:
                value, ok = fn(items[i]), True
            except BUSY:
                value, ok = None, False
            with lock:
                asked[0] += 1
                refused[0] += 0 if ok else 1
            return i, ok, value
        failed: list[int] = []
        with ThreadPoolExecutor(max_workers=n) as ex:
            for i, ok, value in ex.map(one, todo):
                if ok:
                    results[i] = value
                else:
                    failed.append(i)
        todo = failed
    return results, todo


def search(collection: str, lon: float, lat: float, start: str, end: str, *, max_cloud: float | None = None,
           fields: list[str] | None = None, limit: int = 2000, ids: list[str] | None = None,
           bbox: tuple[float, float, float, float] | None = None) -> list[dict]:
    """Items of a collection whose footprint holds the point (or crosses `bbox`), dated start/end (ISO dates),
    oldest first. Pages are followed; `fields` keeps the response small (properties.datetime, assets.B04.href,
    ...); `ids` narrows to named items (a scene cached by id)."""
    body: dict = {"collections": [collection], "datetime": f"{start}/{end}", "limit": min(PAGE, limit),
                  "sortby": [{"field": "properties.datetime", "direction": "asc"}]}
    if bbox is not None:
        body["bbox"] = list(bbox)
    else:
        body["intersects"] = {"type": "Point", "coordinates": [lon, lat]}
    if max_cloud is not None:
        body["query"] = {"eo:cloud_cover": {"lt": max_cloud}}
    if ids:
        body["ids"] = list(ids)
    if fields:
        body["fields"] = {"include": fields, "exclude": ["geometry", "links"]}
    out: list[dict] = []
    with httpx.Client(timeout=TIMEOUT, headers=_headers()) as c:
        url, req = f"{STAC}/search", body
        while url and len(out) < limit:
            page = read_json(lambda url=url, req=req: c.post(url, json=req))
            out += page.get("features", [])
            nxt = next((ln for ln in page.get("links", []) if ln.get("rel") == "next"), None)
            if not nxt:
                break
            url, req = nxt["href"], nxt.get("body") or body
    return out[:limit]


def token(collection: str) -> str:
    """The collection's SAS token (query string), fetched once and kept until five minutes before it expires."""
    with _lock:
        hit = _tokens.get(collection)
        if hit and hit[1] - time.time() > 300:
            return hit[0]
    with httpx.Client(timeout=TIMEOUT, headers=_headers()) as c:
        d = read_json(lambda: c.get(f"{SAS}/{collection}"))
    tok = unquote(d["token"]) if "%3A" in d["token"] else d["token"]
    expiry = time.time() + 3600
    try:
        from datetime import datetime, timezone
        expiry = datetime.fromisoformat(d["msft:expiry"].replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()
    except (KeyError, ValueError):
        pass
    with _lock:
        _tokens[collection] = (tok, expiry)
    return tok


def signed(href: str, collection: str) -> str:
    """A read URL for an asset: its blob href with the collection's token appended."""
    return f"{href}?{token(collection)}"


def asset_href(item: dict, name: str) -> str | None:
    a = (item.get("assets") or {}).get(name)
    return a.get("href") if a else None
