"""One routing rule (app/agent/routing.py): a shortcut fires only on unambiguous intent for its feature, and a
question naming a publisher, survey or report goes to the planner and the document path. Live misroutes, 1 Nov
2026: "What did UNFPA find out about health facilities in Wamakko" got a facility card."""

from __future__ import annotations

import asyncio

import pytest

from app.agent import routing as R


@pytest.mark.parametrize("q", [
    "What did UNFPA find out about health facilities in Wamakko",
    "According to the MICS by NBS, UNICEF, what are the gaps in child healthcare and civil registration for Sokoto State?",
    "What does the World Bank report say about floods in Sokoto?", "What did the NDHS 2024 find about stunting in Sokoto?",
    "Me rahoton UNFPA ya gano game da asibitocin Wamakko?", "A cewar MICS, nawa ne yaran da aka yi musu rajista a Sokoto?",
    "What did IOM report about IDPs in Goronyo?", "the EmONC assessment findings for Kware", "Binciken NDHS ya nuna me a Sokoto?",
])
def test_questions_naming_a_source_are_document_questions(q) -> None:
    assert R.document_question(q), q


@pytest.mark.parametrize("q", [
    "Where is the nearest hospital?", "How far is Arkilla PHC", "What about Arkilla PHC", "nearest clinic in Kware",
    "Ina asibiti mafi kusa?", "Is Kware General Hospital open?", "flood control budget 2026", "will it rain in Wurno tomorrow",
    "Which LGAs get most IDPs?", "How green was my farm in 2024?", "Who is the governor of Sokoto?",
    "How much did the state spend on the Specialist Hospital?", "Alert me if there will be floods in Goronyo",
])
def test_ordinary_questions_are_not(q) -> None:
    assert not R.document_question(q), q


def test_short_publisher_names_count_only_in_capitals_and_own_sources_may_still_answer() -> None:
    assert R.names_a_source("Who is the nearest doctor?") == ""
    assert R.names_a_source("WHO report on measles in Sokoto") == "WHO"
    assert R.own_source("How many cholera cases according to NCDC this week?", ("NCDC",))
    assert not R.own_source("What does the WHO say about cholera in Sokoto?", ("NCDC",))
    assert not R.own_source("cholera cases this week", ("NCDC",))


@pytest.mark.parametrize("q,want", [
    ("Where is Arkilla PHC?", True), ("How far is Kware General Hospital", True), ("What about Arkilla PHC", True),
    ("Is the Specialist Hospital open on Sunday?", True), ("Ina Arkilla PHC?", True), ("Yaya nisan asibitin Kware?", True),
    ("health facilities in Wamakko", False), ("Wamakko Primary Health Center budget", False),
    ("What did UNFPA find out about health facilities in Wamakko", False),
])
def test_a_named_facility_needs_intent_words(q, want) -> None:
    assert R.facility_intent(q) is want


def test_the_conversation_sends_a_report_question_about_facilities_to_the_answer_path(monkeypatch) -> None:
    from app.geo.location import memory
    from app.users import UserStore, user_key
    from app.whatsapp import conversation as C
    from tests.helpers import make_settings
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")
    store = UserStore(":memory:")
    key = user_key("2348000000066", s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    seen: list[str] = []

    async def answer(question, lang, **kw):
        seen.append(question)
        return "DOCUMENT ANSWER"

    def never_lookup(settings, text):
        raise AssertionError("the facility lookup ran for a report question")
    monkeypatch.setattr(C, "lookup", never_lookup)

    async def ok(*a, **k):
        from app.guardrails.scope import Verdict
        return Verdict("ok", "none")

    async def none(*a, **k):
        return None
    msg = {"from": "2348000000066", "id": "w-unfpa", "type": "text",
           "text": {"body": "What did UNFPA find out about health facilities in Wamakko"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=ok, place_fn=none))
    assert seen == ["What did UNFPA find out about health facilities in Wamakko"] and outs[-1].text == "DOCUMENT ANSWER"


def test_the_post_plan_shortcuts_yield_to_a_named_source() -> None:
    from app.agent.answer import Plan, facility_route, hazard_route
    q = "What does the World Bank report say about floods in Sokoto?"
    assert hazard_route(q, Plan(q, ["floods"], [])) == []
    plain = "Is there a flood warning for Goronyo?"
    assert hazard_route(plain, Plan(plain, [], [])) != []
    assert facility_route("What did UNFPA find out about health facilities in Wamakko",
                          Plan("What did UNFPA find out about health facilities in Wamakko", [], []), None, "en") == ""
