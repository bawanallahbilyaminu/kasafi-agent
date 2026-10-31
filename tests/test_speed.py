"""The speed round (Nov 1): searches off the event loop on pooled connections, the keyword and vector searches
side by side, crops rendered during the checks, the code-written entity/level/period check on every answer and
the model-based parts check only for multi-part questions, and a redo that re-reads or searches for the missing
part only. Nothing here may change an answer: only when work happens."""

import asyncio
import threading

from app.retrieval import pool
from tests.helpers import make_settings


def test_without_a_database_the_pool_runs_in_the_calling_thread() -> None:
    s = make_settings()                                   # no database_url: has_database is False
    here = threading.current_thread().name
    got = asyncio.run(pool.run(s, lambda conn, x: (conn, x, threading.current_thread().name), "CONN", 7))
    assert got == ("CONN", 7, here)
    assert pool.run_sync(s, lambda conn, x: x * 2, None, 4).result() == 8


def test_a_pool_that_cannot_open_turns_itself_off_and_stays_off(monkeypatch) -> None:
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")      # nothing listens there
    monkeypatch.setattr(pool, "_pool", None)
    monkeypatch.setattr(pool, "_off", False)
    monkeypatch.setattr(pool, "POOL_MAX", 1)
    monkeypatch.setattr(pool, "POOL_TIMEOUT", 1.0)
    assert asyncio.run(pool.run(s, lambda conn: conn, "C")) == "C"           # falls back to the caller's conn
    assert pool._off and not pool.available(s)                               # and stays off
    pool.close()
