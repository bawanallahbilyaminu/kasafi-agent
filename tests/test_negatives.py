"""Bracketed numbers: accounting negatives vs plain parentheses (docs/extraction-lessons.md)."""

from pathlib import Path

import pytest

from app.agent.answer import render_answer
from app.retrieval.indexer import accounting_negatives, extract_pages

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.mark.parametrize("raw, want", [
    ("Cash Flows From Investing Activities | (56,893,525,653.90) |", "Cash Flows From Investing Activities | -56,893,525,653.90 |"),
    ("TOTAL (1,742,337,258.60) DR", "TOTAL -1,742,337,258.60 DR"),
    ("Balance: (197.55) | Q2: 1.00", "Balance: -197.55 | Q2: 1.00"),           # a labelled two-decimal cell
    ("highest increases in Imo (8.64%), Kaduna (4.46%), and Sokoto\n(3.01%) while", None),  # prose: unchanged
    ("Water Depot and Gwiwa (25,000) 60,000,000.00", None),                        # a quantity, not money
    ("results areas: (1) basic education", None),
    ("Adamawa (-6.10%)", None),
])
def test_accounting_negatives(raw: str, want: str | None) -> None:
    assert accounting_negatives(raw) == (want if want is not None else raw)


def test_bracketed_percentage_is_shown_without_brackets() -> None:
    d = {"summary": "Sokoto month-on-month was (3.01%), third-highest [3].",
         "items": ["Sokoto: (3.01%) [3]", "Adamawa: -6.10% [3]", "Spent: 1.00 (67.8% of the final budget) [1]"]}
    out = render_answer(d, "en")
    assert "(3.01%)" not in out and "was 3.01%, third-highest" in out and "Sokoto: 3.01% [3]" in out
    assert "-6.10%" in out and "(67.8% of the final budget)" in out


# --- regression tests on the real pages ------------------------------------------------------------

def real_page(name: str, page: int) -> str:
    path = DATA / name
    if not path.exists():
        pytest.skip(f"{name} not downloaded")
    return accounting_negatives(extract_pages(path)[page - 1])


def test_cpi_sept_2026_p16_sokoto_is_positive() -> None:
    text = real_page("fetched/nbs-cpi-2026-09.pdf", 16)
    assert "Sokoto \n(3.01%)" in text or "Sokoto\n(3.01%)" in text           # left as written: a parenthesis
    assert "-3.01" not in text and "Adamawa (-6.10%)" in text


def test_audited_statements_cash_flow_negative() -> None:
    assert "-56,893,525,653.90" in real_page("audited-fs-2024.pdf", 46)


def test_budget_quantity_in_brackets_is_not_negative() -> None:
    text = real_page("budget-2026-approved.pdf", 58)
    assert "(25,000)" in text and "-25,000" not in text


def test_cpi_state_table_page_is_an_image_to_ocr() -> None:
    """p19's table (with Sokoto's published year-on-year rate) is an image under a 92-character title."""
    from app.retrieval.indexer import image_table_pages
    path = DATA / "fetched" / "nbs-cpi-2026-09.pdf"
    if not path.exists():
        pytest.skip("CPI not fetched")
    pages = image_table_pages(path)
    assert {19, 21} <= pages and 16 not in pages and 6 not in pages
