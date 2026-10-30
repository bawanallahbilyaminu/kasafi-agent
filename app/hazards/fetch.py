"""The hazard fetchers (docs/hazard-and-services.md section 4). Each writes hazard_values (or fire_detection /
river_history) and logs one hazard_fetch row, ok or not, so answers know how old their data is.

| layer   | source                                         | every | points                  |
| forecast| Open-Meteo forecast API                        | 3 h   | LGA centroids + grid    |
| air     | Open-Meteo Air Quality API (CAMS global)       | 6 h   | LGA centroids + grid    |
| flood   | Open-Meteo Flood API (GloFAS v4)               | 24 h  | river points            |
| flood_history | the same, 1984-01-01 to yesterday, once  | once  | river points            |
| fires   | NASA FIRMS area API, VIIRS (SNPP, NOAA-20)     | 3 h   | Sokoto's bounding box   |

Open-Meteo's free tier is for non-commercial use within its daily call limit (each location counts): ~3,500 calls a
day here. Requests are batched (50 locations), paced, and back off on 429. FIRMS is skipped without FIRMS_MAP_KEY.
"""

from __future__ import annotations

import asyncio
import csv
import io
import logging
from datetime import date, datetime, timedelta, timezone

import httpx
import psycopg

from app.hazards.points import points

log = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}"

FORECAST_VARS = ("temperature_2m", "apparent_temperature", "relative_humidity_2m", "uv_index", "wind_speed_10m",
                 "wind_gusts_10m", "precipitation", "precipitation_probability")
AIR_VARS = ("dust", "pm10", "pm2_5", "aerosol_optical_depth", "us_aqi_pm10", "us_aqi_pm2_5")
UNITS = {"temperature_2m": "°C", "apparent_temperature": "°C", "relative_humidity_2m": "%", "uv_index": "",
         "wind_speed_10m": "km/h", "wind_gusts_10m": "km/h", "precipitation": "mm", "precipitation_probability": "%",
         "dust": "µg/m³", "pm10": "µg/m³", "pm2_5": "µg/m³", "aerosol_optical_depth": "", "us_aqi_pm10": "",
         "us_aqi_pm2_5": "", "river_discharge": "m³/s", "river_discharge_max": "m³/s"}
SOURCES = {"forecast": "Open-Meteo forecast (best-match weather models)",
           "air": "Open-Meteo Air Quality (Copernicus CAMS global)",
           "flood": "Open-Meteo Flood API (GloFAS v4, Copernicus)",
           "fires": "NASA FIRMS VIIRS active fire detections"}
INTERVALS = {"forecast": timedelta(hours=3), "air": timedelta(hours=6), "flood": timedelta(hours=24),
             "fires": timedelta(hours=3)}
FIRMS_SOURCES = ("VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT")
BATCH = 50
TZ = "Africa/Lagos"
HEADERS = {"User-Agent": "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"}


async def _get(http: httpx.AsyncClient, url: str, params: dict | None = None, tries: int = 4) -> httpx.Response:
    for attempt in range(tries):
        r = await http.get(url, params=params, timeout=120)
        if r.status_code != 429 or attempt == tries - 1:
            r.raise_for_status()
            return r
        await asyncio.sleep(20 * (attempt + 1))          # the free tier's per-minute limit
    raise AssertionError("unreachable")


def _log(conn, layer: str, started: datetime, ok: bool, rows: int, error: str = "") -> None:
    conn.execute("INSERT INTO hazard_fetch (layer, started_at, ok, rows, error) VALUES (%s, %s, %s, %s, %s)",
                 (layer, started, ok, rows, error[:300]))


def _local(t: str) -> datetime:
    """Open-Meteo's local time ('2026-10-30T15:00' in Africa/Lagos, UTC+1) as an aware datetime."""
    return datetime.fromisoformat(t).replace(tzinfo=timezone(timedelta(hours=1)))


def _store(conn, layer: str, rows: list[tuple], fetched: datetime) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO hazard_values (layer, point_id, valid_time, variable, value, unit, source, issued_at, "
            "fetched_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (layer, point_id, valid_time, "
            "variable) DO UPDATE SET value = excluded.value, issued_at = excluded.issued_at, "
            "fetched_at = excluded.fetched_at, source = excluded.source",
            [(layer, pid, vt, var, val, UNITS.get(var, ""), SOURCES[layer], None, fetched)
             for pid, vt, var, val in rows])
    return len(rows)


async def _hourly(http, url: str, pts: list, variables: tuple, extra: dict) -> list[tuple]:
    out = []
    for i in range(0, len(pts), BATCH):
        chunk = pts[i:i + BATCH]
        r = await _get(http, url, {"latitude": ",".join(f"{p[2]:.4f}" for p in chunk),
                                   "longitude": ",".join(f"{p[3]:.4f}" for p in chunk),
                                   "hourly": ",".join(variables), "timezone": TZ, **extra})
        data = r.json()
        for (pid, *_), d in zip(chunk, data if isinstance(data, list) else [data]):
            hours = d.get("hourly") or {}
            for j, t in enumerate(hours.get("time") or []):
                vt = _local(t)
                out += [(pid, vt, v, hours[v][j]) for v in variables if hours.get(v) and hours[v][j] is not None]
        await asyncio.sleep(1)
    return out


async def fetch_forecast(conn, http) -> int:
    rows = await _hourly(http, FORECAST_URL, points(conn, ("lga", "grid")), FORECAST_VARS, {"forecast_days": 4})
    return _store(conn, "forecast", rows, datetime.now(timezone.utc))


async def fetch_air(conn, http) -> int:
    rows = await _hourly(http, AIR_URL, points(conn, ("lga", "grid")), AIR_VARS,
                         {"forecast_days": 4, "domains": "cams_global"})
    return _store(conn, "air", rows, datetime.now(timezone.utc))


async def fetch_flood(conn, http) -> int:
    pts = points(conn, ("river",))
    r = await _get(http, FLOOD_URL, {"latitude": ",".join(f"{p[2]:.3f}" for p in pts),
                                     "longitude": ",".join(f"{p[3]:.3f}" for p in pts),
                                     "daily": "river_discharge,river_discharge_max", "forecast_days": 7,
                                     "past_days": 3})
    data = r.json()
    rows = []
    for (pid, *_), d in zip(pts, data if isinstance(data, list) else [data]):
        days = d.get("daily") or {}
        for j, t in enumerate(days.get("time") or []):
            vt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
            rows += [(pid, vt, v, days[v][j]) for v in ("river_discharge", "river_discharge_max")
                     if days.get(v) and days[v][j] is not None]
    return _store(conn, "flood", rows, datetime.now(timezone.utc))


async def fetch_flood_history(conn, http, start: str = "1984-01-01") -> int:
    """Each river point's daily discharge from 1984 to yesterday, once (a point that has it is skipped)."""
    n = 0
    for pid, name, lat, lon in points(conn, ("river",)):
        if conn.execute("SELECT 1 FROM river_history WHERE point_id = %s LIMIT 1", (pid,)).fetchone():
            continue
        r = await _get(http, FLOOD_URL, {"latitude": f"{lat:.3f}", "longitude": f"{lon:.3f}",
                                         "daily": "river_discharge", "start_date": start,
                                         "end_date": (date.today() - timedelta(days=1)).isoformat()})
        days = r.json().get("daily") or {}
        rows = [(pid, t, q) for t, q in zip(days.get("time") or [], days.get("river_discharge") or []) if q is not None]
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO river_history (point_id, day, discharge) VALUES (%s, %s, %s) "
                            "ON CONFLICT DO NOTHING", rows)
        n += len(rows)
        log.info("river history: %s, %d days", name, len(rows))
        await asyncio.sleep(15)                     # forty years is a heavy request: one point at a time
    return n


def parse_firms(text: str, satellite: str) -> list[dict]:
    """FIRMS area CSV rows -> detections (latitude, longitude, acq_date, acq_time HHMM UTC, confidence, frp)."""
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            hhmm = str(row.get("acq_time") or "0").zfill(4)
            at = datetime.fromisoformat(f"{row['acq_date']}T{hhmm[:2]}:{hhmm[2:]}:00+00:00")
            out.append({"lat": float(row["latitude"]), "lon": float(row["longitude"]), "at": at,
                        "confidence": str(row.get("confidence") or ""), "frp": float(row.get("frp") or 0),
                        "satellite": satellite})
        except (KeyError, ValueError):
            continue
    return out


async def fetch_fires(conn, http, key: str) -> int:
    w, s, e, n = conn.execute("SELECT ST_XMin(x), ST_YMin(x), ST_XMax(x), ST_YMax(x) FROM "
                              "(SELECT ST_Extent(geom) x FROM lga) b").fetchone()
    bbox = f"{w:.2f},{s:.2f},{e:.2f},{n:.2f}"
    fetched, count = datetime.now(timezone.utc), 0
    for src in FIRMS_SOURCES:
        r = await _get(http, FIRMS_URL.format(key=key, source=src, bbox=bbox, days=1))
        for d in parse_firms(r.text, src):
            # only detections inside Sokoto, with the LGA they fall in
            cur = conn.execute(
                "INSERT INTO fire_detection (geom, lga_pcode, detected_at, confidence, frp, satellite, source, "
                "fetched_at) SELECT ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), l.pcode, %(at)s, %(confidence)s, "
                "%(frp)s, %(satellite)s, %(source)s, %(fetched)s FROM lga l WHERE ST_Within(ST_SetSRID(ST_MakePoint("
                "%(lon)s, %(lat)s), 4326), l.geom) ON CONFLICT DO NOTHING",
                {**d, "source": SOURCES["fires"], "fetched": fetched})
            count += cur.rowcount
    return count


async def run_layer(conn, layer: str, settings, http: httpx.AsyncClient | None = None) -> int:
    """Run one layer's fetch and log it; a failure is logged (and returns -1), never raised."""
    started = datetime.now(timezone.utc)
    own = http is None
    http = http or httpx.AsyncClient(headers=HEADERS)
    try:
        if layer == "fires":
            if settings.firms_map_key is None:
                return 0                              # no key: the layer is off, nothing logged as a failure
            n = await fetch_fires(conn, http, settings.firms_map_key.get_secret_value())
        else:
            n = await {"forecast": fetch_forecast, "air": fetch_air, "flood": fetch_flood,
                       "flood_history": fetch_flood_history}[layer](conn, http)
        _log(conn, layer, started, True, n)
        log.info("hazard fetch %s: %d rows", layer, n)
        return n
    except (httpx.HTTPError, ValueError, KeyError, psycopg.Error) as e:
        conn.rollback()
        _log(conn, layer, started, False, 0, f"{type(e).__name__}: {str(e)[:200]}")
        log.warning("hazard fetch %s failed: %s", layer, type(e).__name__)
        return -1
    finally:
        if own:
            await http.aclose()


def due(conn, layer: str, now: datetime | None = None) -> bool:
    """The layer's last successful fetch is older than its interval (or there is none)."""
    row = conn.execute("SELECT max(started_at) FROM hazard_fetch WHERE layer = %s AND ok", (layer,)).fetchone()
    return row[0] is None or (now or datetime.now(timezone.utc)) - row[0] >= INTERVALS[layer]


async def run_due(conn, settings) -> dict[str, int]:
    """Every layer that is due, in turn (river history first, once)."""
    out = {}
    async with httpx.AsyncClient(headers=HEADERS) as http:
        if not conn.execute("SELECT 1 FROM river_history LIMIT 1").fetchone():
            out["flood_history"] = await run_layer(conn, "flood_history", settings, http)
        for layer in INTERVALS:
            if due(conn, layer):
                out[layer] = await run_layer(conn, layer, settings, http)
    return out
