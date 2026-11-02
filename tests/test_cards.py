"""Document and section cards, related documents, adaptive reading, and the 2 Nov live-test fixes (absence claims,
two figures for overlapping groups, amounts in house style). Free: no model call; cards are written directly for
fixture documents inside a transaction that is rolled back."""

import json

import pytest

from app.acquisition.registry import Publisher
from app.agent.answer import (BROAD_DOCS, SIMPLE_DOCS, Evidence, Plan, breadth, checked_absence, house_style,
                              widen_for_breadth)
from app.agent.need import Need
from app.agent.topics import cap_sources
from app.retrieval import cards as C

# --- pure: sections, condensing, the caps, house style ------------------------------------------------------------

PAGES = {
    1: "Annual Review 2025\nPrepared by the Water Board",
    2: "1. Introduction\nThis review covers rural water supply in all 23 LGAs.\nIt follows the 2024 baseline.",
    3: "Table 4: Functional water points by LGA\nBinji 12 4 75%\nBodinga 30 9 70%\nDange Shuni 41 8 80%",
    4: "Table 4: Functional water points by LGA (continued)\nWamakko 55 10 82%\nWurno 20 5 75%",
    5: "2. Findings\nOnly 61 percent of hand pumps were working at the end of 2025.",
}


def test_sections_split_at_headings_and_tables_and_a_continued_table_stays_one() -> None:
    secs = C.split_sections(PAGES)
    assert [(s.page_from, s.page_to, s.kind) for s in secs] == [(1, 1, "section"), (2, 2, "section"),
                                                                 (3, 4, "table"), (5, 5, "section")]
    assert secs[2].title.startswith("Table 4") and "Wamakko" in secs[2].text and "55" not in secs[2].text


def test_condensing_keeps_labels_and_prose_and_drops_digit_columns() -> None:
    out = C.condense_page("Ministry of Health | 12,000,000.00 | 9,876,543.21\nThe plan doubles PHC funding by 2023.")
    assert out.splitlines() == ["Ministry of Health", "The plan doubles PHC funding by 2023."]
    budget = C.split_sections({1: "Table 1: Capital\n" + "\n".join(f"Project {i} 1,000.00 2,000.00" for i in range(200))},
                              "budget")
    assert len(budget[0].text) <= C.TABLE_PAGE_CHARS + 20


def test_batches_respect_the_size_limit() -> None:
    secs = [C.Section(i, f"S{i}", "section", i, i, text="x" * 9000) for i in range(1, 6)]
    sizes = [len(b) for b in C.batches(secs, limit=20000)]
    assert sizes == [2, 2, 1]


def test_breadth_three_for_a_fact_eight_for_comparison_or_overview_or_several_measures() -> None:
    def plan(q, measures=()):
        return Plan(english_question=q, search_queries=[q], doc_ids=[], need=Need(q, measures=list(measures)))
    assert breadth("How many PHCs are in Wamakko?", plan("How many PHCs are in Wamakko?")) == SIMPLE_DOCS
    for q in ("Compare what the reports say about maternal deaths in Sokoto",
              "Give me an overview of health financing in Sokoto", "What do the reports say about OOP spending?",
              "Kwatanta rahotanni kan mace-macen mata masu juna biyu"):
        assert breadth(q, plan(q)) == BROAD_DOCS, q
    money = "Compare the 2025 and 2026 health budgets"
    assert breadth(money, plan(money)) == SIMPLE_DOCS                    # a budget comparison: the structured path
    several = "What are stunting, wasting and immunisation rates in Sokoto?"
    assert breadth(several, plan(several, ["stunting", "wasting", "immunisation"])) == BROAD_DOCS


def pub(i):
    return Publisher(f"p{i}", f"P{i}", level="state", tier=1)


def test_the_source_cap_keeps_library_documents_in_place() -> None:
    reg, lib = [pub(i) for i in range(6)], [pub(10 + i) for i in range(3)]
    assert [p.id for p in cap_sources(reg, lib, 3)] == ["p0", "p1", "p10"]
    assert [p.id for p in cap_sources(reg, lib, 8)] == ["p0", "p1", "p2", "p3", "p4", "p5", "p10", "p11"]
    assert [p.id for p in cap_sources(reg, [], 3)] == ["p0", "p1", "p2"]


def test_amounts_in_house_style_for_display_only() -> None:
    assert house_style("NGN29,6 billion out of N29.62 billion", "en") == "₦29.6 billion out of ₦29.62 billion"
    assert house_style("N23.5billion and NGN 1.29bn", "ha") == "₦23.5 biliyan and ₦1.29 biliyan"
    assert house_style("N12,026 million", "en") == "₦12,026 million"           # a thousands comma stays


def test_symmetric_links_need_shared_topics_and_overlapping_years() -> None:
    a = [{"topic": "primary health care financing"}, {"topic": "maternal mortality"}]
    b = [{"topic": "PHC financing and primary health care budgets"}, {"topic": "maternal mortality causes"}]
    assert C.shared_topics(a, b) == ["primary health care financing", "maternal mortality"]
    assert C.years_overlap((2022, 2023), (2023, 2025)) and not C.years_overlap((2010, 2012), (2023, 2025))
    assert C.years_overlap((None, None), (2023, 2025))


# --- with the dev database: a fixture document found only through its card --------------------------------------

DOC, OTHER = "zz-fixture-report-2", "zz-fixture-water-plan"
FIXTURE_PAGES = {
    1: "Report 2. Annex volumes.",
    2: "Annex A lists the field teams and the survey dates.",
    3: "Annex B. Hand pump functionality by ward in Kebbe and Tambuwal: 61 of 100 pumps worked in 2025.",
    4: "Annex C. Borehole yields and depths.",
}


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM doc_cards LIMIT 0")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database with cards (migration 0026): {e}")
    for d, title in ((DOC, "Report 2"), (OTHER, "Rural Water Supply Plan 2025-2027")):
        c.execute("INSERT INTO documents (id, title, category, year, publisher, acquisition, sha256, page_count) "
                  "VALUES (%s, %s, 'partner_report', 2025, 'Fixture Water Board', 'local', 'f', 4)", (d, title))
    for p, text in FIXTURE_PAGES.items():
        c.execute("INSERT INTO pages (doc_id, page, text, source) VALUES (%s, %s, %s, 'text')", (DOC, p, text))
        c.execute("INSERT INTO chunks (doc_id, page, idx, text) VALUES (%s, %s, 0, %s)", (DOC, p, text))
    c.execute("INSERT INTO pages (doc_id, page, text, source) VALUES (%s, 1, 'Rural water plan targets.', 'text')",
              (OTHER,))
    card = {"summary": "A field survey of rural water points: hand pump and borehole functionality by ward.",
            "kind": "assessment", "topics": [{"topic": "hand pump functionality", "pages": [3]},
                                             {"topic": "rural water supply", "pages": [2, 3]}],
            "geography": {"level": "ward", "places": ["Kebbe", "Tambuwal"]}, "period": "2025", "year_from": 2025,
            "year_to": 2025, "measures": ["share of working hand pumps by ward"]}
    sections = [{"seq": 1, "title": "Annex A", "kind": "section", "page_from": 2, "page_to": 2,
                 "summary": "Field teams and survey dates.", "topics": ["survey logistics"], "geography": {},
                 "period": "2025", "measures": []},
                {"seq": 2, "title": "Annex B", "kind": "section", "page_from": 3, "page_to": 3,
                 "summary": "Hand pump functionality by ward in Kebbe and Tambuwal.",
                 "topics": ["hand pump functionality", "rural water supply"],
                 "geography": {"level": "ward", "places": ["Kebbe", "Tambuwal"]}, "period": "2025",
                 "measures": ["working hand pumps"]}]
    C.store(c, DOC, "Report 2", card, sections, "fixture")
    other = {**card, "summary": "The state's rural water supply plan with hand pump repair targets.",
             "kind": "sector plan", "topics": [{"topic": "rural water supply", "pages": [1]},
                                               {"topic": "hand pump functionality targets", "pages": [1]}],
             "year_from": 2025, "year_to": 2027}
    C.store(c, OTHER, "Rural Water Supply Plan 2025-2027", other, [], "fixture")
    yield c
    c.rollback()
    c.close()


Q = "What share of hand pumps were working in Kebbe wards?"


def test_a_document_whose_title_says_nothing_is_found_through_its_card(conn) -> None:
    from app.retrieval.library_search import library_search
    hits = library_search(conn, Q)
    docs = list(dict.fromkeys(h.hit.doc_id for h in hits))
    assert DOC in docs[:3], docs
    assert "card" in next(h for h in hits if h.hit.doc_id == DOC).via


def test_a_section_card_leads_to_its_pages(conn) -> None:
    from app.retrieval.library_search import library_search
    pages = [h.hit.page for h in library_search(conn, Q) if h.hit.doc_id == DOC]
    assert pages and pages[0] == 3
    m = next(x for x in C.card_matches(conn, Q, None) if x.doc_id == DOC)
    assert m.score > 0                                                    # places and words alone already match


def test_related_links_are_symmetric_with_a_reason(conn) -> None:
    C.build_links(conn)
    rows = dict(((a, b), r) for a, b, r in conn.execute(
        "SELECT doc_a, doc_b, reason FROM doc_links WHERE doc_a IN (%s, %s)", (DOC, OTHER)).fetchall())
    assert (DOC, OTHER) in rows and (OTHER, DOC) in rows
    assert "hand pump functionality" in rows[(DOC, OTHER)] and rows[(DOC, OTHER)] == rows[(OTHER, DOC)]
    assert C.related(conn, [DOC])[0][0] == OTHER


def test_a_simple_question_reads_no_related_document_a_broad_one_does(conn) -> None:
    C.build_links(conn)
    p = Plan(english_question=Q, search_queries=[Q], doc_ids=[DOC], need=Need(Q))
    assert widen_for_breadth(conn, p, Q, SIMPLE_DOCS) == [DOC]
    broad = "Compare what the reports say about hand pump functionality"
    pb = Plan(english_question=broad, search_queries=[broad], doc_ids=[DOC], need=Need(broad))
    assert OTHER in widen_for_breadth(conn, pb, broad, BROAD_DOCS)


def test_doesnt_print_is_only_said_after_the_whole_document_was_searched(conn) -> None:
    p = Plan(english_question=Q, search_queries=["hand pump functionality by ward"], doc_ids=[DOC], need=Need(Q))
    read_p2 = [Evidence(1, DOC, "Report 2", 2025, 2, "text", FIXTURE_PAGES[2])]
    text = "The report does not publish hand pump functionality by ward. It lists the field teams."
    out, changed = checked_absence(conn, p, read_p2, read_p2, text, "en")
    assert changed and out.endswith("I didn't find this in the pages I read.") and "page 3" not in out
    assert "does not publish" not in out and out.startswith("It lists the field teams.")
    read_all = [Evidence(i, DOC, "Report 2", 2025, pg, "text", t) for i, (pg, t) in enumerate(FIXTURE_PAGES.items(), 1)]
    same, changed = checked_absence(conn, p, read_all, read_all, text, "en")
    assert not changed and same == text
    # an answer that answered keeps no 'I didn't find this' note: only the unverified sentence goes (3 Nov)
    answered = "The report counts 1,240 hand pumps, 62% of them working. It does not publish the ward split."
    out, changed = checked_absence(conn, p, read_p2, read_p2, answered, "en")
    assert changed and out == "The report counts 1,240 hand pumps, 62% of them working."


def test_cards_cascade_with_their_document(conn) -> None:
    conn.execute("SAVEPOINT s")
    conn.execute("DELETE FROM documents WHERE id = %s", (DOC,))
    assert conn.execute("SELECT count(*) FROM section_cards WHERE doc_id = %s", (DOC,)).fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM doc_cards WHERE doc_id = %s", (DOC,)).fetchone()[0] == 0
    conn.execute("ROLLBACK TO SAVEPOINT s")
    assert json.loads(json.dumps(C.card_text("Report 2", {"summary": "x", "topics": [{"topic": "t"}]}))).startswith(
        "Report 2. x")
