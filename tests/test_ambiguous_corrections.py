"""A correction that could mean "replace" or "add": Kasafi asks once instead of guessing.

Bilyaminu's live test: Kasafi heard "... a shekarar 2024, 2023 da 2022 ..." and he replied
"A shekarar 2025", meaning replace. Kasafi had added 2025 to the list instead.
"""

from app.users import UserStore, user_key
from app.whatsapp.corrections import Resolution, choose_option
from app.whatsapp.messages import FIX_BUTTONS, t
from tests.helpers import heard, make_settings, run_handle

A = "2340000000001"
HEARD = "Naira nawa aka ware wa Ma'aikatar Lafiya a shekarar 2024, 2023 da 2022 kuma naira nawa suka kashe a shekarar?"
REPLACE = "Naira nawa aka ware wa Ma'aikatar Lafiya a shekarar 2025 kuma naira nawa suka kashe a shekarar?"
ADD = "Naira nawa aka ware wa Ma'aikatar Lafiya a shekarar 2024, 2023 da 2022 da 2025 kuma naira nawa suka kashe a shekarar?"
REPLY = "A shekarar 2025"
AMBIGUOUS = {REPLY: Resolution("ambiguous", REPLACE, "", REPLACE, ADD)}


def text(body: str) -> dict:
    return {"from": A, "type": "text", "text": {"body": body}}


def tap(button_id: str) -> dict:
    return {"from": A, "type": "interactive",
            "interactive": {"type": "button_reply", "button_reply": {"id": button_id, "title": button_id}}}


def asked(lang: str = "ha") -> UserStore:
    """Consented user, read-back of HEARD, reply REPLY -> Kasafi asks replace or add."""
    store = UserStore(":memory:")
    run_handle(text("Sannu" if lang == "ha" else "Hello"), store=store)
    run_handle(text("OK"), store=store)
    run_handle({"from": A, "type": "audio", "audio": {"id": "m1"}}, store=store, spoken=heard(HEARD, confirm=True))
    outs, _ = run_handle(text(REPLY), store=store, corrections=AMBIGUOUS, answer_calls=[])
    assert outs[0].text == t("ask_replace_or_add", lang, value=REPLY)
    assert outs[0].buttons == FIX_BUTTONS[lang]
    return store


def test_ambiguous_reply_asks_with_buttons_and_answers_nothing_yet() -> None:
    store = asked()
    key = user_key(A, make_settings())
    assert store.get_pending(key, 15)[0] == HEARD                 # the read-back question is kept
    assert store.get_pending_options(key)["replace"] == REPLACE


def test_replace_button_answers_the_replaced_question() -> None:
    store, calls = asked(), []
    outs, _ = run_handle(tap("fix_replace"), store=store, answer_calls=calls)
    assert calls == [(REPLACE, "ha")]
    assert outs[0].text.startswith(t("corrected_prefix", "ha", question=REPLACE))
    assert store.get_pending(user_key(A, make_settings()), 15) is None


def test_typed_kara_answers_the_added_question() -> None:
    store, calls = asked(), []
    run_handle(text("Ƙara"), store=store, answer_calls=calls)
    assert calls == [(ADD, "ha")]


def test_eh_does_not_pick_one_so_kasafi_asks_again() -> None:
    store, calls = asked(), []
    outs, _ = run_handle(text("Eh"), store=store, answer_calls=calls)
    assert calls == [] and outs[0].buttons == FIX_BUTTONS["ha"]


def test_something_else_drops_the_question_and_carries_on() -> None:
    store, calls = asked(), []
    new_q = "Nawa ne bashin jihar a 2023?"
    run_handle(text(new_q), store=store, answer_calls=calls, corrections={new_q: Resolution("new", new_q)})
    key = user_key(A, make_settings())
    assert calls == [(new_q, "ha")] and store.get_pending_options(key) is None


def test_english_user_gets_english_buttons() -> None:
    store = UserStore(":memory:")
    run_handle(text("Hello"), store=store); run_handle(text("OK"), store=store)
    run_handle({"from": A, "type": "audio", "audio": {"id": "m1"}}, store=store, spoken=heard(HEARD, confirm=True))
    outs, _ = run_handle(text(REPLY), store=store, corrections=AMBIGUOUS, answer_calls=[])
    assert outs[0].buttons == FIX_BUTTONS["en"] and outs[0].text.startswith("Should «A shekarar 2025» replace")


def test_choose_option_words_and_buttons() -> None:
    assert choose_option("fix_replace") == choose_option("Maye gurbi") == choose_option("replace") == "replace"
    assert choose_option("fix_add") == choose_option("ƙara") == choose_option("Kara") == choose_option("add") == "add"
    assert choose_option("2025") is None


def test_button_titles_fit_whatsapp() -> None:
    assert all(len(title) <= 20 for buttons in FIX_BUTTONS.values() for _, title in buttons)


def test_delete_clears_the_options_too() -> None:
    store = asked()
    run_handle(text("GOGE BAYANAI NA"), store=store)
    assert store.get(user_key(A, make_settings())) is None
