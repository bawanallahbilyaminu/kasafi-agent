"""Regression tests on the real pages for every extraction problem fixed so far.

Each test names its lesson in docs/extraction-lessons.md (L1, L2, ...). They run the real indexing
pipeline (extract -> accounting negatives -> table labelling -> chunks) on the actual PDF pages, from a
few pages before the target so table titles and column headers carry over as they do in a full index.
Skipped when the PDFs aren't downloaded (data/ is gitignored).
"""

from functools import lru_cache
from pathlib import Path

import pytest

from app.retrieval import quality
from app.retrieval.indexer import (accounting_negatives, contextual_chunks, extract_pages, image_table_pages,
                                   label_row, parse_columns)

DATA = Path(__file__).resolve().parents[1] / "data"


@lru_cache(maxsize=32)
def run(name: str, first: int, last: int) -> tuple[list[list[str]], list[str]]:
    """(chunks per page, labelled text per page) for pages first..last, as the indexer makes them."""
    path = DATA / name
    if not path.exists():
        pytest.skip(f"{name} not downloaded")
    pages = [accounting_negatives(p) for p in extract_pages(path, first, last)]
    labelled: list[str] = []
    return contextual_chunks(pages, labelled), labelled


def key_rows(name: str, first: int, last: int, page: int) -> list[str]:
    chunks, _ = run(name, first, last)
    return [c for c in chunks[page - first] if c.count("\n") <= 1 and " | " in c]


def test_L1_rows_labelled_with_their_column_2026_p40() -> None:
    rows = key_rows("budget-2026-approved.pdf", 36, 40, 40)
    health = next(r for r in rows if "\n04 Health |" in r)
    assert "2026 Approved Budget: 118,827,792,994.59" in health
    assert health.startswith("[Table: Sokoto State Government 2026 Approved Budget - Total Expenditure by Programme")


def test_L2_header_wrapped_one_word_per_line_2024_p113() -> None:
    rows = key_rows("budget-2024-approved.pdf", 108, 113, 113)
    assert any("05 Education | 2022 Full Year Actuals: 4,759,005,929.68" in r for r in rows)


def test_L3_row_name_not_swallowed_into_a_column_2025_p15() -> None:
    _, labelled = run("budget-2025-approved.pdf", 5, 15)
    row = next(l for l in labelled[-1].splitlines() if "Bureau for Public Procurement" in l)
    assert row.startswith("011101000100 Bureau for Public Procurement and Price Intelligence | 2023 Full Year Actuals:")


def test_L4_title_printed_at_the_top_comes_first_2025_p11() -> None:
    rows = key_rows("budget-2025-approved.pdf", 5, 11, 11)
    mora = next(r for r in rows if "\n017200000000 Ministry for Religious Affairs |" in r)
    assert "Total Expenditure by Administrative Classification" in mora.splitlines()[0]
    assert "2025 Approved Budget: 11,255,447,389.16" in mora


def test_L5_plain_total_row_keeps_the_table_title_amended_p7() -> None:
    chunks, _ = run("budget-2025-amended.pdf", 1, 7)
    assert not any("(table starting at its Total row)" in c.splitlines()[0] for c in chunks[-1]
                   if "Total Expenditure |" in c)


def test_L6_kind_total_row_starts_its_own_table_2025_p15() -> None:
    chunks, _ = run("budget-2025-approved.pdf", 5, 15)
    assert any(c.startswith("[Table: Capital Expenditure (table starting at its Total row)]") for c in chunks[-1])


def test_L7_ministry_total_row_is_its_own_key_row_bir_q4_2025_p17() -> None:
    rows = key_rows("bir-2025-q4.pdf", 14, 17, 17)
    mora = next(r for r in rows if "\n017200000000 Ministry for Religious Affairs |" in r)
    assert "2025 Performance Year to Date (Q1-Q4): 8,457,842,546.60" in mora and "67.8%" in mora


def test_L9_scanned_page_has_no_text_layer_smart_agenda_p3() -> None:
    path = DATA / "Sokoto State 9-Point SMART Agenda.pdf"
    if not path.exists():
        pytest.skip("SMART agenda not present")
    assert len(extract_pages(path, 3, 3)[0]) < 40


def test_L11_accounting_negative_audited_2024_p46() -> None:
    _, labelled = run("audited-fs-2024.pdf", 46, 46)
    assert "-56,893,525,653.90" in labelled[0] and "(56,893,525,653.90)" not in labelled[0]


def test_L12_picture_of_a_table_is_sent_to_ocr_cpi_p19() -> None:
    path = DATA / "fetched" / "nbs-cpi-2026-09.pdf"
    if not path.exists():
        pytest.skip("CPI not fetched")
    assert 19 in image_table_pages(path)


def test_L31_vector_outlined_pages_and_maps_are_sent_to_ocr_afo_p6_scp() -> None:
    afo = DATA / "advisories" / "nihsa-afo-2026.pdf"
    if not afo.exists():
        pytest.skip("NIHSA AFO not present (data/advisories, outside git)")
    assert len(extract_pages(afo, 6, 6)[0]) < 60                       # only the running footer
    assert {6, 14, 24}.issubset(image_table_pages(afo))               # outlines, then a big image, then both
    budget = DATA / "budget-2026-approved.pdf"
    if budget.exists():                                                # a dense text table page stays text
        assert 20 not in image_table_pages(budget)


def test_L15_code_and_quantity_never_land_in_value_cells_amended_p114() -> None:
    _, labelled = run("budget-2025-amended.pdf", 110, 114)
    text = labelled[-1]
    assert "Revised Budget: (25,000)" not in text and ": 23020105" not in text
    assert label_row("23020105 CONSTRUCTION 23020105 1,000.00", ["A", "B"]) == "23020105 CONSTRUCTION 23020105 1,000.00"


def test_L19_name_ending_in_a_bracketed_code_is_labelled_bir_q4_2025_p9() -> None:
    _, labelled = run("bir-2025-q4.pdf", 6, 9)
    row = next(l for l in labelled[-1].splitlines() if l.startswith("22 - OTHER RECURRENT COSTS"))
    assert row.startswith("22 - OTHER RECURRENT COSTS (EXCLUDING 2201) | 2025 Original Budget: 114,687,010,390.70")
    assert quality.check_totals(labelled[-1])               # 21 + 22 + 23 = Total Expenditure again


def test_L19_totals_check_catches_a_missing_row() -> None:
    _, labelled = run("bir-2025-q4.pdf", 6, 9)
    without_22 = "\n".join(l for l in labelled[-1].splitlines() if not l.startswith("22 - OTHER RECURRENT"))
    assert not quality.check_totals(without_22)


def test_L16_printed_page_offset_is_reported_bir_q4_2025() -> None:
    _, labelled = run("bir-2025-q4.pdf", 10, 20)
    rep = quality.check_document("bir-2025-q4", "budget_performance",
                                 [(i, t, "text") for i, t in enumerate(labelled, start=10)])
    assert rep.ok and "PDF page - 1" in rep.warns.get("page_numbers", "")


def test_parse_columns_on_the_bir_header() -> None:
    cols = parse_columns("Code Adminstrative Unit 2025 Original Budget 2025 Final Budget 2025 Q4 Performance "
                         "2025 Performance Year to Date (Q1-Q4) % Performance Year to Date against 2025 Final Budget "
                         "Balance (against Final Budget)")
    assert cols[0] == "2025 Original Budget" and cols[-1] == "Balance (against Final Budget)" and len(cols) == 6
