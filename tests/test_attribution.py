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
    assert att.state == "attribution checked"                     # the Hausa alias table: lafiya -> health
    att = A.bind("Ma'aikatar Jinya ta kashe ₦5.37 biliyan zuwa Q3 2025 [1].", ROWS)
    assert att.state == "figures checked" and att.ok               # a word the rows don't use: the weaker state
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


# --- follow-up review (1 Nov), finding 1: Appendix A probes, then the valid neighbours that must keep working ------

TWO_EDU = [Evidence(1, "budget-2026-approved", "2026 Approved Budget", 2026, 10, "text",
                    "Ministry of Basic Education allocation: 100,000,000.00.\n"
                    "Ministry of Higher Education allocation: 200,000,000.00.")]
TWO_YEARS = [Evidence(1, "budget-2026-approved", "2026 Approved Budget", 2026, 10, "text",
                      "Ministry of Health | 2025 Approved Budget: 100,000,000.00 | 2026 Approved Budget: 200,000,000.00")]
TWO_PERIODS = [Evidence(1, "budget-2026-approved", "2026 Approved Budget", 2026, 10, "text",
                        "Ministry of Health | Actual expenditure Q1 2026: 100,000,000.00 | "
                        "Actual expenditure Q1-Q3 2026: 200,000,000.00")]


def _page(evidence, question, summary, entities=("health",)):
    plan = Plan(question, list(entities), ["budget-2026-approved"])
    compose = AsyncMock(return_value={"summary": summary, "cited": [1], "found": "full"})
    with (patch.object(answer_module, "compose", compose),
          patch.object(answer_module.pool, "run", AsyncMock(return_value=evidence)),
          patch.object(answer_module, "scope_notes", return_value=""),
          patch.object(answer_module, "off_topic_note", return_value="")):
        a = asyncio.run(answer_module._page_path(None, plan, question, "en", None, Settings(_env_file=None), {},
                                                 acq=None, latest=None, prev=None, context="", recheck_note="",
                                                 cache={"evidence": evidence}))
    return a, compose.call_count


@pytest.mark.parametrize("evidence,question,summary,problem", [
    (TWO_EDU, "How much was allocated to Basic Education in 2026?",
     "The Ministry of Basic Education was allocated 200,000,000.00 in 2026 [1].", "entity"),
    (TWO_YEARS, "How much was allocated to health in 2026?",
     "The Ministry of Health was allocated 100,000,000.00 in 2026 [1].", "year"),
    (TWO_PERIODS, "How much did health spend in Q1 2026?",
     "The Ministry of Health spent 200,000,000.00 in Q1 2026 [1].", "period"),
])
def test_followup_probes_are_refused_never_attribution_checked(evidence, question, summary, problem) -> None:
    a, calls = _page(evidence, question, summary)
    assert a.verified is False and a.verification == "unsupported" and calls == 2, (a.verification, a.attribution)
    assert any(p.startswith(problem + ":") for p in a.attribution), a.attribution


@pytest.mark.parametrize("evidence,text", [
    (TWO_EDU, "The Ministry of Basic Education was allocated 100,000,000.00 in 2026 [1]."),
    (TWO_EDU, "The Ministry of Higher Education was allocated 200,000,000.00 in 2026 [1]."),
    (TWO_EDU, "Basic Education got 100,000,000.00 and Higher Education 200,000,000.00 in 2026 [1]."),
    (TWO_YEARS, "The Ministry of Health was allocated 200,000,000.00 in 2026 [1]."),
    (TWO_YEARS, "Health had 100,000,000.00 in 2025 and 200,000,000.00 in 2026 [1]."),
    (TWO_PERIODS, "The Ministry of Health spent 100,000,000.00 in Q1 2026 [1]."),
    (TWO_PERIODS, "The Ministry of Health spent 200,000,000.00 by Q3 2026 [1]."),
    (TWO_PERIODS, "The Ministry of Health spent 200,000,000.00 in the first nine months of 2026 [1]."),
])
def test_valid_neighbours_stay_attribution_checked(evidence, text) -> None:
    att = A.bind(text, evidence)
    assert att.state == "attribution checked", att.problems


def test_a_shared_word_alone_never_binds() -> None:
    # 'Education' with Basic and Higher rows: either figure is in an Education row, but which one is unknown
    att = A.bind("Education was allocated 200,000,000.00 in 2026 [1].", TWO_EDU)
    assert att.state == "figures checked" and att.ok


def test_a_year_or_period_the_row_cannot_settle_is_the_weaker_state() -> None:
    header = [Evidence(1, "b", "Budget", 2026, 3, "text",
                       "Head | 2025 Approved | 2026 Approved\nMinistry of Health | 100,000,000.00 | 200,000,000.00")]
    att = A.bind("The Ministry of Health was allocated 100,000,000.00 in 2026 [1].", header)
    assert att.state == "figures checked" and att.ok                 # two year columns, no label on the cell


def test_hausa_aliases_bind_per_entity_not_through_any_plan_name() -> None:
    names = [["Ministry of Basic Education", "ilimin firamare"], ["Ministry of Higher Education", "ilimi mai zurfi"]]
    ok = A.bind("Ma'aikatar ilimin firamare ta samu 100,000,000.00 a 2026 [1].", TWO_EDU, names)
    assert ok.state == "attribution checked", ok.problems
    wrong = A.bind("Ma'aikatar ilimin firamare ta samu 200,000,000.00 a 2026 [1].", TWO_EDU, names)
    assert wrong.state != "attribution checked"
    assert A.bind("Ma'aikatar Lafiya ta kashe ₦5.37 biliyan zuwa Q3 2025 [1].", ROWS,
                  ["Ministry of Health", "052100100100"]).state == "attribution checked"


def test_periods_parse_in_both_languages() -> None:
    assert A.periods("spent in Q1 2026") == {(1, 1)} and A.periods("Q1-Q3 2026") == {(1, 3)}
    assert A.periods("by Q3 2025") == {(1, 3)} and A.periods("in the first half of 2026") == {(1, 2)}
    assert A.periods("zuwa kwata ta uku") == {(1, 3)} and A.periods("a kwata ta farko") == {(1, 1)}
    assert A.periods("the Q3 2025 report says") == set() and A.periods("in 2026") == set()
