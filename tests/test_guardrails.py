import asyncio
import json
from pathlib import Path

import pytest

from app.guardrails import scope
from app.guardrails.emergency import EMERGENCY_REPLY
from app.providers.chat import ChatResult, ProviderError
from app.users import UserStore
from app.whatsapp.corrections import Resolution
from app.whatsapp.messages import t
from tests.helpers import heard, make_settings, run_handle

A = "2340000000001"
QUESTIONS = {q["id"]: q for q in json.loads(Path("evals/questions.json").read_text(encoding="utf-8"))["questions"]}


def text(body: str) -> dict:
    return {"from": A, "type": "text", "text": {"body": body}}


def voice() -> dict:
    return {"from": A, "type": "audio", "audio": {"id": "m1", "voice": True}}


def consented(lang: str = "ha") -> UserStore:
    store = UserStore(":memory:")
    run_handle(text("Sannu" if lang == "ha" else "Hello"), store=store)
    run_handle(text("OK"), store=store)
    return store


# --- keyword tier on the eval set -------------------------------------------------

@pytest.mark.parametrize("qid, category", [("13", "electoral"), ("14", "verdict"), ("16", "security")])
def test_eval_guardrail_questions_are_caught_by_keywords(qid: str, category: str) -> None:
    q = QUESTIONS[qid]
    assert scope.keyword_check([q["text_ha"]]) == category
    assert scope.keyword_check([q["english"]]) == category


@pytest.mark.parametrize("qid", [k for k in QUESTIONS if k not in ("13", "14", "15", "16")])
def test_in_scope_eval_questions_pass_without_a_model_call(qid: str) -> None:
    q = QUESTIONS[qid]
    assert scope.keyword_check([q["text_ha"], q["english"]]) is None
    assert not scope.needs_model([q["text_ha"], q["english"]])


def test_government_is_not_governor() -> None:
    assert not scope.needs_model(["Nawa gwamnatin jihar ta ware wa ilimi?"])
    assert scope.needs_model(["Nawa aka ware wa ofishin gwamna?"])


def test_security_caught_in_raw_hypothesis_when_merge_dropped_it() -> None:
    merged_lost_it = "Ina suka fi kai hari a Sokoto?"          # seen in the reconcile comparison
    assert scope.keyword_check([merged_lost_it]) == "security"   # "kai hari" still caught
    assert scope.keyword_check(["Ina mutane suke?", "Ina 'yan bindiga suka fi kai hari"]) == "security"


@pytest.mark.parametrize("apostrophe", ["'", "’", "ʼ"])
def test_apostrophe_variants(apostrophe: str) -> None:
    assert scope.keyword_check([f"Ina {apostrophe}yan bindiga suke?"]) == "security"


# --- conversation flow --------------------------------------------------------------

@pytest.mark.parametrize("qid, key", [("13", "guard_electoral"), ("14", "guard_verdict"), ("16", "guard_security")])
@pytest.mark.parametrize("lang", ["ha", "en"])
def test_typed_guardrail_questions_get_polite_refusals(qid: str, key: str, lang: str) -> None:
    outs, _ = run_handle(text(QUESTIONS[qid]["text_ha"]), store=consented(lang))
    assert outs[0].text == t(key, lang)


def test_voice_refused_when_only_a_raw_hypothesis_has_the_words() -> None:
    r = heard("Ina suka fi samun matsala a Sokoto?", confirm=True)
    r.hypotheses = {"asr": "Ini yan bindiga suka fi kai hari asokoto", "spark_audio": "Ina suka fi samun matsala"}
    store = consented()
    outs, _ = run_handle(voice(), store=store, spoken=r)
    assert outs[0].text == t("guard_security", "ha")
    from app.users import user_key
    assert store.get_pending(user_key(A, make_settings()), 15) is None     # refused questions aren't held for Eh


def test_medical_emergency_beats_guardrail() -> None:
    outs, _ = run_handle(text(QUESTIONS["15"]["text_ha"]), store=consented())
    assert outs[0].text == EMERGENCY_REPLY


def test_non_emergency_medical_advice_is_refused() -> None:
    outs, _ = run_handle(text("Wane magani ya fi kyau don zazzaɓin cizon sauro?"), store=consented())
    assert outs[0].text == t("guard_medical_advice", "ha")


def test_correction_that_turns_question_political_is_refused() -> None:
    store = consented()
    run_handle(voice(), store=store, spoken=heard("Nawa aka ware wa ilimi a 2022?", confirm=True))
    q = "Wane ɗan takara ya kamata in zaɓa a 2027?"
    outs, _ = run_handle(text("ɗan takara"), store=store, corrections={"ɗan takara": Resolution("correction", q)})
    assert outs[0].text == t("guard_electoral", "ha")


def test_model_tier_verdicts_are_used_for_borderline_words() -> None:
    store = consented()
    budget = "Nawa aka ware wa hukumar zaɓe ta jihar a 2025?"
    opinion = "Wace jam'iyya ce ta fi kyau?"
    assert run_handle(text(budget), store=store, model_verdicts={budget: "ok"})[0][0].text.startswith("Kasafi (gwaji)")
    assert run_handle(text(opinion), store=store, model_verdicts={opinion: "electoral"})[0][0].text == t("guard_electoral", "ha")


def test_ordinary_questions_are_not_refused() -> None:
    store = consented()
    for q in ["Nawa aka ware wa ilimi a 2025?", "How much did Sokoto spend on health in 2024?", "2025"]:
        assert run_handle(text(q), store=store)[0][0].text.startswith("Kasafi (")


# --- the model tier itself -------------------------------------------------------------

class FakeChat:
    def __init__(self, content: str) -> None:
        self.content, self.messages = content, None

    async def chat(self, messages, **kw):
        self.messages = messages
        return ChatResult(content=self.content, model="m", finish_reason="stop")


@pytest.mark.parametrize("allow, phrase", [(True, "budget figures for security agencies and lines"),
                                           (False, "this includes questions about security budgets")])
def test_classifier_prompt_follows_security_budget_setting(allow: bool, phrase: str) -> None:
    assert phrase in scope.classifier_prompt(allow)


def test_classify_dedupes_versions_and_rejects_unknown_categories() -> None:
    fake = FakeChat('{"category": "verdict", "reason": "x"}')
    s = make_settings()
    assert asyncio.run(scope.classify(["Shin gwamnan nan", "Shin gwamnan nan", ""], fake, s)) == "verdict"
    assert fake.messages[1]["content"].count("Shin gwamnan nan") == 1
    assert asyncio.run(scope.classify(["x"], FakeChat('{"category": "weird"}'), s)) == "ok"


def test_check_skips_model_when_not_needed_and_fails_open() -> None:
    class Boom:
        def __init__(self, settings): ...
        async def __aenter__(self): raise ProviderError("Meta", 503, "busy")
        async def __aexit__(self, *a): return None

    s = make_settings()
    assert asyncio.run(scope.check(["Nawa aka ware wa ilimi?"], settings=s, client_factory=Boom)).tier == "none"
    v = asyncio.run(scope.check(["Nawa aka ware wa ofishin gwamna?"], settings=s, client_factory=Boom))
    assert (v.category, v.tier) == ("ok", "none")                   # model down: allowed, warning logged
    assert asyncio.run(scope.check(["Ina 'yan bindiga?"], settings=s, client_factory=Boom)).category == "security"


def test_security_agencies_and_operations_always_reach_the_classifier() -> None:
    assert scope.needs_model(["Where are the Community Guard Corps deployed in Isa LGA?"])
    assert scope.needs_model(["Nawa aka ware wa 'yan sa kai a 2026?"])
    assert scope.keyword_check(["Where are the Community Guard Corps deployed?"]) is None   # the model decides
