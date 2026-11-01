"""External review (docs/reviews/2026-11-01-external-review.md), findings 02, 04, 05 and 19: Appendix A's
reproductions as regression tests, plus the privacy audit after a place conversation and the store backup."""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from shapely.geometry import Point, shape

from app.alerts.dispatch import dispatch
from app.alerts.triggers import Candidate
from app.config import Settings
from app.place import history as H
from app.place import outline
from app.users import UserStore
from tests.helpers import make_settings

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


# --- finding 02: alert delivery ----------------------------------------------------------------------------------------

def _candidate(key="synthetic-audit-alert"):
    return Candidate(hazard="heat", lga_pcode="NG034006", key=key, official=False, what={"ha": "test", "en": "test"},
                     source={"ha": "test", "en": "test"})


def _live_settings(**kw):
    return Settings(_env_file=None, kasafi_alerts_dry_run=False, kasafi_alerts_daily_cap=10, kasafi_alert_template_langs="ha",
                    **kw)


def test_appendix_a_failed_send_is_never_recorded_as_sent_and_stays_retryable() -> None:
    store = UserStore(":memory:")
    store.subscribe("synthetic-user", ["NG034006"], ["heat"], "ha")
    attempts = []

    async def failed_send(*args):
        attempts.append(True)
        return False
    first = asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, failed_send))
    second = asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, failed_send))
    row = store.alert_log()[0]
    assert dict(first) == {"failed": 1} and dict(second) == {"failed": 1} and len(attempts) == 2
    assert row["status"] == "failed" and row["recipients"] == 0 and "sent" not in store.alert_statuses("synthetic-audit-alert")

    async def good_send(*args):
        return True
    third = asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, good_send))
    assert dict(third) == {"sent": 1} and store.alert_log()[0]["recipients"] == 1
    assert dict(asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, good_send))) == {}   # done


def test_a_partial_send_retries_only_the_failed_recipients() -> None:
    store = UserStore(":memory:")
    for u in ("u1", "u2", "u3"):
        store.subscribe(u, ["NG034006"], ["heat"], "ha")
    sent: list[str] = []

    async def flaky(key, lang, values):
        sent.append(key)
        return key != "u2"
    out = asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, flaky))
    row = store.alert_log()[0]
    assert dict(out) == {"partial": 1} and row["recipients"] == 2 and store.failed_recipients("synthetic-audit-alert") == {"u2"}
    sent.clear()

    async def ok(key, lang, values):
        sent.append(key)
        return True
    out = asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, ok))
    assert dict(out) == {"sent": 1} and sent == ["u2"]                  # u1 and u3 get no duplicate
    assert dict(asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, ok))) == {}


def test_a_dry_run_record_does_not_consume_the_live_send() -> None:
    store = UserStore(":memory:")
    store.subscribe("u1", ["NG034006"], ["heat"], "ha")
    dry = Settings(_env_file=None, kasafi_alerts_dry_run=True, kasafi_alerts_daily_cap=10, kasafi_alert_template_langs="ha")
    assert dict(asyncio.run(dispatch([_candidate()], store, dry, NOW))) == {"dry_run": 1}
    assert dict(asyncio.run(dispatch([_candidate()], store, dry, NOW))) == {}               # the dry run isn't repeated
    sent = []

    async def ok(key, lang, values):
        sent.append(key)
        return True
    assert dict(asyncio.run(dispatch([_candidate()], store, _live_settings(), NOW, ok))) == {"sent": 1} and sent == ["u1"]


# --- finding 04: the outline cache and the plot keys --------------------------------------------------------------------

def test_appendix_a_two_pins_in_one_cell_do_not_share_an_outline_that_excludes_the_second() -> None:
    outline.forget_all()
    first_lat, first_lon = 13.12801, 5.23501
    second_lat, second_lon = 13.12849, 5.23549
    cached = outline.fallback(first_lon, first_lat, "no_chip")
    outline.remember(first_lat, first_lon, cached)
    assert H.cell_id(first_lat, first_lon) == H.cell_id(second_lat, second_lon)
    assert outline.cached(first_lat, first_lon) is not None                       # the first pin: its own outline
    assert outline.cached(second_lat, second_lon) is None                         # the second pin lies outside it
    with patch.object(outline, "true_colour", return_value=None):
        result = asyncio.run(outline.plot_outline(object(), None, second_lat, second_lon))
    assert result.geometry != cached.geometry and shape(result.geometry).covers(Point(second_lon, second_lat))
    outline.forget_all()


def test_plot_results_are_keyed_by_geometry_hash_and_method_version_in_memory_only() -> None:
    H.forget_plots()
    from app.place.raster import circle
    a, b = circle(5.235, 13.128), circle(5.236, 13.128)
    ka, kb = H.plot_key(a), H.plot_key(b)
    assert ka.startswith("mem:") and ka != kb and H.plot_key(json.loads(json.dumps(a))) == ka
    H._save(None, ka, "s2", 2024, {"season_obs": 9}, "test", 9, date(2026, 11, 1))
    assert H._load(None, ka)[("s2", 2024)][0] == {"season_obs": 9} and H._load(None, kb) == {}
    with patch.object(H, "METHOD_VERSION", "s2-v3"):
        assert H.plot_key(a) != ka
    assert H.cell_circle(13.12849, 5.23549) == circle(5.235, 13.128)               # the persisted geometry is the cell's
    H.forget_plots()


# --- finding 05: nothing locational persisted or logged after a place conversation --------------------------------------

@pytest.fixture
def dev_conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_a_place_conversation_leaves_only_cell_statistics_without_coordinates_or_users(dev_conn, caplog) -> None:
    """The exact pin, a plot polygon and a user never reach the database or the logs; the cell row is the rounded
    cell's statistics."""
    from app.place.history import YearRow, cell_id
    lat, lon = 13.0589127, 5.1673341
    pin_digits = ("13.0589", "5.1673", "13.05891", "5.16733")
    cell = cell_id(lat, lon)
    conn = dev_conn
    conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
    conn.commit()
    before = conn.execute("SELECT count(*) FROM sat_cache").fetchone()[0]

    def fake_years(lat_, lon_, geom, years, **kw):
        return {y: YearRow(y, season_obs=12, ndvi_p90=0.5, water_obs=3, water_share=0.0, water_months=[], dry_obs=8,
                           bsi_dry=0.2) for y in years}
    caplog.set_level(logging.DEBUG)
    with (patch.object(H, "compute_years", fake_years), patch.object(H, "jrc_summary", return_value={"occurrence": 0.0, "recurrence": 0.0, "seasonality": 0.0}),
          patch.object(H, "landcover", return_value="cropland"),
          patch.object(H.rain, "daily_rain", return_value={}), patch.object(H.rain, "by_year", return_value={})):
        h = H.point_history(conn, lat, lon, today=date(2026, 11, 1))
        from app.place.raster import circle
        plot = H.point_history(conn, lat, lon, today=date(2026, 11, 1), polygon=circle(lon, lat, 90.0))
    assert h.cell == cell and plot.cell.startswith("mem:")
    rows = conn.execute("SELECT cell, layer, year, values::text FROM sat_cache WHERE cell = %s", (cell,)).fetchall()
    assert rows and all(r[0] == cell for r in rows)
    blob = " ".join(r[3] for r in rows)
    assert not any(d in blob for d in pin_digits) and "mem:" not in blob and "coordinates" not in blob
    assert conn.execute("SELECT count(*) FROM sat_cache WHERE cell LIKE 'mem:%%'").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM sat_cache").fetchone()[0] == before + len(rows)   # the plot wrote nothing
    assert not conn.execute("SELECT to_regclass('plot_outline_cache')").fetchone()[0]           # the table is gone
    assert not any(d in caplog.text for d in pin_digits) and cell not in caplog.text
    cols = {r[0] for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'sat_cache'")}
    assert not cols & {"user_key", "user", "sender", "phone"}
    conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
    conn.commit()


def test_map_captions_and_the_trace_carry_no_coordinates() -> None:
    from app.agent.trace import record, redact
    from app.place.images import T
    assert all("{lat" not in v and "{lon" not in v for lang in T.values() for v in lang.values() if isinstance(v, str))
    assert "13.0589" not in redact("my farm at 13.0589127, 5.1673341 in Wamakko")


# --- finding 19: the store backup -------------------------------------------------------------------------------------

def test_the_store_backup_is_a_consistent_copy_and_old_copies_are_pruned(tmp_path: Path) -> None:
    store = UserStore(str(tmp_path / "state.db"))
    key = "k1"
    store.create(key, "ha")
    store.give_consent(key)
    store.subscribe(key, ["NG034006"], ["heat"], "ha")
    old = tmp_path / "backups" / "kasafi-db-20260901T000000Z.sqlite"
    old.parent.mkdir()
    old.write_bytes(b"old")
    out = store.backup_to(str(tmp_path / "backups"), now=NOW)
    assert out.exists() and out.name == "kasafi-db-20261101T120000Z.sqlite" and not old.exists()
    copy = sqlite3.connect(str(out))
    assert copy.execute("SELECT count(*) FROM users").fetchone()[0] == 1
    assert copy.execute("SELECT count(*) FROM alert_subs").fetchone()[0] == 1
    copy.close()


def test_the_daily_backup_runs_once_a_day_when_a_folder_is_set(tmp_path: Path, monkeypatch) -> None:
    from app import maintenance as fetch
    store = UserStore(":memory:")
    monkeypatch.setattr("app.users.get_store", lambda: store)
    fetch._backup_day.clear()
    assert fetch.daily_store_backup(make_settings(), "2026-11-01") is False                  # no folder: off
    s = make_settings(kasafi_backup_dir=str(tmp_path / "b"))
    assert fetch.daily_store_backup(s, "2026-11-01") is True
    assert fetch.daily_store_backup(s, "2026-11-01") is False and fetch.daily_store_backup(s, "2026-11-02") is True
    assert len(list((tmp_path / "b").glob("kasafi-db-*.sqlite"))) == 2
    fetch._backup_day.clear()


def test_the_daily_backup_runs_with_hazard_fetching_off(tmp_path: Path, monkeypatch) -> None:
    """Follow-up review §5.1: the backup lived in the hazard loop, which never starts without hazard fetching."""
    import time as _time

    from app import maintenance
    from app.hazards.fetch import start_scheduler
    store = UserStore(":memory:")
    monkeypatch.setattr("app.users.get_store", lambda: store)
    maintenance._backup_day.clear()
    maintenance._started.clear()
    s = make_settings(kasafi_backup_dir=str(tmp_path / "b"), kasafi_hazard_fetch=False)
    start_scheduler(s)                                   # off: hazard fetching is off
    assert maintenance.start_maintenance(make_settings()) is None          # no folder: nothing to maintain
    th = maintenance.start_maintenance(s, every_s=0.05)
    assert th is not None and th.is_alive() and th.name == "maintenance"
    deadline = _time.monotonic() + 3
    while not list((tmp_path / "b").glob("kasafi-db-*.sqlite")) and _time.monotonic() < deadline:
        _time.sleep(0.02)
    assert len(list((tmp_path / "b").glob("kasafi-db-*.sqlite"))) == 1   # once a day, though checked often
    _time.sleep(0.2)
    assert len(list((tmp_path / "b").glob("kasafi-db-*.sqlite"))) == 1
    assert maintenance.start_maintenance(s) is th        # started once per process
    maintenance._started.clear()
    maintenance._backup_day.clear()
