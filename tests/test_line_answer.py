"""Model reads, code verifies (app/agent/line_answer.py)."""

import asyncio
import json
from decimal import Decimal

from app.agent import answer as ans
from app.agent.line_answer import _number_ok, allowed_numbers, fill, read_lines, short_name, verify
from app.providers.chat import ChatResult
from app.retrieval.line_search import Cell, Line
from tests.helpers import make_settings


def L(i, name, page, cols, doc="budget-2026-approved", table="Capital Expenditure by Project", row=None):
    cells = [Cell(c, int(c[:4]), "approved" if "Approved" in c else "revised", "full_year", Decimal(v)) for c, v in cols]
    text = row or f"{name} | " + " | ".join(f"{c}: {Decimal(v):,.2f}" for c, v in cols)
    return Line(f"{doc}:{page}:{i}", "Sokoto State FY 2026 Budget", doc, page, table, name, text, "project", "", "", 5.0, cells)


BHC = L(1, "Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT 052100100100 - Ministry of Health 23050103 - M",
        67, [("2025 Revised Budget", "70000000.00"), ("2026 Approved Budget", "70000000.00")])
BHC_COPY = L(2, BHC.name, 229, [("2026 Approved Budget", "70000000.00")], table="Primary Health Capital Expenditure by Project")
SOC = L(3, "BHCF Counterpart Funds for SOCHEMA 052100200100 - Sokoto State contributory health care mgt agency 23050101 - R",
        70, [("2026 Approved Budget", "45000000.00")])
MOH = L(4, "Ministry of Health", 27, [("2026 Approved Budget", "104644218330.85")], table="Capital Expenditure by Administrative")
LINES = [BHC, BHC_COPY, SOC, MOH]


def test_short_name_keeps_the_items_words_and_its_agency() -> None:
    assert short_name(BHC) == "Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health)"


def test_verify_reads_amounts_from_the_cells_and_rejects_bad_ids_and_columns() -> None:
    res, problems = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"},
                                         {"line": "L9", "column": "2026 Approved Budget"},
                                         {"line": "L3", "column": "2027 Out-Year Estimate"}],
                            "operation": "list", "found": "full"}, LINES)
    assert [s.cell.amount for s in res.selections] == [Decimal("70000000.00")]
    assert any("L9 is not one" in p for p in problems) and any("no column '2027 Out-Year Estimate'" in p for p in problems)


def test_same_project_in_two_tables_is_counted_once_and_sums_are_computed_by_code() -> None:
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"},
                                  {"line": "L2", "column": "2026 Approved Budget"},
                                  {"line": "L3", "column": "2026 Approved Budget"}], "operation": "sum", "found": "full"},
                    LINES)
    assert len(res.selections) == 2 and res.total == Decimal("115000000.00")
    assert fill("Together {TOTAL} (Kasafi's calculation) [L1][L3].", res) == \
        "Together 115,000,000.00 (Kasafi's calculation) [L1][L3]."


def test_compare_and_share_and_a_broader_total_is_partial() -> None:
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"},
                                  {"line": "L1", "column": "2025 Revised Budget"}], "operation": "compare",
                     "found": "full"}, LINES)
    assert res.difference == Decimal(0) and res.change_pct == Decimal("0.0")
    res, _ = verify({"selected": [{"line": "L4", "column": "2026 Approved Budget"}], "aggregate_only": True,
                     "found": "full"}, LINES)
    assert res.aggregate_only and res.found == "partial"


def test_summary_numbers_must_be_printed_in_the_chosen_rows_or_computed() -> None:
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "found": "full"}, LINES)
    ok = allowed_numbers(res, ["2026"])
    assert _number_ok("₦70,000,000.00 in 2026 [L1].", ok) == []
    assert _number_ok("₦75,000,000.00 [L1].", ok) == ["75,000,000.00"]


def test_clarify_only_when_nothing_is_selected() -> None:
    c = {"question": "Which one?", "options": [{"title": "Drugs", "question": "q1"}, {"title": "Equipment", "question": "q2"}]}
    res, _ = verify({"selected": [], "found": "none", "clarify": c}, LINES)
    assert res.clarify_question == "Which one?" and [o["title"] for o in res.clarify] == ["Drugs", "Equipment"]
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "clarify": c}, LINES)
    assert res.clarify == []


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


def test_a_wrong_figure_in_the_summary_is_retried_then_dropped() -> None:
    bad = {"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "summary": "It is 75,000,000.00 [L1].",
           "found": "full"}
    fake = Fake([bad, bad])
    res = asyncio.run(read_lines("q", "q", "en", LINES, fake, make_settings(), [], ans.chat_json))
    assert len(fake.calls) == 2 and "CORRECT" not in res.summary and res.summary == ""
    assert res.selections[0].cell.amount == Decimal("70000000.00")      # the verified row still answers


def test_line_answer_shows_rows_with_citations(monkeypatch) -> None:
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"},
                                  {"line": "L3", "column": "2026 Approved Budget"}], "operation": "sum",
                     "summary": "BHCPF counterpart lines total {TOTAL} (Kasafi's calculation) [L1][L3].",
                     "found": "full"}, LINES)
    res.summary = fill(res.summary, res)
    a = ans.line_answer(None, ans.Plan("q", [], []), res, LINES, "en", {}, None)
    assert "BHCPF counterpart lines total ₦115.00 million (Kasafi's calculation) [1][2]." in a.text
    assert "• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved " \
           "Budget: ₦70.00 million [1]" in a.text
    assert "[1] Sokoto State FY 2026 Budget, page 67" in a.text and "[2] Sokoto State FY 2026 Budget, page 70" in a.text
    assert "70,000,000.00" in a.exact and a.found and not a.partial
