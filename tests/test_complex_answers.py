"""Complex questions: query_budget answers show their working; clarifying questions with buttons."""

import asyncio
import json
from decimal import Decimal

from app.agent import answer as ans
from app.agent.answer import Answer
from app.agent.budget_query import Item, ItemResult, Picked, QueryResult
from app.guardrails.scope import Verdict
from app.providers.chat import ChatResult
from app.whatsapp.conversation import handle
from tests.helpers import make_settings
from tests.test_conversation_answers import consented, text


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


T26 = "Sokoto State Government 2026 Approved Budget - Capital Expenditure by Functional Classification"
R26 = "7094 TERTIARY EDUCATION | 2025 Revised Budget: 6,707,032,782.20 | 2026 Approved Budget: 20,666,975,000.00"
R25 = "7094 TERTIARY EDUCATION | 2025 Approved Budget: 7,824,339,750.89"


def P(doc, title, page, label, amount, row, table=T26):
    return Picked(doc, title, page, table, "7094", "TERTIARY EDUCATION", label, Decimal(amount), row)


A26 = P("budget-2026-approved", "Sokoto State FY 2026 Budget", 38, "2026 Approved Budget", "20666975000.00", R26)
A25 = P("budget-2025-approved", "Sokoto State Government 2025 Approved Budget", 22, "2025 Approved Budget", "7824339750.89", R25)
REV = P("budget-2026-approved", "Sokoto State FY 2026 Budget", 38, "2025 Revised Budget", "6707032782.20", R26)

PLAN = {"english_question": "Tertiary capital 2026 vs 2025?", "search_queries": ["x"], "doc_ids": [],
        "budget_query": {"operation": "compare", "items": [{"label": "2026"}, {"label": "2025"}]}}


def run(monkeypatch, q: QueryResult, summary: str, lang="en", plan=PLAN):
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [])
    monkeypatch.setattr(ans, "run_budget_query", lambda conn, spec: q)
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: (_ for _ in ()).throw(AssertionError("no search")))
    monkeypatch.setattr(ans, "log_gap", lambda *a, **k: None)
    monkeypatch.setattr(ans, "cited_sources", lambda conn, cited: [])
    fake = Fake([plan, {"summary": summary, "items": [], "found": "full", "cited": [1, 2]}])
    a = asyncio.run(ans.answer_question("q", lang, conn=None, settings=make_settings(), client_factory=lambda s: fake))
    return a, fake


def compare_result() -> QueryResult:
    q = QueryResult("compare", [ItemResult(Item("2026 capital, tertiary education"), [A26]),
                                ItemResult(Item("2025 capital, tertiary education"), [A25], alt=REV)])
    q.difference, q.change_pct = Decimal("12842635249.11"), Decimal("164.1")
    return q


def test_compare_answer_shows_working_with_every_row_cited(monkeypatch) -> None:
    a, fake = run(monkeypatch, compare_result(),
                  "2026 tertiary capital is 20,666,975,000.00 [1], up 12,842,635,249.11 (Kasafi's calculation) on 2025 [2].")
    assert a.found and a.verified and not a.partial
    # the rows and arithmetic are the working, sent on "show working"; the reply names the sources in one line
    assert "🧮 *Working* (the rows used):" in a.working and "🧮" not in a.text
    assert "• 2026 capital, tertiary education: TERTIARY EDUCATION (7094), 2026 Approved Budget: ₦20.67 billion [1]" in a.working
    assert "(also TERTIARY EDUCATION (7094), 2025 Revised Budget: ₦6.71 billion [1])" in a.working
    assert "• Difference: +₦12.84 billion (+164.1%) (Kasafi's calculation)" in a.working
    assert "📄 *Sources:* Sokoto State FY 2026 Budget, p. 38; Sokoto State Government 2025 Approved Budget, p. 22" in a.text
    assert a.text.startswith("2026 tertiary capital is ₦20.67 billion, up ₦12.84 billion") and "[1]" not in a.text
    composer = fake.calls[1][1]["content"]
    assert "BUDGET QUERY RESULTS" in composer and "12,842,635,249.11" in composer
    assert "20,666,975,000.00" in a.exact                       # for the eval and the evidence crops


def test_missing_item_makes_a_partial_answer(monkeypatch) -> None:
    q = QueryResult("compare", [ItemResult(Item("2026 capital"), [A26]), ItemResult(Item("2019 capital"), [])])
    a, _ = run(monkeypatch, q, "2026 is 20,666,975,000.00 [1]; 2019 was not found.", lang="ha")
    assert a.partial and "• 2019 capital: ba a samu a teburorin kasafi ba" in a.working and "not found" in a.text


def test_no_rows_falls_back_to_document_search(monkeypatch) -> None:
    searched = []
    q = QueryResult("lookup", [ItemResult(Item("x"), [])])
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [])
    monkeypatch.setattr(ans, "run_budget_query", lambda conn, spec: q)
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: searched.append(1) or [])
    monkeypatch.setattr(ans, "log_gap", lambda *a, **k: None)
    asyncio.run(ans.answer_question("q", "en", conn=None, settings=make_settings(), client_factory=lambda s: Fake([PLAN])))
    assert searched == [1]


CLARIFY = {**PLAN, "budget_query": None, "clarify": {"question": "Which 2025 figure do you mean?", "options": [
    {"title": "Approved budget", "question": "Tertiary capital 2026 vs 2025 approved?"},
    {"title": "Revised budget", "question": "Tertiary capital 2026 vs 2025 revised?"}]}}


def test_two_readings_ask_instead_of_answering(monkeypatch) -> None:
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [])
    fake = Fake([CLARIFY])
    a = asyncio.run(ans.answer_question("q", "en", conn=None, settings=make_settings(), client_factory=lambda s: fake))
    assert a.text == "Which 2025 figure do you mean?" and [o["title"] for o in a.clarify] == ["Approved budget", "Revised budget"]
    assert len(fake.calls) == 1                                # no search, no composing


def test_clarify_field_needs_two_usable_options() -> None:
    assert ans._clarify_field({"question": "x", "options": [{"title": "a", "question": "qa"}]}) == {}
    assert ans._clarify_field("nonsense") == {}
    long = ans._clarify_field({"question": "x", "options": [{"title": "a very long button title indeed", "question": "q1"},
                                                            {"title": "b", "question": "q2"}]})
    assert len(long["options"][0]["title"]) <= 20


# --- the WhatsApp flow ----------------------------------------------------------------------------------

def run_flow(store, msg, asked: list):
    async def fake_answer(question, lang, **kw):
        asked.append(question)
        if question.startswith("Tertiary capital 2026 vs 2025?"):
            return Answer("Which 2025 figure do you mean?", False, True, clarify=CLARIFY["clarify"]["options"])
        return Answer(f"ANSWER: {question}", True, True)

    async def no_guard(texts, *, settings):
        return Verdict("ok", "none")
    return asyncio.run(handle(msg, None, store=store, settings=make_settings(), guard_fn=no_guard, answer_fn=fake_answer))


def button(bid: str) -> dict:
    return {"from": "2340000000001", "type": "interactive", "interactive": {"type": "button_reply", "button_reply": {"id": bid}}}


def test_clarify_buttons_then_the_choice_is_answered() -> None:
    store, asked = consented("en"), []
    outs = run_flow(store, text("Tertiary capital 2026 vs 2025?"), asked)
    assert outs[0].buttons == [("clar_0", "Approved budget"), ("clar_1", "Revised budget")]
    outs = run_flow(store, button("clar_1"), asked)
    assert asked[-1] == "Tertiary capital 2026 vs 2025 revised?" and outs[0].text.startswith("ANSWER:")


def test_clarify_by_number_or_title_and_lapse_on_anything_else() -> None:
    store, asked = consented("en"), []
    run_flow(store, text("Tertiary capital 2026 vs 2025?"), asked)
    run_flow(store, text("1"), asked)
    assert asked[-1] == "Tertiary capital 2026 vs 2025 approved?"
    run_flow(store, text("Tertiary capital 2026 vs 2025?"), asked)
    run_flow(store, text("How much for health in 2026?"), asked)            # a new question: the options lapse
    assert asked[-1] == "How much for health in 2026?"
    run_flow(store, text("2"), asked)
    assert asked[-1] == "2"                                                  # nothing pending any more
