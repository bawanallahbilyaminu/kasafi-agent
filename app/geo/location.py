"""Location intake (docs/hazard-and-services.md section 3): a WhatsApp location pin, the "Share location" request,
a typed place (the gazetteer), or the LGA on file.

Privacy: exact coordinates are kept only in this process's memory, for at most 30 minutes, for follow-ups
("route?", "the next one?"). They are never written to the database, logs or traces: a Spot's repr hides them,
and callers log only the LGA. Only the LGA's P-code is stored on the user record (app/users.py, 90 days).
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any

TTL_S = 30 * 60
MAX_KEPT = 10_000            # a bound on memory; the oldest entries go first


@dataclass(frozen=True)
class Spot:
    """A user's point, in memory only. Printing or logging one shows the LGA, never the coordinates."""
    lat: float = field(repr=False)
    lon: float = field(repr=False)
    lga_pcode: str = ""
    lga: str = ""
    ward: str = ""
    how: str = "pin"           # pin | place | lga

    def __repr__(self) -> str:
        return f"Spot(location: {self.lga or 'outside Sokoto'} LGA ({self.how}))"

    __str__ = __repr__


class LocationMemory:
    """User key -> (Spot, when), forgotten after TTL_S. Nothing here is ever persisted."""

    def __init__(self, ttl_s: float = TTL_S) -> None:
        self.ttl_s = ttl_s
        self._spots: dict[str, tuple[Spot, float]] = {}
        self._needs: dict[str, tuple[str, float]] = {}       # a question waiting for a location
        self._searches: dict[str, tuple[Any, float]] = {}    # the last facility search, for "next" / "route?"
        self._lock = threading.Lock()

    def remember_search(self, key: str, search: Any) -> None:
        with self._lock:
            self._searches[key] = (search, time.monotonic())

    def last_search(self, key: str) -> Any:
        with self._lock:
            hit = self._searches.get(key)
            if hit and time.monotonic() - hit[1] < self.ttl_s:
                return hit[0]
            self._searches.pop(key, None)
            return None

    def remember(self, key: str, spot: Spot) -> None:
        with self._lock:
            self._spots[key] = (spot, time.monotonic())
            if len(self._spots) > MAX_KEPT:
                for k in sorted(self._spots, key=lambda k: self._spots[k][1])[: len(self._spots) - MAX_KEPT]:
                    del self._spots[k]

    def recall(self, key: str) -> Spot | None:
        with self._lock:
            hit = self._spots.get(key)
            if hit and time.monotonic() - hit[1] < self.ttl_s:
                return hit[0]
            self._spots.pop(key, None)
            return None

    def wait_for_location(self, key: str, question: str) -> None:
        with self._lock:
            self._needs[key] = (question[:1000], time.monotonic())

    def is_waiting(self, key: str) -> bool:
        with self._lock:
            hit = self._needs.get(key)
        return bool(hit and time.monotonic() - hit[1] < self.ttl_s)

    def waiting_question(self, key: str) -> str | None:
        """The question that asked for a location, once (it is taken)."""
        with self._lock:
            hit = self._needs.pop(key, None)
        return hit[0] if hit and time.monotonic() - hit[1] < self.ttl_s else None

    def forget(self, key: str) -> None:
        with self._lock:
            self._spots.pop(key, None)
            self._needs.pop(key, None)
            self._searches.pop(key, None)


memory = LocationMemory()


async def locate_point(settings, lat: float, lon: float):
    """The Area (LGA, ward) a point is in, or None outside Sokoto; PostGIS, in a thread. Raises without a database."""
    import asyncio

    import psycopg

    from app.geo import locate
    if not settings.has_database:
        raise RuntimeError("no database configured")

    def run():
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            return locate(conn, lat, lon)
    return await asyncio.to_thread(run)


def pin_of(msg: dict[str, Any]) -> tuple[float, float] | None:
    """A WhatsApp location message's (latitude, longitude), or None."""
    if msg.get("type") != "location":
        return None
    loc = msg.get("location") or {}
    try:
        lat, lon = float(loc["latitude"]), float(loc["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    return (lat, lon) if -90 <= lat <= 90 and -180 <= lon <= 180 else None


async def place_from_text(settings, text: str) -> Spot | None:
    """A Sokoto place a message names (gazetteer, in a thread), as a Spot; None if none or no database."""
    import asyncio

    import psycopg
    if not settings.has_database:
        return None

    def run():
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            found = area_from_text(conn, text)
            return found[1] if found else None
    try:
        return await asyncio.to_thread(run)
    except Exception:            # noqa: BLE001 - the gazetteer down: the message is handled as usual
        return None


def area_from_text(conn, text: str, last_lga: str | None = None):
    """The place a message means, as an Area (and a point when the gazetteer has one): a place it names (an LGA,
    ward, town or village, from our own gazetteer), else 'here' / 'a nan' with the LGA on file. None when neither."""
    from app.geo import Area, geocode
    from app.sources.lga_names import name_of
    if places := geocode(conn, text, most=1):
        p = places[0]
        return Area(p.lga_pcode, p.lga), Spot(p.lat, p.lon, p.lga_pcode, p.lga, how="place")
    if last_lga and HERE.search(text or ""):
        return Area(last_lga, name_of(last_lga)), None
    return None


# "here" in a question: the location on file is meant ("a nan", "inda nake", "wurina", "around me")
HERE = re.compile(r"(?i)\b(?:here|near me|around me|my area|where i am|a nan|nan kusa|inda nake|wurina|"
                  r"kusa da ni|unguwata|garinmu)\b")
# asking to share a location ("raba wurina", "share my location"): the request button is sent
SHARE = re.compile(r"(?i)^\s*(?:/?share (?:my )?location|send (?:my )?location|raba wurina|tura wurina|"
                   r"/location|/wuri)\s*$")
