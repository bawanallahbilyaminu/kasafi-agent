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
