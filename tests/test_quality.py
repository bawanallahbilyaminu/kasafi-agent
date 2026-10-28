"""Indexing-time quality checks (app/retrieval/quality.py)."""

import json

from app.retrieval.quality import check_document, check_totals, run

GOOD = ("21 - PERSONNEL | 2026 Approved Budget: 70.00\n22 - OTHER RECURRENT | 2026 Approved Budget: 30.00\n"
        "11 - FAAC | 2026 Approved Budget: 500.00\nTotal Expenditure | 2026 Approved Budget: 100.00")


def test_totals_compare_the_right_group() -> None:
    assert check_totals(GOOD)                                    # 21 + 22, not the revenue row 11
    assert not check_totals(GOOD.replace("30.00", "20.00"))
    assert check_totals("04 Health | A: 5.00\nTotal Expenditure | A: 5.00")   # one row: nothing to compare


def test_failures_and_warnings() -> None:
    pages = [(1, "x | Q1 Performance: 23020105\ny | 2025 Revised Budget: (25,000)\nPage | 0", "text"),
             (2, GOOD + "\nAmounts in N'000\nPage | 1", "text"), (3, "Page | 2", "none"), (4, "Page | 3", "text")]
    rep = check_document("d", "budget", pages)
    assert rep.fails == {"code_in_cell": [1], "bracket_cell": [1]}
    assert set(rep.warns) == {"units", "page_numbers", "image_pages"} and "PDF page - 1" in rep.warns["page_numbers"]


def test_budget_without_labelled_rows_fails_but_a_report_without_tables_doesnt() -> None:
    assert check_document("law", "budget", [(1, "Schedule text", "text")]).fails == {"labelled_rows": [1]}
    assert check_document("plan", "plan", [(1, "Plan text", "text")]).ok


class Conn:
    def __init__(self):
        self.sql = []

    def execute(self, sql, params=None):
        self.sql.append((sql, params))


def test_failing_document_goes_to_the_review_queue_once() -> None:
    conn = Conn()
    run(conn, "d", "budget", [(1, "x | Q1 Performance: 23020105", "text")])
    deletes = [s for s, _ in conn.sql if s.startswith("DELETE FROM gaps")]
    inserts = [p for s, p in conn.sql if s.startswith("INSERT INTO gaps")]
    assert deletes and len(inserts) == 1 and inserts[0][1] == "d"   # the old open record is replaced
    assert json.loads(inserts[0][2])["fails"] == {"code_in_cell": [1]}
    conn = Conn()
    run(conn, "ok", "plan", [(1, "text", "text")])
    assert not any(s.startswith("INSERT") for s, _ in conn.sql)
