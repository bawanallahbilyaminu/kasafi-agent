"""The emergency fast path (docs/hazard-and-services.md section 7): what fires, the reply with and without a
location, the maternal preference, the classifier only after consent, nothing but 'fired' in the log, and speed."""

import asyncio
import logging
import time

from app.geo.facilities import Facility
from app.geo.location import Spot, memory
from app.guardrails import emergency as em
from app.users import UserStore, user_key
from app.whatsapp.conversation import handle
from tests.helpers import make_settings

A = "2348000000009"


def _s():
    return make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")


def _fac(name, level="Secondary", lga="Wamakko"):
    return Facility("f", name, level, "", "Public", "", 13.1, 5.2, lga, lga, 2.4)


class Lookup:
    def __init__(self):
        self.calls = []

    async def __call__(self, settings, lat, lon, maternal, lga_pcode=""):
        self.calls.append((lat is not None, maternal, lga_pcode))
        return [("cemonc" if maternal else "hospital", _fac("Kware General Hospital")),
                ("any", _fac("Rinin Tawaye PHC", "Primary"))]


def _run(body, store, lookup=None, classify=None, kind="text", **kw):
    msg = {"from": A, "id": "w", "type": kind, **({"text": {"body": body}} if kind == "text" else kw)}

    async def no_model(text, settings):
        raise AssertionError("no model call expected")
    return asyncio.run(handle(msg, None, store=store, settings=_s(), answer_fn=None, emergency_fn=lookup or Lookup(),
                              classify_fn=classify or no_model))


def _consented(store, lang="en"):
    key = user_key(A, make_settings())
    store.create(key, lang)
    store.give_consent(key)
    return key


def test_before_consent_a_phrase_fires_with_the_location_request_and_a_pin_answers_it() -> None:
    store, lookup = UserStore(":memory:"), Lookup()
    outs = _run("Matata tana zubar da jini", store, lookup)
    assert outs[0].text == "🚨 Wannan yana kama da gaggawa. Ku nemi taimako yanzu."
    assert outs[-1].location_request and not lookup.calls
    outs = _run("", store, lookup, kind="location", location={"latitude": 13.06, "longitude": 5.24})
    assert lookup.calls == [(True, False, "")]
    assert outs[0].text.startswith("Babban asibiti mafi kusa: *Kware General Hospital*, kusan kilomita 2.4")
    assert outs[1].location["name"] == "Kware General Hospital" and not any(o.location_request for o in outs)
    memory.forget(user_key(A, make_settings()))


def test_with_a_point_the_nearest_suitable_facility_and_its_pin_come_at_once() -> None:
    store, lookup = UserStore(":memory:"), Lookup()
    key = _consented(store)
    memory.remember(key, Spot(13.06, 5.24, "NG034021", "Wamakko"))
    t0 = time.perf_counter()
    outs = _run("My wife is in labour and the baby is stuck", store, lookup)
    took = time.perf_counter() - t0
    text = outs[0].text
    assert text.startswith("🚨 This sounds like an emergency. Get help now.")
    assert "Nearest hospital with comprehensive emergency obstetric care: *Kware General Hospital*" in text
    # one line names the pin's hospital first, then the nearer facility of any kind
    assert "*Kware General Hospital*" in text.splitlines()[1]
    assert "; nearest facility of any kind: *Rinin Tawaye PHC* (primary)" in text.splitlines()[1]
    assert outs[1].location["name"] == "Kware General Hospital" and len(outs) == 3
    assert "google.com/maps/dir" in outs[2].text      # the follow-up: no ORS key here, so the link alone
    assert lookup.calls == [(True, True, "")] and took < 3.0
    memory.forget(key)


def test_with_only_the_lga_on_file_its_centre_and_the_request_for_a_pin() -> None:
    store, lookup = UserStore(":memory:"), Lookup()
    key = _consented(store)
    store.set_last_lga(key, "NG034021")
    outs = _run("someone is unconscious", store, lookup)
    assert lookup.calls == [(False, False, "NG034021")]
    assert "(near the centre of Wamakko LGA)" in outs[0].text and outs[-1].location_request
    memory.forget(key)


def test_a_phrase_in_a_data_question_goes_to_the_classifier_after_consent_only() -> None:
    store = UserStore(":memory:")
    asked = []

    async def says(answer):
        async def f(text, settings):
            asked.append(text)
            return answer
        return f
    q = "How many road accident deaths were there in Sokoto in 2025?"
    assert em.detect(q).ambiguous
    outs = _run(q, store)                                   # before consent: no model, err towards firing
    assert outs[0].text.startswith("🚨") and not asked
    _consented(store)
    outs = _run(q, store, classify=asyncio.run(says(False)))
    assert asked == [q] and not outs[0].text.startswith("🚨")
    outs = _run(q, store, classify=asyncio.run(says(None)))      # no answer from the model: fire
    assert outs[0].text.startswith("🚨")
    memory.forget(user_key(A, make_settings()))


def test_health_words_without_a_phrase_fire_only_on_the_classifiers_yes() -> None:
    store = UserStore(":memory:")
    _consented(store)

    async def yes(text, settings):
        return True
    outs = _run("my child is very sick and weak", store, classify=yes)
    assert outs[0].text.startswith("🚨")
    memory.forget(user_key(A, make_settings()))


def test_only_that_it_fired_is_logged(caplog) -> None:
    caplog.set_level(logging.INFO)
    store = UserStore(":memory:")
    _run("My husband was bitten by a snake", store)
    assert "emergency fast path fired (general; location unknown)" in caplog.text
    assert "snake" not in caplog.text.lower() and "husband" not in caplog.text.lower()
    memory.forget(user_key(A, make_settings()))


def test_no_medical_instructions_and_no_unverified_numbers() -> None:
    for lang in ("en", "ha"):
        for line in em.WORDS[lang].values():
            if isinstance(line, str):
                assert not any(w in line.lower() for w in ("press", "apply", "give her", "tablet", "medicine",
                                                           "magani", "112"))
    assert em.contact_lines("en") == []                     # 112 isn't verified yet
