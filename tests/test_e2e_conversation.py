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

    async def send_list(self, to, body, button, sections, header=""):
        FakeWA.sent.append(("list", to, {"body": body, "button": button, "sections": sections}))
        return {}

    typing: list = []

    async def mark_typing(self, message_id):
        FakeWA.typing.append(message_id)

    async def send_location(self, to, latitude, longitude, name="", address=""):
        FakeWA.sent.append(("location", to, {"latitude": latitude, "longitude": longitude, "name": name, "address": address}))
        return {}

    async def send_image(self, to, jpeg, caption=""):
        FakeWA.sent.append(("image", to, caption))
        return {}

    async def send_document(self, to, data, filename, caption=""):
        FakeWA.sent.append(("document", to, {"filename": filename, "pdf": data[:4], "caption": caption}))
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
    parts: list = field(default_factory=list)
    deep: Any = None


PLACE_TEXT = "*What the satellite record shows for this spot ({lga} LGA)*\n\nThis rainy season (2026) the plot was about as green as in normal years.\n\n{shape}"
BUDGET_TEXT = "For the Ministry of Works, the 2026 approved budget (capital) is ₦12.50 billion.\n\n📄 *Sources:* Sokoto State FY 2026 Budget, p. 61"
VOICE_Q = SpeechResult(transcript="Nawa aka ware wa noma a 2026?", english="How much was allocated to agriculture in 2026?",
                       language="ha", confidence="high", needs_confirmation=False)


async def recorded_answer(question: str, lang: str, *, settings, notify=None, history=None, place=None,
                          understanding=None):
    """The model-backed answer, replaced by recorded replies keyed on the question's words."""
    q = question.lower()
    from app.agent.deep import deep_answer, deep_question, render
    if deep_question(question):              # the real deep analysis on the dev library, models stubbed
        import psycopg
        from tests.test_deep import StubModel
        with psycopg.connect(DEV_DB) as c:
            r = await deep_answer(c, question, question, lang, client=StubModel(), open_client=StubModel(),
                                  settings=settings, notify=notify)
        summary, parts = render(r, lang)
        return Stub(summary, bool(r.claims), parts=parts, deep=r)
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
            await notify("🛰️ I'm checking about 10 years of satellite images for this spot. The first time takes about 1–2 minutes.")
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
    senders = [f"23480000009{n:02d}" for n in range(1, 12)]
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
    sends = h.turn(text("skip", me), lambda s: [k for k, _, _ in s] == ["text", "text", "image", "image", "buttons"], "skip")
    assert sends[0][2].startswith("🛰️") and "satellite record" in sends[1][2] and "circle of about 1 ha" in sends[1][2]
    h.turn(text("show working", me), 1, "show working")


def test_pin_then_how_has_farming_evolved_in_my_ward_is_about_that_ward(harness):
    """The 1 Nov phone test: a pin, then 'How has farming evolved in my ward over the years' got a statewide 2025
    ranking of 232 wards. Now: that ward, named with its LGA, the trend over the years, one map."""
    h, me = harness, "2348000000908"
    consented(h, me, "en")
    sends = h.turn(pin(LAT, LON, me), 2, "pin")
    assert sends[1][2].startswith("📍 Got it: you're in")
    sends = h.turn(text("How has farming evolved in my ward over the years", me),
                   lambda s: [k for k, _, _ in s][-3:] == ["text", "image", "buttons"], "my ward")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: ") and " ward" in body.split("\n")[0] and "Your pin is in" in body
    assert "Since 20" in body and "232 wards" not in body and "244 wards" not in body and "MODIS NDVI" not in body
    sends = h.turn(text("How has farming evolved in my LGA over the years", me),
                   lambda s: [k for k, _, _ in s][-3:] == ["text", "image", "buttons"], "my LGA")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: wards of ") and "Since 20" in body and "*Ranking (" in body
    sends = h.turn(text("How has farming evolved across the state over the years", me),
                   lambda s: [k for k, _, _ in s][-3:] == ["text", "image", "buttons"], "the state")
    body = [p for k, _, p in sends if k == "text"][-1]
    assert body.startswith("*Peak greenness: the 23 LGAs of Sokoto State") and "Sokoto State's farmland greenness" in body


def test_my_ward_in_hausa_and_the_pin_asked_for_when_none_is_on_file(harness):
    h, me = harness, "2348000000909"
    consented(h, me, "ha")
    sends = h.turn(text("Yaya noma ya canza a unguwata tun shekaru?", me), lambda s: s[-1][0] == "location_request", "no pin yet")
    assert "wurin kansa" in sends[-1][2]
    sends = h.turn(pin(LAT, LON, me), lambda s: s[-2][0] == "image" and s[-1][0] == "buttons", "pin resumes the question")
    body = [p for k, _, p in sends if k == "text" and "Wurinku yana gundumar" in str(p)]
    assert body and body[0].startswith("*Koriyar ƙololuwa: gundumar ") and "Tun 20" in body[0]


def test_a_size_in_kadada_gives_the_circle_of_that_area(harness):
    h, me = harness, "2348000000902"
    consented(h, me, "ha")
    h.turn(pin(LAT, LON, me), 2, "pin")
    sends = h.turn(text("Yaya koriyar gonata a 2024?", me), 1, "place question")
    assert "Girman gonar nawa ne" in sends[0][2]
    # the acknowledgement first, then the progress line, the answer and its two images
    sends = h.turn(text("3 kadada", me), lambda s: [k for k, _, _ in s] == ["text", "text", "text", "image", "image", "buttons"], "size")
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
    sends = h.turn(text("an gama", me), lambda s: [k for k, _, _ in s] == ["text", "text", "text", "image", "image", "buttons"], "an gama")
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


def _pins_check(sends, label):
    """Every pin sent carries the coordinates only (no name, no address: a name makes Google Maps search it and land
    on another place), and a text in the same reply has the coordinate-only link to exactly that point, which is a
    facility's stored point in the database."""
    import psycopg
    pins = [p for k, _, p in sends if k == "location"]
    assert pins, f"no pin after {label}"
    texts = "\n".join(str(p) for k, _, p in sends if k == "text")
    with psycopg.connect(DEV_DB) as c:
        for loc in pins:
            assert not loc["name"] and not loc["address"], f"the pin carries a name or address after {label}: {loc}"
            link = f"https://www.google.com/maps/search/?api=1&query={loc['latitude']:.6f},{loc['longitude']:.6f}"
            assert link in texts, f"no coordinate link for the pin after {label}"
            row = c.execute("SELECT name FROM facility WHERE abs(ST_Y(geom) - %s) < 1e-6 AND abs(ST_X(geom) - %s) < 1e-6",
                            (loc["latitude"], loc["longitude"])).fetchone()
            assert row is not None, f"the pin is not a stored facility point after {label}"
            assert f"*{row[0]}*" in texts, f"the text doesn't name the pin's facility ({row[0]}) after {label}"


def test_every_pin_has_no_name_and_a_coordinate_link_to_the_stored_point(harness):
    h, me = harness, "2348000000910"
    consented(h, me, "en")
    h.turn(pin(LAT, LON, me), 2, "pin")
    _pins_check(h.turn(text("nearest hospital", me), lambda s: s and s[0][0] == "text", "nearest hospital"), "nearest hospital")
    _pins_check(h.turn(text("the next one?", me), lambda s: s and s[0][0] == "text", "next one"), "next one")
    _pins_check(h.turn(text("route", me), lambda s: s and s[0][0] == "text", "route"), "route")
    _pins_check(h.turn(text("My wife is in labour and the baby is stuck", me), lambda s: any(k == "location" for k, _, _ in s), "emergency"),
                "emergency")


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
    # a quick answer: the typing indicator, no progress line; its buttons on the answer itself
    sends = h.turn(text("How much is budgeted for roads in 2026?", me), 1, "budget question")
    assert sends[0][0] == "buttons" and "₦12.50 billion" in sends[0][2]
    sends = h.turn(text("show working", me), 1, "show working")
    assert "Rows added" in sends[0][2]
    sends = h.turn(text("recheck", me), 1, "recheck")                     # quick: no progress line
    assert "Checked again" in sends[0][2]


def test_a_missing_document_is_fetched_as_a_word_file_converted_and_cited(harness, tmp_path, monkeypatch):
    """Office documents: question -> the document isn't in the library -> a .docx on an allowlisted site is fetched
    through the real acquisition path (allowlist, robots, type by bytes), converted to PDF, indexed, and the reply
    cites a page of the converted PDF, saying so."""
    import httpx
    import psycopg

    from app.acquisition import convert, library
    from app.agent.answer import Evidence, format_citations, load_catalog
    from app.retrieval.search import search
    from tests.office_fixtures import docx_bytes, fake_converter
    if convert.soffice_path() is None:
        monkeypatch.setattr(convert, "CONVERTER", fake_converter)
    url = "https://sokotostate.gov.ng/wp-content/uploads/2026/03/water-supply-plan-2026.docx"
    body = docx_bytes(["Sokoto State Water Supply Plan 2026", "Budget lines by agency"],
                      [["Agency", "2026 Approved Budget"], ["Rural Water and Sanitation Agency", "12,345,678.00"]])
    responses = {"https://sokotostate.gov.ng/robots.txt": httpx.Response(200, text="User-agent: *\nAllow: /\n"),
                 url: httpx.Response(200, content=body, headers={"content-type": "application/octet-stream"})}

    async def confirm(description, pages, existing_ids, client, settings):
        return {"match": True, "id": "e2e-office-plan", "title": "Sokoto State Water Supply Plan 2026", "category": "plan",
                "year": 2026, "publisher": "Sokoto State Government"}
    monkeypatch.setattr(library, "confirm_document", confirm)
    s = make_settings(database_url=DEV_DB, kasafi_fetch_enabled=True, kasafi_fetch_dir=str(tmp_path / "fetched"))

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        """What answer_from_documents does for a missing document, with the real fetch and index: the planner's
        model calls are stood in for by the fixed URL and the confirm stub."""
        await notify("📥 I don't have this document yet. Looking for it on government and partner sites…")
        with psycopg.connect(DEV_DB) as conn:
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: responses.get(str(r.url), httpx.Response(404)))) as http:
                acq = await library.fetch_and_index(conn, url, "Sokoto water supply plan 2026", settings=s, client=None, http=http)
            assert acq.status == "indexed", acq
            load_catalog(conn)
            hit = search(conn, "Rural Water and Sanitation Agency 12,345,678.00", k=1, doc_ids=[acq.doc_id])[0]
            e = Evidence(1, acq.doc_id, acq.title, 2026, hit.page, "text", hit.text)
        return Stub(f"The plan budgets ₦12,345,678.00 for the Rural Water and Sanitation Agency in 2026 [1].\n\n"
                    f"📄 *Sources:*\n{format_citations([e], lang)}", working="rows: Rural Water and Sanitation Agency 12,345,678.00 (p. 1)")

    import sys
    monkeypatch.setattr(sys.modules[__name__], "recorded_answer", answer)   # the harness looks the stub up by name
    h, me = harness, "2348000000911"
    consented(h, me, "en")
    try:
        sends = h.turn(text("What does the Sokoto water supply plan 2026 budget for the Rural Water and Sanitation Agency?", me),
                       lambda s_: [k for k, _, _ in s_][-1] in ("text", "buttons") and len(s_) >= 2,
                       "missing document fetched as a Word file")
        reply = [p for k, _, p in sends if k in ("text", "buttons")][-1]
        assert "12,345,678.00" in reply and "page 1 (PDF converted from the Word original)" in reply
        assert any("Looking for it" in str(p) for k, _, p in sends if k == "text")
        assert (tmp_path / "fetched" / "e2e-office-plan.docx").exists() and (tmp_path / "fetched" / "e2e-office-plan.pdf").exists()
    finally:
        with psycopg.connect(DEV_DB) as conn:
            conn.execute("DELETE FROM documents WHERE id = 'e2e-office-plan'")
            conn.commit()


def test_a_voice_note_is_transcribed_and_answered(harness):
    h, me = harness, "2348000000907"
    consented(h, me, "ha")
    sends = h.turn(audio(me), lambda s: len(s) >= 2 and s[0][2].startswith("🎧"), "voice note")
    assert "₦12.50" in sends[-1][2] and any("Nawa aka ware wa noma" in str(p) for _, _, p in sends)


def test_a_broad_question_gets_a_deep_analysis_in_several_messages_and_the_brief_as_a_pdf(harness):
    """'Whats the state of PHCs' (00:59) got the registry's one-line count; now: progress per stage, a summary,
    a message per dimension, the differences and gaps, and the full brief as a PDF on request."""
    h, me = harness, "2348000000911"
    consented(h, me, "en")
    store = h.store()
    before = store.usage(h.key(me))[1]
    sends = h.turn(text("Whats the state of PHCs in sokoto state", me),
                   lambda s: len([x for x in s if x[0] == "text"]) >= 5, "deep question")
    bodies = [p for k, _, p in sends if k == "text"]
    assert any(b.startswith("📚 Reading") for b in bodies) and any(b.startswith("*facilities") for b in bodies)
    assert not any("health facilities" in b and b.strip().endswith(".") and len(b) < 80 for b in bodies[:2])
    assert any("full brief" in b for b in bodies)
    assert store.usage(h.key(me))[1] - before == 2                     # a deep answer counts double
    sends = h.turn(text("full brief", me), 1, "full brief")
    kind, _, doc = sends[0]
    assert kind == "document" and doc["filename"] == "kasafi-brief.pdf" and doc["pdf"] == b"%PDF"


# --- 2 Nov evening, live: messages about Kasafi and facility claims, with the understanding step on -----------------

def _with_readings(monkeypatch, h):
    """The harness with the understanding step on, its readings replayed from evals/understanding/recorded.json by
    message, and the conversational reply's Muse Spark call stubbed (the route, the trace and delivery are real)."""
    import json
    from pathlib import Path

    import app.providers.meta as M
    from app.agent import understand as U
    cases = json.loads(Path("evals/understanding/cases.json").read_text(encoding="utf-8"))["cases"]
    recorded = json.loads(Path("evals/understanding/recorded.json").read_text(encoding="utf-8"))
    by_message = {}
    for c in cases:
        d = {k: v for k, v in recorded[c["id"]].items() if k != "seconds"}
        by_message.setdefault((c["message"], bool(c["turns"])), U.Understanding(**d))

    async def understand_fn(text, history, place, settings, fallbacks=None):
        # no reading recorded: the keyword routing decides
        return by_message.get((text, bool(history))) or by_message.get((text, not history))

    class Model:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        async def chat(self, messages, **kw):
            hausa = "Hausa" in messages[-1]["content"].split("USER'S LANGUAGE:")[1][:12]
            return type("R", (), {"content": "Ni ne Kasafi." if hausa else "I'm Kasafi, an assistant for Sokoto."})()
    monkeypatch.setattr(M, "MetaClient", Model)
    s = h.settings.model_copy(update={"kasafi_understanding": True})
    monkeypatch.setattr(webhook, "get_settings", lambda: s)

    async def handle(msg, wa, **kw):
        kw["settings"] = s
        return await conversation.handle(msg, wa, answer_fn=recorded_answer, voice_fn=fake_voice, guard_fn=fake_guard,
                                         resolve_fn=fake_resolve, understand_fn=understand_fn, **kw)
    monkeypatch.setattr(webhook, "handle", handle)


def test_who_are_you_and_thanks_get_kasafis_own_reply_never_the_documents(harness, monkeypatch):
    h, me, ha = harness, "2348000000910", "2348000000911"
    _with_readings(monkeypatch, h)
    consented(h, me, "en")
    consented(h, ha, "ha")
    for body, who in (("Who are you?", me), ("Kai wanene?", ha), ("What can you do?", me), ("Me za ka iya yi?", ha),
                      ("Hello", me), ("Ina kwana", ha)):
        sends = h.turn(text(body, who), 1, body)
        assert "couldn't find" not in sends[0][2] and "Ban sami" not in sends[0][2]
        assert sends[0][2] in ("I'm Kasafi, an assistant for Sokoto.", "Ni ne Kasafi.")
    sends = h.turn(text("How much was allocated to works in 2026?", me), 1, "budget")   # quick: no progress line
    assert "Ministry of Works" in sends[0][2]
    sends = h.turn(text("Thanks", me), 1, "thanks")
    assert sends[0][2] == "I'm Kasafi, an assistant for Sokoto."


def test_a_cold_but_uduth_is_closer_is_checked_from_the_lga_on_file(harness, monkeypatch):
    """Trace #123: no list and no pin, Wamakko on file. The registry and PostGIS answer, from the LGA's centre."""
    h, me = harness, "2348000000910"
    _with_readings(monkeypatch, h)
    consented(h, me, "en")
    h.store().set_last_lga(h.key(me), "NG034021")
    sends = h.turn(text("But uduth is closer to me", me), 1, "cold claim")
    assert "centre of Wamakko LGA" in sends[0][2] and "Usman" in sends[0][2]
    assert "documents" not in sends[0][2]


def test_pin_nearest_hospital_then_but_uduth_is_closer(harness, monkeypatch):
    h, me = harness, "2348000000911"
    _with_readings(monkeypatch, h)
    consented(h, me, "en")
    h.turn(pin(LAT, LON, me), 2, "pin")
    h.turn(text("Where is the nearest hospital?", me), lambda s: s and s[0][0] == "text", "nearest hospital")
    sends = h.turn(text("But Uduth is closer to me", me), 1, "correction")
    assert "Usman" in sends[0][2] and "from your pin" in sends[0][2]


# --- 2 Nov: the menu (an interactive list) and the typing indicator through the real webhook path ------------------

def row(rid, sender):
    return {"from": sender, "id": f"wamid.e2e{next(_ids)}", "type": "interactive",
            "interactive": {"type": "list_reply", "list_reply": {"id": rid, "title": rid}}}


def test_menu_then_budget_for_my_area_then_the_pin_answers(harness, monkeypatch):
    h, me = harness, "2348000000908"
    _with_readings(monkeypatch, h)
    consented(h, me, "en")
    FakeWA.typing = []
    sends = h.turn(text("menu", me), 1, "menu")
    assert sends[0][0] == "list" and len(sends[0][2]["sections"][0]["rows"]) == 8
    assert FakeWA.typing                                            # the typing indicator went on the message
    sends = h.turn(row("menu_budget", me), 1, "budget row")
    assert sends[0][0] == "location_request"
    sends = h.turn(pin(LAT, LON, me), lambda s: len(s) >= 3, "pin answers the row")
    assert any("Ministry of Works" in str(p) or "₦" in str(p) for _, _, p in sends)


def test_menu_in_hausa(harness, monkeypatch):
    h, me = harness, "2348000000909"
    _with_readings(monkeypatch, h)
    consented(h, me, "ha")
    sends = h.turn(text("menu", me), 1, "menu in Hausa")
    assert sends[0][0] == "list" and sends[0][2]["button"] == "Buɗe zaɓuɓɓuka"
    assert sends[0][2]["sections"][0]["rows"][0]["title"] == "Kasafin yankina"
