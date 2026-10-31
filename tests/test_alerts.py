"""Hazard alerts (hazard step 6): sign-up and its explicit OK, the menu, STOP / DAINA, the triggers, the limits
(one per hazard per LGA per day, quiet hours, the daily cap), template languages, the dry run and the admin page."""

import asyncio
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.alerts import dispatch as dp
from app.alerts import recipients, signup, triggers
from app.alerts.triggers import Candidate
from app.config import get_settings
from app.data_rights import delete_user_data
from app.hazards import read
from app.main import app
from app.users import UserStore, user_key
from app.whatsapp import conversation as conv
from tests.helpers import make_settings

GORONYO, WAMAKKO, WURNO = "NG034006", "NG034021", "NG034022"
LAGOS = timezone(timedelta(hours=1))
NOON = datetime(2026, 11, 2, 12, 0, tzinfo=LAGOS)


def _store(lang="ha"):
    store = UserStore(":memory:")
    store.create("k", lang)
    store.give_consent("k")
    return store


# --- sign-up --------------------------------------------------------------------------------------------------

def test_a_hausa_sign_up_message_asks_for_an_explicit_ok_before_storing_anything() -> None:
    store = _store()
    step = signup.reply("Sanar da ni game da ambaliya a Goronyo", None, "k", "ha", store)
    text, buttons = step.messages[0]
    assert "ambaliya a Ƙaramar Hukumar Goronyo" in text and "DAINA" in text and "ba lambar kanta ba" in text
    assert [b[0] for b in buttons] == ["alert_yes", "alert_no", "alert_ask"]
    assert all(len(title) <= 20 for _, title in buttons)
    assert store.subscription("k") is None                                     # nothing until the OK
    done = signup.reply("", "alert_yes", "k", "ha", store)
    assert "An yi maka rajistar" in done.messages[0][0]
    assert store.subscription("k") == {"lgas": [GORONYO], "hazards": ["flood"], "lang": "ha"}


def test_the_subscription_keeps_the_key_lgas_hazards_language_dates_and_the_number_encrypted() -> None:
    store = _store("en")
    s = make_settings(kasafi_alerts_number_key=SecretStr(KEY))
    signup.reply("alert me about heat in Wamakko", None, "k", "en", store)
    signup.reply("yes", None, "k", "en", store, seal=lambda: recipients.encrypt("+234 800 000 0011", s))
    cols = [r[1] for r in store._db.execute("PRAGMA table_info(alert_subs)")]
    assert cols == ["user_key", "lgas", "hazards", "lang", "created_at", "number_enc", "last_contact_at"]
    assert store.subscription("k") == {"lgas": [WAMAKKO], "hazards": ["heat"], "lang": "en"}
    raw = store._db.execute("SELECT number_enc FROM alert_subs").fetchone()[0]
    assert "8000000011" not in raw and recipients.decrypt(raw, s) == "2348000000011"


KEY = "q0Hc3cbjUu0e8VtZJ0d6Dl5c4b1Jt8m2bS0XcN2lq3Y="


def test_no_key_no_number_and_a_wrong_key_reads_nothing() -> None:
    assert recipients.encrypt("2348000000011", make_settings()) is None
    token = recipients.encrypt("2348000000011", make_settings(kasafi_alerts_number_key=SecretStr(KEY)))
    other = "Zm9vYmFyYmF6cXV4cXV1eHF1dXhxdXV4cXV1eHF1dXg="
    assert recipients.decrypt(token, make_settings(kasafi_alerts_number_key=SecretStr(other))) is None


def test_the_number_goes_with_stop_delete_and_90_days_without_contact() -> None:
    s = make_settings(kasafi_alerts_number_key=SecretStr(KEY))
    store = UserStore(":memory:")
    for k in ("a", "b", "c"):
        store.create(k, "en")
        store.subscribe(k, [GORONYO], ["flood"], "en", recipients.encrypt("2348000000011", s))
    signup.reply("STOP", None, "a", "en", store)
    store.delete("b")                                                          # DELETE MY DATA
    assert store.alert_number("a") is None and store.alert_number("b") is None and store.alert_number("c")
    later = datetime.now(timezone.utc) + timedelta(days=91)
    store.touch_alert_contact("c")
    assert store.prune_alert_subs(90, later) == 1 and store.alert_number("c") is None


def test_a_message_keeps_the_sign_up_alive() -> None:
    store = UserStore(":memory:")
    store.subscribe("k", [GORONYO], ["flood"], "en")
    store._db.execute("UPDATE alert_subs SET last_contact_at='2026-01-01T00:00:00+00:00'")
    store.touch_alert_contact("k")
    assert store.prune_alert_subs(90) == 0


def test_live_sends_decrypt_the_number_and_never_log_it(caplog) -> None:
    import logging
    caplog.set_level(logging.DEBUG)
    s = make_settings(kasafi_alerts_number_key=SecretStr(KEY))
    store = UserStore(":memory:")
    store.subscribe("u0", [GORONYO], ["heat"], "ha", recipients.encrypt("2348000000011", s))
    store.subscribe("u1", [GORONYO], ["heat"], "ha")                           # signed up before a key was set

    class WA:
        sent = []

        async def send_template(self, to, name, lang, values):
            self.sent.append((to, name, lang))
    wa = WA()
    send = recipients.live_sender(store, s, wa)
    s2 = make_settings(kasafi_alerts_dry_run=False, kasafi_alerts_daily_cap=10,
                       kasafi_alerts_number_key=SecretStr(KEY))
    out = asyncio.run(dp.dispatch([_cand()], store, s2, NOON, send))
    assert out == {"sent": 1} and wa.sent == [("2348000000011", "kasafi_hazard_alert", "ha")]
    row = store.alert_log()[0]
    assert row["recipients"] == 1 and "1 not delivered" in row["note"]
    assert "8000000011" not in caplog.text and "8000000011" not in str(store.alert_log())


def test_a_missing_lga_comes_from_the_one_on_file_or_is_asked_for() -> None:
    store = _store("en")
    step = signup.reply("Alert me about dust", None, "k", "en", store, on_file=WURNO)
    assert "harmattan dust in Wurno LGA" in step.messages[0][0]
    store.set_pending_alert("k", None)
    ask = signup.reply("Alert me about dust", None, "k", "en", store)
    assert "Which LGA" in ask.messages[0][0]
    step = signup.reply("Goronyo and Wurno", None, "k", "en", store)
    assert "harmattan dust in Goronyo and Wurno LGAs" in step.messages[0][0]


def test_the_menu_takes_numbers_and_names_in_one_reply() -> None:
    store = _store("en")
    menu = signup.reply("ALERTS", None, "k", "en", store)
    assert "1 Heat" in menu.messages[0][0] and "5 All four" in menu.messages[0][0]
    step = signup.reply("1 3 Goronyo", None, "k", "en", store)
    assert "heat and floods in Goronyo LGA" in step.messages[0][0]
    signup.reply("", "alert_yes", "k", "en", store)
    assert store.subscription("k")["hazards"] == ["heat", "flood"]
    again = signup.reply("alerts", None, "k", "en", store)                       # shows what they have
    assert "You're signed up for heat and floods in Goronyo LGA" in again.messages[0][0]


def test_a_second_sign_up_adds_to_the_first() -> None:
    store = _store("en")
    store.subscribe("k", [GORONYO], ["flood"], "en")
    store.subscribe("k", [WURNO], ["heat"], "ha")
    assert store.subscription("k") == {"lgas": [GORONYO, WURNO], "hazards": ["heat", "flood"], "lang": "ha"}


def test_just_answer_now_answers_the_message_and_no_declines() -> None:
    store = _store()
    signup.reply("Sanar da ni game da ambaliya a Goronyo", None, "k", "ha", store)
    assert signup.reply("", "alert_ask", "k", "ha", store).ask == "Sanar da ni game da ambaliya a Goronyo"
    signup.reply("Sanar da ni game da ambaliya a Goronyo", None, "k", "ha", store)
    assert "babu faɗakarwa" in signup.reply("A'a", None, "k", "ha", store).messages[0][0]
    assert store.subscription("k") is None


@pytest.mark.parametrize("text", ["What's the heat like in Wamakko today?", "tell me if the budget for Goronyo rose",
                                  "Yaya zafin rana yake a Wamakko yau?", "alert levels in the 2026 budget"])
def test_questions_are_not_sign_ups(text) -> None:
    assert signup.reply(text, None, "k", "en", _store()) is None


@pytest.mark.parametrize("word", ["STOP", "Daina", "daina!"])
def test_stop_deletes_the_subscription(word) -> None:
    store = _store()
    store.subscribe("k", [GORONYO], ["flood"], "ha")
    assert "An gama" in signup.reply(word, None, "k", "ha", store).messages[0][0]
    assert store.subscription("k") is None
    assert "Ba ka da faɗakarwa" in signup.reply(word, None, "k", "ha", store).messages[0][0]


def test_delete_my_data_removes_the_subscription_too() -> None:
    s = make_settings()
    store = UserStore(":memory:")
    key = user_key("2348000000077", s)
    store.create(key, "en")
    store.subscribe(key, [GORONYO], ["flood"], "en")
    delete_user_data("2348000000077", store=store, settings=s)
    assert store.subscription(key) is None


def test_sign_up_and_stop_through_the_conversation_and_the_template_button() -> None:
    s = make_settings(kasafi_alerts=True)
    store = UserStore(":memory:")
    key = user_key("2348000000088", s)
    store.create(key, "en")
    store.give_consent(key)

    def send(msg):
        return asyncio.run(conv.handle({"from": "2348000000088", "id": "w", **msg}, None, store=store, settings=s,
                                       answer_fn=None))
    out = send({"type": "text", "text": {"body": "Alert me about floods in Goronyo"}})
    assert out[0].buttons and "floods in Goronyo LGA" in out[0].text
    send({"type": "interactive", "interactive": {"type": "button_reply", "button_reply": {"id": "alert_yes"}}})
    assert store.subscription(key)["hazards"] == ["flood"]
    out = send({"type": "button", "button": {"text": "STOP", "payload": "STOP"}})          # the template's button
    assert "won't receive Kasafi alerts" in out[0].text and store.subscription(key) is None


def test_with_alerts_off_a_sign_up_message_is_an_ordinary_question() -> None:
    s = make_settings()
    store = UserStore(":memory:")
    key = user_key("2348000000099", s)
    store.create(key, "en")
    store.give_consent(key)
    out = asyncio.run(conv.handle({"from": "2348000000099", "id": "w", "type": "text",
                                   "text": {"body": "Alert me about floods in Goronyo"}}, None, store=store,
                                  settings=s, answer_fn=None))
    assert not out[0].buttons and store.get_pending_alert(key) is None


def test_more_asks_about_the_last_alert() -> None:
    store = _store("en")
    store.subscribe("k", [GORONYO], ["flood"], "en")
    assert signup.reply("MORE", None, "k", "en", store) is None                   # no alert yet: as usual
    store.log_alert("flood", GORONYO, "flood:x", False, "dry_run", 1)
    assert signup.reply("MORE", None, "k", "en", store).ask == "What is the floods situation in Goronyo LGA today?"


# --- dispatch: limits, quiet hours, cap, languages, dry run ---------------------------------------------------

def _cand(key="heat:NG034006:2026-11-02", hazard="heat", lga=GORONYO, official=False, what="up to 42 °C today."):
    return Candidate(hazard, lga, key, official, {"en": what, "ha": what + "\nna biyu"},
                     {"en": "Open-Meteo forecast, 02 Nov 2026 06:00.", "ha": "Hasashen Open-Meteo, 02 Nov 2026 06:00"})


def _run(store, cands, now=NOON, **kw):
    return asyncio.run(dp.dispatch(cands, store, make_settings(**kw), now))


def _subs(store, *pairs):
    for i, (lang, hazard) in enumerate(pairs):
        store.subscribe(f"u{i}", [GORONYO], [hazard], lang)


def test_the_dry_run_logs_the_template_values_and_sends_nothing() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"))
    sent = []

    async def send(k, lang, values):
        sent.append(k)
        return True
    out = asyncio.run(dp.dispatch([_cand()], store, make_settings(), NOON, send))
    assert out["dry_run"] == 1 and not sent
    row = store.alert_log()[0]
    assert row["status"] == "dry_run" and row["recipients"] == 1
    values = row["message"]["ha"]
    assert values[:2] == ["zafin rana", "Goronyo"]
    assert all("\n" not in v and not v.endswith(".") for v in values)                # one line, no full stop


def test_at_most_one_alert_per_hazard_per_lga_per_day_and_a_key_never_twice() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"))
    _run(store, [_cand(), _cand(key="heat:NG034006:2026-11-03")])
    assert len(store.alert_log()) == 1
    _run(store, [_cand()], now=NOON + timedelta(days=1))                               # the same key, next day
    assert len(store.alert_log()) == 1
    _run(store, [_cand(key="heat:NG034006:2026-11-03")], now=NOON + timedelta(days=1))
    assert len(store.alert_log()) == 2


def test_quiet_hours_hold_back_all_but_official_warnings_until_six() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"), ("ha", "flood"))
    night = datetime(2026, 11, 2, 23, 30, tzinfo=LAGOS)
    cands = [_cand(), _cand(key="adv:7", hazard="flood", official=True, what="NEMA flood alert issued 02 Nov 2026")]
    _run(store, cands, now=night)
    _run(store, cands, now=night + timedelta(minutes=10))
    statuses = sorted(r["status"] for r in store.alert_log())
    assert statuses == ["dry_run", "quiet"]                                           # held back once, logged once
    _run(store, cands, now=datetime(2026, 11, 3, 6, 5, tzinfo=LAGOS))
    assert [r["status"] for r in store.alert_log()][0] == "dry_run"                   # sent at 06:00


@pytest.mark.parametrize("hour,held", [(21, False), (22, True), (3, True), (5, True), (6, False)])
def test_the_quiet_window(hour, held) -> None:
    assert dp.quiet(datetime(2026, 11, 2, hour, 0, tzinfo=LAGOS)) is held


def test_the_daily_cap_counts_messages_across_alerts() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"), ("ha", "heat"), ("ha", "flood"))
    out = _run(store, [_cand(), _cand(key="flood:x", hazard="flood")], kasafi_alerts_daily_cap=2)
    assert out == {"dry_run": 1, "capped": 1}
    assert store.alerts_sent(NOON.date().isoformat()) == 2


def test_live_sending_without_a_cap_sends_nothing() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"))
    out = _run(store, [_cand()], kasafi_alerts_dry_run=False)
    assert out == {"capped": 1}


def test_a_language_whose_template_is_not_approved_is_skipped_and_logged() -> None:
    store = UserStore(":memory:")
    _subs(store, ("en", "heat"))
    assert _run(store, [_cand()]) == {"no_template": 1}
    store2 = UserStore(":memory:")
    _subs(store2, ("en", "heat"), ("ha", "heat"))
    _run(store2, [_cand()])
    row = store2.alert_log()[0]
    assert row["status"] == "dry_run" and row["recipients"] == 1 and "en (1)" in row["note"]
    assert _run(UserStore(":memory:"), [_cand()], kasafi_alert_template_langs="ha,en") == {}   # nobody signed up


def test_live_sends_each_recipient_in_their_language() -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"), ("en", "heat"))
    got = []

    async def send(k, lang, values):
        got.append((lang, values[0]))
        return True
    s = make_settings(kasafi_alerts_dry_run=False, kasafi_alerts_daily_cap=10, kasafi_alert_template_langs="ha,en")
    out = asyncio.run(dp.dispatch([_cand()], store, s, NOON, send))
    assert out == {"sent": 1} and sorted(got) == [("en", "heat"), ("ha", "zafin rana")]


# --- triggers ---------------------------------------------------------------------------------------------------

class Rows:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def __iter__(self):
        return iter(self.rows)


class FakeConn:
    """Answers by the first matching SQL fragment."""
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def execute(self, sql, args=()):
        self.calls.append((sql, args))
        for frag, rows in self.answers.items():
            if frag in sql:
                return Rows(rows(args) if callable(rows) else rows)
        return Rows([])


def _fresh(monkeypatch):
    monkeypatch.setattr(read, "freshness", lambda conn, layer, now=None: read.Freshness(layer, NOON, False, 1.0))


def test_heat_fires_at_danger_not_below(monkeypatch) -> None:
    from app.hazards.categories import heat_category
    _fresh(monkeypatch)
    conn = FakeConn({"p.kind = 'lga'": [(1, "Goronyo", GORONYO), (2, "Wurno", WURNO)]})
    days = {1: 41.0, 2: 38.0}
    monkeypatch.setattr(read, "heat_day", lambda conn, pid, lga, day: read.HeatDay(
        lga, day, days[pid], days[pid], days[pid] - 3, heat_category(days[pid]), 9, 5, 9, 0, 0, "none", 0, NOON,
        "air_temperature"))
    out = triggers.heat(conn, NOON)
    assert [c.lga_pcode for c in out] == [GORONYO]
    assert out[0].what["en"].startswith("up to 41 °C today (air temperature), Danger")
    assert out[0].key == f"heat:{GORONYO}:{NOON.date()}" and not out[0].official


def test_stale_data_fires_nothing(monkeypatch) -> None:
    monkeypatch.setattr(read, "freshness", lambda conn, layer, now=None: read.Freshness(layer, NOON, True, 30.0))
    conn = FakeConn({})
    assert triggers.heat(conn, NOON) == [] and triggers.dust(conn, NOON) == [] and triggers.rivers(conn, NOON) == []


def _air(aqi, cat):
    return lambda conn, pid, lga, day: read.AirDay(lga, day, 300, 80, 200, 1.2, aqi, cat, NOON, "PM10")


def test_dust_fires_at_hazardous_but_not_at_very_unhealthy(monkeypatch) -> None:
    _fresh(monkeypatch)
    conn = FakeConn({"p.kind = 'lga'": [(1, "Goronyo", GORONYO)]})
    monkeypatch.setattr(read, "air_day", _air(250, "very_unhealthy"))
    assert triggers.dust(conn, NOON) == []
    monkeypatch.setattr(read, "air_day", _air(320, "hazardous"))
    out = triggers.dust(conn, NOON)
    assert out[0].what["en"] == "US AQI up to 320 today (set by PM10), Hazardous"
    assert any("INSERT INTO air_daily" in sql for sql, _ in conn.calls)          # today's maximum recorded


def test_dust_fires_when_high_for_the_time_of_year(monkeypatch) -> None:
    _fresh(monkeypatch)
    history = [(float(100 + i),) for i in range(25)]                            # 100..124 over 25 days
    conn = FakeConn({"p.kind = 'lga'": [(1, "Goronyo", GORONYO)], "SELECT aqi_max FROM air_daily": history})
    monkeypatch.setattr(read, "air_day", _air(160, "unhealthy"))
    out = triggers.dust(conn, NOON)
    assert "higher than 95% of the last 25 days" in out[0].what["en"]
    conn.answers["SELECT aqi_max FROM air_daily"] = history[:10]                 # too little history yet
    assert triggers.dust(conn, NOON) == []


def test_rivers_fire_above_the_seasonal_95th_percentile(monkeypatch) -> None:
    _fresh(monkeypatch)

    def days(conn, day, lga_pcode=""):
        rank = 96.5 if day == NOON.date() + timedelta(days=1) else 80.0
        return [read.RiverDay("Rima near Goronyo", "Goronyo", day, 412.0, rank, date(1997, 1, 1), NOON),
                read.RiverDay("Sokoto River at Sokoto city", "Wamakko", day, 90.0, 94.9, date(1997, 1, 1), NOON)]
    monkeypatch.setattr(read, "river_days", days)
    out = triggers.rivers(FakeConn({}), NOON)
    assert [c.lga_pcode for c in out] == [GORONYO]
    assert "412 m³/s tomorrow, higher than 96% of days at this time of year since 1997" in out[0].what["en"]
    assert "not an official warning" in out[0].what["en"]


def test_a_new_state_wide_advisory_fires_for_every_lga_and_counts_as_official() -> None:
    issued = NOON - timedelta(hours=5)
    conn = FakeConn({"FROM advisories": [(7, "nema_alerts", "alert", "flood", issued, None, [], True),
                                         (8, "sokoto_moh", "alert", "fire", issued, None, [GORONYO], False),
                                         (9, "nema_alerts", "alert", "flood", issued - timedelta(days=20), None,
                                          [GORONYO], False)]})
    out = triggers.advisories(conn, NOON)
    assert len(out) == 23 and all(c.official and c.hazard == "flood" and c.key == "adv:7" for c in out)
    assert out[0].what["en"] == "NEMA flood alert issued 02 Nov 2026"


def test_a_new_ncdc_report_fires_only_when_sokoto_figures_rose() -> None:
    rows = [("cholera", 2026, 44, "week 44", 30, 4, 1), ("measles", 2026, 44, "week 44", 10, 2, 0)]
    prev = {"cholera": [(20, 4)], "measles": [(10, 2)]}
    conn = FakeConn({"WHERE listed AND fetched_at": rows, "(year, epi_week) <": lambda a: prev[a[0]]})
    out = triggers.outbreaks(conn, NOON)
    assert {c.key for c in out} == {"ncdc:cholera:2026-44"} and len(out) == 23
    assert out[0].what["en"].startswith("NCDC week 44 2026 report: Cholera in Sokoto, 30 suspected, 4 confirmed")


# --- the admin page --------------------------------------------------------------------------------------------

def test_the_admin_page_shows_the_dry_run(monkeypatch) -> None:
    store = UserStore(":memory:")
    _subs(store, ("ha", "heat"))
    _run(store, [_cand()])
    monkeypatch.setattr("app.users.get_store", lambda: store)
    s = make_settings(admin_user="admin", admin_password=SecretStr("a-long-test-password"))
    app.dependency_overrides[get_settings] = lambda: s
    try:
        r = TestClient(app).get("/admin/alerts", auth=("admin", "a-long-test-password"))
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200 and "DRY RUN" in r.text and "zafin rana | Goronyo" in r.text
    assert "u0" not in r.text                                                    # no user keys shown
