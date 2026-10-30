import asyncio
import contextlib
import json
from pathlib import Path

import httpx
import pytest

from app.acquisition import forget as fg
from app.acquisition import library
from app.acquisition.find import Candidate
from app.acquisition.policy import USER_AGENT
from tests.helpers import make_settings

# --- forget_document -------------------------------------------------------------------------------

DOC = {"id": "bir-2025-q3", "title": "Q3 2025", "acquisition": "fetched", "status": "auto-indexed",
       "source_url": "https://mof.sk.gov.ng/q3.pdf", "final_url": "https://mof.sk.gov.ng/q3.pdf", "sha256": "ab" * 32,
       "fetched_at": "2026-10-28T14:32:50+00:00", "indexed_at": "2026-10-28T14:32:50+00:00", "pages": 85, "chunks": 1111}


class FakeConn:
    def __init__(self) -> None:
        self.sql: list[str] = []

    def execute(self, sql, params=None):
        self.sql.append(sql)

    @contextlib.contextmanager
    def transaction(self):
        yield


def setup(monkeypatch, tmp_path: Path, doc: dict | None = DOC):
    monkeypatch.setattr(fg, "describe", lambda conn, doc_id: dict(doc) if doc else None)
    (tmp_path / "bir-2025-q3.pdf").write_bytes(b"%PDF")
    return make_settings(kasafi_fetch_dir=str(tmp_path)), FakeConn()


def test_dry_run_removes_nothing(monkeypatch, tmp_path: Path) -> None:
    s, conn = setup(monkeypatch, tmp_path)
    rec = fg.forget(conn, "bir-2025-q3", s, reason="demo reset")
    assert conn.sql == [] and (tmp_path / "bir-2025-q3.pdf").exists() and rec["pages"] == 85
    assert not (tmp_path / "forgotten.jsonl").exists()


def test_forget_deletes_row_and_file_and_logs_provenance(monkeypatch, tmp_path: Path) -> None:
    s, conn = setup(monkeypatch, tmp_path)
    fg.forget(conn, "bir-2025-q3", s, reason="demo reset", dry_run=False)
    assert any(q.startswith("DELETE FROM documents") for q in conn.sql)
    assert not (tmp_path / "bir-2025-q3.pdf").exists()
    logged = json.loads((tmp_path / "forgotten.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert logged["reason"] == "demo reset" and logged["sha256"] == DOC["sha256"] and logged["source_url"]


def test_seed_documents_need_explicit_flag(monkeypatch, tmp_path: Path) -> None:
    s, conn = setup(monkeypatch, tmp_path, {**DOC, "id": "budget-2025-approved", "acquisition": "download"})
    with pytest.raises(SystemExit, match="seed document"):
        fg.forget(conn, "budget-2025-approved", s, reason="", dry_run=False)
    assert conn.sql == []
    fg.forget(conn, "budget-2025-approved", s, reason="x", allow_seed=True, dry_run=False)
    assert conn.sql


def test_unknown_document(monkeypatch, tmp_path: Path) -> None:
    s, conn = setup(monkeypatch, tmp_path, None)
    with pytest.raises(SystemExit, match="no document"):
        fg.forget(conn, "nope", s, reason="")


# --- honest user agent; sites that disallow us are "local only" ---------------------------------

def test_user_agent_identifies_kasafi() -> None:
    assert USER_AGENT.startswith("KasafiBot/1.0 ") and "halalnumeriq.com.ng/kasafi" in USER_AGENT


def test_disallowing_site_is_skipped_before_any_fetch(monkeypatch) -> None:
    agents, fetched = [], []

    def handler(req: httpx.Request) -> httpx.Response:
        agents.append(req.headers.get("user-agent", ""))
        if req.url.host == "mof.sk.gov.ng":
            return httpx.Response(200, text="User-agent: KasafiBot\nDisallow: /\n")
        return httpx.Response(200, text="User-agent: *\nAllow: /\n")

    async def candidates(http, description, settings):
        return [Candidate("https://mof.sk.gov.ng/q3.pdf", "Q3 (mof)"), Candidate("https://sokotostate.gov.ng/q3.pdf", "Q3")]

    async def rank(description, cands, client, settings):
        return cands                                                   # both could be it

    async def fetch(conn, url, description, **kw):
        fetched.append(url)
        return library.Acquired("failed", url=url, detail="not the wanted document")

    monkeypatch.setattr(library, "find_local", lambda conn, d: None)
    monkeypatch.setattr(library, "fetches_today", lambda conn: 0)
    monkeypatch.setattr(library, "search_candidates", candidates)
    monkeypatch.setattr(library, "rank_candidates", rank)
    monkeypatch.setattr(library, "fetch_and_index", fetch)
    monkeypatch.setattr(library, "registry_urls", lambda d: [])

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler),
                                     headers={"User-Agent": USER_AGENT}) as http:
            return await library.find_and_fetch(None, "Q3 2025", settings=make_settings(), client=None, http=http)

    acq = asyncio.run(go())
    assert fetched == ["https://sokotostate.gov.ng/q3.pdf"]           # mof.sk.gov.ng never fetched
    assert acq.status == "not_found" and "mof.sk.gov.ng: disallowed by robots.txt" in acq.detail
    assert agents and all(a == USER_AGENT for a in agents)
