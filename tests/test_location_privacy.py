"""Follow-up review (1 Nov), finding 3: an exact location typed or said in a message is never stored: not in the
conversation turns, pending questions, saved working, traces, failure records or logs, and never sent to a model in
the question or the follow-up history. Budget figures and statistics survive the redactor."""

from __future__ import annotations

import asyncio
import logging
import sqlite3

import pytest

from app.geo.location import memory
from app.guardrails.scope import Verdict
from app.privacy import MARK, has_location, strip_location
from app.providers.stt import SpeechResult
from app.users import UserStore, user_key
from app.whatsapp.conversation import handle
from app.whatsapp.voice import VoiceOutcome, compose_reply
from tests.helpers import make_settings

PAIR = "13.0589127, 5.1673341"
SENDER = "2348000000077"


@pytest.mark.parametrize("text", [
    "near my farm at 13.0589127, 5.1673341?", "pin 13.0589 5.1673 please", "lat 13.058 lon 5.167",
    "latitude: 13.0589, longitude: 5.1673", "13°03'32\"N 5°10'02\"E", "13° 3.5' N, 5° 10.0' E",
    "my plus code is 7FG9+X2", "code 7FG9X2V5+7C Sokoto",
])
def test_every_kind_of_typed_location_is_removed(text) -> None:
    out = strip_location(text)
    assert MARK in out and has_location(text)
    assert "13.05" not in out and "7FG9" not in out and "°" not in out


@pytest.mark.parametrize("text", [
    "The 2026 approved budget is ₦70,000,000.00 (p. 61).", "MPI 0.409, 0.239 in 2018", "Q1-Q3 2025: 5.37 billion",
    "Rain was 612.4 mm in 2024", "Wurno, Wamakko and Sokoto North", "share 12.5%, 3.25%", "₦1,234,567.89 and ₦2.5 billion",
])
def test_budget_figures_and_statistics_survive(text) -> None:
    assert strip_location(text) == text


async def _ok(*a, **k):
    return Verdict("ok", "none")


def _user(tmp_path, lang="en"):
    s = make_settings(kasafi_state_db=str(tmp_path / "state.db"))
    store = UserStore(str(tmp_path / "state.db"))
    key = user_key(SENDER, s)
    store.create(key, lang)
    store.give_consent(key)
    memory.forget(key)
    return s, store, key


def _all_text(path) -> str:
    """Every text cell of every table of the SQLite file, as the file holds it."""
    db = sqlite3.connect(path)
    out = []
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        for row in db.execute(f"SELECT * FROM {table}"):
            out += [str(v) for v in row if isinstance(v, str)]
    db.close()
    return "\n".join(out)


def test_a_typed_coordinate_conversation_leaves_no_location_in_sqlite_the_model_or_the_logs(tmp_path, caplog) -> None:
    s, store, key = _user(tmp_path)
    seen = {}

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        seen.setdefault("questions", []).append(question)
        seen.setdefault("history", []).append(history)
        logging.getLogger("app.test").info("answering %s", question)
        logging.getLogger("app.test").warning(f"raw f-string {PAIR}")
        return type("A", (), {"text": f"The 2026 agriculture budget is ₦70,000,000.00. You asked about {PAIR}.",
                              "working": f"rows near {PAIR}: ₦70,000,000.00", "quotes": "", "sources": []})()

    def run(body):
        msg = {"from": SENDER, "id": f"w{len(seen)}{body[:5]}", "type": "text", "text": {"body": body}}
        return asyncio.run(handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok))

    with caplog.at_level(logging.DEBUG):
        run(f"What is the 2026 agriculture budget near my farm at {PAIR}?")
        run("and in 2025?")                                            # the follow-up: history from the store
    assert all("13.0589" not in q for q in seen["questions"])          # the model never sees it
    assert all("13.0589" not in str(h) for h in seen["history"])
    stored = _all_text(tmp_path / "state.db")
    assert "13.0589" not in stored and "5.1673" not in stored and MARK in stored
    assert "₦70,000,000.00" in stored                                  # the figures survive
    assert "13.0589" not in caplog.text and "5.1673" not in caplog.text
    store._db.close()


def test_a_pending_read_back_and_a_voice_transcript_store_no_location(tmp_path) -> None:
    s, store, key = _user(tmp_path, "ha")
    heard = SpeechResult(transcript=f"Nawa aka ware wa noma a gonata a {PAIR}?",
                         english=f"How much was allocated to agriculture at my farm at {PAIR}?",
                         language="ha", confidence="low", needs_confirmation=True)

    async def voice(msg, wa, *, lang, settings):
        return VoiceOutcome(compose_reply(heard, lang), heard)
    msg = {"from": SENDER, "id": "wv1", "type": "audio", "audio": {"id": "m", "mime_type": "audio/ogg"}}
    asyncio.run(handle(msg, None, store=store, settings=s, voice_fn=voice, guard_fn=_ok,
                       answer_fn=lambda *a, **k: None))
    stored = _all_text(tmp_path / "state.db")
    assert "13.0589" not in stored and MARK in stored                 # the pending read-back
    store._db.close()


def test_text_stored_before_the_redactor_is_cleaned_on_open(tmp_path) -> None:
    path = str(tmp_path / "old.db")
    store = UserStore(path)
    store._db.execute("INSERT INTO turns (user_key, at, lang, question, answer, sources) VALUES (?,?,?,?,?,?)",
                      ("k", "2026-11-01T10:00:00+00:00", "en", f"farm at {PAIR}", "ok", "[]"))
    store._db.close()
    UserStore(path)._db.close()
    assert "13.0589" not in _all_text(path)


def test_traces_and_failure_records_use_the_same_redactor() -> None:
    from app.agent.trace import redact
    assert "13.0589" not in redact(f"budget near {PAIR}") and "7FG9" not in redact("at 7FG9+X2")
    assert "13°" not in redact("13°03'32\"N 5°10'02\"E") and redact("₦70,000,000.00") == "₦70,000,000.00"


def test_stop_and_delete_remove_the_coded_id_from_failed_alert_lists(tmp_path) -> None:
    store = UserStore(str(tmp_path / "a.db"))
    store.log_alert("heat", "NG034006", "k1", False, "partial", 1, failed=["u1", "u2"])
    store.unsubscribe("u1")
    assert store.failed_recipients("k1") == {"u2"}
    store.delete("u2")
    assert store.failed_recipients("k1") == set()
    store._db.close()


def test_a_location_at_the_end_of_a_sentence_or_in_brackets_is_removed() -> None:
    for text in (f"You asked about {PAIR}.", f"the farm ({PAIR})", f"{PAIR}", f"pin: {PAIR}; thanks"):
        assert "13.0589" not in strip_location(text), text
