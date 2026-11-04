"""Multi-part questions (4 Nov 2026, KASAFI_MULTI_PART): "Has this area flooded before, and what is the state
spending on erosion here?" had failed entirely, because one message took one capability. Now the understanding
step reads up to three parts, each runs through its own capability with the shared pin, LGA and language, and one
reply joins them in the order asked, with a heading per part and each part's attachments; a part that fails gets
its honest line and the others still go. One-part messages are untouched."""

import asyncio
from types import SimpleNamespace

import pytest

from app.agent import understand as U
from app.geo.location import Spot, memory
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import make_settings

SENDER = "2348000000078"
PIN = Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Kalambaina", how="pin")
TWO = {"kind": "new", "capability": "place_history", "subject": {"level": "pin", "name": ""},
       "time": {"kind": "past", "years": []}, "measure": "flooded", "urgent": False,
       "restatement": "Has my farm (the pin) flooded before, and what is the state spending on erosion in my LGA?",
       "parts": [
           {"capability": "place_history", "subject": {"level": "pin", "name": ""}, "time": {"kind": "past", "years": []},
            "measure": "flooded", "label": "Flood history", "restatement": "Has my farm (the pin) flooded before?"},
           {"capability": "place_budget", "subject": {"level": "lga", "name": ""}, "time": {"kind": "none", "years": []},
            "measure": "amount", "label": "Erosion spending",
            "restatement": "What is the state budget spending on erosion in my LGA?"}]}


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


async def _quiet(*a, **k):
    return None


def _setup(lang="en", multi=True):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True,
                      kasafi_multi_part=multi)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, lang)
    store.give_consent(key)
    memory.forget(key)
    memory.remember(key, PIN)
    return s, store, key


def _handle(s, store, text, reading, answer, monkeypatch, notify=None, **kw):
    async def understand_fn(message, history, place, settings, fallbacks=None):
        return reading
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    msg = {"from": SENDER, "id": "w-mp", "type": "text", "text": {"body": text}}
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn, emergency_fn=_quiet, classify_fn=_quiet,
                                **({"notify": notify} if notify else {}), **kw))


def test_the_reading_carries_the_parts_and_one_thing_asked_is_no_split() -> None:
    u = U.parse(TWO)
    assert [p["capability"] for p in u.parts] == ["place_history", "place_budget"]
    parts = u.part_readings()
    assert [p.level for p in parts] == ["pin", "lga"] and parts[0].time == "past" and parts[0].kind == "new"
    assert parts[1].label == "Erosion spending" and parts[1].restatement.startswith("What is the state budget")
    one = U.parse({**TWO, "parts": [TWO["parts"][0]]})          # one part listed: no split
    assert one.parts == [] and one.part_readings() == []
    assert U.parse({**TWO, "parts": "no"}).parts == []
    four = U.parse({**TWO, "parts": TWO["parts"] * 2})           # capped at three
    assert len(four.parts) == 3
    assert "parts" in U.system_prompt(make_settings(kasafi_multi_part=True))
    assert "ONLY when the message asks for two or three" not in U.system_prompt(make_settings(kasafi_multi_part=False))


def test_flood_history_and_erosion_budget_from_a_wamakko_pin_each_take_their_own_capability(monkeypatch) -> None:
    """The live failure: with the pin in Wamakko, the flood part goes to the satellite record (pin, past) and the
    erosion part to the LGA's budget lines, in parallel, and one reply carries both in the order asked."""
    s, store, key = _setup()
    seen: list = []

    async def answer(question, lang, **kw):
        u = kw["understanding"]
        seen.append((question, u.capability, u.level, u.time, kw.get("place", {}).get("lga")))
        if u.capability == "place_history":
            await asyncio.sleep(0.05)
            return SimpleNamespace(text="Radar shows water on the plot in 2024 and 2022.", found=True, sources=[],
                                   working="", quotes="")
        return SimpleNamespace(text="Wamakko erosion lines 2026: ₦120,000,000 (p. 212).", found=True, sources=[],
                               working="", quotes="")
    outs = _handle(s, store, "Has this area flooded before, and what is the state spending on erosion here?",
                   U.parse(TWO), answer, monkeypatch)
    assert sorted(x[1] for x in seen) == ["place_budget", "place_history"]
    flood = next(x for x in seen if x[1] == "place_history")
    assert flood[2:] == ("pin", "past", "Wamakko") and flood[0].startswith("Has my farm (the pin) flooded")
    assert next(x for x in seen if x[1] == "place_budget")[2] == "lga"
    text = outs[0].text
    assert text.index("*1. Flood history*") < text.index("Radar shows water") < text.index("*2. Erosion spending*") \
        < text.index("Wamakko erosion lines")
    assert len(outs) == 1 and outs[0].buttons is None
    turns = store.recent_turns(key)                              # both parts kept for follow-ups
    assert len(turns) == 2 and {t["question"][:12] for t in turns} == {"Has my farm ", "What is the "}


def test_a_hausa_two_part_question_keeps_hausa_headings(monkeypatch) -> None:
    s, store, key = _setup(lang="ha")
    hausa = {**TWO, "parts": [{**TWO["parts"][0], "label": "Tarihin ambaliya"},
                              {**TWO["parts"][1], "label": "Kashe kuɗi kan zaizayar ƙasa"}]}
    progress: list = []

    async def notify(out):
        progress.append(out.text)

    async def answer(question, lang, **kw):
        assert lang == "ha"
        return SimpleNamespace(text=f"AMSA {kw['understanding'].capability}", found=True, sources=[], working="",
                               quotes="")
    outs = _handle(s, store, "Shin wannan wuri ya taɓa ambaliya, kuma nawa gwamnati ke kashewa kan zaizayar ƙasa a nan?",
                   U.parse(hausa), answer, monkeypatch, notify=notify)
    assert outs[0].text.startswith("*1. Tarihin ambaliya*\nAMSA place_history\n\n*2. Kashe kuɗi kan zaizayar ƙasa*")
    assert progress and progress[0].startswith("Ina duba abubuwa 2: Tarihin ambaliya, Kashe kuɗi")


def test_budget_and_nearest_facility_split_between_the_documents_and_the_registry(monkeypatch) -> None:
    """The facility part takes the registry search (never the documents); the budget part the documents."""
    s, store, key = _setup()
    reading = U.parse({**TWO, "parts": [
        {"capability": "budget", "subject": {"level": "sector", "name": "health"}, "time": {"kind": "year", "years": [2026]},
         "measure": "amount", "label": "Health budget 2026", "restatement": "What is the 2026 health budget?"},
        {"capability": "facility", "subject": {"level": "pin", "name": ""}, "time": {"kind": "now", "years": []},
         "measure": "nearest", "label": "Nearest hospital", "restatement": "Which hospital is nearest my farm (the pin)?"}]})
    reading.care, reading.facility_level = "general", "hospital"
    seen: dict = {}

    async def facility_reading(text, u, key_, lang, settings, facility_fn, spot=None):
        seen["facility"] = (text, u.capability, u.facility_level)
        return [C.Out("Nearest: Specialist Hospital Sokoto, 6.5 km", lang=lang),
                C.Out("Specialist Hospital Sokoto", lang=lang, location={"latitude": 13.06, "longitude": 5.24})]

    async def answer(question, lang, **kw):
        seen["answer"] = (question, kw["understanding"].capability)
        return SimpleNamespace(text="Health 2026: ₦58.4 billion (p. 9).", found=True, sources=[], working="", quotes="")

    async def no_trace(*a, **k):
        return None
    monkeypatch.setattr(C, "_facility_reading", facility_reading)
    monkeypatch.setattr(C, "_trace_route", no_trace)
    monkeypatch.setattr(C, "_add_buttons", lambda *a, **k: None)

    async def understand_fn(message, history, place, settings, fallbacks=None):
        return reading
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: True))
    msg = {"from": SENDER, "id": "w-mp2", "type": "text", "text": {"body": "What is the 2026 health budget and which hospital is nearest me?"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn, emergency_fn=_quiet, classify_fn=_quiet))
    assert seen["facility"][1:] == ("facility", "hospital") and seen["answer"][1] == "budget"
    text = outs[0].text
    assert text.index("*1. Health budget 2026*") < text.index("₦58.4 billion") < text.index("*2. Nearest hospital*") \
        < text.index("Nearest: Specialist")
    assert outs[1].location == {"latitude": 13.06, "longitude": 5.24}       # the pin stays with its part


THREE = {**TWO, "restatement": "What is the government spending in my ward, has my farm (the pin) ever flooded, and "
                                "where is the nearest clinic?",
         "parts": [
             {"capability": "place_budget", "subject": {"level": "lga", "name": ""}, "time": {"kind": "none", "years": []},
              "measure": "amount", "label": "Government spending here",
              "restatement": "What is the government budget spending in my LGA?"},
             {"capability": "place_history", "subject": {"level": "pin", "name": ""}, "time": {"kind": "past", "years": []},
              "measure": "flooded", "label": "Flood history", "restatement": "Has my farm (the pin) ever flooded?"},
             {"capability": "facility", "subject": {"level": "pin", "name": ""}, "time": {"kind": "now", "years": []},
              "measure": "nearest", "label": "Nearest clinic",
              "restatement": "Where is the nearest clinic to my farm (the pin)?"}]}


def test_moving_my_family_here_gets_budget_flood_history_and_the_nearest_clinic_in_one_reply(monkeypatch) -> None:
    """The live case (4 Nov, a pin in Wamakko): three parts in one reply, in the order asked: the LGA's budget lines
    with their page crop, the pin's flood history with its map, and the nearest clinic with its distance."""
    s, store, key = _setup()
    reading = U.parse(THREE)
    reading.care, reading.facility_level = "general", "primary"
    seen: dict = {}

    async def facility_reading(text, u, key_, lang, settings, facility_fn, spot=None):
        seen["facility"] = (u.capability, u.facility_level, u.level)
        return [C.Out("Nearest clinic: Wajake Dispensary, 0.9 km by road, about 3 min", lang=lang),
                C.Out("Wajake Dispensary", lang=lang, location={"latitude": 13.05, "longitude": 5.16})]

    async def answer(question, lang, **kw):
        u = kw["understanding"]
        seen[u.capability] = (u.level, u.time, kw.get("place", {}).get("lga"))
        if u.capability == "place_budget":
            return SimpleNamespace(text="Wamakko LGA, 2026 budget: 201 project lines, ₦4.2 billion (p. 212).",
                                   found=True, sources=[], working="", quotes="", exact="", cited=[])
        return SimpleNamespace(text="Radar shows water on the plot in 2024 and 2022.", found=True, sources=[],
                               working="", quotes="", maps=["MAP-SPEC"])

    def crops(result, n):
        return ["CROP p. 212"] if "project lines" in result.text else []

    def render(settings, specs, lang, day):
        return [SimpleNamespace(caption="Floods seen by radar around the pin", jpeg=b"JPEG-MAP")]

    async def no_trace(*a, **k):
        return None
    monkeypatch.setattr(C, "_facility_reading", facility_reading)
    monkeypatch.setattr(C, "_trace_route", no_trace)
    monkeypatch.setattr(C, "_add_buttons", lambda *a, **k: None)
    monkeypatch.setattr(C, "plan_crops", crops)
    monkeypatch.setattr(C, "render_specs", render)

    async def understand_fn(message, history, place, settings, fallbacks=None):
        return reading
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: True))
    msg = {"from": SENDER, "id": "w-mp3", "type": "text",
           "text": {"body": "I'm thinking of moving my family here. What is the government spending in this area, "
                            "has it ever flooded, and where's the nearest clinic?"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn, emergency_fn=_quiet, classify_fn=_quiet))
    assert seen["place_budget"] == ("lga", "none", "Wamakko") and seen["place_history"][:2] == ("pin", "past")
    assert seen["facility"] == ("facility", "primary", "pin")
    text = outs[0].text
    assert text.index("*1. Government spending here*") < text.index("₦4.2 billion") < text.index("*2. Flood history*") \
        < text.index("Radar shows water") < text.index("*3. Nearest clinic*") < text.index("0.9 km by road")
    assert outs[0].crops == ["CROP p. 212"]                                   # the budget part's page crop
    assert [o.image for o in outs[1:] if o.image] == [b"JPEG-MAP"]           # the flood part's map
    assert [o.location for o in outs[1:] if o.location] == [{"latitude": 13.05, "longitude": 5.16}]


@pytest.mark.parametrize("given, kept", [
    ("Has my farm (the pin) in Gumbi ward ever been flooded in past years?", "Has my farm (the pin) ever been flooded in past years?"),
    ("Has my farm (the pin) in Gumbi, Wamakko LGA ever flooded?", "Has my farm (the pin) ever flooded?"),
    ("What is the government spending in my ward (Gumbi, Wamakko LGA) where my farm (the pin) is?",
     "What is the government spending in my ward where my farm (the pin) is?"),
    ("Where is the nearest clinic to my farm (the pin) in Gumbi, Wamakko LGA?", "Where is the nearest clinic to my farm (the pin)?"),
    ("What did the 2026 budget give my LGA, Wamakko?", "What did the 2026 budget give my LGA?"),
    ("Has my farm (the pin) flooded in the past?", "Has my farm (the pin) flooded in the past?"),   # nothing added
    ("What did my LGA get in 2026?", "What did my LGA get in 2026?"),
])
def test_a_parts_restatement_never_carries_a_name_the_model_added_to_the_users_own_place(given, kept) -> None:
    """4 Nov live: 'my farm (the pin) in Gumbi, Wamakko LGA' made the flood part ask for the pin again and the
    clinic part match a facility called Gumbi."""
    assert U.own_place_words(given) == kept
    u = U.parse({**TWO, "parts": [{**TWO["parts"][0], "restatement": given}, TWO["parts"][1]]})
    assert u.parts[0]["restatement"] == kept


def test_a_place_budget_part_from_a_pin_takes_the_lga_tool_so_no_planner_clarify_can_ask_which_ward() -> None:
    """4 Nov live: the budget part of the three-part question got 'My specific ward / Whole Wamakko LGA?' from the
    planner; the reading (place_budget, ward level, a pin on file) settles it and the LGA tool answers."""
    from app.agent import answer as ans
    place = {"lat": 13.045, "lon": 5.155, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Gumbi"}
    u = U.Understanding(capability="place_budget", level="ward", measure="amount",
                        restatement="What is the government spending in my ward?")
    plan = ans.Plan(english_question="q", search_queries=[], doc_ids=[])
    spec = ans.reading_lga_route(u, "What government spending / budget allocation is for my ward?", plan, place)
    assert spec and spec["tool"] == "lga_projects" and spec["lga"] == "Wamakko" and spec["ward"] == "Gumbi"
    assert ans.reading_lga_route(u, "What is the spending in my ward?", plan, None) == {"tool": "need_place"}
    other = U.Understanding(capability="budget", level="state", restatement="What is the 2026 health budget?")
    assert ans.reading_lga_route(other, "What is the 2026 health budget?", plan, place) is None


def test_a_voice_note_takes_exactly_the_text_path_so_a_three_part_question_is_split(monkeypatch) -> None:
    """4 Nov live: the three-part question as a voice note (transcribed fine) went straight to 'Checking the
    documents' as one question and failed, while the same text was split. The transcript now re-enters the text
    path: understanding, multi-part, each capability, the shared pin; 'I heard: …' first."""
    from app.providers.stt import SpeechResult
    from app.whatsapp.voice import VoiceOutcome
    s, store, key = _setup()
    reading = U.parse(THREE)
    reading.care, reading.facility_level = "general", "primary"
    heard = ("I'm thinking of moving my family here. What is the government spending in this area? Has it ever "
             "flooded? And where is the nearest clinic?")
    seen: dict = {}

    async def voice_fn(msg, wa, *, lang, settings):
        return VoiceOutcome("echo of the voice path", SpeechResult(heard, heard, "en", "high", False))

    async def understand_fn(message, history, place, settings, fallbacks=None):
        seen["message"] = message
        return reading

    async def answer(question, lang, **kw):
        u = kw["understanding"]
        seen[u.capability] = (u.level, kw.get("place", {}).get("lga"))
        return SimpleNamespace(text=f"ANSWER {u.capability}", found=True, sources=[], working="", quotes="")

    async def facility_reading(text, u, key_, lang, settings, facility_fn, spot=None):
        seen["facility"] = (u.level, spot.lga if spot else None)
        return [C.Out("Nearest clinic: Wajake Dispensary, 0.8 km by road", lang=lang)]

    async def no_trace(*a, **k):
        return None
    monkeypatch.setattr(C, "_facility_reading", facility_reading)
    monkeypatch.setattr(C, "_trace_route", no_trace)
    monkeypatch.setattr(C, "_add_buttons", lambda *a, **k: None)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: True))
    msg = {"from": SENDER, "id": "w-voice3", "type": "audio", "audio": {"id": "a1"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn, emergency_fn=_quiet, classify_fn=_quiet, voice_fn=voice_fn))
    assert seen["message"] == heard                                        # the transcript was read as a message
    assert outs[0].text.startswith("I heard") or "heard" in outs[0].text.lower()
    text = outs[1].text
    assert text.index("*1. Government spending here*") < text.index("ANSWER place_budget") \
        < text.index("*2. Flood history*") < text.index("ANSWER place_history") < text.index("*3. Nearest clinic*") \
        < text.index("Wajake")
    assert seen["place_budget"] == ("lga", "Wamakko") and seen["place_history"] == ("pin", "Wamakko")
    assert seen["facility"] == ("pin", "Wamakko")                          # the shared pin reached every part
    voice, questions = store.usage(key)
    assert voice == 1 and questions == 0                                   # counted once, as voice


def test_a_single_part_question_is_answered_exactly_as_before(monkeypatch) -> None:
    s, store, key = _setup()
    calls: list = []

    async def answer(question, lang, **kw):
        calls.append((question, kw["understanding"].capability))
        return SimpleNamespace(text="117 public schools.", found=True, sources=[], working="", quotes="")
    one = U.parse({**TWO, "capability": "statistics", "restatement": "How many schools are in Dange Shuni LGA?",
                   "parts": []})
    outs = _handle(s, store, "How many schools are in Dange Shuni?", one, answer, monkeypatch)
    assert calls == [("How many schools are in Dange Shuni?", "statistics")]
    assert outs[0].text.startswith("117 public schools.") and "*1." not in outs[0].text


def test_with_the_switch_off_a_two_part_reading_is_answered_as_one_question(monkeypatch) -> None:
    s, store, key = _setup(multi=False)
    calls: list = []

    async def answer(question, lang, **kw):
        calls.append(question)
        return SimpleNamespace(text="ONE", found=True, sources=[], working="", quotes="")
    outs = _handle(s, store, "Has this area flooded before, and what is the state spending on erosion here?",
                   U.parse(TWO), answer, monkeypatch)
    assert calls == ["Has this area flooded before, and what is the state spending on erosion here?"]
    assert outs[0].text.startswith("ONE")


def test_one_part_failing_still_sends_the_other_with_an_honest_line(monkeypatch) -> None:
    s, store, key = _setup()

    async def answer(question, lang, **kw):
        if kw["understanding"].capability == "place_history":
            raise RuntimeError("satellite API down")
        return SimpleNamespace(text="Wamakko erosion lines 2026: ₦120,000,000 (p. 212).", found=True, sources=[],
                               working="", quotes="")

    async def no_note(*a, **k):
        return None
    monkeypatch.setattr(C, "_note_failure", no_note)
    outs = _handle(s, store, "Has this area flooded before, and what is the state spending on erosion here?",
                   U.parse(TWO), answer, monkeypatch)
    text = outs[0].text
    assert "*1. Flood history*" in text and "*2. Erosion spending*" in text and "₦120,000,000" in text
    flood_section = text.split("*2. Erosion spending*")[0]
    assert "satellite" in flood_section.lower() or "sorry" in flood_section.lower()   # the honest line, in place


def test_join_parts_keeps_each_parts_attachments_in_order() -> None:
    a = U.Understanding(capability="place_history", restatement="Has my farm flooded?", label="Flood history")
    b = U.Understanding(capability="place_budget", restatement="Erosion budget for my LGA", label="Erosion spending")
    outs = C.join_parts([a, b], [[C.Out("water in 2024", crops=["cropA"]), C.Out("map of the plot", image=b"JPEG-A")],
                                 [C.Out("₦120,000,000", crops=["cropB"]), C.Out("map of the LGA", image=b"JPEG-B")]],
                        "en", 3)
    assert outs[0].text == "*1. Flood history*\nwater in 2024\n\n*2. Erosion spending*\n₦120,000,000"
    assert outs[0].crops == ["cropA", "cropB"]
    assert [o.image for o in outs[1:]] == [b"JPEG-A", b"JPEG-B"]
    empty = C.join_parts([a, b], [[], [C.Out("₦120,000,000")]], "ha", 3)         # a part with no reply at all
    assert "Ban iya amsa wannan ɓangaren ba." in empty[0].text and "₦120,000,000" in empty[0].text


def test_a_part_is_kept_short_its_lead_and_sources_with_the_detail_in_show_working() -> None:
    """4 Nov: the budget part of a three-part reply ran to 20 lines (execution detail, statewide agency figures).
    A part keeps its lead paragraph and its sources line; the rest goes to 'show working'."""
    body = ("_Assumption: used the latest budget, 2026._\n\n"
            "The 2026 budget has 163 capital projects located in Wamakko, worth ₦79.98 billion, mostly health "
            "(₦30.1 billion). The implementation reports give spending by project only for primary healthcare and "
            "basic education; other sectors are reported by ministry.\n\n"
            "118 of these lines were also in the 2025 budget (₦13.61 billion), and ₦1.08 billion was spent on them "
            "by September 2025.\n\n"
            "Capital spent so far by these agencies (Q3 2026 report; statewide):\n• Ministry of Health: ₦3.43 billion\n\n"
            "📄 *Sources:* Sokoto State FY 2026 Budget, p. 49, 51\n_Reply *show working* to see the rows and arithmetic._")
    short, rest = C.short_form(body)
    assert short == ("The 2026 budget has 163 capital projects located in Wamakko, worth ₦79.98 billion, mostly health "
                     "(₦30.1 billion). The implementation reports give spending by project only for primary healthcare "
                     "and basic education; other sectors are reported by ministry.\n\n"
                     "📄 *Sources:* Sokoto State FY 2026 Budget, p. 49, 51\n_Reply *show working* to see the rows and arithmetic._")
    assert rest.startswith("_Assumption") and "118 of these lines" in rest and "Ministry of Health" in rest
    assert C.short_form("One short answer.\n\n📄 *Sources:* p. 3") == ("One short answer.\n\n📄 *Sources:* p. 3", "")


def test_a_parts_title_line_stays_with_its_first_paragraph() -> None:
    """4 Nov live: the flood part showed only '*Flooding: Gumbi ward (likely), Wamakko LGA* — experimental' and
    its findings went to show working."""
    body = ("*Flooding: Gumbi ward (likely), Wamakko LGA* — experimental\n\n"
            "Your pin is in Gumbi ward (likely) of Wamakko LGA, so this answer is about that ward.\n\n"
            "Floodwater was seen in 2020 (25.2% of the ward's land, the most) and 2024 (8.1%). Radar can't judge "
            "about 6% of the ward.\n\n"
            "Years 2016–2026; clear images per year: 2016 9, 2017 14.\n\n"
            "📄 *Sources:* Copernicus Sentinel-1 via Planetary Computer")
    short, rest = C.short_form(body)
    assert short.startswith("*Flooding: Gumbi ward (likely), Wamakko LGA* — experimental\n\nYour pin is in Gumbi ward "
                            "(likely) of Wamakko LGA, so this answer is about that ward.\n\nFloodwater was seen in 2020")
    assert short.endswith("📄 *Sources:* Copernicus Sentinel-1 via Planetary Computer") and rest.startswith("Years 2016")
    # a lead that ends with a colon keeps the list it introduces
    years = "Projects located in Wamakko, year by year (2024–2026):\n\n• 2024: 120 projects\n• 2025: 118 projects\n\n" \
            "Extra detail here, 2 lines.\n\n📄 *Sources:* p. 1"
    short, rest = C.short_form(years)
    assert "• 2024: 120 projects" in short and rest == "Extra detail here, 2 lines."


def test_a_facility_part_whose_name_is_the_users_own_place_searches_nearest_instead_of_a_card(monkeypatch) -> None:
    """4 Nov live: 'nearest clinic to my ward' read with name 'Gumbi' (the ward) matched Gumbi Health Clinic's
    registry card, with no distance. A name at pin, ward, LGA or state level is the place, not a facility."""
    from app.geo.location import Spot
    looked, searched = [], []
    monkeypatch.setattr(C, "lookup", lambda settings, name: looked.append(name) or [])

    async def replies(spot, search, lang, settings, facility_fn, how, key):
        searched.append((spot.lga, search.filters.levels if hasattr(search.filters, "levels") else None))
        return [C.Out("Nearest: Wajake Dispensary, 0.8 km by road", lang=lang)]
    monkeypatch.setattr(C, "_facility_replies", replies)
    u = U.Understanding(capability="facility", level="ward", name="Gumbi", care="general", facility_level="primary",
                        restatement="Where is the nearest clinic to my ward?")
    spot = Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Gumbi", how="pin")
    outs = asyncio.run(C._facility_reading(u.restatement, u, "k-fac", "en", make_settings(), None, spot))
    assert looked == [] and searched and outs[0].text.startswith("Nearest: Wajake")


def test_part_headings_are_capitalised() -> None:
    a = U.Understanding(restatement="x", label="government spending")
    b = U.Understanding(restatement="y", label="flood history")
    outs = C.join_parts([a, b], [[C.Out("A")], [C.Out("B")]], "en", 3)
    assert outs[0].text == "*1. Government spending*\nA\n\n*2. Flood history*\nB"


@pytest.mark.parametrize("lang", ["en", "ha"])
def test_the_progress_line_names_the_parts(lang) -> None:
    a = U.Understanding(restatement="x", label="Flood history")
    b = U.Understanding(restatement="y", label="Erosion spending")
    line = C.parts_progress(lang, [a, b])
    assert "2" in line and "Flood history, Erosion spending" in line
