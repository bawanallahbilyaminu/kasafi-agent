"""Model reads, code verifies (app/agent/line_answer.py)."""

import asyncio
import json
from decimal import Decimal

from app.agent import answer as ans
from app.agent.line_answer import LineResult, _number_ok, allowed_numbers, fill, read_lines, short_name, verify
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


def test_bare_zero_figures_are_left_out_of_the_summary_list() -> None:
    s = ("Medical equipment: 0.00 [L4], 150,000,000.00 [L1], 0.00 [L2], 2,500,000,000.00 [L3], 0.00 [L5] [L6], "
         "jimillarsu. Another: 40,000,000.00 [L7], 0.00 [L8] and 5.00 [L9]; Line X: 0.00 [L2].")
    assert fill(s, LineResult()) == ("Medical equipment: 150,000,000.00 [L1], 2,500,000,000.00 [L3], jimillarsu. "
                                     "Another: 40,000,000.00 [L7] and 5.00 [L9]; Line X: 0.00 [L2].")


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
    # the reply: plain sentence, the top rows (no [n] markers), one sources line; the working on request
    assert a.text.startswith("BHCPF counterpart lines total ₦115.00 million (Kasafi's calculation).")
    assert "• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved " \
           "Budget: ₦70.00 million\n" in a.text
    assert "📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 70" in a.text and "show working" in a.text
    assert "Budget: ₦70.00 million [1]" in a.working and "• Total: ₦115.00 million (Kasafi's calculation)" in a.working
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
    assert "(code 014800000000)" in a.text and "p. 16" in a.text


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


HEALTH = L(5, "HEALTH", 32, [("2026 Approved Budget", "120127992994.59")], table="Expenditure by Function")
TOTAL_EXP = L(6, "Total Expenditure", 1, [("2026 Approved Budget", "758700526537.89")], table="Budget Summary")
TOTAL_REV = L(7, "Total Revenue (including OB)", 1, [("2026 Approved Budget", "760000000000.00")],
              table="Budget Summary")
SHARE_LINES = [HEALTH, TOTAL_EXP, TOTAL_REV]


def _share(*picks):
    return {"selected": [{"line": l, "column": "2026 Approved Budget", "part": p} for l, p in picks],
            "operation": "share", "found": "full", "summary": ""}


def test_a_share_of_spending_is_never_of_revenue() -> None:
    res, problems = verify(_share(("L1", "top"), ("L2", "bottom"), ("L3", "bottom")), SHARE_LINES)
    assert [s.line.name for s in res.selections] == ["HEALTH", "Total Expenditure"] and res.share_pct == Decimal("15.8")
    assert any("not revenue" in p for p in problems)          # the reader is told, and retries
    _, problems = verify(_share(("L1", "top")), SHARE_LINES)
    assert any("a share needs its whole" in p for p in problems)


def test_a_share_stands_on_the_printed_whole_only_one_reading_found() -> None:
    from app.agent.line_answer import reconcile
    d1 = _share(("L1", "top"))
    r1, _ = verify(d1, SHARE_LINES)
    r2, _ = verify(_share(("L1", "top"), ("L2", "bottom")), SHARE_LINES)
    res = reconcile(r1, d1, r2, SHARE_LINES, [], "q", "en")
    assert res is r2 and res.share_pct == Decimal("15.8")
    listed = {**d1, "operation": "list"}                  # the other reading only listed the part
    assert reconcile(verify(listed, SHARE_LINES)[0], listed, r2, SHARE_LINES, [], "q", "en") is r2
    r3, _ = verify(_share(("L1", "top"), ("L2", "bottom"), ("L3", "both")), SHARE_LINES)   # two wholes: disputed
    assert reconcile(r1, d1, r3, SHARE_LINES, [], "q", "en").share_pct is None


def test_a_share_of_the_whole_budget_takes_the_printed_total_expenditure() -> None:
    from app.agent.line_answer import budget_whole
    q = "What percentage of the overall 2026 Sokoto State budget is allocated to the health sector?"
    res, _ = verify(_share(("L1", "top")), SHARE_LINES)
    budget_whole(res, SHARE_LINES, q)
    assert [s.line.name for s in res.selections] == ["HEALTH", "Total Expenditure"] and res.share_pct == Decimal("15.8")
    sub = L(10, "Total Expenditure", 79, [("2026 Approved Budget", "7210210444.94")],
            table="Primary Health Expenditure by Economic Classification")
    lines = [HEALTH, sub, TOTAL_EXP]
    for picks in ((("L1", "top"),), (("L1", "top"), ("L2", "bottom"))):    # left out, or a sector's own total
        res, _ = verify(_share(*picks), lines)
        budget_whole(res, lines, q)
        assert [s.line.page for s in res.selections] == [32, 1] and res.share_pct == Decimal("15.8")
    res, _ = verify(_share(("L1", "top")), SHARE_LINES)           # a ministry's share: no whole is guessed
    budget_whole(res, SHARE_LINES, "What share of the Ministry of Health's 2026 budget is capital?")
    assert res.share_pct is None and len(res.selections) == 1


def test_a_question_naming_no_kind_of_spending_gets_the_lines_total_row() -> None:
    from dataclasses import replace

    from app.agent.line_answer import prefer_total
    cap = replace(L(11, "Information Communication and Technology", 46, [("2026 Approved Budget", "3700000000.00")],
                    table="Capital Expenditure by Programme"), code="11", spend_kind="capital")
    tot = replace(L(12, "Information Communication and Technology", 41, [("2026 Approved Budget", "7150000000.00")],
                    table="Total Expenditure by Programme"), code="11", spend_kind="total")
    lines = [cap, tot]
    res, _ = verify(_pick("L1"), lines)
    prefer_total(res, lines, "Jimillar kudin da aka ware wa bangaren ICT a 2026")
    assert [s.line.page for s in res.selections] == [41] and res.summary == ""
    res, _ = verify(_pick("L1"), lines)
    prefer_total(res, lines, "How much capital was allocated to ICT in 2026?")     # a kind asked: it stands
    assert [s.line.page for s in res.selections] == [46]


def test_the_whole_of_a_share_is_one_printed_total() -> None:
    rec = L(8, "Recurrent Expenditure", 1, [("2026 Approved Budget", "205356934434.43")], table="Budget Summary")
    res, problems = verify(_share(("L1", "top"), ("L2", "bottom"), ("L3", "bottom")), [HEALTH, TOTAL_EXP, rec])
    assert [s.line.name for s in res.selections] == ["HEALTH", "Total Expenditure"] and res.share_pct == Decimal("15.8")
    assert any("one printed total" in p for p in problems)


def test_two_printed_totals_of_one_thing_give_both_shares() -> None:
    from app.agent.line_answer import reconcile
    sector = L(9, "Health", 40, [("2026 Approved Budget", "118827792994.59")],
               table="Sokoto State Government 2026 Approved Budget - Total Expenditure by Programme (Sector)")
    lines = [HEALTH, TOTAL_EXP, sector]
    d1 = _share(("L1", "top"), ("L2", "bottom"))
    r1, _ = verify(d1, lines)
    r2, _ = verify(_share(("L3", "top"), ("L2", "bottom")), lines)
    res = reconcile(r1, d1, r2, lines, [], "q", "en")
    assert [p for _, p in res.shares] == [Decimal("15.8"), Decimal("15.7")] and res.found == "partial"
    a = ans.line_answer(None, ans.Plan("q", [], []), res, lines, "en", {}, None)
    assert "two totals for this" in a.text and "15.8%" in a.text and "15.7%" in a.text and a.partial
    assert "Total Expenditure by Programme (Sector)" in a.text


def test_missing_terms_split_on_and_or_and_hausa_da() -> None:
    assert ans.missing_terms("orphanages and destitute homes")[:2] == ["orphanages", "destitute homes"]
    assert ans.missing_terms("gidajen ma'aikata da gidaje")[:2] == ["gidajen ma'aikata", "gidaje"]
    assert ans.missing_terms("special schools – none shown")[:1] == ["special schools"]


def test_a_word_in_many_line_names_is_too_common_to_search_for_alone() -> None:
    class Conn:
        def execute(self, sql, params):
            return type("R", (), {"fetchone": lambda _: (30000, {"%government%": 649, "%maternal%": 7}[params[0]])})()
    assert ans.common_word(Conn(), "government") and not ans.common_word(Conn(), "maternal")


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


def test_nothing_is_the_item_but_related_lines_are_named_as_the_nearest() -> None:
    rmnh = L(7, "Reproductive, maternal and neonatal health", 45, [("2026 Approved Budget", "170000000.00")])
    phc = L(8, "Primary Healthcare Expenditure", 43, [("2026 Approved Budget", "1220000000.00")])
    res, problems = verify({"selected": [], "found": "none", "summary": "", "missing": "rural maternal centres",
                            "nearest": [{"line": "L1", "column": "2026 Approved Budget"},
                                        {"line": "L2", "column": "no such column"}, {"line": "L9", "column": "x"}]},
                           [rmnh, phc])
    assert not res.selections and not problems
    assert [s.line.name for s in res.nearest] == ["Reproductive, maternal and neonatal health"]   # bad ones dropped
    plan = ans.Plan("q", ["q"], [])
    a = ans.nearest_answer(None, plan, res, "en", {}, None)
    assert a.found and a.partial and "No line in the documents is exactly that (rural maternal centres)" in a.text
    assert "170,000,000.00" in a.exact and "p. 45" in a.text
