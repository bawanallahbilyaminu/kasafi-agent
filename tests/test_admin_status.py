"""The admin status page (step 7): counters in the store, place-history paths in the trace, and the page's data
against the dev database (skipped without it)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.agent.answer import Answer
from app.agent.trace import path
from app.users import UserStore
from tests.helpers import make_settings

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def test_event_counts_per_day_without_keys() -> None:
    store = UserStore(":memory:")
    store.count_event("emergency_fast_path", NOW)
    store.count_event("emergency_fast_path", NOW)
    store.count_event("emergency_fast_path", NOW - timedelta(days=2))
    store.count_event("emergency_fast_path", NOW - timedelta(days=30))
    assert store.event_counts("emergency_fast_path", 7, NOW) == {"2026-10-30": 1, "2026-11-01": 2}
    cols = {r[1] for r in store._db.execute("PRAGMA table_info(events)")}
    assert cols == {"day", "kind", "n"}


def test_alert_status_counts() -> None:
    store = UserStore(":memory:")
    store.log_alert("heat", "NG034006", "k1", False, "dry_run", 2, now=NOW)
    store.log_alert("heat", "NG034006", "k2", False, "failed", 0, now=NOW, failed=["u1"])
    store.log_alert("heat", "NG034006", "k3", False, "sent", 1, now=NOW - timedelta(days=10))
    assert store.alert_status_counts(7, NOW) == {"dry_run": 1, "failed": 1}


def test_place_answers_are_traced_as_first_cached_or_area() -> None:
    a = Answer("x", True, True, timings={"plan": 1.0, "place": 45.0, "place_first": 1.0})
    assert path(a) == "place:first"
    a.timings["place_first"] = 0.0
    assert path(a) == "place:cached"
    assert path(Answer("x", True, True, timings={"place_area": 0.2})) == "place_area"
    assert path(Answer("x", True, True)) == "search"


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


def test_status_data_from_the_database(dev_conn) -> None:
    from app.admin import status_data
    store = UserStore(":memory:")
    store.count_event("emergency_fast_path")
    d = status_data(dev_conn, store, make_settings())
    assert {"layers", "advisories", "alerts", "emergency", "place", "failures", "commit"} <= set(d)
    assert set(d["place"]) == {"first", "cached", "area", "failed"} and sum(d["emergency"].values()) == 1
    for x in d["layers"]:
        assert x["age"] == "never" or x["age"].split()[1] in ("min", "h", "days")
