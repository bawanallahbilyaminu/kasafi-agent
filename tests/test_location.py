"""Location intake and privacy (docs/hazard-and-services.md section 3): a pin gives the LGA (and ward), a point
outside Sokoto gets a polite reply, "share my location" sends the request button, and coordinates are never
persisted: not in the user store, not in the logs, not in a trace."""

import asyncio
import logging
from pathlib import Path

from app.agent.trace import redact
from app.geo import Area
from app.geo.location import LocationMemory, Spot, memory, pin_of
from app.users import UserStore, user_key
from app.whatsapp.conversation import handle
from tests.helpers import make_settings

LAT, LON = 13.0589127, 5.1673341            # distinctive digits, searched for afterwards
WAMAKKO = Area("NG034021", "Wamakko", "Gumbi", "62109")


def pin(lat=LAT, lon=LON, sender="2348000000001") -> dict:
    return {"from": sender, "id": "wamid.x", "type": "location",
            "location": {"latitude": lat, "longitude": lon, "name": "Kasuwa", "address": "Sokoto"}}


async def located(settings, lat, lon):
    return WAMAKKO if 12 < lat < 14 else None


def consented(store: UserStore, settings, sender="2348000000001", lang="en") -> str:
    key = user_key(sender, settings)
    store.create(key, lang)
    store.give_consent(key)
    return key


def run(msg, store, settings, **kw):
    return asyncio.run(handle(msg, None, store=store, settings=settings, locate_fn=located, answer_fn=None, **kw))


def test_a_pin_gives_the_lga_and_ward_with_the_notice_once() -> None:
    s, store = make_settings(), UserStore(":memory:")
    key = consented(store, s)
    out = run(pin(), store, s)
    assert out[0].text.startswith("Kasafi will use your location only to answer this and won't keep it")
    assert out[1].text == "📍 Got it: you're in Wamakko LGA (Gumbi ward), Sokoto State. What would you like to know about it?"
    assert store.get_last_lga(key) == "NG034021"
    spot = memory.recall(key)
    assert (spot.lat, spot.lon) == (LAT, LON) and "13.05" not in repr(spot) and "Wamakko" in repr(spot)
    out = run(pin(), store, s)
    assert len(out) == 1 and out[0].text.startswith("📍")              # the notice is shown once
    memory.forget(key)


def test_a_pin_outside_sokoto_gets_a_polite_reply_and_nothing_is_kept() -> None:
    s, store = make_settings(), UserStore(":memory:")
    key = consented(store, s, lang="ha")
    out = run(pin(lat=9.0765, lon=7.3986), store, s)                    # Abuja
    assert out[-1].text.startswith("Wannan wurin yana wajen Jihar Sokoto")
    assert store.get_last_lga(key) is None and memory.recall(key) is None


def test_share_my_location_sends_the_request_button() -> None:
    s, store = make_settings(), UserStore(":memory:")
    consented(store, s)
    out = run({"from": "2348000000001", "id": "wamid.y", "type": "text", "text": {"body": "share my location"}},
              store, s)
    assert out[-1].location_request and out[-1].text.startswith("Tap the button below to share your location")


def test_after_the_request_a_typed_place_is_the_location() -> None:
    s, store = make_settings(), UserStore(":memory:")
    key = consented(store, s)

    async def gazetteer(settings, text):
        return Spot(13.43, 5.66, "NG034006", "Goronyo", how="place") if "goronyo" in text.lower() else None
    say = lambda body: asyncio.run(handle({"from": "2348000000001", "id": "w", "type": "text",       # noqa: E731
                                           "text": {"body": body}}, None, store=store, settings=s,
                                          locate_fn=located, place_fn=gazetteer, answer_fn=None))
    say("share my location")
    out = say("Goronyo")
    assert out[-1].text.startswith("📍 Got it: you're in Goronyo LGA") and store.get_last_lga(key) == "NG034006"
    assert memory.recall(key).how == "place"
    out = say("Goronyo")                       # no request pending: an ordinary message, not a location
    assert not out[-1].text.startswith("📍")
    memory.forget(key)


def test_before_consent_a_pin_gets_the_consent_notice_and_no_lookup() -> None:
    s, store = make_settings(), UserStore(":memory:")
    looked = []

    async def spy(settings, lat, lon):
        looked.append(1)
        return WAMAKKO
    asyncio.run(handle(pin(), None, store=store, settings=s, locate_fn=spy, answer_fn=None))
    assert not looked


def test_memory_forgets_after_30_minutes_and_on_delete() -> None:
    m = LocationMemory(ttl_s=0.0)
    m.remember("k", Spot(LAT, LON, "NG034021", "Wamakko"))
    assert m.recall("k") is None
    s, store = make_settings(), UserStore(":memory:")
    key = consented(store, s)
    run(pin(), store, s)
    assert memory.recall(key) is not None
    run({"from": "2348000000001", "id": "wamid.z", "type": "text", "text": {"body": "delete my data"}}, store, s)
    assert memory.recall(key) is None


def _db_settings():
    return make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")      # has_database; never connected


def _text(body, sender="2348000000001"):
    return {"from": sender, "id": "w", "type": "text", "text": {"body": body}}


class FakeSearch:
    """search_replies without PostGIS or ORS: records the searches, answers with numbered facilities."""

    def __init__(self):
        self.calls = []

    async def __call__(self, settings, lat, lon, search, lang, *, mode="list", **kw):
        self.calls.append((round(lat, 2), search.filters, search.skip, search.profile, mode))
        search.shown = [f"F{search.skip + i}" for i in (1, 2, 3)]
        return [(f"{mode} from {search.skip + 1}", None),
                ("", {"latitude": 13.1, "longitude": 5.2, "name": f"F{search.skip + 1}", "address": "x"})]


def test_nearest_facility_asks_for_a_location_then_answers_from_the_pin() -> None:
    s, store, fake = _db_settings(), UserStore(":memory:"), FakeSearch()
    key = consented(store, s)
    out = run(_text("Where is the nearest hospital?"), store, s, facility_fn=fake)
    assert out[-1].location_request and "share your location" in out[-1].text and not fake.calls
    out = run(pin(), store, s, facility_fn=fake)                       # the pin answers the waiting question
    assert out[-2].text == "list from 1" and out[-1].location["name"] == "F1" and out[-1].text == ""
    assert fake.calls[-1][0] == 13.06
    out = run(_text("the next one"), store, s, facility_fn=fake)       # follow-ups reuse the point in memory
    assert out[0].text == "list from 4"
    out = run(_text("route?"), store, s, facility_fn=fake)
    assert out[0].text == "route from 4"
    out = run(_text("only government hospitals"), store, s, facility_fn=fake)
    _, filters, skip, profile, _ = fake.calls[-1]
    assert filters.ownership == "Public" and filters.levels == ("Secondary", "Tertiary") and skip == 0
    run(_text("on foot"), store, s, facility_fn=fake)
    assert fake.calls[-1][3] == "foot"
    n = len(fake.calls)
    run(_text("What did the state government spend on health in 2025?"), store, s, facility_fn=fake)
    assert len(fake.calls) == n                                        # a new question, not a filter
    memory.forget(key)


def test_a_facility_question_naming_a_place_needs_no_pin() -> None:
    s, store, fake = _db_settings(), UserStore(":memory:"), FakeSearch()
    key = consented(store, s, lang="ha")

    async def gazetteer(settings, text):
        return Spot(13.43, 5.66, "NG034006", "Goronyo", how="place") if "goronyo" in text.lower() else None
    out = run(_text("Ina asibiti mafi kusa a Goronyo?"), store, s, facility_fn=fake, place_fn=gazetteer)
    assert out[0].text == "list from 1" and fake.calls[0][0] == 13.43
    assert store.get_last_lga(key) == "NG034006"
    memory.forget(key)


def test_pin_of_reads_only_a_valid_location_message() -> None:
    assert pin_of(pin()) == (LAT, LON)
    assert pin_of({"type": "location", "location": {"latitude": "x"}}) is None
    assert pin_of({"type": "text"}) is None


def test_no_coordinates_are_persisted_after_a_location_conversation(tmp_path: Path, caplog) -> None:
    """The privacy test: a whole location conversation, then the user store's files, the logs and the trace
    wording are searched for the coordinates. Only the LGA is kept."""
    s, db = make_settings(), tmp_path / "kasafi.db"
    store = UserStore(str(db))
    key = consented(store, s)
    caplog.set_level(logging.DEBUG)
    run(pin(), store, s)
    run({"from": "2348000000001", "id": "wamid.a", "type": "text", "text": {"body": "share my location"}}, store, s)
    run(pin(lat=LAT + 0.0011, lon=LON + 0.0022), store, s)
    typed = f"Ina asibiti mafi kusa da {LAT}, {LON}?"                      # coordinates typed into a question
    run({"from": "2348000000001", "id": "wamid.b", "type": "text", "text": {"body": typed}}, store, s)
    store._db.execute("PRAGMA wal_checkpoint(FULL)")
    stored = b"".join(p.read_bytes() for p in tmp_path.iterdir())
    for digits in ("13.0589", "5.1673", "13.0600", "5.1695", "130589", "51673"):
        assert digits.encode() not in stored, f"{digits} found in the user store"
        assert digits not in caplog.text, f"{digits} found in the logs"
    assert "13.0589" not in redact(typed) and "[location removed]" in redact(typed)
    assert store.get_last_lga(key) == "NG034021"
    assert "location: Wamakko LGA (pin)" in caplog.text                  # the log says the LGA, nothing finer
    assert redact("MPI fell from 0.409, 0.239") == "MPI fell from 0.409, 0.239"   # figures aren't coordinates
    memory.forget(key)
