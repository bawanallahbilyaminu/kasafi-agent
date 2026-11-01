"""A dash in a table cell is 'not available', never zero (the Dange Shuni school-count test, 1 Nov 2026); the
newest edition of a named series answers a question that names no year; count questions reach the 'Number of'
table; the topic sweep reads publishers at the question's geography level."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.acquisition.editions import SERIES, valid_edition
from app.acquisition.registry import Publisher, Topic
from app.agent import answer as ans
from app.agent import topics as tp
from app.agent.answer import Need, Plan, count_queries, dash_misread, prefer_newest_edition
from app.agent.line_answer import listing
from app.retrieval.line_search import Cell, Line, is_blank_cell, printed_cell

ROW = "DANGE SHUNI | 2025 Revised Budget: - | 2026 Approved Budget: 5,608.00 | 2024 Actual: n/a"


def test_printed_cell_reads_the_dash_from_the_rows_own_text() -> None:
    assert printed_cell(ROW, "2025 Revised Budget") == "-"
    assert printed_cell(ROW, "2026 Approved Budget") == "5,608.00"
    assert printed_cell(ROW, "2024 Actual") == "n/a"
    assert printed_cell(ROW, "2027 Estimate") == ""
    for v in ("-", "–", "—", "…", "...", "n/a", "N/A", "n.a.", "nil", ""):
        assert is_blank_cell(v)
    assert not is_blank_cell("0") and not is_blank_cell("5,608.00")


def test_listing_says_no_figure_printed_for_a_dash_cell_not_zero() -> None:
    cells = [Cell("2025 Revised Budget", 2025, "revised", "full_year", Decimal(0), printed="-"),
             Cell("2026 Approved Budget", 2026, "approved", "full_year", Decimal("5608.00"), printed="5,608.00"),
             Cell("2024 Actual", 2024, "actual", "full_year", Decimal(0))]     # unknown printed text: the figure
    line = Line("d:1:1", "Doc", "d", 1, "Table", "Dange Shuni", ROW, "project", "", "", 1.0, cells)
    out = listing([line])
    assert "2025 Revised Budget: - (no figure printed)" in out
    assert "2026 Approved Budget: 5,608.00" in out
    assert "2024 Actual: 0" in out and "2024 Actual: - (no" not in out


@pytest.mark.parametrize("text", [
    "Dange Shuni shows no enrolment (- in the table).",
    "The table gives 0 for Dange Shuni (\"-\").",
    "Dange Shuni: none ( – in the table)",
    "A dash in the table means zero schools.",
    "Dange Shuni ba ta da makarantu (- a tebur).",
])
def test_a_dash_read_as_a_figure_is_caught(text: str) -> None:
    assert dash_misread(text)


@pytest.mark.parametrize("text", [
    "Dange Shuni has 8 public and 11 private senior secondary schools (Table 3.14, p. 53).",
    "The table prints no figure for Dange Shuni in that column (a dash).",
    "Babu adadi a tebur ɗin: an buga '-' ne kawai.",
    "There is no figure published for 2025 - the report covers 2024.",
])
def test_plain_sentences_and_the_right_wording_pass(text: str) -> None:
    assert not dash_misread(text)


def test_the_compose_rules_and_the_topic_reader_say_a_dash_is_not_available() -> None:
    rules = " ".join(ans.COMPOSE_RULES) if hasattr(ans, "COMPOSE_RULES") else Path("app/agent/answer.py").read_text("utf-8")
    assert "6g. A dash (-)" in rules and "never" in rules and "NOT AVAILABLE" in rules
    assert "A dash (-), '…', 'n/a' or a blank cell means the figure is not available" in tp.CARD_SYSTEM


def test_count_questions_become_the_count_tables_own_phrases() -> None:
    assert count_queries("How many Senior Secondary Schools are in Dange Shuni") == [
        "Number of Senior Secondary Schools", "Number of schools", "No. of schools"]
    assert count_queries("number of primary health centres in Wamakko")[0] == "Number of primary health centres"
    assert "Number of makarantu" in count_queries("makarantu nawa ne a Dange Shuni")
    assert count_queries("What was the health budget in 2026?") == []


class FakeConn:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, sql, args=()):
        rows = self.rows
        if "category" in sql:
            rows = [(r[3],) for r in self.rows if r[0] in args[0]]
        else:
            rows = [r[:3] for r in self.rows if r[1] and r[2]]

        class R:
            def fetchall(self_inner):
                return rows

            def fetchone(self_inner):
                return rows[0] if rows else None
        return R()


DOCS = [("asc-2022-2023", "sokoto_asc", "2022", "statistics"), ("asc-sokoto-2023-2024", "sokoto_asc", "2023", "statistics"),
        ("budget-2025-approved", "sokoto_budget", "2025", "budget"), ("budget-2026-approved", "sokoto_budget", "2026", "budget"),
        ("mtef-2025-2027", None, None, "fiscal")]


def plan(q, docs):
    return Plan(english_question=q, search_queries=[q], doc_ids=list(docs), need=Need(q, geo_level="lga"))


def test_no_year_named_the_newest_edition_replaces_an_older_one_the_planner_listed() -> None:
    p = plan("How many senior secondary schools are in Dange Shuni", ["asc-2022-2023", "mtef-2025-2027"])
    prefer_newest_edition(FakeConn(DOCS), p, "How many senior secondary schools are in Dange Shuni")
    assert p.doc_ids == ["asc-sokoto-2023-2024", "mtef-2025-2027"] and p.skip_docs == ["asc-2022-2023"]


def test_both_editions_listed_keep_only_the_newest_and_a_year_named_keeps_the_planners_choice() -> None:
    p = plan("school census senior secondary schools by LGA", ["asc-2022-2023", "asc-sokoto-2023-2024"])
    prefer_newest_edition(FakeConn(DOCS), p, "school census senior secondary schools by LGA")
    assert p.doc_ids == ["asc-sokoto-2023-2024"]
    p = plan("senior secondary schools by LGA in the 2022/2023 school census", ["asc-2022-2023"])
    prefer_newest_edition(FakeConn(DOCS), p, "senior secondary schools by LGA in the 2022/2023 school census")
    assert p.doc_ids == ["asc-2022-2023"] and not p.skip_docs
    p = plan("the 2025 approved budget for health", ["budget-2025-approved"])
    prefer_newest_edition(FakeConn(DOCS), p, "the 2025 approved budget for health")
    assert p.doc_ids == ["budget-2025-approved"]


def test_the_school_census_is_a_series_and_the_manifest_entry_names_its_edition() -> None:
    assert "sokoto_asc" in SERIES and SERIES["sokoto_asc"].frequency == "yearly" and valid_edition("2023")
    docs = json.loads(Path("data/manifest.json").read_text("utf-8"))["documents"]
    asc = next(d for d in docs if d["id"] == "asc-sokoto-2023-2024")
    assert asc["series"] == "sokoto_asc" and asc["edition"] == "2023" and asc["category"] == "statistics"


def pub(pid, level, tier=1):
    return Publisher(pid, pid, (f"{pid}.example",), level=level, tier=tier, verified="2026-10-29")


def test_the_topic_sweep_drops_coarser_publishers_for_an_lga_question() -> None:
    topic = Topic("education", ("school",), ("makaranta",), "", (pub("asc", "lga"), pub("ubec", "state"),
                                                           pub("ndhs_mics", "state", 2), pub("ctx", "state", 3)))
    lga, _ = tp.choose_publishers(topic, geo_level="lga")
    assert [p.id for p in lga] == ["asc"]
    state, _ = tp.choose_publishers(topic, geo_level="state")
    assert [p.id for p in state] == ["asc", "ubec", "ndhs_mics"]
    none, _ = tp.choose_publishers(topic)
    assert [p.id for p in none] == ["asc", "ubec", "ndhs_mics"]
    only_state = Topic("t", ("x",), ("x",), "", (pub("ubec", "state"), pub("nat", "national", 2)))
    kept, _ = tp.choose_publishers(only_state, geo_level="lga")        # nothing finer: the state ones stay
    assert [p.id for p in kept] == ["ubec", "nat"]


def test_the_structured_core_says_a_dash_is_no_figure_printed_and_computes_no_change_from_it() -> None:
    from app.agent.capabilities import Cell as SCell
    from app.agent.need import Entity
    from app.agent.tools import dash_printed
    bir = ("12020448 DEVELOPMENT LEVIES | 2026 Original Budget: 300,000.00 | 2026 Q1 Performance: - | "
           "2026 Performance Year to Date (Q1): - | % Performance Year to Date against 2026 Original Budget: 0.0% | "
           "Balance (against Original Budget): 300,000.00")
    assert dash_printed(bir, "quarter_spent", 2026, 1) and dash_printed(bir, "actual_ytd", 2026, 1)
    assert not dash_printed(bir, "original", 2026, 1)
    budget = "021500000000 Ministry of Agriculture | 2024 Full Year Actuals: 19,353,550.00 | 2026 Approved Budget: -"
    assert dash_printed(budget, "approved", 2026, None) and not dash_printed(budget, "approved", 2024, None)
    gh = Entity("sub_agency", "Government House", "Government House", "011100100100")
    cells = [SCell("approved", gh, "state", "overhead", 2025, value=Decimal("4201809645.00"), source="p. 14"),
             SCell("approved", gh, "state", "overhead", 2026, value=Decimal(0), source="p. 21", note="dash")]
    text, exact = ans.write_budget_cells(Need("q", operation="compare"), cells, "en")
    assert "2026 approved budget no figure printed (a dash in the table)" in text
    assert "₦0.00" not in text and "change" not in text.lower()
    assert "approved 2026: - (a dash: no figure printed; counted as nil)" in exact
    ha, _ = ans.write_budget_cells(Need("q", operation="compare"), cells, "ha")
    assert "ba a buga adadi ba" in ha


def test_the_count_table_page_is_found_by_the_places_row_and_the_number_of_column(conn) -> None:
    from app.agent.answer import count_table_pages
    hits = count_table_pages(conn, ["asc-sokoto-2023-2024"], "How many Senior Secondary Schools are in Dange Shuni")
    assert [h.page for h in hits][:1] == [53] and "DANGE SHUNI 8 5,608" in hits[0].text
    assert count_table_pages(conn, ["asc-sokoto-2023-2024"], "How many pupils are in Sokoto State") == []  # no LGA
    assert count_table_pages(conn, ["budget-2026-approved"], "How many schools are in Dange Shuni") == []


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT 1 FROM documents WHERE id = 'asc-sokoto-2023-2024'").fetchone():
            pytest.skip("the 2023/24 school census is not indexed here")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database: {e}")
    yield c
    c.close()
