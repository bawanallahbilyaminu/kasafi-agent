"""Searches off the event loop: a small pool of database connections and worker threads.

The searches (keyword and vector SQL, the local embedding model) are synchronous. Run on the event loop they stall
every conversation on the server while one user's search runs, and a question's line and page searches can't
overlap. `run(fn, conn, *args)` runs `fn(pooled_conn, *args)` in a worker thread with a connection of its own, so
searches overlap each other and other users' turns. Without a pool (no database in tests, or the pool can't
open) it runs `fn(conn, *args)` in the calling thread, unchanged.

Sized for a few concurrent users: POOL_MAX connections and the same number of threads (each search holds one of
each). A database on the same host opens a connection in a few ms, so the pool starts empty and grows.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

log = logging.getLogger(__name__)
POOL_MIN, POOL_MAX = 0, 6
POOL_TIMEOUT = 10.0                       # seconds to wait for a pooled connection before giving up
_pool = None
_executor: ThreadPoolExecutor | None = None
_lock = threading.Lock()
_off = False                               # the pool couldn't open: stay off for the process


def _open(db_url: str):
    global _pool, _executor, _off
    with _lock:
        if _pool is not None or _off:
            return _pool
        try:
            from psycopg_pool import ConnectionPool
            _pool = ConnectionPool(db_url, min_size=POOL_MIN, max_size=POOL_MAX, open=True, timeout=POOL_TIMEOUT,
                                   kwargs={"connect_timeout": 5}, name="kasafi-search")
            _executor = ThreadPoolExecutor(max_workers=POOL_MAX, thread_name_prefix="search")
            log.info("search pool open: up to %d connections", POOL_MAX)
        except Exception as e:                  # noqa: BLE001 - never take search down with the pool
            log.warning("search pool unavailable (%s): searches run on the event loop", type(e).__name__)
            _off = True
        return _pool


def available(settings) -> bool:
    url = getattr(settings, "db_url", None)
    return not _off and bool(url) and getattr(settings, "has_database", False) and _open(url()) is not None


async def run(settings, fn: Callable[..., Any], conn, /, *args, **kw) -> Any:
    """`fn(conn, *args, **kw)` in a worker thread on a pooled connection; in the calling thread on `conn` when
    there is no pool."""
    if not available(settings):
        return fn(conn, *args, **kw)

    def work():
        with _pool.connection() as c:
            return fn(c, *args, **kw)
    try:
        return await asyncio.get_running_loop().run_in_executor(_executor, work)
    except Exception as e:                      # noqa: BLE001 - a pool failure never costs the answer
        if not _pool_error(e):
            raise
        return fn(conn, *args, **kw)


def run_sync(settings, fn: Callable[..., Any], conn, /, *args, **kw):
    """Like `run`, for a caller that is itself in a worker thread: a future to wait on (or the result at once when
    there is no pool), so two synchronous searches can overlap."""
    if not available(settings):
        return _Done(fn(conn, *args, **kw))

    def work():
        try:
            with _pool.connection() as c:
                return fn(c, *args, **kw)
        except Exception as e:                  # noqa: BLE001 - a pool failure never costs the answer
            if not _pool_error(e):
                raise
            return fn(conn, *args, **kw)
    return _executor.submit(work)


def _pool_error(e: Exception) -> bool:
    """A failure to get a pooled connection (the database refusing, a timeout): the pool is switched off for the
    process and the search runs on the caller's own connection."""
    global _off
    import psycopg
    from psycopg_pool import PoolTimeout
    if isinstance(e, (PoolTimeout, psycopg.OperationalError)):
        log.warning("search pool failed (%s): searches run on the event loop from now on", type(e).__name__)
        _off = True
        return True
    return False


class _Done:
    def __init__(self, value):
        self._v = value

    def result(self, timeout=None):
        return self._v


def close() -> None:
    global _pool, _executor
    with _lock:
        if _pool is not None:
            _pool.close()
            _pool = None
        if _executor is not None:
            _executor.shutdown(wait=False)
            _executor = None
