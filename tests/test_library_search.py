"""The library-wide search (app/retrieval/library_search.py): a freshly indexed document is found by a question that
doesn't name it, on every path: the search itself, the document path's evidence, the intention route (a plan for
'plan to raise'), the topic sweep's sources, and before a web fetch. The fixture document is written inside a
transaction that is rolled back, so the dev library is untouched."""

import pytest

from app.agent.answer import Plan, gather_evidence, intention_docs, library_first
from app.agent.need import Need
from app.agent.topics import LIBRARY_PREFIX, library_sources
from app.retrieval.library_search import distinctive_phrases, library_search

DOC = "zz-fixture-cold-chain-2026"
PAGES = {
    1: "Sokoto State Cold Chain Strengthening Strategy 2026. Prepared by the State Immunisation Working Group.",
    2: ("Findings. In the cold chain equipment inventory carried out in March 2026, only 47 of the 112 ward "
        "vaccine stores had a working solar direct-drive refrigerator. Stock-outs of measles vaccine lasted on "
        "average 19 days in the wards without one."),
    3: ("Targets. The state intends to raise the number of ward vaccine stores with a working solar direct-drive "
        "refrigerator from 47 to 100 by December 2027, at a cost of NGN2.4 billion, of which NGN0.9 billion is "
        "proposed for 2026."),
}


def test_distinctive_phrases_are_the_questions_own_multi_word_terms() -> None:
    ph = distinctive_phrases("How many primary health centres met the minimum staffing requirements in the drug "
                             "revolving fund readiness assessment?")
    assert "drug revolving fund" in ph and "minimum staffing requirements" in ph
    assert not any(p in ("sokoto state", "how many") for p in ph)


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT embedding FROM chunks LIMIT 0")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database with chunk vectors (migration 0025): {e}")
    from app.retrieval.library_search import embed_chunks
    c.execute("INSERT INTO documents (id, title, category, year, publisher, acquisition, sha256, page_count) VALUES "
              "(%s, 'Sokoto State Cold Chain Strengthening Strategy 2026', 'sector_plan', 2026, "
              "'Sokoto State Primary Health Care Development Agency', 'local', 'fixture', 3)", (DOC,))
    for p, text in PAGES.items():
        c.execute("INSERT INTO pages (doc_id, page, text, source) VALUES (%s, %s, %s, 'text')", (DOC, p, text))
        c.execute("INSERT INTO chunks (doc_id, page, idx, text) VALUES (%s, %s, 0, %s)", (DOC, p, text))
    try:
        embed_chunks(c, DOC)
    except Exception as e:  # noqa: BLE001
        c.rollback()
        pytest.skip(f"the embedding model isn't available here: {e}")
    yield c
    c.rollback()
    c.close()


def plan(q: str, docs: list[str], queries: list[str] | None = None) -> Plan:
    return Plan(english_question=q, search_queries=queries or [q], doc_ids=docs, need=Need(q))


UNNAMED = "How many ward vaccine stores in Sokoto have a working solar direct-drive refrigerator?"


def test_a_fresh_document_is_found_by_a_question_that_does_not_name_it(conn) -> None:
    hits = library_search(conn, UNNAMED)
    assert hits[0].hit.doc_id == DOC and hits[0].hit.page == 2 and hits[0].strong
    assert "phrase" in hits[0].via and len(hits[0].via) >= 2     # the question's own phrase, and one other list


def test_meaning_finds_it_in_other_words(conn) -> None:
    hits = library_search(conn, "Do Sokoto's villages have fridges powered by the sun to keep vaccines cold?")
    assert DOC in list(dict.fromkeys(h.hit.doc_id for h in hits))[:3]       # among the first three documents


def test_the_document_path_reads_it_although_the_plan_chose_other_documents(conn) -> None:
    ev = gather_evidence(conn, plan(UNNAMED, ["health-aop-2025", "emonc-sokoto"],
                                    ["vaccine cold chain equipment", "ward vaccine stores refrigerator"]))
    assert (DOC, 2) in [(e.doc_id, e.page) for e in ev]


def test_an_intention_question_reads_the_plan_first(conn) -> None:
    q = "What did Sokoto plan to raise the number of ward vaccine stores with solar fridges to by 2027?"
    p = plan(q, ["budget-2026-approved"], ["vaccine stores solar refrigerator target 2027"])
    assert intention_docs(conn, q, p)[0] == DOC
    plain = "How many ward vaccine stores have a solar fridge?"
    assert intention_docs(conn, plain, plan(plain, ["budget-2026-approved"])) == []     # no intention words


def test_before_a_fetch_the_library_is_checked(conn) -> None:
    p = plan(UNNAMED, ["health-aop-2025"])
    p.missing_document = "Sokoto State cold chain equipment inventory 2026"
    assert library_first(conn, p, UNNAMED)[0] == DOC


def test_the_topic_sweep_takes_indexed_documents_as_sources(conn) -> None:
    got = library_sources(conn, UNNAMED, have={"emonc-sokoto"})
    ids = [p.id for p, _ in got]
    assert f"{LIBRARY_PREFIX}{DOC}" in ids
    pub, pages = got[ids.index(f"{LIBRARY_PREFIX}{DOC}")]
    assert pub.name == "Sokoto State Primary Health Care Development Agency" and 2 in pages
    assert library_sources(conn, UNNAMED, have={DOC}) == [] or f"{LIBRARY_PREFIX}{DOC}" not in \
        [p.id for p, _ in library_sources(conn, UNNAMED, have={DOC})]
