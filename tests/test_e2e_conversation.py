"""End-to-end conversations through the real webhook handler (app/whatsapp/webhook.py: `_reply`, delivery,
duplicate suppression) and the real conversation flow, against the dev database (PostGIS boundaries and
facilities, the traces table). Model and satellite clients are stubbed with recorded replies where the path is
deterministic. Every scripted turn must get exactly one reply, or the expected sequence: never silence, never a
duplicate.

Skipped without the dev database; `KASAFI_E2E_REQUIRED=1` (set by deploy/deploy.sh) turns the skip into a failure.
The 1 Nov live silence (a resumed place answer crashing after "skip") only showed in a real multi-turn
conversation with the database on; this suite covers that path.
"""

from __future__ import annotations

import asyncio
import itertools
import os
from dataclasses import dataclass, field
from typing import Any

import pytest
from pydantic import SecretStr

from app.config import get_settings
from app.geo.location import memory
from app.guardrails.scope import Verdict, keyword_check
from app.maps.render import MapImage
from app.providers.stt import SpeechResult
from app.users import UserStore, user_key
from app.whatsapp import conversation, webhook
from app.whatsapp.corrections import Resolution, quick_resolve
from app.whatsapp.voice import VoiceOutcome, compose_reply
from tests.helpers import make_settings

LAT, LON = 13.0589127, 5.1673341            # a point inside Sokoto State (the boundaries say which LGA)
_ids = itertools.count(1)


def _dev_db() -> str | None:
    s = get_settings()
    if not s.has_database:
        return None
    try:
        import psycopg
        with psycopg.connect(s.db_url(), connect_timeout=3) as c:
            c.execute("SELECT 1 FROM lga LIMIT 1").fetchone()
            c.execute("SELECT 1 FROM facility LIMIT 1").fetchone()
        return s.db_url()                       # DATABASE_URL, or the one built from POSTGRES_PASSWORD on dev
    except Exception:              # noqa: BLE001
        return None


DEV_DB = _dev_db()
if DEV_DB is None and os.environ.get("KASAFI_E2E_REQUIRED") == "1":
    pytest.fail("KASAFI_E2E_REQUIRED=1 but the dev database (lga, facility tables) is not reachable", pytrace=False)
pytestmark = pytest.mark.skipif(DEV_DB is None, reason="dev database with boundaries and facilities not available")


# --- the fakes -----------------------------------------------------------------------------------------------------

class FakeWA:
    """Records what the webhook would send to WhatsApp."""
    sent: list[tuple[str, str, Any]] = []

    async def send_text(self, to, body):
        FakeWA.sent.append(("text", to, body))
        return {}

    async def send_buttons(self, to, body, buttons):
        FakeWA.sent.append(("buttons", to, body))
        return {}

    async def send_location_request(self, to, body):
        FakeWA.sent.append(("location_request", to, body))
        return {}

    async def send_location(self, to, latitude, longitude, name="", address=""):
        FakeWA.sent.append(("location", to, name))
        return {}

    async def send_image(self, to, jpeg, caption=""):
        FakeWA.sent.append(("image", to, caption))
        return {}

    async def send_template(self, to, name, lang, values):
        FakeWA.sent.append(("template", to, name))
        return {}

    async def download_media(self, media_id, *, max_bytes=0):
        return b""

    async def aclose(self):
        return None


@dataclass
class Stub:
    """A recorded answer, as answer_from_documents would return it."""
    text: str
    found: bool = True
    needs_size: bool = False
    needs_pin: bool = False
    sources: list = field(default_factory=list)
    working: str = ""
    quotes: str = ""
    maps: list = field(default_factory=list)
    clarify: Any = None
    offer: Any = None


PLACE_TEXT = "*What the satellite record shows for this spot ({lga} LGA)*\n\nThis rainy season (2026) the plot was about as green as in normal years.\n\n{shape}"
BUDGET_TEXT = "For the Ministry of Works, the 2026 approved budget (capital) is ₦12.50 billion.\n\n📄 *Sources:* Sokoto State FY 2026 Budget, p. 61"
VOICE_Q = SpeechResult(transcript="Nawa aka ware wa noma a 2026?", english="How much was allocated to agriculture in 2026?",
                       language="ha", confidence="high", needs_confirmation=False)


async def recorded_answer(question: str, lang: str, *, settings, notify=None, history=None, place=None):
    """The model-backed answer, replaced by recorded replies keyed on the question's words."""
    q = question.lower()
    from app.place import planner as P
    if (r := P.area_route(question, "", place)):             # a ward / LGA / state question: the real code path
        import psycopg
        from datetime import date
        with psycopg.connect(DEV_DB) as c:
            aa = P.area_answer(c, question, "", lang, r[0], r[1], date.today(), place=place)
        return Stub(aa.text, aa.found, needs_pin=aa.needs_pin, working=aa.working, maps=aa.specs)
    if "farm" in q or "gonata" in q:
        if not place or place.get("lat") is None:
            return Stub(conversation.t("echo", lang, text=question), False, needs_pin=True)
        shape = place.get("shape") or {}
        if place.get("ask_size") and not shape:
            from app.place.answer import W
            return Stub(W["ha" if lang == "ha" else "en"]["ask_size"], False, needs_size=True)
        if notify is not None:
            await notify("🛰️ I'm checking about 10 years of satellite images for this spot. I'll send it in about a minute.")
        how = {"given_circle": f"the circle of {shape.get('area_ha')} ha you gave", "corners": f"from your {shape.get('corners')} corner pins"
               }.get(shape.get("method"), "a circle of about 1 ha")
        return Stub(PLACE_TEXT.format(lga=place.get("lga", "?"), shape=f"Plot shape: {how}."), working="Per year: 2024 …",
                    maps=[{"kind": "place_chart", "lat": place["lat"], "lon": place["lon"], "lga": place.get("lga", "")},
                          {"kind": "place_map", "lat": place["lat"], "lon": place["lon"], "lga": place.get("lga", "")}])
    if "recheck" in q or "check again" in q:
        return Stub(BUDGET_TEXT + "\n\n(Checked again: the same figure.)", working="rows: 23010105 …")
    return Stub(BUDGET_TEXT, working="Rows added: 1. Capital Expenditure 12,500,000,000.00 (p. 61)")


async def fake_voice(msg, wa, *, lang, settings):
    return VoiceOutcome(compose_reply(VOICE_Q, lang), VOICE_Q)


async def fake_guard(texts, *, settings):
    cat = keyword_check(texts)
    return Verdict(cat, "keyword") if cat else Verdict("ok", "none")


async def fake_resolve(pending, reply, *, settings):
    return quick_resolve(reply) or Resolution("new", reply)


def fake_render(settings, specs, lang, today=None):
    return [MapImage(b"\xff\xd8\xff" + bytes(20), f"image for {s['kind']}") for s in specs]


# --- the harness -----------------------------------------------------------------------------------------------------

@pytest.fixture
def harness(monkeypatch, tmp_path):
    from cryptography.fernet import Fernet
    senders = [f"23480000009{n:02d}" for n in range(1, 8)]
    s = make_settings(database_url=DEV_DB, kasafi_alerts=True, kasafi_alerts_number_key=SecretStr(Fernet.generate_key().decode()),
                      kasafi_exempt_numbers=",".join(senders), kasafi_evidence_images=False,
                      kasafi_state_db=str(tmp_path / "state.db"))
    store = UserStore(str(tmp_path / "state.db"))
    real_handle = conversation.handle

    async def handle_with_stubs(msg, wa, **kw):
        return await real_handle(msg, wa, answer_fn=recorded_answer, voice_fn=fake_voice, guard_fn=fake_guard,
                                 resolve_fn=fake_resolve, **kw)
    monkeypatch.setattr(webhook, "get_settings", lambda: s)
    monkeypatch.setattr(webhook, "get_store", lambda: store)
    monkeypatch.setattr(webhook, "WhatsAppClient", FakeWA)
    monkeypatch.setattr(webhook, "handle", handle_with_stubs)
    monkeypatch.setattr(conversation, "render_specs", fake_render)
    webhook._delivered.clear()
    for n in senders:
        memory.forget(user_key(n, s))

    class H:
        settings = s

        @staticmethod
        def store():
            return store

        @staticmethod
        def key(sender):
            return user_key(sender, s)

        @staticmethod
        def turn(msg, expect=1, label=""):
            """One incoming message through the real webhook reply path; returns the sends. `expect`: the exact
            number of sends, or a predicate on the list. Never silence, never a duplicate."""
            FakeWA.sent = []
            asyncio.run(webhook._reply([msg]))
            sends = list(FakeWA.sent)
            where = label or str(msg.get("text", msg.get("type")))[:60]
            assert sends, f"silence after {where}"
            bodies = [p for k, _, p in sends if k in ("text", "buttons", "location_request")]
            assert len(bodies) == len(set(bodies)), f"duplicate reply after {where}: {bodies}"
            assert all(b.strip() for b in bodies), f"empty reply after {where}"
            if callable(expect):
                assert expect(sends), f"unexpected sequence after {where}: {[(k, str(p)[:60]) for k, _, p in sends]}"
            else:
                assert len(sends) == expect, f"{len(sends)} sends after {where}, expected {expect}: " \
                                             f"{[(k, str(p)[:60]) for k, _, p in sends]}"
            return sends
    return H


def text(body, sender):
    return {"from": sender, "id": f"wamid.e2e{next(_ids)}", "type": "text", "text": {"body": body}}


def pin(lat, lon, sender):
    return {"from": sender, "id": f"wamid.e2e{next(_ids)}", "type": "location", "location": {"latitude": lat, "longitude": lon}}


def button(bid, sender):
    return {"from": sender, "id": f"wamid.e2e{next(_ids)}", "type": "interactive",
            "interactive": {"type": "button_reply", "button_reply": {"id": bid, "title": bid}}}


def audio(sender):
    return {"from": sender, "id": f"wamid.e2e{next(_ids)}", "type": "audio", "audio": {"id": "media-1", "mime_type": "audio/ogg"}}


def consented(h, sender, lang="en"):
    store = h.store()
    store.create(h.key(sender), lang)
    store.give_consent(h.key(sender))


def bodies(sends):
    return [str(p) for k, _, p in sends if k != "image"]


# --- the scripts -----------------------------------------------------------------------------------------------------

def test_consent_language_pin_place_question_size_and_skip(harness):
    h, me = harness, "2348000000901"
    sends = h.turn(text("Sannu", me), 2, "first contact")                        # the notice: Hausa, then English with buttons
    assert sends[1][0] == "buttons" and "Kasafi" in sends[0][2]
    sends = h.turn(text("Na yarda", me), 1, "consent")
    assert "Na gode" in sends[0][2] or "Mun gode" in sends[0][2] or "gode" in sends[0][2].lower()
    sends = h.turn(text("english", me), 1, "language switch")
    assert "English" in sends[0][2]
    sends = h.turn(pin(LAT, LON, me), 2, "pin")                                     # the location notice, then "Got it"
    assert sends[1][2].startswith("📍 Got it: you're in")
    sends = h.turn(text("How green was my farm in 2024?", me), 1, "place question")
    assert sends[0][2].startswith("I couldn't draw this farm's outline")
    sends = h.turn(text("skip", me), lambda s: [k for k, _, _ in s] == ["text", "text", "image", "image"], "skip")
    assert sends[0][2].startswith("🛰️") and "satellite record" in sends[1][2] and "circle of about 1 ha" in sends[1][2]
    h.turn(text("show working", me), 1, "show working")


def test_pin_then_how_has_farming_evolved_in_my_ward_is_about_that_ward(harness):
    """The 1 Nov phone test: a pin, then 'How has farming evolved in my ward over the years' got a statewide 2025
    ranking of 232 wards. Now: that ward, named with its LGA, the trend over the years, one map."""
    h, me = harness, "2348000000904"
    consented(h, me, "en")
    sends = h.turn(pin(LAT, LON, me), 2, "pin")
    assert sends[1][2].startswith("📍 Got it: you're in")
    sends = h.turn(text("How has farming evolved in my ward over the years", me),
                   lambda s: [k for k, _, _ in s][-2:] == ["text", "image"], "my ward")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: ") and " ward" in body.split("\n")[0] and "Your pin is in" in body
    assert "Since 20" in body and "232 wards" not in body and "244 wards" not in body and "MODIS NDVI" not in body
    sends = h.turn(text("How has farming evolved in my LGA over the years", me),
                   lambda s: [k for k, _, _ in s][-2:] == ["text", "image"], "my LGA")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: wards of ") and "Since 20" in body and "*Ranking (" in body
    sends = h.turn(text("How has farming evolved across the state over the years", me),
                   lambda s: [k for k, _, _ in s][-2:] == ["text", "image"], "the state")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: the 23 LGAs of Sokoto State") and "Sokoto State's farmland greenness" in body


def test_my_ward_in_hausa_and_the_pin_asked_for_when_none_is_on_file(harness):
    h, me = harness, "2348000000905"
    consented(h, me, "ha")
    sends = h.turn(text("Yaya noma ya canza a unguwata tun shekaru?", me), lambda s: s[-1][0] == "location_request", "no pin yet")
    assert "wurin kansa" in sends[-1][2]
    sends = h.turn(pin(LAT, LON, me), lambda s: s[-1][0] == "image", "pin resumes the question")
    body = [p for k, _, p in sends if k == "text" and "Wurinka yana gundumar" in str(p)]
    assert body and body[0].startswith("*Koriyar ƙololuwa: gundumar ") and "Tun 20" in body[0]


def test_a_size_in_kadada_gives_the_circle_of_that_area(harness):
    h, me = harness, "2348000000902"
    consented(h, me, "ha")
    h.turn(pin(LAT, LON, me), 2, "pin")
    sends = h.turn(text("Yaya koriyar gonata a 2024?", me), 1, "place question")
    assert "Girman gonar nawa ne" in sends[0][2]
    # the acknowledgement first, then the progress line, the answer and its two images
    sends = h.turn(text("3 kadada", me), lambda s: [k for k, _, _ in s] == ["text", "text", "text", "image", "image"], "size")
    assert sends[0][2].startswith("An gama: da'irar hekta 1.21") and sends[1][2].startswith("🛰️")
    assert "1.21 ha you gave" in sends[2][2]                                        # the recorded answer saw the shape


def test_corner_pins_then_an_gama_make_the_plot(harness):
    h, me = harness, "2348000000903"
    consented(h, me, "ha")
    h.turn(pin(LAT, LON, me), 2, "pin")
    h.turn(text("Yaya koriyar gonata a 2024?", me), 1, "place question")
    corners = [(LAT, LON), (LAT, LON + 0.002), (LAT + 0.002, LON + 0.002), (LAT + 0.002, LON)]
    for i, (lat, lon) in enumerate(corners, 1):
        sends = h.turn(pin(lat, lon, me), 1, f"corner {i}")
        assert sends[0][2].startswith(f"📍 An karɓi wurin kusurwa na {i}")
    sends = h.turn(text("an gama", me), lambda s: [k for k, _, _ in s] == ["text", "text", "text", "image", "image"], "an gama")
    assert sends[0][2].startswith("An gama: gona ta kusan hekta 4.8") and sends[1][2].startswith("🛰️")
    assert "4 corner pins" in sends[2][2]


def test_pin_nearest_hospital_then_the_next_one(harness):
    h, me = harness, "2348000000904"
    consented(h, me, "en")
    h.turn(pin(LAT, LON, me), 2, "pin")
    first = h.turn(text("nearest hospital", me), lambda s: s and s[0][0] == "text", "nearest hospital")
    assert "hospital" in first[0][2].lower() or "Hospital" in first[0][2]
    nxt = h.turn(text("the next one?", me), lambda s: s and s[0][0] == "text", "next one")
    assert nxt[0][2] != first[0][2]


def test_alert_sign_up_and_daina(harness):
    h, me = harness, "2348000000905"
    consented(h, me, "en")
    sends = h.turn(text("Alert me about floods in Goronyo", me), 1, "sign-up")
    assert sends[0][0] == "buttons" and "floods in Goronyo LGA" in sends[0][2]
    sends = h.turn(button("alert_yes", me), 1, "alert_yes")
    assert h.store().subscription(h.key(me))["hazards"] == ["flood"]
    sends = h.turn(text("DAINA", me), 1, "DAINA")
    assert h.store().subscription(h.key(me)) is None and "alerts" in sends[0][2].lower()


def test_budget_question_show_working_and_recheck(harness):
    h, me = harness, "2348000000906"
    consented(h, me, "en")
    sends = h.turn(text("How much is budgeted for roads in 2026?", me), 2, "budget question")   # the ack, then the answer
    assert sends[0][2].startswith("🔎") or "document" in sends[0][2].lower()
    assert "₦12.50 billion" in sends[1][2]
    sends = h.turn(text("show working", me), 1, "show working")
    assert "Rows added" in sends[0][2]
    sends = h.turn(text("recheck", me), 2, "recheck")
    assert "Checked again" in sends[1][2]


def test_a_voice_note_is_transcribed_and_answered(harness):
    h, me = harness, "2348000000907"
    consented(h, me, "ha")
    sends = h.turn(audio(me), lambda s: len(s) >= 2 and s[0][2].startswith("🎧"), "voice note")
    assert "₦12.50" in sends[-1][2] and any("Nawa aka ware wa noma" in str(p) for _, _, p in sends)
