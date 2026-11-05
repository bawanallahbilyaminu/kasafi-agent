"""A name the user states for themselves is held in memory for an hour after their last message (5 Nov 2026), as the
location is for 30 minutes: a greeting or a thank-you may use it, sparingly. It is never written anywhere: the
follow-up history, traces, logs, the review queues and a voice question waiting for its read-back carry
'[name removed]'. Only a name stated in a message counts, never the WhatsApp profile name. After an hour without a
message, or on DELETE MY DATA, it is gone.

The conversation-understanding step finds the name (`user_name` in the reading: any wording or letter case, 'my name
is musa', 'Ni ne Musa', 'Call me Musa', 'Musa ne sunana'; evals/understanding cases p01-p14). The wording rules of
app/privacy.py decide only when that step doesn't run or fails, and always decide what is removed from storage."""

import asyncio
import json
import logging
from pathlib import Path

import pytest

from app import privacy
from app.agent import conversational as CV
from app.agent import understand as U
from app.agent.understand import Understanding
from app.guardrails.scope import Verdict
from app.privacy import NAME_MARK, NAME_TTL_S, NameMemory
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import heard, make_settings, run_handle

SENDER = "2348000000001"
RECORDED = json.loads(Path("evals/understanding/recorded.json").read_text(encoding="utf-8"))


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


async def _no_documents(*a, **k):
    raise AssertionError("a greeting never reaches the documents")


@pytest.fixture
def chat(monkeypatch):
    """A consented user, the conversational route with a fake model that greets by the name it is given, and a
    fake database that keeps what a trace row would store. `say(body, reads=name)`: the message, and the name the
    understanding step reads in it ('' for none; None: the step fails and the wording rules decide)."""
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "en")
    store.give_consent(key)
    privacy.names.forget(key)
    seen: dict = {"names": [], "rows": []}

    async def reply(message, lang, history, place, settings, client_cls=None, name=""):
        seen["names"].append(name)
        body = f"You're welcome, {name}!" if name else "You're welcome!"
        logging.getLogger("kasafi.test").info("reply for %r: %s", message, body)     # a careless log line
        return body, "model"
    monkeypatch.setattr(CV, "reply", reply)

    class Conn:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def execute(self, sql, params=()):
            seen["rows"].append(params)

        def commit(self):
            pass
    import psycopg
    monkeypatch.setattr(psycopg, "connect", lambda *a, **k: Conn())

    def say(body: str, reads: str | None = "", profile: str = "") -> list:
        async def understand_fn(text, history, place, settings, fallbacks=None):
            if reads is None:
                return None                                     # both models failed
            return Understanding(kind="chitchat", capability="conversation", restatement="a greeting",
                                 user_name=reads)
        msg = {"from": SENDER, "id": f"w-{len(seen['names'])}-{abs(hash(body))}", "type": "text",
               "text": {"body": body}, **({"profile": {"name": profile}} if profile else {})}
        return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=_no_documents, guard_fn=_ok,
                                    place_fn=_none, understand_fn=understand_fn))
    yield say, store, key, seen
    privacy.names.forget(key)


def test_the_name_is_used_in_a_follow_up_within_the_hour(chat) -> None:
    say, store, key, seen = chat
    outs = say("Hello, my name is Musa Bello", reads="Musa Bello")
    assert seen["names"] == ["Musa Bello"] and "Musa Bello" in outs[-1].text
    outs = say("Thank you")                                   # the follow-up states no name: it is remembered
    assert seen["names"][-1] == "Musa Bello" and outs[-1].text == "You're welcome, Musa Bello!"
    assert privacy.names.recall(key) == "Musa Bello"


@pytest.mark.parametrize("message, read, name", [
    ("my name is musa", "Musa", "Musa"), ("Ni ne Musa", "Musa", "Musa"), ("Call me Musa", "Musa", "Musa"),
    ("Musa ne sunana", "Musa", "Musa"), ("ku kira ni malam sani", "Malam Sani", "Malam Sani"),
    ("good morning, hauwa here", "hauwa", "Hauwa"),           # the reading's name gets its capital
])
def test_the_reading_finds_the_name_in_any_wording_or_letter_case(chat, message, read, name) -> None:
    say, store, key, seen = chat
    say(message, reads=read)
    assert privacy.names.recall(key) == name and seen["names"] == [name]
    assert name.split()[-1].lower() not in json.dumps(store.recent_turns(key)).lower()      # and it is not stored


@pytest.mark.parametrize("cid", ["p01", "p02", "p03", "p04"])
def test_the_recorded_live_readings_give_the_name(cid) -> None:
    """What Muse Spark Open read live for 'my name is musa', 'Ni ne Musa', 'Call me Musa', 'Musa ne sunana'."""
    assert RECORDED[cid]["user_name"] == "Musa" and RECORDED[cid]["capability"] == "conversation"


def test_a_name_the_reading_did_not_take_from_the_message_is_not_used(chat) -> None:
    say, store, key, seen = chat
    say("Thank you", reads="Abubakar")                        # not in the message: a guess, or from an earlier turn
    assert privacy.names.recall(key) == "" and seen["names"] == [""]
    say("I am a farmer from Wamakko", reads="Farmer")         # a job is not a name
    say("Is this Kasafi?", reads="Kasafi")
    assert privacy.names.recall(key) == ""
    # when the step read the message and found no name, the wording rules don't add one
    say("I am Sorry, I meant the 2026 budget", reads="")
    assert privacy.names.recall(key) == ""


def test_when_the_step_fails_the_wording_rules_find_the_name(chat) -> None:
    say, store, key, seen = chat
    say("my name is musa", reads=None)
    assert privacy.names.recall(key) == "Musa"
    for text, name in (("My name is Musa Bello", "Musa Bello"), ("my name is musa", "Musa"), ("Ni ne Musa", "Musa"),
                       ("Call me Musa", "Musa"), ("call me musa please", "Musa"), ("Musa ne sunana", "Musa"),
                       ("musa ne sunana", "Musa"), ("Sunana Abubakar Sadiq, ina so in sani", "Abubakar Sadiq"),
                       ("sunana aisha", "Aisha"), ("I'm Hauwa from the Ministry of Finance", "Hauwa"),
                       ("I am Dr. Aisha Umar, a teacher", "Dr. Aisha Umar"), ("Ana kira na Malam Sani", "Malam Sani"),
                       ("ku kira ni malam sani", "Malam Sani"), ("Aisha is my name", "Aisha")):
        assert privacy.stated_name(text) == name, text
    for text in ("I am Director of the Budget Office, tell me about the 2026 budget", "I am Nigerian, from Sokoto",
                 "This is Kasafi, right?", "I am a farmer in Wamakko", "Sunana Malam", "How much is the health budget?",
                 "my name is not important", "call me when the report is out", "This is Wamakko.",
                 "Ni manomi ne a Wurno"):
        assert privacy.stated_name(text) == "", text


def test_the_name_is_gone_an_hour_after_the_last_message(chat, monkeypatch) -> None:
    say, store, key, seen = chat
    import time
    now = [time.time()]
    monkeypatch.setattr(time, "time", lambda: now[0])
    say("My name is Musa Bello", reads="Musa Bello")
    now[0] += NAME_TTL_S - 60                                 # 59 minutes later: still held, and the hour restarts
    assert say("Thanks")[-1].text == "You're welcome, Musa Bello!"
    now[0] += NAME_TTL_S - 60                                 # 59 minutes after that message: still held
    assert say("Thanks again")[-1].text == "You're welcome, Musa Bello!"
    now[0] += NAME_TTL_S + 1                                  # an hour and a second of silence
    outs = say("Thank you")
    assert seen["names"][-1] == "" and outs[-1].text == "You're welcome!"
    assert privacy.names.recall(key) == "" and key not in privacy.names._names


def test_the_name_is_never_in_what_is_stored(chat, caplog) -> None:
    say, store, key, seen = chat
    with caplog.at_level(logging.INFO):
        say("My name is Musa Bello. Thank you for the help", reads="Musa Bello")
        say("Thanks, that is all from Musa")                  # the name again, without 'my name is'
    # the follow-up history on disk
    turns = store.recent_turns(key)
    kept = json.dumps(turns)
    assert len(turns) == 2 and "Musa" not in kept and "Bello" not in kept and NAME_MARK in kept
    assert turns[0]["question"] == f"My name is {NAME_MARK}. Thank you for the help"
    assert turns[0]["answer"] == f"You're welcome, {NAME_MARK}!"
    assert turns[1]["question"] == f"Thanks, that is all from {NAME_MARK}"
    # the trace rows (question, reading, reply), as handed to the database
    stored = json.dumps(seen["rows"], default=str)
    assert len(seen["rows"]) == 2 and "Musa" not in stored and "Bello" not in stored and NAME_MARK in stored
    # the logs
    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert "reply for" in logged and NAME_MARK in logged and "Musa" not in logged and "Bello" not in logged
    # … while the user did get their name back in the reply
    assert seen["names"] == ["Musa Bello", "Musa Bello"]


def test_a_name_in_a_form_only_the_reading_finds_is_not_stored_either(chat) -> None:
    say, store, key, seen = chat
    say("good morning, hauwa here. thank you", reads="Hauwa")
    kept = json.dumps(store.recent_turns(key)) + json.dumps(seen["rows"], default=str)
    assert "hauwa" not in kept.lower() and NAME_MARK in kept
    # the reading itself never carries the name into a trace or a waiting question
    u = Understanding(capability="conversation", restatement="a greeting", user_name="Hauwa")
    assert u.to_dict()["user_name"] == "" and u.to_record()["user_name"] == "Hauwa"
    assert U.parse({"capability": "conversation", "restatement": "a greeting", "user_name": "hauwa"}).user_name == "Hauwa"
    assert U.parse({"capability": "budget", "restatement": "x", "user_name": "none"}).user_name == ""
    # the live reading restated 'Call me Musa' as 'User asks to be called Musa': the name leaves the restatement
    # (it is logged, traced and used as the question) and every part's
    r = U.parse({"capability": "conversation", "restatement": "User asks to be called Musa", "user_name": "Musa",
                 "parts": [{"capability": "budget", "restatement": "Musa asks for the 2026 health budget"},
                           {"capability": "facility", "restatement": "Where is the nearest clinic to Musa's ward?"}]})
    assert r.user_name == "Musa" and r.restatement == f"User asks to be called {NAME_MARK}"
    assert [p["restatement"] for p in r.parts] == [f"{NAME_MARK} asks for the 2026 health budget",
                                                   f"Where is the nearest clinic to {NAME_MARK}'s ward?"]
    for cid in ("p01", "p02", "p03", "p04", "p05", "p06", "p07", "p08"):
        assert RECORDED[cid]["user_name"].split()[-1] not in RECORDED[cid]["restatement"], cid
    assert '"user_name"' in U.system_prompt(make_settings()) and "Musa ne sunana" in U.system_prompt(make_settings())


def test_a_voice_question_waiting_for_its_read_back_is_stored_without_the_name() -> None:
    """A transcript heard unclearly waits in the user store (pending_question, pending_english) until 'Eh'."""
    privacy.names.forget(user_key("2348000000002", make_settings()))
    store = UserStore(":memory:")
    s = make_settings()
    key = user_key("2348000000002", s)
    store.create(key, "ha")
    store.give_consent(key)
    spoken = heard("Sunana Musa Bello, nawa ne kasafin lafiya na 2026?", confirm=True,
                   english="My name is Musa Bello, how much is the 2026 health budget?")
    run_handle({"from": "2348000000002", "id": "v1", "type": "audio", "audio": {"id": "m1"}}, store=store, settings=s,
               spoken=spoken)
    q, english = store.get_pending(key, 30)
    assert q == f"Sunana {NAME_MARK}, nawa ne kasafin lafiya na 2026?"
    assert english == f"My name is {NAME_MARK}, how much is the 2026 health budget?"
    row = store._db.execute("SELECT * FROM users WHERE user_key=?", (key,)).fetchone()
    assert "Musa" not in json.dumps(row, default=str) and "Bello" not in json.dumps(row, default=str)
    assert privacy.names.recall(key) == "Musa Bello"          # held in memory, as for a typed message
    privacy.names.forget(key)
    # pending choices and clarifications go through the same boundary
    store.set_pending_options(key, {"1": "My name is Aisha Umar and I asked about health"})
    store.set_pending_clarify(key, [{"label": "Sunana Aisha, kasafin lafiya"}])
    row = json.dumps(store._db.execute("SELECT * FROM users WHERE user_key=?", (key,)).fetchone(), default=str)
    assert "Aisha" not in row and "Umar" not in row and NAME_MARK in row
    # an alert subscriber's encrypted number is never rewritten, whatever name is held
    privacy.speaking("Ali")
    try:
        store.subscribe(key, ["NG034021"], ["flood"], "ha", number_enc="gAAAA+Ali/xyz=")
        assert store.alert_number(key) == "gAAAA+Ali/xyz="
    finally:
        privacy.speaking("")


def test_the_review_queues_hold_the_question_without_the_name() -> None:
    """/admin/review lists flagged traces (already redacted), open gaps and sites waiting for approval."""
    from app.acquisition.library import log_gap
    from app.acquisition.review import queue_domain
    from app.acquisition.find import Candidate
    rows: list = []

    class Conn:
        def execute(self, sql, params=()):
            rows.append((sql, params))
    q = "My name is Musa Bello and I need the 2019 fiscal strategy paper. I am at 13.0589127, 5.1673341"
    log_gap(Conn(), q, "fiscal strategy paper 2019", "not_found", {"detail": "asked by Musa Bello: my name is Musa Bello",
                                                                   "url": "https://mof.sk.gov.ng/doc/1234567890123"})
    insert = next(p for sql, p in rows if "INSERT INTO gaps" in sql)
    assert insert[0].startswith(f"My name is {NAME_MARK} and I need the 2019 fiscal strategy paper")
    assert "Musa" not in insert[0] and "13.0589" not in insert[0]
    assert "my name is [name removed]" in insert[3] and "1234567890123" in insert[3]      # the address keeps its digits
    rows.clear()
    queue_domain(Conn(), Candidate(url="https://example.org/report.pdf", title="A report", snippet=""), q)
    insert = next(p for sql, p in rows if "INSERT INTO domain_reviews" in sql)
    assert insert[1].startswith(f"My name is {NAME_MARK}") and "Musa" not in insert[1] and "13.0589" not in insert[1]
    # with the name held for the user being answered, it goes wherever it appears
    privacy.speaking("Musa Bello")
    try:
        rows.clear()
        log_gap(Conn(), "Musa wants the 2019 fiscal strategy paper", "", "no_answer")
        assert next(p for sql, p in rows if "INSERT INTO gaps" in sql)[0] == f"{NAME_MARK} wants the 2019 fiscal strategy paper"
    finally:
        privacy.speaking("")


def test_delete_my_data_clears_the_name(chat) -> None:
    say, store, key, seen = chat
    say("Sunana Aisha Umar", reads="Aisha Umar")
    assert privacy.names.recall(key) == "Aisha Umar"
    outs = say("DELETE MY DATA")
    assert outs[0].text == C.DELETED_REPLY and privacy.names.recall(key) == "" and key not in privacy.names._names


def test_only_a_name_stated_in_a_message_counts_never_the_profile_name(chat) -> None:
    say, store, key, seen = chat
    outs = say("Thank you", profile="Bilyaminu Profile")      # the WhatsApp profile name is never read
    assert seen["names"] == [""] and outs[-1].text == "You're welcome!" and privacy.names.recall(key) == ""
    # the webhook payload carries the profile name under 'contacts': nothing in the WhatsApp code reads that block
    # ('profile' elsewhere in it is the route profile: driving or walking)
    for src in Path(C.__file__).parent.glob("*.py"):
        code = src.read_text(encoding="utf-8")
        assert "contacts" not in code and '["profile"]' not in code and '"profile")' not in code, src.name


def test_the_memory_is_per_user_and_holds_nothing_after_its_time() -> None:
    m = NameMemory(ttl_s=10)
    m.remember("a", "Musa")
    assert m.recall("a") == "Musa" and m.recall("b") == ""
    m._names["a"] = ("Musa", m._names["a"][1] - 11)           # eleven seconds ago
    m.touch("a")                                              # a message after the time doesn't revive it
    assert m.recall("a") == "" and m._names == {}


def test_the_sweep_deletes_a_name_an_hour_after_the_last_message_for_a_user_who_never_returns(monkeypatch) -> None:
    """Reading a name checks its time, but only for the user who writes: a user who never comes back stayed in memory,
    unusable but not deleted. The sweep really removes it."""
    import time
    now = [1_000_000.0]
    monkeypatch.setattr(time, "time", lambda: now[0])
    m = NameMemory()
    m.remember("gone", "Musa Bello")
    now[0] += NAME_TTL_S - 300
    m.remember("here", "Aisha")
    now[0] += 299                                             # 59:59 after 'gone' last wrote
    assert m.sweep() == 0 and set(m._names) == {"gone", "here"}
    now[0] += 2                                               # past the hour, and nobody has written since
    assert m.sweep() == 1 and set(m._names) == {"here"} and "Musa Bello" not in repr(m._names)
    m.touch("here")                                           # a message restarts the hour
    now[0] += NAME_TTL_S - 1
    assert m.sweep() == 0 and m.recall("here") == "Aisha"
    now[0] += 2
    assert m.sweep() == 1 and m._names == {}


def test_the_sweep_runs_by_itself_at_boot_whatever_else_is_switched_on(monkeypatch) -> None:
    import time as _time

    from app import maintenance
    from app.geo.location import LocationMemory, Spot
    from app.geo import location
    maintenance._swept.clear()
    fake = NameMemory(ttl_s=0.01)
    monkeypatch.setattr(privacy, "names", fake)
    fake.remember("gone", "Musa")
    th = maintenance.start_held_sweep(every_s=0.02)
    try:
        deadline = _time.monotonic() + 3
        while fake._names and _time.monotonic() < deadline:
            _time.sleep(0.01)
        assert fake._names == {} and th.is_alive() and th.daemon
        assert maintenance.start_held_sweep() is th           # one per process
    finally:
        maintenance._swept.clear()
    # started at boot, not behind a backup folder or hazard fetching
    src = Path("app/main.py").read_text(encoding="utf-8")
    assert "start_held_sweep()" in src
    # the same sweep deletes locations, plot shapes, waiting questions and first messages past their time
    mem = LocationMemory(ttl_s=0.0, corner_ttl_s=0.0)
    mem.remember("k", Spot(13.0, 5.0))
    mem.wait_for_location("k", "q")
    mem.remember_search("k", object())
    mem.remember_shape("k", {"declined": True})
    mem.add_pin("k", 13.0, 5.0)
    assert mem.sweep() == 5 and not (mem._spots or mem._needs or mem._searches or mem._shapes or mem._pins)
    keep = LocationMemory()
    keep.remember("k", Spot(13.0, 5.0))
    assert keep.sweep() == 0 and keep.recall("k") is not None
    monkeypatch.setattr(location, "memory", mem)
    now = _time.time()
    monkeypatch.setitem(C._first_messages, "old", (now - C.FIRST_TTL_S - 1, {"id": "x"}))
    monkeypatch.setitem(C._first_messages, "new", (now, {"id": "y"}))
    assert maintenance.sweep_held()["first_messages"] == 1 and "old" not in C._first_messages
    assert "new" in C._first_messages


def test_the_privacy_page_says_what_the_code_does() -> None:
    """docs/site/privacy.md, the source of the published page."""
    from app.config import Settings
    page = " ".join(Path("docs/site/privacy.md").read_text(encoding="utf-8").split())
    # the providers actually used
    for gone in ("Baseten", "Azure"):
        assert gone not in page
    assert Settings.model_fields["kasafi_open_hosts"].default == "fireworks" and "Fireworks AI" in page
    for used in ("Meta Model API", "WhatsApp Cloud API", "Serper", "OpenRouteService", "Planetary Computer", "Open-Meteo"):
        assert used in page, used
    # names, as built: the numbers the code uses, and no claim that nothing can slip through
    assert NAME_TTL_S == 3600 and "up to 1 hour after your last message" in page
    from app.maintenance import SWEEP_EVERY_S
    assert SWEEP_EVERY_S <= 60 and "deleted within about a minute" in page
    assert NAME_MARK in page and "goes to the Meta Model API" in page and "stays in the saved text" in page
    section = page.split("### If you tell Kasafi your name")[1].split("### Your location")[0]
    for over_claim in ("never written to disk", "never stored", "never claims to know", "does not keep"):
        assert over_claim not in section and over_claim not in page.split("## How long we keep it")[1], over_claim
    assert "doesn't read, use or store it" in page


def test_the_prompt_uses_the_name_sparingly_and_claims_nothing_more() -> None:
    assert "NAME THE USER GAVE: Musa Bello" in CV.user_message("Thanks", "en", [], None, name="Musa Bello")
    assert "NAME THE USER GAVE: none" in CV.user_message("Thanks", "en", [], None)
    for rule in ("Use it sparingly", "never more than once in a reply", "In Hausa be respectful",
                 "never say you know who they are", "never say you keep a record of them"):
        assert rule in " ".join(CV.SYSTEM.split()), rule

    class Client:
        sent: list = []

        def __init__(self, settings=None, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        async def chat(self, messages, **kw):
            Client.sent = messages
            from types import SimpleNamespace
            return SimpleNamespace(content="Barka da zuwa, Malam Musa!")
    text, how = asyncio.run(CV.reply("Sannu", "ha", [], None, make_settings(), client_cls=Client, name="Malam Musa"))
    assert how == "model" and text == "Barka da zuwa, Malam Musa!"
    assert "NAME THE USER GAVE: Malam Musa" in Client.sent[1]["content"]
