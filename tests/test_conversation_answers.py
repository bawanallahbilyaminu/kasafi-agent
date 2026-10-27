"""The WhatsApp flow with answers from the documents switched on (a fake answer function)."""

import pytest

from app.guardrails.emergency import EMERGENCY_REPLY
from app.users import UserStore, user_key
from app.whatsapp.corrections import Resolution
from app.whatsapp.messages import NOTICE_BUTTONS, t
from tests.helpers import heard, make_settings, run_handle

A = "2340000000001"
Q = "Nawa aka ware wa ilimi a 2026?"


def text(body: str) -> dict:
    return {"from": A, "type": "text", "text": {"body": body}}


def voice() -> dict:
    return {"from": A, "type": "audio", "audio": {"id": "m1", "voice": True}}


def consented(lang: str = "ha") -> UserStore:
    store = UserStore(":memory:")
    run_handle(text("Sannu" if lang == "ha" else "Hello"), store=store)
    run_handle(text("OK"), store=store)
    return store


def test_typed_question_gets_searching_ack_then_answer() -> None:
    calls, notified = [], []
    outs, _ = run_handle(text(Q), store=consented(), answer_calls=calls, notified=notified)
    assert calls == [(Q, "ha")]
    assert [o.text for o in notified] == [t("searching", "ha")]
    assert outs[0].text == f"ANSWER[ha]: {Q}"


def test_english_user_gets_english_answer() -> None:
    calls = []
    outs, _ = run_handle(text("How much for health in 2026?"), store=consented("en"), answer_calls=calls)
    assert calls == [("How much for health in 2026?", "en")] and outs[0].text.startswith("ANSWER[en]")


def test_clear_voice_question_is_answered_with_what_was_heard() -> None:
    calls = []
    outs, _ = run_handle(voice(), store=consented(), spoken=heard(Q, confirm=False), answer_calls=calls)
    assert calls == [(Q, "ha")]
    assert outs[0].text == f"{t('heard_prefix', 'ha', transcript=Q)}\n\nANSWER[ha]: {Q}"


def test_unclear_voice_waits_for_eh_then_answers() -> None:
    store, calls = consented(), []
    outs, _ = run_handle(voice(), store=store, spoken=heard(Q, confirm=True), answer_calls=calls)
    assert calls == [] and "Kana nufin haka?" in outs[0].text                 # nothing answered yet
    outs, _ = run_handle(text("Eh"), store=store, answer_calls=calls)
    assert calls == [(Q, "ha")]
    assert outs[0].text.startswith(t("confirmed_prefix", "ha", question=Q)) and outs[0].text.endswith(f"ANSWER[ha]: {Q}")


def test_correction_is_answered_with_the_corrected_question() -> None:
    store, calls = consented(), []
    run_handle(voice(), store=store, spoken=heard("Nawa aka ware wa ilimi a 2022?", confirm=True))
    outs, _ = run_handle(text("2026"), store=store, answer_calls=calls,
                         corrections={"2026": Resolution("correction", Q)})
    assert calls == [(Q, "ha")] and outs[0].text.startswith(t("corrected_prefix", "ha", question=Q))


def test_cancel_answers_nothing() -> None:
    store, calls = consented(), []
    run_handle(voice(), store=store, spoken=heard(Q, confirm=True))
    outs, _ = run_handle(text("A'a"), store=store, answer_calls=calls)
    assert calls == [] and outs[0].text == t("cancelled", "ha")


def test_confirming_counts_as_a_question_and_respects_the_limit() -> None:
    s = make_settings(kasafi_questions_per_day=1)
    store, calls = consented(), []
    run_handle(voice(), store=store, spoken=heard(Q, confirm=True), settings=s)
    run_handle(text("Eh"), store=store, settings=s, answer_calls=calls)
    assert store.usage(user_key(A, s))[1] == 1 and calls == [(Q, "ha")]
    run_handle(voice(), store=store, spoken=heard(Q, confirm=True), settings=s)
    outs, _ = run_handle(text("Eh"), store=store, settings=s, answer_calls=calls)
    assert outs[0].text == t("question_limit", "ha", n=1) and len(calls) == 1


def test_answers_cost_against_the_spend_cap() -> None:
    s = make_settings(kasafi_daily_spend_cap_usd=0.015, kasafi_cost_per_question_usd=0.01)
    store, calls = consented(), []
    assert run_handle(text(Q), store=store, settings=s, answer_calls=calls)[0][0].text.startswith("ANSWER")
    outs, _ = run_handle(text(Q), store=store, settings=s, answer_calls=calls)
    assert outs[0].text == t("busy", "ha") and len(calls) == 1


def test_answer_failure_is_reported_politely() -> None:
    outs, _ = run_handle(text(Q), store=consented(), answer_error=RuntimeError("db down"))
    assert outs[0].text == t("answer_failed", "ha")


@pytest.mark.parametrize("body", ["Wane ɗan takara ya kamata in zaɓa?", "Ina 'yan bindiga suka fi kai hari?"])
def test_out_of_scope_questions_are_never_answered(body: str) -> None:
    calls = []
    outs, _ = run_handle(text(body), store=consented(), answer_calls=calls)
    assert calls == [] and outs[0].text.startswith(("Kasafi ba ya", "Yi haƙuri"))


def test_emergency_is_never_answered_from_documents() -> None:
    calls = []
    outs, _ = run_handle(text("Matata tana zubar da jini"), store=consented(), answer_calls=calls)
    assert calls == [] and outs[0].text == EMERGENCY_REPLY
    outs, _ = run_handle(voice(), store=consented(), spoken=heard("Matata tana zubar da jini"), answer_calls=calls)
    assert calls == [] and outs[0].text == EMERGENCY_REPLY


def test_nothing_is_answered_before_consent() -> None:
    calls = []
    outs, _ = run_handle(text(Q), answer_calls=calls)
    assert calls == [] and outs[-1].buttons == NOTICE_BUTTONS
