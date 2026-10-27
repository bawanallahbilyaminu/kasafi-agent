import pytest

from app.data_rights import DELETED_REPLY
from app.users import UserStore, user_key
from app.whatsapp.messages import LANG_BUTTONS, NOTICE_BUTTONS, PRIVACY_URL, first_contact_notice, t
from tests.helpers import make_settings, run_handle

A = "2340000000001"


def text(body: str, sender: str = A) -> dict:
    return {"from": sender, "type": "text", "text": {"body": body}}


def voice(sender: str = A) -> dict:
    return {"from": sender, "type": "audio", "audio": {"id": "m1", "voice": True}}


def button(bid: str, sender: str = A) -> dict:
    return {"from": sender, "type": "interactive", "interactive": {"type": "button_reply",
            "button_reply": {"id": bid, "title": bid}}}


def consented(store: UserStore, lang: str = "ha", sender: str = A) -> UserStore:
    run_handle(text("Sannu" if lang == "ha" else "Hello", sender), store=store)
    run_handle(button("consent_ok", sender), store=store)
    return store


# --- consent gate -------------------------------------------------------------

def test_first_contact_gets_notice_with_buttons_and_no_model_call() -> None:
    calls: list = []
    outs, store = run_handle(voice(), voice_calls=calls)
    assert calls == []                                   # nothing reached a model
    assert len(outs) == 2 and outs[0].buttons is None and outs[1].buttons == NOTICE_BUTTONS
    assert all(PRIVACY_URL in o.text and "Meta" in o.text for o in outs)
    assert not store.get(user_key(A, make_settings())).consented


def test_messages_before_consent_keep_getting_the_notice() -> None:
    store = UserStore(":memory:")
    calls: list = []
    run_handle(text("Nawa aka ware wa ilimi?"), store=store)
    outs, _ = run_handle(voice(), store=store, voice_calls=calls)
    assert calls == [] and outs[-1].buttons == NOTICE_BUTTONS


@pytest.mark.parametrize("agree", [button("consent_ok"), text("OK"), text("Na yarda"), text("i agree")])
def test_consent_by_button_or_text_then_voice_is_processed(agree: dict) -> None:
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store)
    outs, _ = run_handle(agree, store=store)
    assert outs[0].text == t("consent_thanks", "ha")
    calls: list = []
    outs, _ = run_handle(voice(), store=store, voice_calls=calls)
    assert calls == ["ha"] and outs[0].text == "VOICE[ha]"


def test_yes_is_not_consent() -> None:
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store)
    outs, _ = run_handle(text("Eh"), store=store)
    assert outs[-1].buttons == NOTICE_BUTTONS


def test_consent_with_unknown_language_asks_for_it() -> None:
    outs, store = run_handle(text("OK"))           # first message ever is "OK": consent, language unclear
    assert outs[0].buttons == LANG_BUTTONS
    assert store.get(user_key(A, make_settings())).consented


def test_emergency_and_delete_work_before_consent() -> None:
    from app.guardrails.emergency import EMERGENCY_REPLY
    assert run_handle(text("Matata tana zubar da jini"))[0][0].text == EMERGENCY_REPLY
    assert run_handle(text("GOGE BAYANAI NA"))[0][0].text == DELETED_REPLY


def test_deletion_resets_consent() -> None:
    store = consented(UserStore(":memory:"))
    run_handle(text("GOGE BAYANAI NA"), store=store)
    assert store.get(user_key(A, make_settings())) is None
    outs, _ = run_handle(text("Sannu"), store=store)
    assert outs[-1].buttons == NOTICE_BUTTONS


# --- notice -------------------------------------------------------------------

@pytest.mark.parametrize("lang, source", [("ha", "detected"), ("en", "detected"), ("ha", "chosen"),
                                          ("en", "chosen"), (None, None)])
def test_notice_is_two_messages_hausa_then_english_within_limits(lang, source) -> None:
    ha, en = first_contact_notice(lang, source)
    assert ha.startswith("*Barka da zuwa Kasafi*") and en.startswith("*Welcome to Kasafi*")
    assert len(en) <= 1024                                   # the English one carries the buttons
    assert all(len(title) <= 20 for _, title in NOTICE_BUTTONS) and len(NOTICE_BUTTONS) <= 3


def test_notice_states_detected_language_in_both_languages() -> None:
    ha, en = first_contact_notice("en", "detected")
    assert "I'll reply in English. Switch any time with /hausa" in en
    assert "zan riƙa amsa da Turanci. Don sauyawa, aika /hausa" in ha
    assert "Which language" in first_contact_notice(None, None)[1]


# --- language -----------------------------------------------------------------

def test_first_message_language_is_detected_and_stored() -> None:
    _, store = run_handle(text("How much was allocated to health in 2026?"))
    u = store.get(user_key(A, make_settings()))
    assert (u.lang, u.lang_source) == ("en", "detected")


@pytest.mark.parametrize("cmd, lang", [("/hausa", "ha"), ("Hausa", "ha"), ("/english", "en"), ("English", "en"),
                                       ("Turanci", "en"), ("turanci.", "en")])
def test_language_commands_after_consent(cmd: str, lang: str) -> None:
    store = consented(UserStore(":memory:"), lang="en" if lang == "ha" else "ha")
    outs, _ = run_handle(text(cmd), store=store)
    assert outs[0].text == t("lang_set", lang)
    calls: list = []
    run_handle(voice(), store=store, voice_calls=calls)
    assert calls == [lang]


def test_language_button_before_consent_resends_notice_in_that_language() -> None:
    store = UserStore(":memory:")
    run_handle(text("Sannu"), store=store)
    outs, _ = run_handle(button("lang_en"), store=store)
    assert outs[-1].buttons == NOTICE_BUTTONS and "I'll reply in English." in outs[-1].text
    assert not store.get(user_key(A, make_settings())).consented   # choosing a language isn't consent


def test_sentence_containing_english_is_not_a_command() -> None:
    store = consented(UserStore(":memory:"))
    outs, _ = run_handle(text("English version of the 2026 budget?"), store=store)
    assert outs[0].text.startswith("Kasafi (gwaji)")


# --- limits and spend cap -------------------------------------------------------

def test_per_number_voice_limit() -> None:
    s = make_settings(kasafi_voice_per_day=2)
    store = consented(UserStore(":memory:"))
    calls: list = []
    for _ in range(3):
        outs, _ = run_handle(voice(), store=store, settings=s, voice_calls=calls)
    assert len(calls) == 2 and outs[0].text == t("voice_limit", "ha", n=2)


def test_per_number_question_limit_is_per_user() -> None:
    s = make_settings(kasafi_questions_per_day=1)
    store = consented(consented(UserStore(":memory:")), sender="2340000000002")
    assert run_handle(text("Tambaya 1"), store=store, settings=s)[0][0].text.startswith("Kasafi (gwaji)")
    assert run_handle(text("Tambaya 2"), store=store, settings=s)[0][0].text == t("question_limit", "ha", n=1)
    other = run_handle(text("Tambaya", sender="2340000000002"), store=store, settings=s)[0][0].text
    assert other.startswith("Kasafi (gwaji)")                                # another number isn't affected


def test_global_spend_cap_blocks_model_calls_for_everyone() -> None:
    s = make_settings(kasafi_daily_spend_cap_usd=0.05, kasafi_cost_per_voice_usd=0.02)
    store = consented(consented(UserStore(":memory:"), lang="en", sender="2340000000002"))
    calls: list = []
    run_handle(voice(), store=store, settings=s, voice_calls=calls)                      # 0.02
    run_handle(voice("2340000000002"), store=store, settings=s, voice_calls=calls)       # 0.04
    outs, _ = run_handle(voice(), store=store, settings=s, voice_calls=calls)           # would be 0.06
    assert len(calls) == 2 and outs[0].text == t("busy", "ha")
    assert store.spent_today() == pytest.approx(0.04)


# --- closed pilot fallback ------------------------------------------------------

def test_closed_mode_serves_only_pilot_numbers() -> None:
    s = make_settings(kasafi_open_access=False, kasafi_pilot_numbers=A)
    from app.whatsapp.messages import NOT_IN_PILOT
    assert run_handle(text("Sannu", "2349999999999"), settings=s)[0][0].text == NOT_IN_PILOT
    assert run_handle(text("Sannu"), settings=s)[0][-1].buttons == NOTICE_BUTTONS     # pilot still needs consent


def test_exempt_number_skips_limits_and_cap_but_still_counts_spend() -> None:
    s = make_settings(kasafi_voice_per_day=1, kasafi_questions_per_day=1, kasafi_daily_spend_cap_usd=0.01,
                      kasafi_cost_per_voice_usd=0.02, kasafi_exempt_numbers="+234 000 000 0001")
    store = consented(consented(UserStore(":memory:")), sender="2340000000002")
    calls: list = []
    for _ in range(3):
        run_handle(voice(), store=store, settings=s, voice_calls=calls)
        assert run_handle(text("Tambaya"), store=store, settings=s)[0][0].text.startswith("Kasafi (gwaji)")
    assert len(calls) == 3                                           # no voice limit, no cap for the exempt number
    assert store.spent_today() == pytest.approx(0.06)                # ...but its spend still counts
    outs, _ = run_handle(voice("2340000000002"), store=store, settings=s, voice_calls=calls)
    assert outs[0].text == t("busy", "ha") and len(calls) == 3       # everyone else is capped


def test_exempt_number_still_needs_consent() -> None:
    s = make_settings(kasafi_exempt_numbers=A)
    calls: list = []
    outs, _ = run_handle(voice(), settings=s, voice_calls=calls)
    assert calls == [] and outs[-1].buttons == NOTICE_BUTTONS
