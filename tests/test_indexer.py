from pathlib import Path

import pytest

from app.retrieval.indexer import CHUNK_CHARS, chunk_page, clean_text, find_file, normalise_name


def test_short_page_is_one_chunk_and_empty_page_none() -> None:
    assert chunk_page("Ministry of Health 1,000") == ["Ministry of Health 1,000"]
    assert chunk_page("") == []


def test_long_page_splits_on_lines_with_overlap_and_keeps_everything() -> None:
    lines = [f"052100100100 - Ministry of Health line {i:03d} 1,234,567.00" for i in range(200)]
    chunks = chunk_page("\n".join(lines))
    assert len(chunks) > 1 and all(len(c) <= CHUNK_CHARS for c in chunks)
    joined = "\n".join(chunks)
    assert all(line in joined for line in lines)                       # nothing lost
    assert chunks[1].split("\n")[0] in chunks[0]                       # overlap carries context forward
    assert all(not c.startswith("\n") for c in chunks)


def test_one_huge_line_is_hard_split() -> None:
    chunks = chunk_page("x" * (CHUNK_CHARS * 2 + 10))
    assert all(len(c) <= CHUNK_CHARS for c in chunks) and sum(map(len, chunks)) >= CHUNK_CHARS * 2


def test_clean_text() -> None:
    assert clean_text("a\r\n\r\n\r\n\r\nb\t\t c\x00") == "a\n\nb c"


def test_find_file_by_id_or_title(tmp_path: Path) -> None:
    (tmp_path / "budget-2026-approved.pdf").write_bytes(b"%PDF-")
    (tmp_path / "Sokoto State MTEF Fiscal Strategy Paper 2025-2027.pdf").write_bytes(b"%PDF-")
    assert find_file({"id": "budget-2026-approved", "title": "x"}, tmp_path).name == "budget-2026-approved.pdf"
    mtef = {"id": "mtef-2025-2027", "title": "Sokoto State MTEF / Fiscal Strategy Paper 2025-2027"}
    assert find_file(mtef, tmp_path).name.startswith("Sokoto State MTEF")
    assert find_file({"id": "nope", "title": "Nope"}, tmp_path) is None
    assert normalise_name("MTEF / Fiscal") == normalise_name("MTEF Fiscal")


# --- against the dev database, rolled back (skipped when unavailable) ----------------------

SEED = Path("data/berap-2025.pdf")


@pytest.fixture
def db():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    try:
        conn = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except Exception:
        pytest.skip("dev database not available")
    try:
        if not conn.execute("SELECT to_regclass('public.chunks')").fetchone()[0]:
            pytest.skip("migrations not applied")
        with conn.transaction(force_rollback=True):
            yield conn
    finally:
        conn.close()


@pytest.mark.skipif(not SEED.exists(), reason="seed PDF not present (data/ is gitignored)")
def test_index_and_search_a_real_document(db) -> None:
    from app.retrieval.indexer import index_document
    from app.retrieval.search import search
    doc = {"id": "test-berap", "title": "Test BERAP", "category": "test", "year": 2025}
    r = index_document(db, doc, SEED)
    assert (r.status, r.pages) == ("indexed", 4) and r.chunks > 0
    assert index_document(db, doc, SEED).status == "unchanged"          # idempotent
    hits = search(db, "reform objectives", k=3, doc_ids=["test-berap"])
    assert hits and all(h.doc_id == "test-berap" and 1 <= h.page <= 4 for h in hits)


# --- column labelling ---------------------------------------------------------------------------

from app.retrieval.indexer import label_row, label_tables, parse_columns  # noqa: E402

H2026 = ("Code Sector, Objective and Programme 2024 Full Year Actuals 2025 Revised Budget 2025 Performance "
         "January to September 2026 Approved Budget 2027 Out-Year Estimate 2028 Out-Year Estimate 2026 Nutrition Tagging")
ROW = "05 Education 8,139,687,377.37 80,287,078,732.62 39,577,019,325.11 128,495,868,362.13 123,242,901,775.81 120,393,444,275.81 -"


def test_parse_columns_keeps_against_year_inside_a_column() -> None:
    cols = parse_columns("Code Adminstrative Unit 2025 Original Budget 2025 Final Budget 2025 Q4 Performance "
                         "2025 Performance Year to Date (Q1-Q4) % Performance Year to Date against 2025 Final Budget "
                         "Balance (against Final Budget)")
    assert cols[4] == "% Performance Year to Date against 2025 Final Budget" and len(cols) == 6


def test_row_is_labelled_only_when_counts_match() -> None:
    cols = parse_columns(H2026)
    assert "2026 Approved Budget: 128,495,868,362.13" in label_row(ROW, cols)
    assert label_row(ROW + " 99.00", cols) == ROW + " 99.00"                 # 8 values for 7 columns: untouched
    assert label_row("Prose 12 13", cols) == "Prose 12 13"


def test_item_header_and_header_split_across_pages() -> None:
    page1 = "Summary\nItem 2023 Full Year\nActuals 2024 Revised Budget"
    page2 = "2025 Approved\nBudget\nTotal Revenue 1.00 2.00 3.00"
    _, cols, open_h = label_tables(page1, [])
    assert open_h                                                            # header still open at the page end
    text, cols, _ = label_tables(page2, cols, open_h)
    assert cols == ["2023 Full Year Actuals", "2024 Revised Budget", "2025 Approved Budget"]
    assert "Total Revenue | 2023 Full Year Actuals: 1.00" in text


def test_row_name_below_header_is_not_swallowed_into_a_column() -> None:
    page = ("Code Unit 2025 Revised Budget 2025 Q1 Performance Balance (against Revised Budget)\n"
            "Bureau for Public Procurement\n011101000100 FEES 60,000,000.00 5,762,000.00 54,238,000.00")
    text, cols, _ = label_tables(page, [])
    assert cols[-1] == "Balance (against Revised Budget)"
    assert "Balance (against Revised Budget): 54,238,000.00" in text


def test_2024_style_header_wrapped_one_word_per_line() -> None:
    page = ("Code Economic 2022 Full Year\nActuals\n2023 Revised\nBudget\n2023 Performance\nJanuary to\nSeptember\n"
            "2024 Executive\nBudget Proposal\n2024 Approved\nBudget\n2025 Out-Year\nEstimate\n"
            "21 PERSONNEL 1.00 2.00 3.00 4.00 5.00 6.00")
    text, cols, _ = label_tables(page, [])
    assert "2024 Executive Budget Proposal" in cols and "2024 Approved Budget: 5.00" in text
