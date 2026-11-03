"""The Meta credit guard (app/spend.py, app/providers/meta.py): calls priced into a ledger, the balance read on the
dashboard minus what was spent since, the switch to Muse Spark Open below the threshold or on a 402, voice kept on
Meta, and the admin banner."""

import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app import spend
from app.providers.chat import ChatResult
from app.providers.meta import MetaClient
from tests.helpers import make_settings


class FakeConn:
    """Just enough of a psycopg connection for the guard's queries."""

    def __init__(self, reading=None, spent=0.0):
        self.reading, self.spent, self.inserted = reading, spent, []

    def execute(self, sql, params=()):
        class R:
            def __init__(self, row):
                self.row = row

            def fetchone(self):
                return self.row
        if sql.startswith("INSERT INTO model_spend"):
            self.inserted.append(params)
            if params[1] == "Meta":
                self.spent += float(params[6])
            return R(None)
        if "FROM meta_credit_readings" in sql:
            return R(self.reading)
        if "FROM model_spend" in sql:
            return R((self.spent,))
        return R(None)

    def commit(self):
        pass

    def rollback(self):
        pass


@pytest.fixture(autouse=True)
def fresh_state():
    spend.state = spend.State()
    spend._pending.clear()
    yield
    spend.state = spend.State()
    spend._pending.clear()


def test_a_call_is_priced_into_the_ledger_and_taken_off_the_reading() -> None:
    s = make_settings()
    spend.add("Meta", {"prompt_tokens": 1_000_000, "completion_tokens": 0}, s)     # $1.25 at the Meta price
    conn = FakeConn(reading=(12.0, datetime.now(timezone.utc) - timedelta(hours=2)))
    st = spend.compute(conn, s)
    assert conn.inserted and st.configured and abs(st.spent_usd - 1.25) < 1e-6
    assert abs(st.remaining_usd - 10.75) < 1e-6 and not st.low
    spend.add("Meta", {"prompt_tokens": 1_000_000}, s)
    assert spend.compute(conn, s).low                                               # $9.50 left: under $10


def test_no_reading_no_guard_and_the_settings_reading_counts() -> None:
    assert not spend.compute(FakeConn(), make_settings()).configured
    s = make_settings(kasafi_meta_credit_usd=8.0, kasafi_meta_credit_as_of="2026-11-03T10:00:00Z")
    st = spend.compute(FakeConn(), s)
    assert st.configured and st.low and st.balance_usd == 8.0


def test_a_402_switches_at_once() -> None:
    spend.billing_refused(make_settings())
    assert spend.state.low and spend.state.exhausted and spend.state.since


class FakeOpen:
    def __init__(self):
        self.calls = 0

    async def chat(self, messages, model=None, **kw):
        self.calls += 1
        return ChatResult(content="from open", model="open", finish_reason="stop", reasoning="", usage={}, raw={})

    async def aclose(self):
        pass


def _meta(status: int = 200):
    hits = []

    def handler(request):
        hits.append(request)
        if status != 200:
            return httpx.Response(status, json={"error": {"type": "billing_error", "message": "no balance"}})
        return httpx.Response(200, json={"choices": [{"message": {"content": "from meta"}, "finish_reason": "stop"}],
                                         "usage": {}})
    client = MetaClient(make_settings(), transport=httpx.MockTransport(handler), max_retries=0)
    return client, hits


def test_low_credit_sends_text_to_open_and_keeps_voice_on_meta() -> None:
    client, hits = _meta()
    client._open = FakeOpen()
    spend.state.low, spend.state.exhausted = True, True        # e.g. a 402 earlier
    r = asyncio.run(client.chat([{"role": "user", "content": "hi"}]))
    assert r.content == "from open" and not hits
    audio = [{"role": "user", "content": [{"type": "input_audio", "input_audio": {"data": "x", "format": "wav"}}]}]
    assert asyncio.run(client.chat(audio)).content == "from meta" and len(hits) == 1


def test_a_402_from_meta_is_answered_by_open() -> None:
    client, hits = _meta(402)
    client._open = FakeOpen()
    r = asyncio.run(client.chat([{"role": "user", "content": "hi"}]))
    assert r.content == "from open" and hits and spend.state.exhausted


def test_credit_fine_meta_answers() -> None:
    client, hits = _meta()
    client._open = FakeOpen()
    assert asyncio.run(client.chat([{"role": "user", "content": "hi"}])).content == "from meta"


def test_every_admin_page_says_when_the_credit_is_low() -> None:
    from app.admin import page
    spend.state.low, spend.state.remaining_usd, spend.state.since = True, 9.4, "2026-11-05T10:00+00:00"
    html = page("Traces", "<p>x</p>").body.decode()
    assert "Meta credit low" in html and "$9.40" in html and "Muse Spark Open" in html
    spend.state.low = False
    assert "Meta credit low" not in page("Traces", "<p>x</p>").body.decode()
