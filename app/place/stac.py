"""Planetary Computer STAC: the scenes covering a point, and signed read URLs for their assets.

No key is needed: the catalogue is open and the data token (a SAS token per collection, good for about an
hour) is issued to anonymous callers, rate-limited. PC_SDK_SUBSCRIPTION_KEY, when set, is sent and raises the
limit (a free Planetary Computer account). Everything here is synchronous (it runs in worker threads).
"""

from __future__ import annotations

import os
import threading
import time
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


def search(collection: str, lon: float, lat: float, start: str, end: str, *, max_cloud: float | None = None,
           fields: list[str] | None = None, limit: int = 2000, ids: list[str] | None = None) -> list[dict]:
    """Items of a collection whose footprint holds the point, dated start/end (ISO dates), oldest first.
    Pages are followed; `fields` keeps the response small (properties.datetime, assets.B04.href, ...); `ids`
    narrows to named items (a scene cached by id)."""
    body: dict = {"collections": [collection], "intersects": {"type": "Point", "coordinates": [lon, lat]},
                  "datetime": f"{start}/{end}", "limit": min(PAGE, limit),
                  "sortby": [{"field": "properties.datetime", "direction": "asc"}]}
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
            r = c.post(url, json=req)
            r.raise_for_status()
            page = r.json()
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
        r = c.get(f"{SAS}/{collection}")
        r.raise_for_status()
        d = r.json()
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
