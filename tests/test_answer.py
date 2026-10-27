import asyncio
import json

import pytest

from app.agent import answer as ans
from app.agent.answer import Evidence, Plan, format_citations, unverified_numbers
from app.providers.chat import ChatResult
from tests.helpers import make_settings

EV = [
    Evidence(1, "budget-2026-approved", "Sokoto State FY 2026 Budget", 2026, 40, "text",
             "[Table: Total Expenditure by Programme]\n05 Education | 2026 Approved Budget: 128,495,868,362.13"),
    Evidence(2, "smart-agenda", "Sokoto State 9-Point SMART Agenda", None, 3, "ocr", "Security 01 Education 03"),
]


def test_unverified_numbers_ignores_citation_markers_and_formatting() -> None:
    assert unverified_numbers("An ware 128,495,868,362.13 ga ilimi [1].", EV) == []
    assert unverified_numbers("An ware 128495868362.13 [1]", EV) == []                 # commas don't matter
    assert unverified_numbers("An ware 130,000,000,000.00 [1]", EV) == ["130,000,000,000.00"]
    assert unverified_numbers("Kashi 12% ne [1]", EV) == ["12"]                      # a computed % isn't in the evidence


def test_citations_show_page_word_in_user_language_and_ocr_flag() -> None:
    assert format_citations(EV, "ha") == ("[1] Sokoto State FY 2026 Budget, shafi 40\n"
                                          "[2] Sokoto State 9-Point SMART Agenda, shafi 3 (OCR)")
    assert "page 40" in format_citations(EV[:1], "en")


def test_assumption_shown_in_user_language() -> None:
    p = Plan("q", ["x"], [], "used the latest budget, 2026", "Na yi amfani da kasafin 2026 mafi sabo.")
    assert p.assumption_for("ha") == "Na yi amfani da kasafin 2026 mafi sabo."
    assert p.assumption_for("en") == "Assumption: used the latest budget, 2026."
    assert Plan("q", [], []).assumption_for("ha") == ""


# --- answer_question with a fake model and fake retrieval ------------------------------------

class FakeClient:
    """Replies to the planner, then to each compose call, from a queue."""

    def __init__(self, replies: list[dict]) -> None:
        self.replies, self.calls = list(replies), []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


PLAN = {"english_question": "How much for education?", "search_queries": ["education total"],
        "doc_ids": ["budget-2026-approved"], "assumption": "used the latest budget, 2026",
        "assumption_ha": "Na yi amfani da kasafin 2026 mafi sabo."}


def run(monkeypatch, replies: list[dict], evidence=EV):
    fake = FakeClient(replies)
    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "budget-2026-approved", "title": "t"}])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: evidence)
    a = asyncio.run(ans.answer_question("Nawa aka ware wa ilimi?", "ha", conn=None, settings=make_settings(),
                                        client_factory=lambda s: fake))
    return a, fake


def test_grounded_answer_with_assumption_and_citation(monkeypatch) -> None:
    a, fake = run(monkeypatch, [PLAN, {"answer": "An ware 128,495,868,362.13 ga ilimi [1].", "found": "full", "cited": [1]}])
    assert a.found and a.verified and not a.partial
    assert a.text.startswith("_Na yi amfani da kasafin 2026 mafi sabo._")
    assert "128,495,868,362.13" in a.text and "[1] Sokoto State FY 2026 Budget, shafi 40" in a.text
    evidence_msg = fake.calls[1][1]["content"]
    assert "EVIDENCE:" in evidence_msg and "Reply in Hausa" in evidence_msg


def test_unverified_figure_is_retried_then_replaced_by_sources(monkeypatch) -> None:
    bad = {"answer": "An ware 130,000,000,000.00 [1].", "found": "full", "cited": [1]}
    a, fake = run(monkeypatch, [PLAN, bad, bad])
    assert len(fake.calls) == 3 and "CORRECTION NEEDED" in fake.calls[2][1]["content"]
    assert a.found and not a.verified and "130,000,000,000.00" not in a.text
    assert a.text.startswith(ans.UNVERIFIED["ha"]) and "shafi 40" in a.text


def test_retry_that_fixes_the_figure_is_accepted(monkeypatch) -> None:
    bad = {"answer": "An ware 130,000,000,000.00 [1].", "found": "full", "cited": [1]}
    good = {"answer": "An ware 128,495,868,362.13 [1].", "found": "full", "cited": [1]}
    a, _ = run(monkeypatch, [PLAN, bad, good])
    assert a.verified and "128,495,868,362.13" in a.text


def test_partial_answer_is_sent(monkeypatch) -> None:
    a, _ = run(monkeypatch, [PLAN, {"answer": "Rahoton bai bayar da jimillar ba [1].", "found": "partial", "cited": [1]}])
    assert a.found and a.partial and "Rahoton bai bayar" in a.text


@pytest.mark.parametrize("reply", [{"answer": "Ban samu ba.", "found": "none", "cited": []},
                                   {"answer": "x", "found": "full", "cited": [99]},          # cites nothing real
                                   {"answer": "", "found": "full", "cited": [1]}])
def test_not_found_cases(monkeypatch, reply: dict) -> None:
    a, _ = run(monkeypatch, [PLAN, reply])
    assert not a.found and a.text == ans.NOT_FOUND["ha"]


def test_no_evidence_skips_the_answer_call(monkeypatch) -> None:
    a, fake = run(monkeypatch, [PLAN], evidence=[])
    assert not a.found and len(fake.calls) == 1


def test_planner_drops_unknown_doc_ids_and_caps_lists(monkeypatch) -> None:
    plan = {**PLAN, "doc_ids": ["nope", "budget-2026-approved", "x", "y"], "search_queries": ["a", "b", "c", "d"]}
    a, _ = run(monkeypatch, [plan, {"answer": "An ware 128,495,868,362.13 [1].", "found": "full", "cited": [1]}])
    assert a.plan.doc_ids == ["budget-2026-approved"] and len(a.plan.search_queries) == 3
