"""The Meta credit guard (3 Nov 2026): about $40 of Meta credit must last through judging (4-8 Nov).

The Meta Model API has no endpoint or header for the remaining credit (dev.meta.ai docs, read 3 Nov: usage and
billing are only on the dashboard; a 402 'billing_error' comes only once the balance is gone). So the balance is
read on dev.meta.ai/usage by a person and recorded (KASAFI_META_CREDIT_USD and _AS_OF, or the admin status page),
and Kasafi takes off what its own Meta calls have cost since then: every call's tokens are priced
(kasafi_price_meta_*) and kept per hour in `model_spend` (migration 0031), across restarts.

Below kasafi_meta_credit_low_usd (default $10), every Muse Spark text call goes to Muse Spark Open instead
(Baseten, then Fireworks; app/providers/meta.py), a warning is logged once, and every admin page says so. A 402 from
Meta switches at once, whatever the estimate. Voice (audio) stays on Meta: Muse Spark Open takes no audio.

The estimate counts only this server's calls: Meta calls made elsewhere with the same key (evals on a laptop) aren't
in it, so the balance should be read again from the dashboard now and then (the status page shows its age).
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

log = logging.getLogger(__name__)

REFRESH_S = 60.0
_lock = threading.Lock()
_pending: dict[tuple[datetime, str], list[float]] = {}     # (hour, provider) -> [calls, prompt, cached, completion, usd]


@dataclass
class State:
    configured: bool = False          # a balance has been recorded (else no guard)
    balance_usd: float = 0.0          # the last reading
    as_of: datetime | None = None
    spent_usd: float = 0.0            # Meta spend recorded since the reading
    remaining_usd: float | None = None
    low: bool = False                 # under the threshold: Muse Spark calls go to Muse Spark Open
    exhausted: bool = False           # Meta said 402 (no balance): switched whatever the estimate
    checked: float = 0.0              # time.monotonic() of the last refresh
    since: str = ""                   # when the switch happened (UTC, ISO)
    error: str = ""
    notes: list[str] = field(default_factory=list)


state = State()


def _hour(now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now.replace(minute=0, second=0, microsecond=0)


def add(provider: str, usage: dict, settings=None) -> None:
    """One call's tokens, priced, waiting to be written (flush)."""
    from app import usage as U
    if settings is None:
        from app.config import get_settings
        settings = get_settings()
    p = U.prices(settings).get(provider)
    t = U.Tokens()
    t.add(usage or {})
    usd = U.dollars(t, *p) if p else 0.0
    with _lock:
        row = _pending.setdefault((_hour(), provider), [0, 0, 0, 0, 0.0])
        for i, v in enumerate((t.calls, t.prompt, t.cached, t.completion, usd)):
            row[i] += v


def flush(conn) -> int:
    """Write the waiting spend to `model_spend`; the rows written (0 when none or no table yet)."""
    with _lock:
        rows = list(_pending.items())
        _pending.clear()
    if not rows:
        return 0
    try:
        for (hour, provider), (calls, prompt, cached, completion, usd) in rows:
            conn.execute(
                "INSERT INTO model_spend (hour, provider, calls, prompt_tokens, cached_tokens, completion_tokens, usd) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (hour, provider) DO UPDATE SET "
                "calls = model_spend.calls + EXCLUDED.calls, prompt_tokens = model_spend.prompt_tokens + "
                "EXCLUDED.prompt_tokens, cached_tokens = model_spend.cached_tokens + EXCLUDED.cached_tokens, "
                "completion_tokens = model_spend.completion_tokens + EXCLUDED.completion_tokens, "
                "usd = model_spend.usd + EXCLUDED.usd",
                (hour, provider, int(calls), int(prompt), int(cached), int(completion), usd))
        conn.commit()
        return len(rows)
    except Exception as e:              # noqa: BLE001 - kept for the next flush (e.g. before migration 0031)
        log.info("spend not written yet (%s)", type(e).__name__)
        try:
            conn.rollback()
        except Exception:               # noqa: BLE001
            pass
        with _lock:
            for key, vals in rows:
                row = _pending.setdefault(key, [0, 0, 0, 0, 0.0])
                for i, v in enumerate(vals):
                    row[i] += v
        return 0


def reading(conn, settings) -> tuple[float, datetime] | None:
    """The newest balance reading: the admin page's, else the settings'; None when neither is set."""
    got = None
    try:
        got = conn.execute("SELECT usd, as_of FROM meta_credit_readings ORDER BY as_of DESC, id DESC LIMIT 1").fetchone()
    except Exception:                   # noqa: BLE001 - no table yet: the settings
        conn.rollback()
    cfg = None
    if settings.kasafi_meta_credit_usd > 0 and settings.kasafi_meta_credit_as_of:
        try:
            when = datetime.fromisoformat(settings.kasafi_meta_credit_as_of.replace("Z", "+00:00"))
            cfg = (float(settings.kasafi_meta_credit_usd), when if when.tzinfo else when.replace(tzinfo=timezone.utc))
        except ValueError:
            log.warning("KASAFI_META_CREDIT_AS_OF is not an ISO date-time: guard off")
    if got and (cfg is None or got[1] >= cfg[1]):
        return float(got[0]), got[1]
    return cfg


def record_reading(conn, usd: float, as_of: datetime) -> None:
    conn.execute("INSERT INTO meta_credit_readings (usd, as_of) VALUES (%s, %s)", (usd, as_of))
    conn.commit()


def compute(conn, settings) -> State:
    """The guard's state now: flush, then the reading minus the Meta spend recorded since it."""
    flush(conn)
    s = State(exhausted=state.exhausted, since=state.since)
    r = reading(conn, settings)
    if r is None:
        s.low = s.exhausted
        return s
    s.configured, (s.balance_usd, s.as_of) = True, r
    try:
        spent = conn.execute("SELECT coalesce(sum(usd), 0) FROM model_spend WHERE provider = 'Meta' AND "
                             "hour >= date_trunc('hour', %s::timestamptz)", (s.as_of,)).fetchone()[0]
    except Exception as e:              # noqa: BLE001
        conn.rollback()
        spent, s.error = 0, type(e).__name__
    with _lock:                         # what isn't written yet counts too
        spent = float(spent) + sum(v[4] for (h, p), v in _pending.items() if p == "Meta" and h >= _hour(s.as_of))
    s.spent_usd = spent
    s.remaining_usd = s.balance_usd - spent
    s.low = s.exhausted or s.remaining_usd < settings.kasafi_meta_credit_low_usd
    return s


def refresh(settings, conn=None) -> State:
    """Recompute the state (its own connection when none is given) and warn once when it turns low."""
    global state
    try:
        if conn is None:
            import psycopg
            with psycopg.connect(settings.db_url(), connect_timeout=5) as c:
                new = compute(c, settings)
        else:
            new = compute(conn, settings)
    except Exception as e:              # noqa: BLE001 - no database (tests, dev without one): the old state stands
        state.checked = time.monotonic()
        state.error = type(e).__name__
        return state
    new.checked = time.monotonic()
    if new.low and not state.low:
        new.since = datetime.now(timezone.utc).isoformat(timespec="minutes")
        log.warning("META CREDIT LOW: about $%.2f left (reading $%.2f at %s, $%.2f spent since)%s: Muse Spark calls "
                    "now go to Muse Spark Open (Baseten, then Fireworks)", new.remaining_usd or 0, new.balance_usd,
                    new.as_of, new.spent_usd, " - Meta returned 402" if new.exhausted else "")
    elif state.low and not new.low:
        log.warning("Meta credit guard: back on Muse Spark (about $%.2f left)", new.remaining_usd or 0)
        new.since = ""
    state = new
    return state


def billing_refused(settings) -> None:
    """Meta answered 402 (no balance or payment): switch now, and say so."""
    global state
    if not state.exhausted:
        state.exhausted, state.low = True, True
        state.since = datetime.now(timezone.utc).isoformat(timespec="minutes")
        log.warning("META CREDIT LOW: Meta returned 402 (billing): Muse Spark calls now go to Muse Spark Open")
