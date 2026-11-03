"""Before consent (2 Nov night): the notice carries a short emergency line; the first message is kept in memory
and handled right after the user accepts, emergency checks first (the classifier, then the understanding step's
'urgent'). A conditional urgent reading opens with "If this is happening now…". Hausa addresses the user with the
respectful plural everywhere, and no literal <br> reaches a payload."""

import asyncio
import re
from types import SimpleNamespace

import pytest

from app.agent import understand as U
from app.geo.location import memory
from app.guardrails import emergency as em
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from app.whatsapp import menu as M
from app.whatsapp import messages as MSG
from tests.helpers import make_settings

SENDER = "2348000000066"


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


async def _no_facilities(*a, **k):
    return []


def _msg(body, n):
    return {"from": SENDER, "id": f"w-first-{n}", "type": "text", "text": {"body": body}}


def _run(msg, store, s, *, classify, understand=_none, answer=None):
    async def default(question, lang, **k):
        return SimpleNamespace(text=f"ANSWER {question}", found=True, sources=[], working="", quotes="")
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer or default, guard_fn=_ok,
                                place_fn=_none, classify_fn=classify, understand_fn=understand,
                                emergency_fn=_no_facilities))


@pytest.fixture
def fresh():
    s = make_settings(kasafi_understanding=True)
    key = user_key(SENDER, s)
    C._first_messages.pop(key, None)
    memory.forget(key)
    return s, UserStore(":memory:"), key


def test_the_notice_carries_the_emergency_line_in_both_languages() -> None:
    ha, en = MSG.first_contact_notice("ha", "detected")
    assert "🚨 Idan gaggawar lafiya ce, kada ku jira: ku je asibiti mafi kusa nan take." in ha
    assert "🚨 In a medical emergency, don't wait: go to the nearest health facility now." in en
    # the same verified numbers as the emergency reply (none until one is verified)
    nums = [ln for ln in em.contact_lines("ha")]
    assert all(n in ha for n in nums) and all(n.split(":")[0] in em.EMERGENCY_REPLY for n in nums)


@pytest.mark.parametrize("layer", ["classifier", "understanding"])
def test_first_ever_message_matata_na_nakuda_then_ok_gets_the_emergency_reply(fresh, layer) -> None:
    s, store, key = fresh
    asked = []

    async def classify(text, settings):
        asked.append(text)
        return layer == "classifier"            # the understanding step is the net when the classifier says no

    async def understand(*a, **k):
        return U.Understanding(kind="new", capability="facility", care="maternal", urgent=True,
                               urgent_reason="woman in labour now", restatement="My wife is in labour now")
    outs = _run(_msg("Matata na naƙuda", 1), store, s, classify=classify, understand=understand)
    assert "🚨 Idan gaggawar lafiya ce" in outs[0].text and outs[1].buttons      # the notice, with the line
    assert asked == []                                                         # no model before consent
    outs = _run(_msg("Na yarda", 2), store, s, classify=classify, understand=understand)
    assert outs[0].text.startswith("🚨 Wannan yana kama da gaggawa")             # the emergency reply, first
    assert asked == ["Matata na naƙuda"] and key not in C._first_messages


def test_a_first_question_that_isnt_an_emergency_is_answered_after_consent(fresh) -> None:
    s, store, key = fresh

    async def no(*a, **k):
        return False
    _run(_msg("How much is the 2026 health budget?", 1), store, s, classify=no)
    outs = _run(_msg("OK", 2), store, s, classify=no)
    assert outs[0].text.startswith("Thank you. Here is the answer to your first message.")
    assert outs[-1].text.startswith("ANSWER How much is the 2026 health budget?")


def test_with_no_language_yet_the_first_question_waits_for_it(fresh) -> None:
    s, store, key = fresh

    async def no(*a, **k):
        return False
    store.create(key, None)                               # e.g. a first message whose language wasn't detected
    C._keep_first(key, _msg("12345", 1))
    outs = _run(_msg("OK", 2), store, s, classify=no)
    assert outs[0].buttons and key in C._first_messages   # which language? the question still kept
    btn = {"from": SENDER, "id": "w-first-3", "type": "interactive",
           "interactive": {"type": "button_reply", "button_reply": {"id": "lang_en", "title": "English"}}}
    outs = _run(btn, store, s, classify=no)
    assert outs[0].text.startswith("Thank you. Here is the answer") and outs[-1].text.startswith("ANSWER 12345")


def test_delete_my_data_drops_the_kept_first_message(fresh) -> None:
    s, store, key = fresh

    async def no(*a, **k):
        return False
    _run(_msg("How much is the 2026 health budget?", 1), store, s, classify=no)
    assert key in C._first_messages
    _run(_msg("DELETE MY DATA", 2), store, s, classify=no)
    assert key not in C._first_messages


def test_a_conditional_urgent_reading_opens_with_if_this_is_happening_now(fresh) -> None:
    s, store, key = fresh
    store.create(key, "en")
    store.give_consent(key)

    async def no(*a, **k):
        return False

    async def understand(*a, **k):
        return U.Understanding(kind="new", capability="facility", care="children", urgent=True,
                               urgent_reason="conditional: if the child has trouble breathing",
                               restatement="Which hospital near me if my child has trouble breathing?")
    outs = _run(_msg("Which hospital near me can I go to if my child has trouble breathing?", 1), store, s,
                classify=no, understand=understand)
    assert outs[0].text.startswith("🚨 If this is happening now, it is an emergency. Get help now.")
    store.set_lang(key, "ha")
    outs = _run(_msg("Wane asibiti zan je idan yarona yana fama da numfashi?", 2), store, s, classify=no,
                understand=understand)
    assert outs[0].text.startswith("🚨 Idan hakan na faruwa yanzu")


# --- Hausa: the respectful plural, and no literal <br> ------------------------------------------------------------

def _strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)
    elif isinstance(v, (list, tuple)):
        for x in v:
            yield from _strings(x)


SINGULAR = re.compile(r"\b(?:ka|kana|kake|maka)\b|\b(?:wurin|tambayar|tambayoyin|saƙon|hukumar|garin|gonar|yankin|"
                      r"gundumar|harshen|amincewar|wayar|bayanan)ka\b", re.IGNORECASE)
ALLOWED = ("ka iya shafarta",)            # 'that may affect it': not 'you'


def _hausa_texts():
    from app.agent.conversational import HELP
    from app.geo.facilities import WORDS as FAC
    from app.place.answer import W as PLACE
    yield from _strings({k: v.get("ha", "") for k, v in MSG.TEXTS.items()})
    yield from _strings(MSG.first_contact_notice("ha", "detected")[0])
    yield from _strings(M.WORDS["ha"])
    yield from _strings(em.WORDS["ha"])
    yield from _strings(FAC["ha"])
    yield from _strings(PLACE["ha"])
    yield from _strings(HELP["ha"])
    yield from _strings(C.CORRECTION_WORDS["ha"])


def test_hausa_addresses_the_user_with_the_respectful_plural() -> None:
    bad = [s for s in _hausa_texts() if SINGULAR.search(s) and not any(a in s for a in ALLOWED)]
    bad = [s for s in bad if s != M.WORDS["ha"]["about"]]        # the user's own question to Kasafi
    assert bad == []


@pytest.mark.parametrize("lang", ["ha", "en"])
def test_no_literal_br_reaches_a_whatsapp_payload(lang) -> None:
    p = M.menu_payload(lang)
    texts = list(_strings(p)) + list(_strings(M.WORDS[lang])) + list(_strings({k: v.get(lang, "") for k, v in
                                                                                 MSG.TEXTS.items()}))
    texts += list(MSG.first_contact_notice(lang, "detected"))
    assert not any("<br" in t.lower() for t in texts)
