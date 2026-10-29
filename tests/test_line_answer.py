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
    fake = Fake([bad] * 4)                                   # two readings, each retried once
    res = asyncio.run(read_lines("q", "q", "en", LINES, fake, make_settings(), [], ans.chat_json))
    assert len(fake.calls) == 4 and "CORRECT" not in res.summary and res.summary == ""
    assert res.selections[0].cell.amount == Decimal("70000000.00")      # the verified row still answers


GOOD = {"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "summary": "It is 70,000,000.00 [L1].",
        "found": "full"}


class Slow(Fake):
    async def chat(self, messages, **kw):
        await asyncio.sleep(5)


class Down(Fake):
    async def chat(self, messages, **kw):
        raise RuntimeError("Baseten API 503")


def test_the_second_reading_runs_on_muse_spark_open() -> None:
    meta, spark_open = Fake([GOOD]), Fake([GOOD])
    s = make_settings()
    res = asyncio.run(read_lines("q", "q", "en", LINES, meta, s, [], ans.chat_json, spark_open))
    assert len(meta.calls) == 1 and len(spark_open.calls) == 1
    assert res.readers == [s.meta_model, "meta-models/muse-spark-open-1026"] and res.selections


def test_a_slow_or_failing_muse_spark_open_falls_back_to_muse_spark(caplog) -> None:
    s = make_settings(kasafi_open_read_timeout_s=0.05)
    for second in (Slow([]), Down([])):
        meta = Fake([GOOD, GOOD])
        res = asyncio.run(read_lines("q", "q", "en", LINES, meta, s, [], ans.chat_json, second))
        assert len(meta.calls) == 2 and res.readers == [s.meta_model, f"{s.meta_model} (fallback)"]
        assert res.selections[0].cell.amount == Decimal("70000000.00")
    assert caplog.text.count("Muse Spark Open reading fell back to Muse Spark") == 2


def test_no_baseten_key_means_no_open_reader() -> None:
    async def get():
        async with ans.open_reader(make_settings()) as c:
            return c
    assert asyncio.run(get()) is None


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


def test_share_and_ratio_sum_each_side() -> None:
    tot = L(5, "Total Expenditure", 16, [("2026 Approved Budget", "758700526537.89")], table="Total Expenditure")
    hea = L(6, "Health", 40, [("2026 Approved Budget", "118827792994.59")], table="Expenditure by Programme")
    per = L(7, "PERSONNEL COST", 1, [("2026 Approved Budget", "70571647882.76")], table="Summary")
    ovh = L(8, "OTHER RECURRENT COSTS", 1, [("2026 Approved Budget", "134785286551.67")], table="Summary")
    cap = L(9, "CAPITAL EXPENDITURE", 1, [("2026 Approved Budget", "553343592103.46")], table="Summary")
    lines = [tot, hea, per, ovh, cap]
    res, _ = verify({"operation": "share", "found": "full", "selected": [
        {"line": "L2", "column": "2026 Approved Budget", "part": "top"},
        {"line": "L1", "column": "2026 Approved Budget", "part": "bottom"}]}, lines)
    assert res.share_pct == Decimal("15.7")                         # health / total expenditure, never revenue
    res, _ = verify({"operation": "ratio", "found": "full", "selected": [
        {"line": "L5", "column": "2026 Approved Budget", "part": "top"},
        {"line": "L3", "column": "2026 Approved Budget", "part": "bottom"},
        {"line": "L4", "column": "2026 Approved Budget", "part": "bottom"}]}, lines)
    assert res.ratio == Decimal("2.69")                             # capital / (personnel + other recurrent)
    assert fill("Ratio {RATIO} (Kasafi's calculation).", res) == "Ratio 2.69 : 1 (Kasafi's calculation)."


def test_lga_question_with_nothing_found_explains_state_vs_lga_money() -> None:
    from app.agent.budget_query import lga_in
    assert lga_in("Karamar Hukumar Wamakko") == "Wamakko" and lga_in("Ministry of Health") is None
    assert "statutory allocations" in ans.LGA_NOT_FOUND["en"].format(lga="Wamakko")


def test_compare_is_always_the_change_from_the_earlier_year() -> None:
    old = L(10, "State Universal Basic Education Board (SUBEB)", 16, [("2025 Approved Budget", "8420000000.00")],
            doc="budget-2025-approved", table="Capital Expenditure by Administrative Classification")
    new = L(11, "State Universal Basic Education Board (SUBEB)", 27, [("2026 Approved Budget", "9150000000.00")],
            table="Capital Expenditure by Administrative Classification")
    res, _ = verify({"operation": "compare", "found": "full", "selected": [
        {"line": "L1", "column": "2025 Approved Budget"}, {"line": "L2", "column": "2026 Approved Budget"}]}, [old, new])
    assert res.difference == Decimal("730000000.00") and res.change_pct == Decimal("8.7")      # a rise, not a cut
    assert res.compared == "2026 Approved Budget vs 2025 Approved Budget"


def test_lines_from_different_tables_of_one_budget_are_not_added() -> None:
    programme = L(12, "Animal health and livestock diseases management", 40, [("2026 Approved Budget", "12930000000.00")],
                  table="Expenditure by Programme")
    project = L(13, "Development of Grazing Reserve", 61, [("2026 Approved Budget", "50000000.00")])
    res, _ = verify({"operation": "sum", "found": "full", "selected": [
        {"line": "L1", "column": "2026 Approved Budget"}, {"line": "L2", "column": "2026 Approved Budget"}]},
        [programme, project])
    assert res.total is None and res.not_summed
    a = ans.line_answer(None, ans.Plan("q", [], []), res, [programme, project], "en", {}, None)
    assert "Not added up" in a.text and "Total:" not in a.text


def test_the_code_of_a_line_is_shown_to_the_model_and_the_reader() -> None:
    siec = L(14, "Sokoto State Independent Electoral Commission", 16, [("2026 Approved Budget", "460480000.00")],
             table="Total Expenditure by Administrative Classification")
    siec.code = "014800000000"
    from app.agent.line_answer import listing
    assert "code 014800000000" in listing([siec])
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "found": "full"}, [siec])
    a = ans.line_answer(None, ans.Plan("q", [], []), res, [siec], "en", {}, None)
    assert "(code 014800000000)" in a.text and "page 16" in a.text


def _c(i, name, page, col, amount, doc="budget-2026-approved", measure=None):
    x = L(i, name, page, [(col, amount)], doc=doc, table="Capital Expenditure by Administrative Classification")
    if measure:
        x.cells[0].measure = measure
    return x


def test_budget_against_spending_of_the_same_year_is_the_share_spent() -> None:
    lines = [_c(1, "SEMA", 27, "2026 Approved Budget", "1200000000"),
             _c(2, "SEMA", 27, "2026 Performance Year to Date (Q1-Q2)", "543570000", doc="bir-2026-q2", measure="actual")]
    res, _ = verify({"operation": "compare", "found": "full", "selected": [
        {"line": "L1", "column": "2026 Approved Budget"},
        {"line": "L2", "column": "2026 Performance Year to Date (Q1-Q2)"}]}, lines)
    assert res.spent_pct == Decimal("45.3") and res.change_pct is None and res.difference == Decimal("-656430000")


def test_a_share_of_a_combined_total_counts_the_part_in_the_whole() -> None:
    lines = [_c(1, "Agency for Almajiri Matters", 27, "2026 Approved Budget", "370000000"),
             _c(2, "Arabic and Islamic Education Board", 27, "2026 Approved Budget", "840000000")]
    res, _ = verify({"operation": "share", "found": "full", "selected": [
        {"line": "L1", "column": "2026 Approved Budget", "part": "both"},
        {"line": "L2", "column": "2026 Approved Budget", "part": "bottom"}]}, lines)
    assert res.share_pct == Decimal("30.6")                     # 370 / (370 + 840), not 370 / 840


def test_a_ratio_across_years_drops_items_only_one_side_has() -> None:
    lines = [_c(1, "Ministry of Commerce", 27, "2026 Performance Year to Date (Q1-Q2)", "112820000", measure="actual"),
             _c(2, "Ministry for Skills Acquisition", 27, "2026 Performance Year to Date (Q1-Q2)", "115780000",
                measure="actual"),
             _c(3, "Ministry of Commerce", 30, "2025 Performance Year to Date (Q1-Q4)", "1420000000",
                doc="bir-2025-q4", measure="actual")]
    res, problems = verify({"operation": "ratio", "found": "full", "selected": [
        {"line": "L1", "column": "2026 Performance Year to Date (Q1-Q2)", "part": "top"},
        {"line": "L2", "column": "2026 Performance Year to Date (Q1-Q2)", "part": "top"},
        {"line": "L3", "column": "2025 Performance Year to Date (Q1-Q4)", "part": "bottom"}]}, lines)
    assert [s.line.name for s in res.selections] == ["Ministry of Commerce", "Ministry of Commerce"]
    assert res.ratio == Decimal("0.08") and "Ministry for Skills Acquisition" in res.missing and problems


def test_missing_terms_split_phrases_into_searchable_words() -> None:
    terms = ans.missing_terms("domestic debt servicing; external debt deductions")
    assert terms[:2] == ["domestic debt servicing", "external debt deductions"]
    assert "domestic" in terms and "servicing" in terms and "the" not in terms


def test_a_printed_figure_is_never_labelled_a_calculation() -> None:
    res, _ = verify({"selected": [{"line": "L4", "column": "2026 Approved Budget"}], "found": "full"}, LINES)
    assert fill("The ministry total is ₦104.64 biliyan [L4] (lissafin Kasafi).", res) == \
        "The ministry total is ₦104.64 biliyan [L4]."


def test_spending_by_location_is_never_called_an_lga_allocation() -> None:
    loc = L(20, "WAMAKKO", 75, [("2026 Approved Budget", "82180000000")],
            table="Sokoto State Government 2026 Approved Budget - Total Expenditure by Location")
    loc.code, loc.classification = "33312100", "other"
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "found": "full",
                     "summary": "₦82,180,000,000.00 was allocated directly to Wamakko LGA [L1]."}, [loc])
    a = ans.line_answer(None, ans.Plan("q", [], []), res, [loc], "en", {}, None)
    assert "allocated directly" not in a.text and "state spending located in Wamakko" in a.text
    assert "not money allocated to Wamakko Local Government" in a.text


def test_an_uncomputed_placeholder_drops_the_summary() -> None:
    res, _ = verify({"selected": [{"line": "L1", "column": "2026 Approved Budget"}], "operation": "list",
                     "found": "full"}, LINES)
    assert fill("It is {SPENT_PCT} (Kasafi's calculation) spent [L1].", res) == ""


def _pick(*picks, op="list"):
    return {"selected": [{"line": l, "column": "2026 Approved Budget"} for l in picks], "operation": op,
            "found": "full", "summary": ""}


def test_two_readings_that_agree_answer_as_one() -> None:
    from app.agent.line_answer import reconcile
    r1, _ = verify(_pick("L1", "L3"), LINES)
    r2, _ = verify(_pick("L3", "L1"), LINES)
    res = reconcile(r1, _pick("L1", "L3"), r2, LINES, [], "q", "en")
    assert res is r1 and not res.uncertain


def test_rows_only_one_reading_chose_are_named_but_not_counted() -> None:
    from app.agent.line_answer import reconcile
    d1 = _pick("L1", "L3", op="sum")
    r1, _ = verify(d1, LINES)
    r2, _ = verify(_pick("L1", "L4", op="sum"), LINES)
    res = reconcile(r1, d1, r2, LINES, [], "q", "en")
    assert [s.line.id for s in res.selections] == [BHC.id]
    assert res.total is None and res.disputed           # a total of the agreed rows alone would mislead
    assert res.found == "partial" and len(res.uncertain) == 2 and any("SOCHEMA" in u for u in res.uncertain)
    a = ans.line_answer(None, ans.Plan("q", [], []), res, LINES, "en", {}, None)
    assert "not counted" in a.text and "Not added up: on a second reading" in a.text and "Total:" not in a.text
    assert a.partial


def test_two_readings_with_nothing_in_common_ask_which_one() -> None:
    from app.agent.line_answer import reconcile
    r1, _ = verify(_pick("L1"), LINES)
    r2, _ = verify(_pick("L4"), LINES)
    res = reconcile(r1, _pick("L1"), r2, LINES, [], "How much for counterpart funds?", "ha")
    assert not res.selections and len(res.clarify) == 2 and res.clarify_question.startswith("Zan iya")
    assert res.clarify[1]["question"].startswith("How much for counterpart funds? (Ministry of Health")


def test_missing_terms_split_on_and_or_and_hausa_da() -> None:
    assert ans.missing_terms("orphanages and destitute homes")[:2] == ["orphanages", "destitute homes"]
    assert ans.missing_terms("gidajen ma'aikata da gidaje")[:2] == ["gidajen ma'aikata", "gidaje"]
    assert ans.missing_terms("special schools – none shown")[:1] == ["special schools"]


def test_the_same_figure_from_another_document_counts_as_the_same_pick() -> None:
    from app.agent.line_answer import reconcile
    bud = _c(1, "INDEPENDENT REVENUE", 1, "2025 Approved Budget", "47444195829.40", doc="budget-2025-approved")
    rep = _c(2, "INDEPENDENT REVENUE", 9, "2025 Original Budget", "47444195829.40", doc="bir-2025-q4")
    rep.cells[0].measure = "original"
    lines = [bud, rep]
    d1 = {"selected": [{"line": "L1", "column": "2025 Approved Budget"}], "found": "full"}
    r1, _ = verify(d1, lines)
    r2, _ = verify({"selected": [{"line": "L2", "column": "2025 Original Budget"}], "found": "full"}, lines)
    res = reconcile(r1, d1, r2, lines, [], "q", "en")
    assert [s.line.id for s in res.selections] == [bud.id] and not res.uncertain and not res.clarify
