"""External review, finding 01: every cited figure bound to its row (app/agent/attribution.py). Appendix A's
wrong-attribution harness as a test, the five mismatch kinds, and the states in the answer, show working and
the trace."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.agent import answer as answer_module
from app.agent import attribution as A
from app.agent.answer import Answer, Evidence, Plan, settle_verification
from app.config import Settings

PAGE = [Evidence(1, "budget-2026-approved", "2026 Approved Budget", 2026, 10, "text",
                 "Health allocation: 100,000,000.00. Education allocation: 200,000,000.00.")]
ROWS = [Evidence(1, "bir-2025-q3", "Budget Implementation Report Q3 2025", 2025, 19, "text",
                 "[Table: Total Expenditure by Administrative Classification]\n"
                 "052100100100 Ministry of Health | 2025 Approved Budget 14,000,000,000.00 | Actual Expenditure Q1-Q3 5,370,000,000.00\n"
                 "051700100100 Ministry of Education | 2025 Approved Budget 20,000,000,000.00 | Actual Expenditure Q1-Q3 9,100,000,000.00")]


def _page_path(evidence, model_output: dict):
    plan = Plan("How much was allocated to health in 2026?", ["health"], ["budget-2026-approved"])
    with (patch.object(answer_module, "compose", AsyncMock(return_value=model_output)),
          patch.object(answer_module.pool, "run", AsyncMock(return_value=evidence)),
          patch.object(answer_module, "scope_notes", return_value=""),
          patch.object(answer_module, "off_topic_note", return_value="")):
        return asyncio.run(answer_module._page_path(None, plan, plan.english_question, "en", None, Settings(_env_file=None),
                                                    {}, acq=None, latest=None, prev=None, context="", recheck_note="",
                                                    cache={"evidence": evidence}))


def test_appendix_a_wrong_attribution_is_refused_not_verified() -> None:
    """The review's harness: health given education's figure, with a citation. The old check passed it."""
    wrong = {"summary": "Health was allocated 200,000,000.00 in 2026 [1].", "cited": [1], "found": "full"}
    a = _page_path(PAGE, wrong)
    assert a.verified is False and a.verification == "unsupported"
    assert "200,000,000.00" not in a.text and "Sorry" in a.text or "couldn't verify" in a.text.lower() or not a.verified
    assert any(p.startswith("entity:") for p in a.attribution)
    settle_verification(a, "en")
    assert "Verification: unsupported" in a.working


def test_the_correct_attribution_is_checked_and_said() -> None:
    right = {"summary": "Health was allocated 100,000,000.00 in 2026 [1].", "cited": [1], "found": "full"}
    a = _page_path(PAGE, right)
    assert a.verified and a.verification == "attribution checked" and a.attribution == []
    settle_verification(a, "en")
    assert "Verification: attribution checked (1 figure(s)" in a.working
    settle_verification(Answer(a.text, True, True, a.cited, exact=a.exact), "ha")   # the Hausa line exists


def test_a_contradiction_is_corrected_on_the_retry_when_the_model_fixes_it() -> None:
    wrong = {"summary": "Health was allocated 200,000,000.00 in 2026 [1].", "cited": [1], "found": "full"}
    right = {"summary": "Health was allocated 100,000,000.00 in 2026 [1].", "cited": [1], "found": "full"}
    plan = Plan("How much was allocated to health in 2026?", ["health"], ["budget-2026-approved"])
    compose = AsyncMock(side_effect=[wrong, right])
    with (patch.object(answer_module, "compose", compose), patch.object(answer_module.pool, "run", AsyncMock(return_value=PAGE)),
          patch.object(answer_module, "scope_notes", return_value=""), patch.object(answer_module, "off_topic_note", return_value="")):
        a = asyncio.run(answer_module._page_path(None, plan, plan.english_question, "en", None, Settings(_env_file=None), {},
                                                 acq=None, latest=None, prev=None, context="", recheck_note="", cache={"evidence": PAGE}))
    assert compose.call_count == 2 and "wrong row" in compose.call_args.kwargs["feedback"]
    assert a.verified and a.verification == "attribution checked" and "100,000,000.00" in a.exact


@pytest.mark.parametrize("text,state,problem", [
    ("The Ministry of Health spent ₦5.37 billion by Q3 2025 [1].", "attribution checked", ""),
    ("The Ministry of Education spent ₦5.37 billion by Q3 2025 [1].", "unsupported", "entity"),       # wrong entity
    ("The Ministry of Health spent ₦5.37 billion by Q3 2024 [1].", "unsupported", "year"),           # wrong year
    ("The Ministry of Health spent ₦5.37 million by Q3 2025 [1].", "unsupported", "unit"),           # wrong unit
    ("The Ministry of Health was allocated ₦5.37 billion in 2025 [1].", "unsupported", "kind"),      # spending as allocation
    ("Health (₦9.10 billion) spent more than Education (₦5.37 billion) by Q3 2025 [1].", "unsupported", "entity"),  # swapped
    ("Education (₦9.10 billion) spent more than Health (₦5.37 billion) by Q3 2025 [1].", "attribution checked", ""),
    ("The Ministry of Health's 2025 approved budget is ₦14.00 billion, of which ₦5.37 billion was spent by Q3 [1].",
     "attribution checked", ""),
])
def test_wrong_entity_year_unit_kind_and_swapped_comparison(text, state, problem) -> None:
    att = A.bind(text, ROWS)
    assert att.state == state, att.problems
    if problem:
        assert att.problems and att.problems[0].startswith(problem + ":")


def test_hausa_wording_binds_through_the_plans_resolved_names_and_is_otherwise_figures_checked() -> None:
    att = A.bind("Ma'aikatar Lafiya ta kashe ₦5.37 biliyan zuwa Q3 2025 [1].", ROWS, ["Ministry of Health", "052100100100"])
    assert att.state == "attribution checked"
    att = A.bind("Ma'aikatar Lafiya ta kashe ₦5.37 biliyan zuwa Q3 2025 [1].", ROWS)
    assert att.state == "figures checked" and att.ok
    assert A.bind("Ma'aikatar Lafiya ta kashe ₦5.37 biliyan zuwa Q3 2025 [1].", PAGE).state == "unsupported"


def test_structured_answers_are_calculation_checked_and_the_trace_carries_the_state() -> None:
    from app.agent.trace import record
    a = Answer("For the Ministry of Health, the approved budget is ₦70.00 million.", True, True, [], exact="₦70.00 million")
    settle_verification(a, "en")                       # rows and arithmetic in code, no cited page excerpt: calculation
    assert a.verification == "calculation checked" and "Verification: calculation checked" in a.working
    a2 = Answer("text", True, True, [Evidence(1, "d", "t", 2026, 1, "text", "x 70,000,000.00")], exact="₦70,000,000.00 [1]")
    settle_verification(a2, "en")
    assert a2.verification == "figures checked"
    a3 = Answer("Sorry", True, False, [], verification="unsupported", attribution=["entity: …"])
    settle_verification(a3, "en")
    t = record(a3)
    assert t["verification"] == {"state": "unsupported", "problems": ["entity: …"]} and t["verified"] is False
    assert record(a)["verification"]["state"] == "calculation checked"
