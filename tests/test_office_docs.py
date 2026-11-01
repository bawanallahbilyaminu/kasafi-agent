"""Office documents in the library (docs/architecture.md, "Office documents"): the real type from the bytes,
unsafe files rejected with a reason, Word-type files converted to PDF (LibreOffice when installed, else a fake
converter) and indexed like any PDF, provenance recorded, citations saying the pages are the converted PDF's, and
an on-demand fetch of a .docx through the real acquisition path. Fixture files only (tests/office_fixtures.py)."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import httpx
import pytest

from app.acquisition import convert
from app.acquisition.convert import ConversionError, convert_to_pdf
from app.acquisition.filetype import sniff
from tests.office_fixtures import (docx_bytes, fake_converter, fake_doc_bytes, odt_bytes, pdf_bytes, rtf_bytes,
                                   zip_bomb_bytes)

REAL = convert.soffice_path() is not None
TABLE = [["Agency", "2026 Approved Budget"], ["Rural Water and Sanitation Agency", "12,345,678.00"],
         ["Ministry of Health", "98,765,432.10"]]
PARAS = ["Sokoto State Water Supply Plan 2026", "Section 2: Budget lines by agency"]


@pytest.fixture
def converter(monkeypatch):
    """The real LibreOffice when it is installed, else the fake converter (a minimal PDF writer)."""
    if not REAL:
        monkeypatch.setattr(convert, "CONVERTER", fake_converter)
    return "libreoffice" if REAL else "fake"


# --- 1. the real type from the bytes ---------------------------------------------------------------------------

def test_the_type_comes_from_the_bytes_not_the_name(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_bytes(pdf_bytes(["x"]))
    (tmp_path / "b.docx").write_bytes(docx_bytes(PARAS))
    (tmp_path / "mislabelled.pdf").write_bytes(docx_bytes(PARAS))         # a Word file named .pdf
    (tmp_path / "mislabelled.docx").write_bytes(pdf_bytes(["x"]))         # a PDF named .docx
    (tmp_path / "c.odt").write_bytes(odt_bytes(PARAS))
    (tmp_path / "d.doc").write_bytes(fake_doc_bytes())
    (tmp_path / "e.rtf").write_bytes(rtf_bytes(PARAS))
    (tmp_path / "f.html").write_bytes(b"<html>not a document</html>")
    kinds = {n: sniff(tmp_path / n) for n in ("a.pdf", "b.docx", "mislabelled.pdf", "mislabelled.docx", "c.odt", "d.doc", "e.rtf", "f.html")}
    assert {n: k.kind for n, k in kinds.items()} == {"a.pdf": "pdf", "b.docx": "docx", "mislabelled.pdf": "docx",
                                                     "mislabelled.docx": "pdf", "c.odt": "odt", "d.doc": "doc",
                                                     "e.rtf": "rtf", "f.html": "unknown"}
    assert all(not k.rejected for n, k in kinds.items() if n != "f.html") and kinds["f.html"].rejected


# --- 2. unsafe files are rejected with a reason, before anything is opened -------------------------------------

@pytest.mark.parametrize("name,data,reason", [
    ("m.docm", docx_bytes(PARAS, macro=True), "macro-enabled"),
    ("m.doc", fake_doc_bytes(macro=True), "macro-enabled"),
    ("ext.docx", docx_bytes(PARAS, external_image=True), "external link"),
    ("m.odt", odt_bytes(PARAS, macro=True), "macro part"),
    ("ext.odt", odt_bytes(PARAS, external_link=True), "external link"),
    ("o.rtf", rtf_bytes(PARAS, embedded_object=True), "embedded object"),
    ("bomb.docx", zip_bomb_bytes(), "zip bomb"),
], ids=["docm", "doc-vba", "docx-external-image", "odt-basic", "odt-external", "rtf-object", "zip-bomb"])
def test_macros_external_links_objects_and_zip_bombs_are_rejected(tmp_path: Path, name, data, reason) -> None:
    (tmp_path / name).write_bytes(data)
    ft = sniff(tmp_path / name)
    assert ft.rejected and reason in ft.reason, ft


# --- 3. conversion: timeouts and failures are reported once, the temp directory is deleted ---------------------

def test_a_conversion_timeout_is_reported_with_its_reason_and_leaves_nothing_behind(tmp_path: Path, monkeypatch) -> None:
    async def slow(src, out_dir, timeout):
        await asyncio.sleep(timeout + 3)
        return out_dir / "never.pdf"
    monkeypatch.setattr(convert, "CONVERTER", slow)
    monkeypatch.setattr(convert, "_libreoffice", slow)
    src = tmp_path / "slow.docx"
    src.write_bytes(docx_bytes(PARAS))
    before = {p.name for p in Path(tempfile.gettempdir()).glob("kasafi-convert-*")}
    with pytest.raises(ConversionError, match="timed out"):
        asyncio.run(convert_to_pdf(src, tmp_path / "slow.pdf", timeout=0.2))
    assert not (tmp_path / "slow.pdf").exists()
    assert {p.name for p in Path(tempfile.gettempdir()).glob("kasafi-convert-*")} <= before


def test_a_converter_that_produces_no_pdf_is_a_failure_not_a_retry(tmp_path: Path, monkeypatch) -> None:
    async def broken(src, out_dir, timeout):
        (out_dir / (src.stem + ".pdf")).write_bytes(b"not a pdf")
        return out_dir / (src.stem + ".pdf")
    monkeypatch.setattr(convert, "CONVERTER", broken)
    src = tmp_path / "x.docx"
    src.write_bytes(docx_bytes(PARAS))
    with pytest.raises(ConversionError, match="did not produce a PDF"):
        asyncio.run(convert_to_pdf(src, tmp_path / "x.pdf"))


@pytest.mark.skipif(not REAL, reason="LibreOffice not installed here (the server image has it)")
def test_hausa_letters_survive_a_real_conversion(tmp_path: Path) -> None:
    from app.retrieval.indexer import extract_pages
    src = tmp_path / "hausa.docx"
    src.write_bytes(docx_bytes(["Ƙaramar Hukumar Wamakko: kasafin ban ruwa ₦12,345,678.00", "ɓ ɗ ƙ ƴ Ɓ Ɗ Ƙ Ƴ"]))
    conv = asyncio.run(convert_to_pdf(src, tmp_path / "hausa.pdf"))
    text = "\n".join(extract_pages(conv.pdf))
    assert "Ƙaramar Hukumar Wamakko" in text and "ɓ ɗ ƙ ƴ" in text and "12,345,678.00" in text
    assert conv.converter.startswith("LibreOffice")


# --- 4. a local manifest entry: converted, indexed, a figure found on its page ---------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT original_format FROM documents LIMIT 1").fetchone()
    except Exception:              # noqa: BLE001
        pytest.skip("dev database (migration 0023) not available")
    yield c
    c.close()


def _manifest(tmp_path: Path, doc_id: str, file_name: str) -> Path:
    m = {"version": 1, "documents": [{"id": doc_id, "title": "Sokoto State Water Supply Plan 2026", "category": "plan",
                                      "year": 2026, "publisher": "Sokoto State Government", "acquisition": "local",
                                      "file": file_name}]}
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(m), encoding="utf-8")
    return p


def _cleanup(conn, doc_id: str) -> None:
    conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    conn.commit()


@pytest.mark.parametrize("name,data", [("plan.docx", docx_bytes(PARAS, TABLE)), ("plan.odt", odt_bytes(PARAS + [" | ".join(r) for r in TABLE])),
                                       ("plan.rtf", rtf_bytes(PARAS + [" | ".join(r) for r in TABLE])),
                                       ("plan.pdf", docx_bytes(PARAS, TABLE))],       # a Word file named .pdf
                         ids=["docx", "odt", "rtf", "docx-named-pdf"])
def test_a_local_word_file_is_converted_indexed_and_its_figure_is_on_the_right_page(tmp_path: Path, conn, converter, name, data) -> None:
    from app.retrieval.indexer import index_manifest
    from app.retrieval.search import search
    doc_id = f"test-office-{name.split('.')[-1]}"
    (tmp_path / name).write_bytes(data)
    try:
        res = index_manifest(conn, _manifest(tmp_path, doc_id, name), only=[doc_id])
        assert res[0].status == "indexed", res[0]
        assert (tmp_path / f"{doc_id}.pdf").exists() and (tmp_path / name).exists()      # the original stays
        row = conn.execute("SELECT original_format, original_sha256, converter, sha256 FROM documents WHERE id = %s",
                           (doc_id,)).fetchone()
        assert row[0] in ("docx", "odt", "rtf") and len(row[1]) == 64 and row[2] and row[3] != row[1]
        hits = search(conn, "Rural Water and Sanitation Agency 12,345,678.00", k=3, doc_ids=[doc_id])
        assert hits and hits[0].page == 1 and "12,345,678.00" in hits[0].text
        # unchanged on a second run: no second conversion
        res2 = index_manifest(conn, _manifest(tmp_path, doc_id, name), only=[doc_id])
        assert res2[0].status == "unchanged"
    finally:
        _cleanup(conn, doc_id)


def test_a_pdf_named_docx_is_indexed_as_the_pdf_it_is(tmp_path: Path, conn) -> None:
    from app.retrieval.indexer import index_manifest
    doc_id = "test-office-pdfnamed"
    (tmp_path / "plan.docx").write_bytes(pdf_bytes(PARAS + ["Rural Water and Sanitation Agency 12,345,678.00"]))
    try:
        res = index_manifest(conn, _manifest(tmp_path, doc_id, "plan.docx"), only=[doc_id])
        assert res[0].status == "indexed"
        assert conn.execute("SELECT original_format FROM documents WHERE id = %s", (doc_id,)).fetchone()[0] is None
    finally:
        _cleanup(conn, doc_id)


def test_a_legacy_doc_fixture_is_detected_and_a_rejected_file_fails_with_the_reason(tmp_path: Path, conn, converter) -> None:
    from app.retrieval.indexer import index_manifest
    (tmp_path / "plan.docm").write_bytes(docx_bytes(PARAS, macro=True))
    res = index_manifest(conn, _manifest(tmp_path, "test-office-docm", "plan.docm"), only=["test-office-docm"])
    assert res[0].status == "failed" and "macro-enabled" in res[0].detail
    assert not conn.execute("SELECT 1 FROM documents WHERE id = 'test-office-docm'").fetchone()
    if converter == "fake":                                   # the fake OLE fixture: detection, then the fake converter
        (tmp_path / "plan.doc").write_bytes(fake_doc_bytes())
        try:
            res = index_manifest(conn, _manifest(tmp_path, "test-office-doc", "plan.doc"), only=["test-office-doc"])
            assert res[0].status == "indexed"
            assert conn.execute("SELECT original_format FROM documents WHERE id = 'test-office-doc'").fetchone()[0] == "doc"
        finally:
            _cleanup(conn, "test-office-doc")


# --- 5. citations say the pages are the converted PDF's --------------------------------------------------------

def test_citations_and_show_working_say_the_pages_are_the_converted_pdfs() -> None:
    from app.agent import answer as M
    from app.agent.answer import Answer, Evidence, format_citations, settle_verification, sources_line
    M.CONVERTED.clear()
    M.CONVERTED["plan-docx"] = "docx"
    e = Evidence(1, "plan-docx", "Sokoto State Water Supply Plan 2026", 2026, 3, "text", "x")
    try:
        assert format_citations([e], "en") == "[1] Sokoto State Water Supply Plan 2026, page 3 (PDF converted from the Word original)"
        assert "shafi 3 (PDF da aka canza daga asalin Word)" in format_citations([e], "ha")
        assert sources_line([e], "en").endswith("p. 3 (PDF converted from the Word original)")
        a = Answer("text", True, True, [e], exact="₦12,345,678.00 [1]")
        settle_verification(a, "en")
        assert "pages of the PDF Kasafi converted from the Word original" in a.working
        plain = Evidence(2, "budget-2026-approved", "Sokoto State FY 2026 Budget", 2026, 5, "text", "x")
        assert format_citations([plain], "en") == "[2] Sokoto State FY 2026 Budget, page 5"
    finally:
        M.CONVERTED.clear()


# --- 6. an on-demand fetch of a .docx from an allowlisted site, through the real acquisition path --------------

ROBOTS = "User-agent: *\nAllow: /\n"
DOCX_URL = "https://sokotostate.gov.ng/wp-content/uploads/2026/03/water-supply-plan-2026.docx"


def _http(responses: dict[str, httpx.Response]) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return responses.get(str(request.url), httpx.Response(404))
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_a_docx_fetched_on_demand_is_converted_indexed_and_kept_with_its_original(tmp_path: Path, conn, converter, monkeypatch) -> None:
    from app.acquisition import library
    from tests.helpers import make_settings
    s = make_settings(kasafi_fetch_enabled=True, kasafi_fetch_dir=str(tmp_path / "fetched"))

    async def confirm(description, pages, existing_ids, client, settings):
        assert "12,345,678.00" in "\n".join(pages)                   # the converted PDF's text reached the check
        return {"match": True, "id": "test-office-fetched", "title": "Sokoto State Water Supply Plan 2026",
                "category": "plan", "year": 2026, "publisher": "Sokoto State Government"}
    monkeypatch.setattr(library, "confirm_document", confirm)
    body = docx_bytes(PARAS, TABLE)
    responses = {"https://sokotostate.gov.ng/robots.txt": httpx.Response(200, text=ROBOTS),
                 DOCX_URL: httpx.Response(200, content=body, headers={
                     "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})}
    try:
        async def go():
            async with _http(responses) as http:
                return await library.fetch_and_index(conn, DOCX_URL, "Sokoto water supply plan 2026", settings=s,
                                                     client=None, http=http)
        acq = asyncio.run(go())
        assert acq.status == "indexed" and acq.doc_id == "test-office-fetched", acq
        row = conn.execute("SELECT original_format, original_sha256, converter, acquisition FROM documents WHERE id = %s",
                           (acq.doc_id,)).fetchone()
        assert row[0] == "docx" and len(row[1]) == 64 and row[2] and row[3] == "fetched"
        assert (tmp_path / "fetched" / "test-office-fetched.pdf").exists()
        assert (tmp_path / "fetched" / "test-office-fetched.docx").read_bytes() == body     # the original beside it
        assert not list((tmp_path / "fetched").glob("incoming-*"))
        # the same original again (another URL): known by the original's hash, no second conversion
        responses[DOCX_URL + "?v=2"] = responses[DOCX_URL]
        again = asyncio.run(_again(conn, DOCX_URL + "?v=2", s, responses))
        assert again.status == "known" and again.doc_id == "test-office-fetched"
    finally:
        _cleanup(conn, "test-office-fetched")


async def _again(conn, url, s, responses):
    from app.acquisition import library
    async with _http(responses) as http:
        return await library.fetch_and_index(conn, url, "Sokoto water supply plan 2026", settings=s, client=None, http=http)


def test_a_macro_enabled_docx_fetched_on_demand_is_refused_with_the_reason(tmp_path: Path, conn, converter) -> None:
    from app.acquisition import library
    from tests.helpers import make_settings
    s = make_settings(kasafi_fetch_enabled=True, kasafi_fetch_dir=str(tmp_path / "fetched"))
    responses = {"https://sokotostate.gov.ng/robots.txt": httpx.Response(200, text=ROBOTS),
                 DOCX_URL: httpx.Response(200, content=docx_bytes(PARAS, macro=True))}
    acq = asyncio.run(_again(conn, DOCX_URL, s, responses))
    assert acq.status == "failed" and "macro-enabled" in acq.detail
    assert not list((tmp_path / "fetched").glob("*")) or not list((tmp_path / "fetched").glob("incoming-*"))
