"""The advisories crawl's schedule (text daily at 06:00, NCDC Mondays at 07:00, Sokoto time) and its $2 monthly
cap on model spend (app/hazards/advisories.py run_due)."""

import asyncio
from datetime import datetime, timedelta, timezone

from app import usage
from app.hazards import advisories as adv
from tests.helpers import make_settings

LAGOS = timezone(timedelta(hours=1))
FRI = datetime(2026, 10, 30, 12, 0, tzinfo=LAGOS)             # a Friday


def test_slots() -> None:
    assert adv.last_slot("advisories", FRI) == datetime(2026, 10, 30, 6, 0, tzinfo=LAGOS)
    assert adv.last_slot("advisories", FRI.replace(hour=5)) == datetime(2026, 10, 29, 6, 0, tzinfo=LAGOS)
    assert adv.last_slot("ncdc", FRI) == datetime(2026, 10, 26, 7, 0, tzinfo=LAGOS)          # Monday
    monday_early = datetime(2026, 11, 2, 6, 30, tzinfo=LAGOS)
    assert adv.last_slot("ncdc", monday_early) == datetime(2026, 10, 26, 7, 0, tzinfo=LAGOS)


class Conn:
    def __init__(self, last_ok=None, spent=0.0):
        self.last_ok, self.spent, self.log = last_ok, spent, []

    def execute(self, sql, args=()):
        if sql.startswith("SELECT max(started_at)"):
            rows = [(self.last_ok.get(args[0]) if self.last_ok else None,)]
        elif "sum(usd)" in sql:
            rows = [(self.spent,)]
        else:
            if sql.startswith("INSERT INTO hazard_fetch"):
                self.log.append(args)
            rows = []
        return type("R", (), {"fetchone": lambda _: rows[0] if rows else None, "fetchall": lambda _: rows})()

    def rollback(self):
        pass


def _patch(monkeypatch, per_report=0.03):
    ran = {"advisories": 0, "ncdc": 0}

    async def wp(conn, http):
        ran["advisories"] += 1
        return 2

    async def ncdc(conn, http, client, settings, can_spend=lambda: True):
        n = 0
        for _ in range(10):                          # ten unread reports, each a few model calls
            if not can_spend():
                break
            usage.record_chat("Meta", {"prompt_tokens": 0, "completion_tokens": 0})
            usage.by_account["Meta/crawl_ncdc"].completion += int(per_report * 1e6 / 6.0)   # ~ $per_report
            n += 1
        ran["ncdc"] += 1
        return n

    class Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False
    monkeypatch.setattr(adv, "crawl_wordpress", wp)
    monkeypatch.setattr(adv, "crawl_ncdc", ncdc)
    monkeypatch.setattr("app.providers.meta.MetaClient", Client)
    return ran


def _settings(**kw):
    return make_settings(kasafi_price_meta_in=0.0, kasafi_price_meta_cached=0.0, kasafi_price_meta_out=6.0, **kw)


def test_each_crawl_runs_once_per_slot(monkeypatch) -> None:
    ran = _patch(monkeypatch)
    done = {"advisories": datetime(2026, 10, 30, 6, 5, tzinfo=LAGOS), "ncdc": datetime(2026, 10, 26, 7, 5, tzinfo=LAGOS)}
    asyncio.run(adv.run_due(Conn(done), _settings(), FRI))
    assert ran == {"advisories": 0, "ncdc": 0}                      # both already ran since their slots
    done["advisories"] = datetime(2026, 10, 29, 6, 5, tzinfo=LAGOS)  # yesterday's: today's 06:00 is due
    asyncio.run(adv.run_due(Conn(done), _settings(), FRI))
    assert ran == {"advisories": 1, "ncdc": 0}


def test_the_monthly_cap_stops_the_ncdc_crawl(monkeypatch) -> None:
    ran = _patch(monkeypatch, per_report=0.03)
    conn = Conn(spent=1.95)                                         # $1.95 of $2 already spent this month
    asyncio.run(adv.run_due(conn, _settings(), FRI))
    ncdc = [a for a in conn.log if a[0] == "ncdc"][0]
    assert ncdc[2] is True and ncdc[3] == 2 and 0.05 <= float(ncdc[6]) < 0.1     # stopped after 2 reports
    ran["ncdc"] = 0
    asyncio.run(adv.run_due(Conn(spent=2.0), _settings(), FRI))
    assert ran["ncdc"] == 0                                         # spent: not started at all
    assert ran["advisories"] == 2                                   # the free text crawl still runs
