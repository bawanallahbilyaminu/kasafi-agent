"""A name the user states for themselves is held in memory for an hour after their last message (5 Nov 2026), as the
location is for 30 minutes: a greeting or a thank-you may use it, sparingly. It is never written anywhere: the
follow-up history, traces and logs carry '[name removed]'. Only a name stated in a message counts, never the
WhatsApp profile name. After an hour without a message, or on DELETE MY DATA, it is gone."""

import asyncio
import json
import logging

import pytest

from app import privacy
from app.agent import conversational as CV
from app.agent.understand import Understanding
from app.guardrails.scope import Verdict
from app.privacy import NAME_MARK, NAME_TTL_S, NameMemory
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import make_settings

SENDER = "2348000000001"


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


async def _chat(text, history, place, settings, fallbacks=None):
    return Understanding(kind="chitchat", capability="conversation", restatement="")


async def _no_documents(*a, **k):
    raise AssertionError("a greeting never reaches the documents")


@pytest.fixture
def chat(monkeypatch):
    """A consented user, the conversational route with a fake model that greets by the name it is given, and a
    fake database that keeps what a trace row would store."""
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

    def say(body: str, profile: str = "") -> list:
        msg = {"from": SENDER, "id": f"w-{len(seen['names'])}-{abs(hash(body))}", "type": "text",
               "text": {"body": body}, **({"profile": {"name": profile}} if profile else {})}
        return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=_no_documents, guard_fn=_ok,
                                    place_fn=_none, understand_fn=_chat))
    yield say, store, key, seen
    privacy.names.forget(key)


def test_the_name_is_used_in_a_follow_up_within_the_hour(chat) -> None:
    say, store, key, seen = chat
    outs = say("Hello, my name is Musa Bello")
    assert seen["names"] == ["Musa Bello"] and "Musa Bello" in outs[-1].text
    outs = say("Thank you")                                   # the follow-up states no name: it is remembered
    assert seen["names"][-1] == "Musa Bello" and outs[-1].text == "You're welcome, Musa Bello!"
    assert privacy.names.recall(key) == "Musa Bello"


def test_the_name_is_gone_an_hour_after_the_last_message(chat, monkeypatch) -> None:
    say, store, key, seen = chat
    import time
    now = [time.time()]
    monkeypatch.setattr(time, "time", lambda: now[0])
    say("My name is Musa Bello")
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
        say("My name is Musa Bello. Thank you for the help")
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


def test_delete_my_data_clears_the_name(chat) -> None:
    say, store, key, seen = chat
    say("Sunana Aisha Umar")
    assert privacy.names.recall(key) == "Aisha Umar"
    outs = say("DELETE MY DATA")
    assert outs[0].text == C.DELETED_REPLY and privacy.names.recall(key) == "" and key not in privacy.names._names


def test_only_a_name_stated_in_a_message_counts_never_the_profile_name(chat) -> None:
    say, store, key, seen = chat
    outs = say("Thank you", profile="Bilyaminu Profile")      # the WhatsApp profile name is never read
    assert seen["names"] == [""] and outs[-1].text == "You're welcome!" and privacy.names.recall(key) == ""
    # the webhook payload carries the profile name under 'contacts': nothing in the WhatsApp code reads that block
    # ('profile' elsewhere in it is the route profile: driving or walking)
    from pathlib import Path
    for src in Path(C.__file__).parent.glob("*.py"):
        code = src.read_text(encoding="utf-8")
        assert "contacts" not in code and '["profile"]' not in code and '"profile")' not in code, src.name
    # words that follow 'I am …' without being a person's name are never used to address anyone
    for text in ("I am Director of the Budget Office, tell me about the 2026 budget", "I am Nigerian, from Sokoto",
                 "This is Kasafi, right?", "I am a farmer in Wamakko", "Sunana Malam", "How much is the health budget?"):
        assert privacy.stated_name(text) == "", text
    for text, name in (("My name is Musa Bello", "Musa Bello"), ("Sunana Abubakar Sadiq, ina so in sani", "Abubakar Sadiq"),
                       ("I'm Hauwa from the Ministry of Finance", "Hauwa"), ("I am Dr. Aisha Umar, a teacher", "Dr. Aisha Umar"),
                       ("Ana kira na Malam Sani", "Malam Sani")):
        assert privacy.stated_name(text) == name, text


def test_the_memory_is_per_user_and_holds_nothing_after_its_time() -> None:
    m = NameMemory(ttl_s=10)
    m.remember("a", "Musa")
    assert m.recall("a") == "Musa" and m.recall("b") == ""
    m._names["a"] = ("Musa", m._names["a"][1] - 11)           # eleven seconds ago
    m.touch("a")                                              # a message after the time doesn't revive it
    assert m.recall("a") == "" and m._names == {}


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
