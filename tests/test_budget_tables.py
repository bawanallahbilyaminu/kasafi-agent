"""Structured budget rows (app/retrieval/tables.py)."""

from decimal import Decimal

import pytest

from app.retrieval.tables import classification, extract_rows, parse_column, rows_from_page, spend_kind_of


@pytest.mark.parametrize("label, want", [
    ("2026 Approved Budget", (2026, "approved", "full_year")),
    ("2025 Revised Budget", (2025, "revised", "full_year")),
    ("2025 Performance January to September", (2025, "actual", "jan_sep")),
    ("2024 Full Year Actuals", (2024, "actual", "full_year")),
    ("2025 Original Budget", (2025, "original", "full_year")),
    ("2025 Final Budget", (2025, "final", "full_year")),
    ("2025 Q4 Performance", (2025, "actual", "q4")),
    ("2025 Performance Year to Date (Q1-Q4)", (2025, "actual", "q1_q4")),
    ("2026 Performance Year to Date (Q1-Q2)", (2026, "actual", "q1_q2")),
    ("2027 Out-Year Estimate", (2027, "estimate", "full_year")),
    ("2024 Executive Budget Proposal", (2024, "proposal", "full_year")),
    ("% Performance Year to Date against 2025 Final Budget", None),
    ("Balance (against Final Budget)", None),
    ("2026 Nutrition Tagging", None),
])
def test_parse_column(label: str, want) -> None:
    assert parse_column(label) == want


@pytest.mark.parametrize("title, cls, kind", [
    ("Sokoto State Government 2026 Approved Budget - Capital Expenditure by Functional Classification", "function", "capital"),
    ("Sokoto State Government 2026 Approved Budget - Other Non-Debt Recurrent Expenditure by Functional Classification",
     "function", "overhead"),
    ("Sokoto State Government 2025 Approved Budget - Total Expenditure by Administrative Classification", "administrative", "total"),
    ("Sokoto State Government 2026 Approved Budget - Personnel Expenditure by Programme (Sector, Objective and Programme)",
     "programme", "personnel"),
    ("MDA EXPENDITURE BY FUNCTION", "function_by_mda", "total"),
    ("Revenue by Economic Classification", "economic", "revenue"),
    ("Debt Service Expenditure by Administrative Classification", "administrative", "debt"),
])
def test_classification_and_kind(title: str, cls: str, kind: str) -> None:
    assert classification(title) == cls and spend_kind_of(title) == kind


TITLE = "Sokoto State Government 2026 Approved Budget - Capital Expenditure by Functional Classification"
LINE = ("7094 TERTIARY EDUCATION | 2024 Full Year Actuals: 1,277,572,854.64 | 2025 Revised Budget: 6,707,032,782.20 | "
        "2025 Performance January to September: 1,788,033,281.38 | 2026 Approved Budget: 20,666,975,000.00 | "
        "2027 Out-Year Estimate: 18,838,575,000.00")


def test_one_labelled_row_becomes_typed_rows() -> None:
    rows = rows_from_page(38, LINE, TITLE)
    approved = next(r for r in rows if r.year == 2026 and r.measure == "approved")
    assert (approved.code, approved.name, approved.classification, approved.spend_kind) == \
        ("7094", "TERTIARY EDUCATION", "function", "capital")
    assert approved.amount_naira == Decimal("20666975000.00") and approved.page == 38 and approved.row_text == LINE
    assert {(r.year, r.measure, r.period) for r in rows} == {
        (2024, "actual", "full_year"), (2025, "revised", "full_year"), (2025, "actual", "jan_sep"),
        (2026, "approved", "full_year"), (2027, "estimate", "full_year")}


def test_dash_is_zero_names_without_codes_and_thousands_tables() -> None:
    rows = rows_from_page(1, "Total Expenditure | 2026 Approved Budget: - | 2025 Revised Budget: 5.00", "Total Expenditure")
    assert [(r.code, r.name, r.amount_naira) for r in rows] == [(None, "Total Expenditure", Decimal(0)),
                                                                (None, "Total Expenditure", Decimal("5.00"))]
    page = "Amounts in N'000\n23 - CAPITAL EXPENDITURE | 2026 Approved Budget: 1,500.00"
    rows = extract_rows([page], [["", TITLE]])
    assert rows[0].amount_naira == Decimal("1500000.00") and rows[0].code == "23" and rows[0].name == "CAPITAL EXPENDITURE"
