import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest

from app.providers.chat import ChatResult, ProviderError
from app.users import UserStore, user_key
from app.whatsapp.corrections import Resolution, merge_with_model, quick_resolve
from app.whatsapp.messages import t
from tests.helpers import heard, make_settings, run_handle

A = "2340000000001"
WRONG = "Nawa aka ware wa ɓangaren ilimi, a shekarar 2022?"
FIXED = "Nawa aka ware wa ɓangaren ilimi, a shekarar 2025?"


def text(body: str) -> dict:
    return {"from": A, "type": "text", "text": {"body": body}}


def voice() -> dict:
    return {"from": A, "type": "audio", "audio": {"id": "m1", "voice": True}}


def setup_pending() -> UserStore:
    """Consented Hausa user whose voice note was read back with the wrong year."""
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store)
    run_handle(text("OK"), store=store)
    outs, _ = run_handle(voice(), store=store, spoken=heard(WRONG, confirm=True))
    assert "Kana nufin haka?" in outs[0].text and WRONG in outs[0].text
    return store


def pending_of(store: UserStore):
    return store.get_pending(user_key(A, make_settings()), 15)


# --- the example from the spec --------------------------------------------------

def test_short_text_correction_updates_only_the_year() -> None:
    store = setup_pending()
    calls: list = []
    outs, _ = run_handle(text("2025"), store=store, resolve_calls=calls,
                         corrections={"2025": Resolution("correction", FIXED, "How much ... in 2025?")})
    assert calls == [(WRONG, "2025")]                    # the model got the pending question + the reply
    assert outs[0].text == t("corrected", "ha", question=FIXED)
    assert outs[0].text.startswith("Na gyara:") and "«" + FIXED + "»" in outs[0].text
    assert pending_of(store) is None


def test_spoken_correction_works_too() -> None:
    store = setup_pending()
    outs, _ = run_handle(voice(), store=store, spoken=heard("Na ce 2025"),
                         corrections={"Na ce 2025": Resolution("correction", FIXED)})
    assert outs[0].text.startswith("Na gyara:") and FIXED in outs[0].text
    assert pending_of(store) is None


# --- confirm / cancel without a model -------------------------------------------

@pytest.mark.parametrize("reply", ["Eh", "Ee", "Yes", "OK", "eh.", "Eh, haka ne"])
def test_confirm_words(reply: str) -> None:
    store = setup_pending()
    calls: list = []
    outs, _ = run_handle(text(reply), store=store, resolve_calls=calls)
    assert calls == [] and outs[0].text == t("confirmed", "ha", question=WRONG)
    assert pending_of(store) is None


@pytest.mark.parametrize("reply", ["A'a", "a'a", "No", "A'a, ba haka ba"])
def test_cancel_words(reply: str) -> None:
    store = setup_pending()
    calls: list = []
    outs, _ = run_handle(text(reply), store=store, resolve_calls=calls)
    assert calls == [] and outs[0].text == t("cancelled", "ha")
    assert pending_of(store) is None


def test_spoken_eh_confirms() -> None:
    store = setup_pending()
    outs, _ = run_handle(voice(), store=store, spoken=heard("Eh"))
    assert outs[0].text == t("confirmed", "ha", question=WRONG)


def test_confirm_does_not_use_a_question_from_the_limit() -> None:
    store = setup_pending()
    run_handle(text("Eh"), store=store)
    assert store.usage(user_key(A, make_settings()))[1] == 0


# --- a different, full question is new ------------------------------------------

def test_clearly_new_question_is_handled_as_new() -> None:
    store = setup_pending()
    q = "Nawa ne bashin da ake bin jihar Sakkwato a 2023?"
    outs, _ = run_handle(text(q), store=store, corrections={q: Resolution("new", q)})
    assert outs[0].text == t("echo", "ha", text=q) and pending_of(store) is None


def test_new_voice_question_replaces_the_pending_one() -> None:
    store = setup_pending()
    other = "Wadanne ƙananan hukumomi ne talauci ya fi yawa?"
    outs, _ = run_handle(voice(), store=store, spoken=heard(other, confirm=True))
    assert other in outs[0].text and pending_of(store)[0] == other


# --- when there's nothing pending -------------------------------------------------

def test_confident_voice_sets_no_pending_and_2025_is_just_a_message() -> None:
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store); run_handle(text("OK"), store=store)
    run_handle(voice(), store=store, spoken=heard(FIXED, confirm=False))
    calls: list = []
    outs, _ = run_handle(text("2025"), store=store, resolve_calls=calls)
    assert calls == [] and outs[0].text == t("echo", "ha", text="2025")


def test_pending_expires() -> None:
    store = setup_pending()
    key = user_key(A, make_settings())
    old = (datetime.now(timezone.utc) - timedelta(minutes=16)).isoformat()
    store._exec("UPDATE users SET pending_at=? WHERE user_key=?", (old, key))
    calls: list = []
    outs, _ = run_handle(text("2025"), store=store, resolve_calls=calls)
    assert calls == [] and outs[0].text == t("echo", "ha", text="2025")


# --- failures and safety -----------------------------------------------------------

@pytest.mark.parametrize("err", [ProviderError("Meta", 503, "busy"), ValueError("bad json")])
def test_merge_failure_asks_for_the_full_question(err: Exception) -> None:
    store = setup_pending()
    outs, _ = run_handle(text("2025"), store=store, corrections={"2025": err})
    assert outs[0].text == t("correction_failed", "ha") and pending_of(store) is None


def test_corrected_question_still_passes_the_emergency_check() -> None:
    store = setup_pending()
    q = "Matata tana zubar da jini"
    outs, _ = run_handle(text("matata ce"), store=store, corrections={"matata ce": Resolution("correction", q)})
    assert outs[0].text.startswith("🚨")


def test_emergency_voice_is_not_left_pending() -> None:
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store); run_handle(text("OK"), store=store)
    outs, _ = run_handle(voice(), store=store, spoken=heard("Matata tana zubar da jini", confirm=True))
    assert outs[0].text.startswith("🚨") and pending_of(store) is None


def test_delete_removes_pending_question() -> None:
    store = setup_pending()
    run_handle(text("GOGE BAYANAI NA"), store=store)
    assert pending_of(store) is None


def test_english_mode_correction_reply_is_english_but_question_stays_as_spoken() -> None:
    store = UserStore(":memory:")
    run_handle(text("Hello"), store=store); run_handle(text("OK"), store=store)
    run_handle(voice(), store=store, spoken=heard(WRONG, confirm=True))
    outs, _ = run_handle(text("2025"), store=store, corrections={"2025": Resolution("correction", FIXED)})
    assert outs[0].text.startswith("Corrected:") and FIXED in outs[0].text


# --- the resolver itself --------------------------------------------------------------

def test_quick_resolve() -> None:
    assert quick_resolve("Ee").kind == "confirm" and quick_resolve("A'a").kind == "cancel"
    assert quick_resolve("2025") is None and quick_resolve("Eh amma 2025") is None


class FakeChat:
    def __init__(self, reply: dict) -> None:
        self.reply, self.messages = reply, None

    async def chat(self, messages, **kw):
        self.messages = messages
        return ChatResult(content=json.dumps(self.reply), model="m", finish_reason="stop")


def test_merge_with_model_parses_and_keeps_reply_as_data() -> None:
    fake = FakeChat({"kind": "correction", "question": FIXED, "english": "How much ... 2025?"})
    res = asyncio.run(merge_with_model(WRONG, "2025", fake, make_settings()))
    assert (res.kind, res.question) == ("correction", FIXED)
    assert fake.messages[1] == {"role": "user", "content": f"PENDING: {WRONG}\nREPLY: 2025"}
    bad = asyncio.run(merge_with_model(WRONG, "x", FakeChat({"kind": "weird"}), make_settings()))
    assert bad.kind == "new"


def test_logs_show_reply_kind_and_timing_but_never_content(caplog) -> None:
    import logging
    store = setup_pending()
    with caplog.at_level(logging.INFO):
        run_handle(text("2025"), store=store, corrections={"2025": Resolution("correction", FIXED)})
    store = setup_pending()
    with caplog.at_level(logging.INFO):
        run_handle(text("Eh"), store=store)
    logs = caplog.text
    assert "resolved: correction in" in logs and "read-back reply from **01: confirm (typed, no model)" in logs
    assert "2025" not in logs and FIXED not in logs and WRONG not in logs and A not in logs
