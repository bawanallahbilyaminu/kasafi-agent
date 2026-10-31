"""Nearest health facilities and routes (docs/hazard-and-services.md section 6).

nearest_facilities: a PostGIS nearest-neighbour search (the index's candidates, re-sorted by true distance on the
sphere) with filters for level, ownership and EmONC capability; the top 3 by straight-line distance. Then road
distance and time for those 3 from OpenRouteService (one Matrix call, car or foot); without ORS (no key, an error,
the daily budget spent) the straight-line distance with "road distance may be longer".

The facility's LGA is the one its point is in (COD-AB decides), said with the file's own LGA when they differ.
Functional status isn't in the GRID3 / NHFR file, so it can't be filtered: the reply says opening hours and
services aren't confirmed. The user's point goes to ORS rounded to 3 decimals (about 100 m), and is never stored or
logged (app/geo/location.py).
"""

from __future__ import annotations

import logging
import math
import re
import threading
import time
from dataclasses import dataclass, field, replace
from datetime import date

import httpx

from app.geo.corrections import checked_on
from app.sources.lga_names import canonical

log = logging.getLogger(__name__)

ORS_MATRIX = "https://api.openrouteservice.org/v2/matrix/{profile}"
PROFILES = {"car": "driving-car", "foot": "foot-walking"}
ORS_DAILY = 400                 # the free Matrix plan allows 500 a day; keep a margin
CANDIDATES = 40                 # index candidates re-sorted by true distance
LEVELS = ("Primary", "Secondary", "Tertiary")


@dataclass(frozen=True)
class Filters:
    levels: tuple[str, ...] = ()            # empty: any
    ownership: str = ""                     # Public | Private | "" (any)
    emonc: str = ""                         # bemonc | cemonc | "" ; cemonc also satisfies bemonc
    confirmed_only: bool = False            # EmONC links a person confirmed (the emergency fast path)

    def describe(self, lang: str) -> str:
        w = WORDS[lang]
        bits = ([w["own"][self.ownership]] if self.ownership else []) + \
               ([w["hospitals"]] if set(self.levels) == {"Secondary", "Tertiary"} else []) + \
               ([w["emonc"][self.emonc]] if self.emonc else [])
        return ", ".join(bits)


@dataclass
class Facility:
    fid: str
    name: str
    level: str
    level_option: str
    ownership: str
    ownership_type: str
    lat: float
    lon: float
    lga: str                    # from the point
    lga_attr: str               # the file's own
    km: float                   # straight line
    emonc: str = ""
    road_km: float | None = None
    minutes: float | None = None
    checked: str = ""           # the date a person checked its location (data/geo/facility_corrections.yaml)

    @property
    def lga_differs(self) -> bool:
        return bool(self.lga_attr) and canonical(self.lga_attr) != canonical(self.lga)


def _sphere_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def nearest_facilities(conn, lat: float, lon: float, filters: Filters = Filters(), k: int = 3, skip: int = 0
                       ) -> list[Facility]:
    """The k nearest facilities matching the filters (after `skip` nearer ones: 'the next one'), by straight-line
    distance on the sphere."""
    where, args = ["f.geom IS NOT NULL", "NOT f.hidden"], {"lat": lat, "lon": lon, "n": CANDIDATES + skip}
    if filters.levels:
        # a hospital by its level or by its type: the file lists Goronyo General Hospital as 'Primary'
        hospital = " OR f.level_option ILIKE '%%hospital%%'" if "Secondary" in filters.levels else ""
        where.append(f"(f.level = ANY(%(levels)s){hospital})")
        args["levels"] = list(filters.levels)
    if filters.ownership:
        where.append("f.ownership = %(own)s")
        args["own"] = filters.ownership
    if filters.emonc:
        caps = ["cemonc"] if filters.emonc == "cemonc" else ["bemonc", "cemonc"]
        where.append("EXISTS (SELECT 1 FROM facility_capability c WHERE c.fid = f.fid AND c.capability = ANY(%(caps)s)"
                     + (" AND c.confirmed" if filters.confirmed_only else " AND (c.confirmed OR c.score >= 1.0)") + ")")
        args["caps"] = caps
    rows = conn.execute(
        "SELECT f.fid, f.name, f.level, coalesce(f.level_option, ''), coalesce(f.ownership, ''), "
        "coalesce(f.ownership_type, ''), ST_Y(f.geom), ST_X(f.geom), coalesce(l.name, ''), coalesce(f.lga_attr, ''), "
        "(SELECT string_agg(c.capability, ',') FROM facility_capability c WHERE c.fid = f.fid "
        " AND (c.confirmed OR c.score >= 1.0)), f.correction "
        "FROM facility f LEFT JOIN lga l ON l.pcode = f.lga_pcode WHERE " + " AND ".join(where) +
        " ORDER BY f.geom <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326) LIMIT %(n)s", args).fetchall()
    exact = sorted((_sphere_km(lat, lon, r[6], r[7]), r[0], r) for r in rows)      # sort before rounding: no ties
    return [Facility(r[0], r[1], r[2] or "", r[3].replace("\xa0", " "), r[4], r[5], r[6], r[7], r[8], r[9],
                     round(d, 2), "cemonc" if "cemonc" in (r[10] or "") else "bemonc" if r[10] else "",
                     checked=checked_on(r[11] if len(r) > 11 else None))
            for d, _, r in exact[skip:skip + k]]


def checked_text(lang: str, f) -> str:
    """' (location checked 1 Nov 2026)' for a facility whose location a person verified, else ''."""
    if not getattr(f, "checked", ""):
        return ""
    d = date.fromisoformat(f.checked)
    return WORDS[lang]["checked"].format(d=f"{d.day} {d:%b %Y}")


class OrsBudget:
    """Matrix calls today (UTC), in memory: past the daily budget the reply uses straight-line distances."""

    def __init__(self, per_day: int = ORS_DAILY) -> None:
        self.per_day, self._day, self._n, self._lock = per_day, date.min, 0, threading.Lock()

    def take(self) -> bool:
        with self._lock:
            today = date.today()
            if today != self._day:
                self._day, self._n = today, 0
            if self._n >= self.per_day:
                return False
            self._n += 1
            return True


ors_budget = OrsBudget()


async def add_routes(settings, lat: float, lon: float, facilities: list[Facility], profile: str = "car",
                     http: httpx.AsyncClient | None = None, timeout: float = 6.0) -> bool:
    """Road distance and time for each facility (one ORS Matrix call). False, and the facilities unchanged, when
    there is no key, ORS fails, or today's budget is spent."""
    key = getattr(settings, "ors_api_key", None)
    if not facilities or key is None or not key.get_secret_value() or not ors_budget.take():
        return False
    body = {"locations": [[round(lon, 3), round(lat, 3)]] + [[f.lon, f.lat] for f in facilities],
            "sources": [0], "destinations": list(range(1, len(facilities) + 1)), "metrics": ["distance", "duration"]}
    own = http is None
    http = http or httpx.AsyncClient()
    try:
        r = await http.post(ORS_MATRIX.format(profile=PROFILES.get(profile, PROFILES["car"])), json=body,
                            headers={"Authorization": key.get_secret_value()}, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        dist, dur = data["distances"][0], data["durations"][0]
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as e:
        log.warning("ORS matrix failed: %s", type(e).__name__)
        return False
    finally:
        if own:
            await http.aclose()
    for f, d, s in zip(facilities, dist, dur):
        if d is not None and s is not None:
            f.road_km, f.minutes = round(d / 1000, 1), round(s / 60)
    return any(f.road_km is not None for f in facilities)


ORS_DIRECTIONS = "https://api.openrouteservice.org/v2/directions/{profile}/geojson"
directions_budget = OrsBudget(per_day=1500)          # the free Directions plan allows 2,000 a day


async def route_line(settings, lat: float, lon: float, f: Facility, profile: str = "car",
                     http: httpx.AsyncClient | None = None, timeout: float = 6.0) -> list[tuple[float, float]]:
    """The road route's (lon, lat) points to the facility from ORS Directions, for the near-you map; [] when there
    is no key, the call fails or today's budget is spent. The start is rounded to about 100 m, as for the Matrix."""
    key = getattr(settings, "ors_api_key", None)
    if key is None or not key.get_secret_value() or not directions_budget.take():
        return []
    own = http is None
    http = http or httpx.AsyncClient()
    try:
        r = await http.post(ORS_DIRECTIONS.format(profile=PROFILES.get(profile, PROFILES["car"])),
                            # a rural pin is often further than ORS's default 350 m from a road: snap at any distance
                            json={"coordinates": [[round(lon, 3), round(lat, 3)], [f.lon, f.lat]],
                                  "radiuses": [-1, -1]},
                            headers={"Authorization": key.get_secret_value()}, timeout=timeout)
        r.raise_for_status()
        coords = r.json()["features"][0]["geometry"]["coordinates"]
        return [(float(x), float(y)) for x, y, *_ in coords]
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as e:
        log.warning("ORS directions failed: %s", type(e).__name__)
        return []
    finally:
        if own:
            await http.aclose()


def maps_link(f: Facility, profile: str = "car") -> str:
    """Google Maps directions to the facility (the URL scheme, no API key); the phone supplies the start."""
    mode = "walking" if profile == "foot" else "driving"
    return f"https://www.google.com/maps/dir/?api=1&destination={f.lat:.6f},{f.lon:.6f}&travelmode={mode}"


def address_of(f: Facility, lang: str) -> str:
    return WORDS[lang]["address"].format(lga=f.lga or f.lga_attr)


# --- the reply -------------------------------------------------------------------------------------------------

WORDS = {
    "en": {"head": "🏥 *Nearest health facilities*{what}{where}:", "where_spot": " to your location",
           "where_lga": " near the centre of {lga} LGA",
           "row": "{n}. *{name}*, {level} ({kind}), {place}: {dist}",
           "road": "{km} km by road, about {mins}", "foot": "{km} km on foot, about {mins}",
           "line": "about {km} km in a straight line", "road_note": "Road distance may be longer.",
           "lga": "in {lga} LGA", "lga_differs": "in {lga} LGA (the facility list says {attr})",
           "levels": {"Primary": "primary", "Secondary": "secondary", "Tertiary": "tertiary"},
           "own": {"Public": "government", "Private": "private"}, "hospitals": "hospitals",
           "emonc": {"bemonc": "emergency obstetric care", "cemonc": "comprehensive emergency obstetric care"},
           "emonc_tag": {"bemonc": "basic EmONC", "cemonc": "comprehensive EmONC"},
           "caution": "Kasafi can't confirm opening hours or services; call ahead if you can.",
           "pin": "📍 The nearest one's location follows. Directions: {link}",
           "none": "No facility matching that ({what}) was found in Sokoto's facility list.",
           "next_none": "There are no more facilities matching that in the list.",
           "need_location": "To find the nearest facility, share your location, or tell me your LGA or town.",
           "address": "{lga} LGA, Sokoto State", "mins_h": "{h} h {m} min", "mins": "{m} min",
           "route_head": "🧭 *Route to {name}*{checked}: {dist}.",
           "checked": " (location checked {d})",
           "nearer": "Nearer, but not a hospital: *{name}* ({level}), about {km} km in a straight line.",
           "summary": "The nearest health facility is {name}, {dist}.",
           "summary_hospital": "The nearest hospital is {name}, {dist}.",
           "follow": "Reply “next” for the next one, “route”, “only government”, “only hospitals” or “on foot”."},
    "ha": {"head": "🏥 *Cibiyoyin lafiya mafi kusa*{what}{where}:", "where_spot": " da inda kake",
           "where_lga": " kusa da tsakiyar Ƙaramar Hukumar {lga}",
           "row": "{n}. *{name}*, {level} ({kind}), {place}: {dist}",
           "road": "kilomita {km} ta hanya, kusan {mins}", "foot": "kilomita {km} da ƙafa, kusan {mins}",
           "line": "kusan kilomita {km} a miƙe", "road_note": "Nisan hanya zai iya fi haka.",
           "lga": "a Ƙaramar Hukumar {lga}", "lga_differs": "a Ƙaramar Hukumar {lga} (jerin ya ce {attr})",
           "levels": {"Primary": "matakin farko", "Secondary": "mataki na biyu", "Tertiary": "babban asibiti"},
           "own": {"Public": "na gwamnati", "Private": "masu zaman kansu"}, "hospitals": "asibitoci",
           "emonc": {"bemonc": "kulawar gaggawa ta haihuwa", "cemonc": "cikakkiyar kulawar gaggawa ta haihuwa"},
           "emonc_tag": {"bemonc": "EmONC na asali", "cemonc": "cikakken EmONC"},
           "caution": "Kasafi ba zai iya tabbatar da lokutan buɗewa ko ayyuka ba; ka kira kafin ka je idan za ka iya.",
           "pin": "📍 Wurin mafi kusa yana zuwa. Hanya: {link}",
           "none": "Ba a sami cibiyar da ta dace da haka ({what}) a jerin cibiyoyin lafiya na Sokoto ba.",
           "next_none": "Babu ƙarin cibiyoyi da suka dace da haka a jerin.",
           "need_location": "Don nemo cibiyar lafiya mafi kusa, raba wurinka, ko faɗa mini ƙaramar hukumarka ko "
                            "garinka.",
           "address": "Ƙaramar Hukumar {lga}, Jihar Sokoto", "mins_h": "awa {h} da minti {m}", "mins": "minti {m}",
           "route_head": "🧭 *Hanya zuwa {name}*{checked}: {dist}.",
           "checked": " (an tabbatar da wurin {d})",
           "nearer": "Akwai mafi kusa, amma ba asibiti ba: *{name}* ({level}), kusan kilomita {km} a miƙe.",
           "summary": "Cibiyar lafiya mafi kusa ita ce {name}, {dist}.",
           "summary_hospital": "Asibiti mafi kusa shi ne {name}, {dist}.",
           "follow": "Rubuta “na gaba” don na gaba, “hanya”, “na gwamnati kawai”, “asibitoci kawai” ko “da ƙafa”."},
}


def _mins(lang: str, m: float) -> str:
    w = WORDS[lang]
    m = int(round(m))
    return w["mins_h"].format(h=m // 60, m=m % 60) if m >= 60 else w["mins"].format(m=max(m, 1))


def distance_text(lang: str, f: Facility, profile: str = "car") -> str:
    w = WORDS[lang]
    if f.road_km is not None and f.minutes is not None:
        return w["foot" if profile == "foot" else "road"].format(km=f"{f.road_km:g}", mins=_mins(lang, f.minutes))
    return w["line"].format(km=f"{f.km:.1f}")


def facilities_text(lang: str, found: list[Facility], filters: Filters, profile: str = "car", routed: bool = True,
                    where: str = "spot", lga: str = "", start: int = 1) -> str:
    w = WORDS[lang]
    what = filters.describe(lang)
    head = w["head"].format(what=f" ({what})" if what else "",
                            where=w["where_spot"] if where == "spot" else w["where_lga"].format(lga=lga))
    rows = []
    for n, f in enumerate(found, start):
        kind = f.level_option if f.level_option and f.level_option != "Unknown" else ""
        if f.emonc:
            kind = ", ".join(x for x in (kind, w["emonc_tag"][f.emonc]) if x)
        place = w["lga_differs"].format(lga=f.lga, attr=f.lga_attr) if f.lga_differs else w["lga"].format(lga=f.lga)
        rows.append(w["row"].format(n=n, name=f.name, level=w["levels"].get(f.level, f.level), kind=kind or "-",
                                    place=place, dist=distance_text(lang, f, profile)).replace(" (-)", "")
                    + checked_text(lang, f))
    tail = [] if routed else [w["road_note"]]
    return "\n".join([head, *rows, *tail, "", w["caution"]])


# --- what a message asks ---------------------------------------------------------------------------------------

FACILITY = re.compile(
    r"(?i)\b(?:hospitals?|clinics?|health ?(?:cent(?:er|re)|facilit\w+|post)s?|phcs?|dispensar\w+|maternit\w+|"
    r"asibiti\w*|cibiyar lafiya|cibiyoyin lafiya|ɗakin shan magani|dakin shan magani|gidan haihuwa)\b")
NEAR = re.compile(r"(?i)\b(?:nearest|near(?:by| me| here)?|closest|close to|around|where is|where can|kusa|mafi kusa|"
                  r"ina\b|a ina)\b")
NEXT = re.compile(r"(?i)^\s*(?:(?:the )?next(?: one)?|another( one)?|na gaba|wani(?:n)?|wata)\s*[?.!]*\s*$")
ROUTE = re.compile(r"(?i)\b(?:route|directions?|how (?:do|can) i get|way there|how far|distance|from me|hanya(?:r)?|"
                   r"yaya zan je|ta ina zan bi|nisan?\w*)\b")
FOOT = re.compile(r"(?i)\b(?:on foot|walk(?:ing)?|da ƙafa|da kafa|tafiya a ƙasa)\b")
CAR = re.compile(r"(?i)\b(?:by car|driving|drive|da mota|a mota)\b")
GOV = re.compile(r"(?i)\b(?:government|public|state|gwamnati)\b")
PRIVATE = re.compile(r"(?i)\b(?:private|masu zaman kansu|na kai|mai zaman kansa)\b")
HOSPITAL_ONLY = re.compile(r"(?i)\b(?:only\b.{0,25}\bhospitals?|hospitals? only|(?:general|big|main) hospitals?|"
                           r"asibitoci kawai|babban asibiti|manyan asibitoci)\b")
HOSPITAL_WORD = re.compile(r"(?i)\b(?:hospitals?|asibiti\w*)\b")
ANY_KIND = re.compile(r"(?i)\b(?:clinics?|health ?(?:cent(?:er|re)|facilit\w+|post)s?|phcs?|dispensar\w+|"
                      r"cibiyar lafiya|cibiyoyin lafiya|any)\b")
MATERNAL = re.compile(r"(?i)\b(?:emonc|maternity|labou?r|deliver(?:y|ing)|childbirth|obstetric|pregnan\w+|"
                      r"haihuwa|naƙuda|nakuda|mai ciki)\b")
MONEY = re.compile(r"(?i)\b(?:budget\w*|allocat\w*|spent|spend\w*|naira|₦|kasafi\w*|kuɗi|kudi|how many|nawa|"
                   r"adadin|number of)\b")


def is_facility_query(text: str) -> bool:
    """'Where is the nearest hospital?' / 'Ina asibiti mafi kusa?': a facility word with a 'near' word, and not a
    budget or count question ('how many hospitals in Wamakko?' stays a document question)."""
    t = text or ""
    return bool(FACILITY.search(t) and NEAR.search(t) and not MONEY.search(t))


def filters_from(text: str, base: Filters = Filters()) -> Filters:
    """The filters a message adds: government / private, hospitals only, emergency obstetric care."""
    f = base
    if GOV.search(text or ""):
        f = replace(f, ownership="Public")
    elif PRIVATE.search(text or ""):
        f = replace(f, ownership="Private")
    # 'hospital' / 'asibiti' means a hospital (general, specialist, teaching), not any health facility
    if HOSPITAL_ONLY.search(text or "") or (HOSPITAL_WORD.search(text or "") and not ANY_KIND.search(text or "")):
        f = replace(f, levels=("Secondary", "Tertiary"))
    if MATERNAL.search(text or ""):
        f = replace(f, emonc=f.emonc or "bemonc")
    return f


def profile_from(text: str, current: str = "car") -> str:
    return "foot" if FOOT.search(text or "") else "car" if CAR.search(text or "") else current


@dataclass
class FacilitySearch:
    """The last facility search, kept in memory with the point for follow-ups (30 minutes; never stored)."""
    filters: Filters = field(default_factory=Filters)
    skip: int = 0
    profile: str = "car"
    shown: list = field(default_factory=list)          # the facilities last shown (for "route?")
    at: float = field(default_factory=time.monotonic)


def follow_up(text: str) -> str:
    """'next' | 'route' | 'filter' | '' for a reply to a facility answer: a short message (up to 7 words), never a
    budget or count question ('what did the state government spend on health?' is a new question)."""
    t = text or ""
    if len(t.split()) > 7 or MONEY.search(t):
        return ""
    if NEXT.match(t):
        return "next"
    if ROUTE.search(t):
        return "route"
    if GOV.search(t) or PRIVATE.search(t) or HOSPITAL_ONLY.search(t) or FOOT.search(t) or CAR.search(t) or \
            (MATERNAL.search(t) and len(t.split()) <= 6):
        return "filter"
    return ""


def link_line(lang: str, f: Facility, profile: str = "car") -> str:
    return WORDS[lang]["pin"].format(link=maps_link(f, profile))


def route_text(lang: str, f: Facility, profile: str, routed: bool) -> str:
    w = WORDS[lang]
    return "\n".join([w["route_head"].format(name=f.name, checked=checked_text(lang, f),
                                             dist=distance_text(lang, f, profile)),
                      *([] if routed else [w["road_note"]]), link_line(lang, f, profile)])


def location_payload(f: Facility, lang: str) -> dict:
    """A WhatsApp location message's fields for a facility (name and address set)."""
    return {"latitude": f.lat, "longitude": f.lon, "name": f.name[:100], "address": address_of(f, lang)[:100]}


def emergency_picks(conn, lat: float, lon: float, maternal: bool) -> list[tuple[str, Facility]]:
    """For the emergency fast path: for pregnancy or labour, the nearest comprehensive EmONC hospital whose link a
    person confirmed; otherwise (or when none is confirmed) the nearest general or specialist hospital; then the
    nearest facility of any level when it is another one. (kind, facility): cemonc | hospital | any."""
    picks: list[tuple[str, Facility]] = []
    if maternal and (c := nearest_facilities(conn, lat, lon, Filters(emonc="cemonc", confirmed_only=True), k=1)):
        picks.append(("cemonc", c[0]))
    if not picks and (h := nearest_facilities(conn, lat, lon, Filters(levels=("Secondary", "Tertiary")), k=1)):
        picks.append(("hospital", h[0]))
    if (a := nearest_facilities(conn, lat, lon, k=1)) and (not picks or a[0].fid != picks[0][1].fid):
        picks.append(("any", a[0]))
    return picks


def lga_point(conn, pcode: str) -> tuple[float, float] | None:
    row = conn.execute("SELECT ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom)) FROM lga WHERE pcode = %s",
                       (pcode,)).fetchone()
    return (row[0], row[1]) if row else None


async def emergency_lookup(settings, lat: float | None, lon: float | None, maternal: bool, lga_pcode: str = ""
                           ) -> list[tuple[str, Facility]]:
    """The fast path's picks from a point, or from the LGA's centre when only the LGA is known (no ORS: speed)."""
    import asyncio

    import psycopg

    def run():
        with psycopg.connect(settings.db_url(), connect_timeout=3) as conn:
            point = (lat, lon) if lat is not None else lga_point(conn, lga_pcode)
            return emergency_picks(conn, *point, maternal) if point else []
    return await asyncio.to_thread(run)


def _query(settings, lat: float, lon: float, filters: Filters, skip: int) -> list[Facility]:
    import psycopg
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        return nearest_facilities(conn, lat, lon, filters, skip=skip)


def _near_map(settings, lat: float, lon: float, lga: str, found: list[Facility], line: list, lang: str,
              caption: str) -> bytes | None:
    """The near-you map's JPEG, or None when it can't be drawn (no PostGIS): the text answer stands alone."""
    import psycopg

    from app.maps.render import near_you_map
    try:
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            return near_you_map(conn, lat, lon, lga, found, line, lang, caption).jpeg
    except Exception as e:                       # noqa: BLE001 - a map is extra; never lose the answer over it
        log.warning("near-you map failed: %s", type(e).__name__)
        return None


async def search_replies(settings, lat: float, lon: float, search: FacilitySearch, lang: str, *, mode: str = "list",
                         where: str = "spot", lga: str = "", route: bool = True, drawn: bool = True
                         ) -> list[tuple[str, dict | None, bytes | None]]:
    """The messages to send, as (text, location message or None, map image or None): the list with the nearest
    one's directions link, the near-you map (the route to 1 drawn when ORS gives it), then its location pin; or
    ('route') the route to the facility shown first. `search.shown` is updated. `route=False` skips ORS (the
    emergency fast path answers in under 3 seconds); `drawn=False` sends no map."""
    import asyncio
    w = WORDS[lang]
    lga = lga or (search.shown[0].lga if search.shown else "")
    if mode == "route" and search.shown:
        f = search.shown[0]
        routed = route and await add_routes(settings, lat, lon, [f], search.profile)
        text = route_text(lang, f, search.profile, routed)
        line = await route_line(settings, lat, lon, f, search.profile) if route and drawn else []
        image = await asyncio.to_thread(_near_map, settings, lat, lon, f.lga, [f], line, lang,
                                        text.splitlines()[0]) if drawn else None
        return [(text, None, None), ("", None, image), ("", location_payload(f, lang), None)]
    found = await asyncio.to_thread(_query, settings, lat, lon, search.filters, search.skip)
    if not found:
        return [(w["next_none"] if search.skip else w["none"].format(what=search.filters.describe(lang) or "-"), None,
                 None)]
    routed = route and await add_routes(settings, lat, lon, found, search.profile)
    if routed:                           # nearest by road when the road distances are known
        found.sort(key=lambda f: (f.minutes is None, f.minutes or 0, f.road_km or 0, f.km))
    search.shown = found
    text = facilities_text(lang, found, search.filters, search.profile, routed, where, lga, start=search.skip + 1)
    # hospitals asked for: a facility of any kind much nearer than the nearest hospital gets its own line
    if search.filters.levels and not search.skip:
        nearer = await asyncio.to_thread(_query, settings, lat, lon, Filters(), 0)
        if nearer and nearer[0].fid not in {f.fid for f in found} and nearer[0].km < 0.5 * found[0].km:
            n = nearer[0]
            text = text.replace(f"\n\n{w['caution']}", "\n" + w["nearer"].format(
                name=n.name, level=w["levels"].get(n.level, n.level), km=f"{n.km:.1f}") + f"\n\n{w['caution']}")
    image = None
    if drawn:
        line = await route_line(settings, lat, lon, found[0], search.profile) if route else []
        caption = "\n".join(text.splitlines()[1:len(found) + 1])          # the numbered rows: names and distances
        image = await asyncio.to_thread(_near_map, settings, lat, lon, found[0].lga, found, line, lang, caption)
    summary = w["summary_hospital" if search.filters.levels else "summary"].format(
        name=found[0].name, dist=distance_text(lang, found[0], search.profile))
    return [(f"{summary}\n\n{text}\n\n{link_line(lang, found[0], search.profile)}\n\n{w['follow']}", None, None),
            ("", None, image), ("", location_payload(found[0], lang), None)]
