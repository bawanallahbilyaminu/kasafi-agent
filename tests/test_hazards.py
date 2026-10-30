"""Hazard layers (docs/hazard-and-services.md section 4): the named scales, the fetchers (mocked HTTP), and
freshness: old data is never passed off as current."""

import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.hazards import categories as cat
from app.hazards import fetch
from app.hazards.read import freshness


def test_the_nws_heat_index_and_its_categories_in_celsius() -> None:
    # NWS heat index chart: 90 F / 60 % -> 100 F; 96 F / 65 % -> 121 F; 80 F / 40 % -> 80 F (simple formula)
    assert cat.heat_index_c(32.2, 60) == pytest.approx(37.8, abs=0.6)
    assert cat.heat_index_c(35.6, 65) == pytest.approx(49.4, abs=0.8)
    assert cat.heat_index_c(26.7, 40) == pytest.approx(26.7, abs=0.6)
    assert cat.heat_index_c(40.0, 10) < 40.0                     # dry air: the low-humidity adjustment
    assert [cat.heat_category(x) for x in (25, 26.7, 32.2, 39.4, 51.1)] == \
        ["below", "caution", "extreme_caution", "danger", "extreme_danger"]


def test_aqi_rain_and_river_scales() -> None:
    assert [cat.aqi_category(x) for x in (10, 51, 101, 151, 201, 301)] == \
        ["good", "moderate", "unhealthy_sensitive", "unhealthy", "very_unhealthy", "hazardous"]
    assert [cat.rain_class(x) for x in (0, 1, 2.5, 10, 50)] == ["none", "light", "moderate", "heavy", "violent"]
    assert cat.percentile_rank(10, [1, 2, 3, 20]) == 75.0
    assert cat.WHO_24H == {"pm10": 45.0, "pm2_5": 15.0}
    assert cat.label("danger", "ha") == "Haɗari" and cat.label("very_unhealthy", "en") == "Very unhealthy"


def test_firms_csv_rows_become_detections() -> None:
    text = ("latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,"
            "bright_ti5,frp,daynight\n13.0512,5.2211,330.1,0.4,0.4,2026-10-30,0112,N,VIIRS,n,2.0NRT,290.2,3.4,N\n"
            "bad,row\n")
    rows = fetch.parse_firms(text, "VIIRS_SNPP_NRT")
    assert len(rows) == 1 and rows[0]["at"] == datetime(2026, 10, 30, 1, 12, tzinfo=timezone.utc)
    assert rows[0]["frp"] == 3.4 and rows[0]["confidence"] == "n"


class FakeConn:
    """Records inserts; answers the few selects the fetchers make."""

    def __init__(self, last_ok=None):
        self.rows, self.fetch_log, self.last_ok = [], [], last_ok

    def execute(self, sql, args=()):
        if sql.startswith("INSERT INTO hazard_fetch"):
            self.fetch_log.append(args)
        res = {"SELECT id, name, ST_Y": [(1, "Binji", 13.2, 4.9), (2, "grid 13.1 5.2", 13.1, 5.2)],
               "SELECT max(started_at)": [(self.last_ok,)]}
        rows = next((v for k, v in res.items() if sql.startswith(k)), [])
        return type("R", (), {"fetchall": lambda _: rows, "fetchone": lambda _: rows[0] if rows else None})()

    def cursor(self):
        conn = self

        class C:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def executemany(self, sql, rows):
                conn.rows += rows
        return C()

    def rollback(self):
        pass


def test_a_forecast_fetch_stores_every_value_with_its_source_and_time_and_backs_off_on_429(monkeypatch) -> None:
    calls = []

    def reply(request):
        calls.append(request.url.params)
        if len(calls) == 1:
            return httpx.Response(429)
        loc = {"hourly": {"time": ["2026-10-30T14:00"], **{v: [30.0] for v in fetch.FORECAST_VARS}}}
        return httpx.Response(200, json=[loc, loc])

    async def no_wait(_s):
        return None
    monkeypatch.setattr(fetch.asyncio, "sleep", no_wait)
    conn = FakeConn()
    s = type("S", (), {"firms_map_key": None})()
    n = asyncio.run(fetch.run_layer(conn, "forecast", s, httpx.AsyncClient(transport=httpx.MockTransport(reply))))
    assert n == 2 * len(fetch.FORECAST_VARS) and len(calls) == 2              # retried after the 429
    layer, pid, vt, var, val, unit, source, issued, fetched = conn.rows[0]
    assert layer == "forecast" and vt == datetime(2026, 10, 30, 14, 0, tzinfo=timezone(timedelta(hours=1)))
    assert source.startswith("Open-Meteo forecast") and fetched.tzinfo is not None and unit == "°C"
    assert conn.fetch_log[-1][2] is True                                      # logged ok


def test_a_failed_fetch_is_logged_and_never_raises() -> None:
    conn = FakeConn()
    s = type("S", (), {"firms_map_key": None})()
    n = asyncio.run(fetch.run_layer(conn, "air", s, httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(500)))))
    layer, started, ok, rows, calls, error = conn.fetch_log[-1]
    assert n == -1 and ok is False and "HTTPStatusError" in error and calls == 2        # a refused call counts too
    assert asyncio.run(fetch.run_layer(conn, "fires", s)) == 0              # no FIRMS key: the layer is off


def test_open_meteo_calls_are_counted_as_billed_and_capped(monkeypatch) -> None:
    assert fetch.calls_for(50, 4, 8) == 50 and fetch.calls_for(1, 10_894, 1) == 779 and fetch.calls_for(4, 10, 2) == 4
    ran = []

    async def fake_run(conn, layer, settings, http=None):
        ran.append(layer)
        return 1
    monkeypatch.setattr(fetch, "run_layer", fake_run)
    monkeypatch.setattr(fetch, "due", lambda conn, layer, now=None: True)
    monkeypatch.setattr(fetch, "calls_today", lambda conn: 4_900)
    monkeypatch.setattr(fetch, "estimate", lambda conn, layer: {"forecast": 23, "forecast_grid": 269, "air": 292,
                                                               "flood": 4}.get(layer, 0))

    class Conn:
        def execute(self, *a):
            return type("R", (), {"fetchone": lambda _: (1,)})()
    s = type("S", (), {"kasafi_openmeteo_daily_cap": 5000, "firms_map_key": None})()
    out = asyncio.run(fetch.run_due(Conn(), s))
    assert ran == ["forecast", "flood", "fires"] and out["air"] == 0 and out["forecast_grid"] == 0   # over the cap


def test_the_scheduler_is_off_unless_asked(monkeypatch) -> None:
    import threading
    started = []
    monkeypatch.setattr(threading, "Thread", lambda **kw: started.append(kw) or type("T", (), {"start": lambda s: 0})())
    from tests.helpers import make_settings
    fetch.start_scheduler(make_settings())                                    # off by default
    assert started == []


def test_freshness_says_how_old_the_data_is_or_that_there_is_none() -> None:
    now = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
    fresh = freshness(FakeConn(now - timedelta(hours=2)), "forecast", now)
    stale = freshness(FakeConn(now - timedelta(hours=9)), "forecast", now)
    none = freshness(FakeConn(None), "forecast", now)
    assert not fresh.stale and fresh.hours_old == 2.0
    assert stale.stale and stale.hours_old == 9.0                            # > 2 x 3 h
    assert not none.available and none.stale
    assert fetch.due(FakeConn(now - timedelta(hours=4)), "forecast", now) and \
        not fetch.due(FakeConn(now - timedelta(hours=1)), "forecast", now)
