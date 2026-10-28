"""OCR'd pipe tables are labelled like budget tables (docs/extraction-lessons.md)."""

from app.retrieval.indexer import is_table_title, label_pipe_tables, ocr_page_chunks

# NBS CPI September 2026, p19, as Muse Spark OCR returned it (two-line header with spanning blank cells)
P19 = """APPENDIX
Combined Urban and Rural State Consumer Price Index
(Base Period: 2024 = 100)
State | Sep-25 | | Aug-26 | | Sep-26 | | MoM | YoY | MoM | YoY
State | Food | All Items | Food | All Items | Food | All Items | Food | | All Items |
Abia | 126.5 | 130.5 | 152.0 | 147.7 | 154.1 | 149.0 | 1.4 | 21.8 | 0.9 | 14.2
Sokoto | 127.0 | 125.1 | 136.9 | 131.2 | 134.7 | 135.1 | -1.6 | 6.1 | 3.0 | 8.0"""


def test_two_line_header_is_combined_and_rows_labelled() -> None:
    _, rows = label_pipe_tables(P19)
    sokoto = next(r for r in rows if r.startswith("Sokoto"))
    assert sokoto == ("Sokoto | Sep 2025 Food: 127.0 | Sep 2025 All Items: 125.1 | Aug 2026 Food: 136.9 | "
                      "Aug 2026 All Items: 131.2 | Sep 2026 Food: 134.7 | Sep 2026 All Items: 135.1 | "
                      "Month-on-Month Food: -1.6 | Year-on-Year Food: 6.1 | Month-on-Month All Items: 3.0 | "
                      "Year-on-Year All Items: 8.0")


def test_each_state_row_is_a_key_row_with_the_table_title() -> None:
    assert is_table_title("Combined Urban and Rural State Consumer Price Index")
    chunks = ocr_page_chunks(P19)
    key = [c for c in chunks if c.count("\n") == 1 and "Sokoto |" in c]
    assert key and key[0].startswith("[Table: Combined Urban and Rural State Consumer Price Index]")


def test_rows_that_dont_fit_the_header_are_left_alone() -> None:
    text = "State | Sep-25 | Aug-26\nKano | 1.0 | 2.0 | 3.0\nSome text\nLagos | 4.0 | 5.0"
    _, rows = label_pipe_tables(text)
    assert rows == set()                     # wrong count, and the header ends at the text line
