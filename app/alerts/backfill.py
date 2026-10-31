"""The dust alert's season baseline (air_daily): each LGA's highest US AQI per past day, from the Open-Meteo Air
Quality API's past days (CAMS global, the same source as the live layer), so 'high for the time of year' works
from the first day instead of after 20 days of recording.

One request per batch of LGA centroids (23 points, two variables: us_aqi_pm10 and us_aqi_pm2_5), as many past days
as the free API gives (it is asked for 92, then fewer if refused). The calls count towards today's Open-Meteo cap
(KASAFI_OPENMETEO_DAILY_CAP) and are logged in hazard_fetch as 'air_history'; the backfill is skipped when it
would pass the cap. The alerts round runs it when the baseline is short (app/alerts/dispatch.py).

    python -m app.alerts.backfill          (by hand; prints the days stored and the calls)
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone

import httpx

from app.alerts.triggers import AIR_MIN_DAYS, LAGOS
from app.hazards.fetch import AIR_URL, HEADERS, TZ, _get, _local, _log, calls_for, calls_today, points

log = logging.getLogger(__name__)
LAYER = "air_history"
PAST_DAYS = (92, 61, 31)                   # the free API's limit is tried first, then less if refused
VARS = ("us_aqi_pm10", "us_aqi_pm2_5")


def history_days(conn) -> int:
    return conn.execute("SELECT count(DISTINCT day) FROM air_daily").fetchone()[0]


def daily_max(data: list[dict], pids: list[int], today) -> list[tuple[int, object, float]]:
    """(point id, Lagos day, the day's highest US AQI) for each past day: the higher of PM10's and PM2.5's AQI."""
    out = []
    for pid, d in zip(pids, data):
        hours = d.get("hourly") or {}
        best: dict = defaultdict(float)
        for j, t in enumerate(hours.get("time") or []):
            day = _local(t).date()
            if day >= today:
                continue                       # today belongs to the live layer
            vals = [hours[v][j] for v in VARS if hours.get(v) and hours[v][j] is not None]
            if vals:
                best[day] = max(best[day], max(vals))
        out += [(pid, day, v) for day, v in best.items() if v > 0]
    return out


async def backfill(conn, settings, http: httpx.AsyncClient | None = None) -> tuple[int, int]:
    """(distinct days now in air_daily, Open-Meteo calls made). Skipped (0 calls) when it would pass the cap."""
    pts = points(conn, ("lga",))
    pid_lga = {r[0]: r[1] for r in conn.execute("SELECT id, lga_pcode FROM hazard_point WHERE kind = 'lga'")}
    today = datetime.now(LAGOS).date()
    own = http is None
    http = http or httpx.AsyncClient(headers=HEADERS)
    started, calls = datetime.now(timezone.utc), 0
    try:
        for past in PAST_DAYS:
            need = calls_for(len(pts), past + 1, len(VARS))
            if calls_today(conn) + need > settings.kasafi_openmeteo_daily_cap:
                log.warning("air history backfill skipped: %d calls would pass the daily cap", need)
                return history_days(conn), 0
            try:
                r = await _get(http, AIR_URL, {"latitude": ",".join(f"{p[2]:.4f}" for p in pts),
                                               "longitude": ",".join(f"{p[3]:.4f}" for p in pts),
                                               "hourly": ",".join(VARS), "timezone": TZ, "past_days": past,
                                               "forecast_days": 1, "domains": "cams_global"}, calls=need)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:           # more past days than the API gives: ask for fewer
                    continue
                raise
            calls = need
            data = r.json()
            rows = daily_max(data if isinstance(data, list) else [data], [p[0] for p in pts], today)
            with conn.cursor() as cur:
                cur.executemany("INSERT INTO air_daily (lga_pcode, day, aqi_max) VALUES (%s, %s, %s) ON CONFLICT "
                                "(lga_pcode, day) DO UPDATE SET aqi_max = greatest(air_daily.aqi_max, "
                                "excluded.aqi_max)", [(pid_lga[pid], day, v) for pid, day, v in rows])
            _log(conn, LAYER, started, True, len(rows), calls=calls)
            log.info("air history backfill: %d past days asked, %d LGA-days stored, %d calls", past, len(rows), calls)
            return history_days(conn), calls
        _log(conn, LAYER, started, False, 0, "every past_days asked was refused", calls=calls)
        return history_days(conn), calls
    finally:
        if own:
            await http.aclose()


def due(conn) -> bool:
    """The baseline is short and no backfill has succeeded today."""
    if history_days(conn) >= AIR_MIN_DAYS:
        return False
    return not conn.execute("SELECT 1 FROM hazard_fetch WHERE layer = %s AND ok AND started_at >= now() - "
                            "interval '1 day'", (LAYER,)).fetchone()


if __name__ == "__main__":
    import psycopg

    from app.config import get_settings
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    s = get_settings()
    with psycopg.connect(s.db_url(), autocommit=True) as c:
        days, n = asyncio.run(backfill(c, s))
        print(f"air_daily: {days} distinct days; {n} Open-Meteo calls")
