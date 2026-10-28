"""Kasafi's calculations: checked inputs, no mixed index bases, exact arithmetic, clearly labelled."""

import asyncio
from decimal import Decimal

import pytest

from app.agent import answer as ans
from app.agent.answer import Evidence
from app.agent.calculate import (CalcError, Calculation, MixedBases, compute, evaluate, result_text, validate)
from app.users import UserStore
from app.whatsapp.conversation import handle
from tests.helpers import make_settings
from tests.test_conversation_answers import consented, text

# The real Sokoto row of the NBS CPI September 2026 state table (p19, OCR), base 2024 = 100.
P19 = ("Combined Urban and Rural State Consumer Price Index\n(Base Period: 2024 = 100)\n"
       "State | Sep-25 | | Aug-26 | | Sep-26 | | MoM | YoY | MoM | YoY\n"
       "Sokoto | 127.0 | 125.1 | 136.9 | 131.2 | 134.7 | 135.1 | -1.6 | 6.1 | 3.0 | 8.0")
EV = [Evidence(1, "nbs-cpi-2026-09", "Consumer Price Index September 2026", 2026, 19, "ocr", P19)]
SPEC = {"description": "Sokoto year-on-year All Items inflation, September 2026", "unit": "%",
        "formula": "(sep26 / sep25 - 1) * 100",
        "formula_text": "(September 2026 index ÷ September 2025 index − 1) × 100",
        "inputs": [{"name": "sep26", "value": "135.1", "label": "Sokoto All Items index, September 2026", "cited": 1},
                   {"name": "sep25", "value": "125.1", "label": "Sokoto All Items index, September 2025", "cited": 1}]}


def test_sokoto_yoy_matches_the_published_rate() -> None:
    calc = validate(SPEC, EV)
    assert compute(calc) == Decimal("7.99")           # NBS publishes 8.0 (rounded) in the same table
    assert [i.base for i in calc.inputs] == ["2024=100", "2024=100"]


def test_result_is_labelled_with_formula_and_cited_inputs() -> None:
    out = result_text(validate(SPEC, EV), "en")
    assert out.startswith("🧮 *Kasafi's calculation, not an official figure*")
    assert "*7.99%*" in out and "= (135.1 ÷ 125.1 − 1) × 100 = 7.99%" in out
    assert "• Sokoto All Items index, September 2025: 125.1 [1] (base 2024=100)" in out
    assert "[1] Consumer Price Index September 2026, page 19" in out
    assert result_text(validate(SPEC, EV), "ha").startswith("🧮 *Lissafin Kasafi, ba alƙalumman hukuma ba*")


def test_mixed_index_bases_are_refused() -> None:
    old = Evidence(2, "cpi-2024-09", "CPI September 2024", 2024, 30, "text",
                   "State CPI (November 2009 = 100)\nSokoto 811.2 | Base Year 2009 = 100")
    spec = {**SPEC, "inputs": [SPEC["inputs"][0], {**SPEC["inputs"][1], "value": "811.2", "cited": 2}]}
    with pytest.raises(MixedBases) as e:
        validate(spec, EV + [old])
    assert e.value.bases == ["2009=100", "2024=100"]


@pytest.mark.parametrize("change, why", [
    ({"inputs": [{**SPEC["inputs"][0], "value": "140.0"}, SPEC["inputs"][1]]}, "not in its cited evidence"),
    ({"inputs": [{**SPEC["inputs"][0], "cited": 9}, SPEC["inputs"][1]]}, "citation"),
    ({"formula": "(sep26 / other - 1) * 100"}, "don't match"),
    ({"formula": "__import__('os').system('x')"}, "allowed|match"),
    ({"formula": "sep26 ** 2 + sep25"}, "not allowed"),
])
def test_bad_proposals_are_rejected(change: dict, why: str) -> None:
    with pytest.raises(CalcError, match=why):
        validate({**SPEC, **change}, EV)


def test_arithmetic_is_exact_and_safe() -> None:
    assert evaluate("(a - b) / b * 100", {"a": Decimal("0.3"), "b": Decimal("0.1")}) == Decimal("200")
    with pytest.raises(CalcError, match="division by zero"):
        evaluate("a / b", {"a": Decimal(1), "b": Decimal(0)})
    with pytest.raises(CalcError):
        evaluate("open('x')", {})


def test_round_trip_for_the_pending_offer() -> None:
    calc = validate(SPEC, EV)
    assert Calculation.from_dict(calc.to_dict()) == calc


# --- the answer step offers it ------------------------------------------------------------------

class Fake:
    def __init__(self, replies):
        self.replies = list(replies)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def chat(self, messages, **kw):
        import json
        from app.providers.chat import ChatResult
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


PLAN = {"english_question": "Sokoto YoY CPI?", "search_queries": ["Sokoto CPI"], "doc_ids": ["nbs-cpi-2026-09"]}


def answer(monkeypatch, reply, evidence=EV, lang="en"):
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "nbs-cpi-2026-09"}])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: evidence)
    monkeypatch.setattr(ans, "log_gap", lambda *a, **k: None)
    return asyncio.run(ans.answer_question("q", lang, conn=None, settings=make_settings(),
                                           client_factory=lambda s: Fake([PLAN, reply])))


def test_answer_offers_a_checked_calculation(monkeypatch) -> None:
    reply = {"summary": "The Sokoto year-on-year rate isn't stated; the index was 135.1 [1].", "items": [],
             "found": "partial", "cited": [1], "calculation": SPEC}
    a = answer(monkeypatch, reply)
    assert a.offer is not None and "Reply *Eh* (yes) to calculate." in a.text
    assert "7.99" not in a.text                      # nothing computed until the user agrees


def test_answer_refuses_mixed_bases(monkeypatch) -> None:
    old = Evidence(2, "cpi-2024-09", "CPI September 2024", 2024, 30, "text", "(November 2009 = 100) Sokoto 811.2")
    spec = {**SPEC, "inputs": [SPEC["inputs"][0], {**SPEC["inputs"][1], "value": "811.2", "cited": 2}]}
    a = answer(monkeypatch, {"summary": "Index 135.1 [1].", "items": [], "found": "partial", "cited": [1],
                             "calculation": spec}, evidence=EV + [old])
    assert a.offer is None and "different index base periods (2009=100 / 2024=100)" in a.text


# --- the WhatsApp flow: offer, then Eh runs it with no model call --------------------------------

def run(store: UserStore, msg: dict, answer_fn=None):
    async def no_guard(texts, *, settings):
        from app.guardrails.scope import Verdict
        return Verdict("ok", "none")
    return asyncio.run(handle(msg, None, store=store, settings=make_settings(), guard_fn=no_guard,
                              **({"answer_fn": answer_fn} if answer_fn else {"answer_fn": None})))


class Result:
    def __init__(self, offer):
        self.text, self.sources, self.offer = "Index 135.1 [1]. Reply *Eh* to calculate.", [], offer


def test_eh_runs_the_offered_calculation() -> None:
    store = consented("en")

    async def fake_answer(question, lang, **kw):
        return Result(validate(SPEC, EV))
    outs = run(store, text("Sokoto YoY CPI?"), fake_answer)
    assert outs[0].buttons and outs[0].buttons[0][0] == "calc_yes"
    outs = run(store, text("Eh"))
    assert outs[0].text.startswith("🧮 *Kasafi's calculation, not an official figure*") and "7.99%" in outs[0].text
    assert store.get_pending_calc(store_key(store)) is None


def test_no_or_a_new_question_drops_the_offer() -> None:
    store = consented("en")

    async def fake_answer(question, lang, **kw):
        return Result(validate(SPEC, EV))
    run(store, text("Sokoto YoY CPI?"), fake_answer)
    assert run(store, text("No"))[0].text == "OK, I won't calculate it."
    run(store, text("Sokoto YoY CPI?"), fake_answer)
    outs = run(store, text("How much for health in 2026?"), fake_answer)     # moves on: answered normally
    assert "Kasafi's calculation" not in outs[0].text


def store_key(store: UserStore) -> str:
    return store._exec("SELECT user_key FROM users").fetchone()[0]
