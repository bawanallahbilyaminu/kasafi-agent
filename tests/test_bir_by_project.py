"""The Budget Implementation Reports' by-project tables (4 Nov 2026, from the source): Table 24 'Primary Healthcare
Capital Expenditure by Project' and Table 29 'Basic Education Capital Expenditure by Project' (2025 Q4 and 2026 Q2
pp. 53-58). Their header starts with 'Administrative Code and Description' and every row ends with two 0/1 flag
columns the header doesn't name, so the labeller had skipped them and no report had them as structured rows."""

from decimal import Decimal

from app.retrieval import indexer as I
from app.retrieval import tables as T

PAGE = """Budget Implementation Report - 2026 Quarter 3 Page | 53
Sokoto State Government
3.C Primary Healthcare Capital Expenditure by Project
Table 24: Primary Healthcare Capital Expenditure by Project
Sokoto State Government Budget Performance Report 2026 Q3 - Capital Expenditure by Project
Administrative Code and Description Project Description 2026 Original Budget 2026 Revised Budget 2026 Q3 Performance 2026 Performance Year
to Date (Q1-Q3)
% Performance Year to
Date against 2026
Revised Budget
Balance (against Revised
Budget)
017200700100 - Zakat and Waqf (Endowment) Agency Renovation of Hospital at Farfaru 95,000,000.00 95,000,000.00 - - 0.0% 95,000,000.00 1 0
052100300100 - Primary Health Care Development Agency Support for CHIPS activities in the State 40,000,000.00 40,000,000.00 14,700,000.00 14,700,000.00 36.8% 25,300,000.00 1 0
"""


def test_the_by_project_header_is_read_and_the_flag_columns_dropped() -> None:
    labelled, columns, open_header = I.label_tables(PAGE, [])
    assert columns == ["2026 Original Budget", "2026 Revised Budget", "2026 Q3 Performance",
                       "2026 Performance Year to Date (Q1-Q3)", "% Performance Year to Date against 2026 Revised Budget",
                       "Balance (against Revised Budget)"] and open_header == []
    rows = [ln for ln in labelled.splitlines() if " | 2026 Original Budget: " in ln]
    assert len(rows) == 2
    assert rows[1].startswith("052100300100 - Primary Health Care Development Agency Support for CHIPS activities in the "
                              "State | 2026 Original Budget: 40,000,000.00 | 2026 Revised Budget: 40,000,000.00 | "
                              "2026 Q3 Performance: 14,700,000.00 | 2026 Performance Year to Date (Q1-Q3): 14,700,000.00")
    assert rows[1].endswith("| Balance (against Revised Budget): 25,300,000.00")   # the flags are gone, not a column
    title = "Sokoto State Government Budget Performance Report 2026 Q3 - Capital Expenditure by Project"
    typed = T.rows_from_page(54, rows[1], title)
    assert [(r.measure, r.period, str(r.amount_naira)) for r in typed] == [
        ("original", "full_year", "40000000.00"), ("revised", "full_year", "40000000.00"), ("actual", "q3", "14700000.00"),
        ("actual", "q1_q3", "14700000.00")]
    assert typed[0].classification == "project" and typed[0].spend_kind == "capital" and typed[0].code == "052100300100"
    assert typed[0].name == "Primary Health Care Development Agency Support for CHIPS activities in the State"


def test_a_row_with_the_right_count_and_no_flags_is_unchanged_by_the_flag_rule() -> None:
    cols = ["2026 Original Budget", "2026 Revised Budget"]
    assert I.label_row("05 Health 1,000.00 1 0", cols) == "05 Health 1,000.00 1 0"      # 3 values, 2 columns: not a flag case
    assert I.label_row("05 Health 1,000.00 2,000.00 1 0", cols) == "05 Health | 2026 Original Budget: 1,000.00 | 2026 Revised Budget: 2,000.00"
    assert I.label_row("05 Health 1,000.00 2,000.00", cols) == "05 Health | 2026 Original Budget: 1,000.00 | 2026 Revised Budget: 2,000.00"
