import asyncio
import json
from pathlib import Path

import httpx
import pytest

from app.acquisition.fetch import FetchError, download_pdf
from app.acquisition.policy import ALLOWLIST, BASE_ALLOWLIST, Robots, content_signals, host_allowed, https_url
from app.acquisition.registry import registry
from app.acquisition.sandbox import ParseError, child_env, extract_pages_sandboxed

ROOT = Path(__file__).resolve().parents[1]
PDF = b"%PDF-1.4\n" + b"x" * 1000 + b"\n%%EOF\n"


@pytest.mark.parametrize("url, ok", [
    ("https://sokotostate.gov.ng/wp-content/uploads/a.pdf", True),
    ("https://mof.sk.gov.ng/wp-content/uploads/a.pdf", True),
    ("https://documents1.worldbank.org/curated/en/x.pdf", True),
    ("http://sokotostate.gov.ng/a.pdf", False),                    # https only
    ("https://kebbistate.gov.ng/file/2497/download", False),       # another state
    ("https://budgit.org/report.pdf", False),                      # do_not_ingest
    ("https://sokotostate.gov.ng.evil.com/a.pdf", False),          # suffix trick
    ("https://evilsokotostate.gov.ng/a.pdf", False),
    ("https://user@sokotostate.gov.ng/a.pdf", False),
    ("https://sokotostate.gov.ng:8443/a.pdf", False),
])
def test_allowlist(url: str, ok: bool) -> None:
    assert host_allowed(url) is ok


def test_allowlist_matches_manifest() -> None:
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["allowlist_domains"]) == set(BASE_ALLOWLIST)


def test_allowlist_adds_the_registrys_verified_domains_only() -> None:
    reg = registry()
    assert reg.version >= 1 and "displacement_humanitarian" in reg.topics
    assert set(BASE_ALLOWLIST) <= set(ALLOWLIST)
    assert {"sbs.sk.gov.ng", "data.unhcr.org", "data.humdata.org"} <= set(ALLOWLIST)
    assert not set(reg.unverified_domains()) & (set(ALLOWLIST) - set(BASE_ALLOWLIST))
    assert host_allowed("https://sbs.sk.gov.ng/api/documents/x/download")
    assert not host_allowed("https://ncfrmi.gov.ng/a.pdf")          # verified: "no"


def test_http_links_are_upgraded() -> None:
    assert https_url("http://documents.worldbank.org/a.pdf") == "https://documents.worldbank.org/a.pdf"
    assert https_url("https://x.org/a.pdf") == "https://x.org/a.pdf"


SOKOTO_ROBOTS = """# comments
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /
User-agent: GPTBot
Disallow: /
User-agent: *
Disallow: /wp-admin/
"""


def test_content_signals_from_our_groups_only() -> None:
    assert content_signals(SOKOTO_ROBOTS) == {"search": "yes", "ai-train": "no", "use": "reference"}
    other = "User-agent: GPTBot\nContent-Signal: ai-input=no\nDisallow: /\n"
    assert content_signals(other) == {}


def transport(routes: dict[str, httpx.Response], seen: list[str] | None = None) -> httpx.MockTransport:
    def handler(req: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(str(req.url))
        return routes.get(str(req.url), httpx.Response(404))
    return httpx.MockTransport(handler)


def fetch(routes: dict, url: str, tmp_path: Path, seen: list | None = None, **kw):
    async def go():
        async with httpx.AsyncClient(transport=transport(routes, seen)) as http:
            return await download_pdf(url, tmp_path / "doc.pdf", http, Robots(http), **kw)
    return asyncio.run(go())


ROBOTS_OK = {"https://sokotostate.gov.ng/robots.txt": httpx.Response(200, text=SOKOTO_ROBOTS)}
URL = "https://sokotostate.gov.ng/wp-content/uploads/2025/10/q3.pdf"


def test_download_records_provenance(tmp_path: Path) -> None:
    d = fetch({**ROBOTS_OK, URL: httpx.Response(200, content=PDF)}, URL, tmp_path)
    assert d.path.read_bytes() == PDF and d.bytes == len(PDF) and len(d.sha256) == 64 and d.final_url == URL


def test_robots_disallow_and_ai_input_no_are_refused(tmp_path: Path) -> None:
    with pytest.raises(FetchError, match="disallowed"):
        fetch({"https://sokotostate.gov.ng/robots.txt": httpx.Response(200, text="User-agent: *\nDisallow: /\n"),
               URL: httpx.Response(200, content=PDF)}, URL, tmp_path)
    with pytest.raises(FetchError, match="ai-input=no"):
        fetch({"https://sokotostate.gov.ng/robots.txt":
               httpx.Response(200, text="User-agent: *\nContent-Signal: ai-input=no\nAllow: /\n"),
               URL: httpx.Response(200, content=PDF)}, URL, tmp_path)


def test_unreadable_robots_is_refused(tmp_path: Path) -> None:
    with pytest.raises(FetchError, match="unreadable"):
        fetch({"https://sokotostate.gov.ng/robots.txt": httpx.Response(503), URL: httpx.Response(200, content=PDF)},
              URL, tmp_path)


def test_redirect_off_the_allowlist_is_refused(tmp_path: Path) -> None:
    seen: list[str] = []
    with pytest.raises(FetchError, match="allowlisted"):
        fetch({**ROBOTS_OK, URL: httpx.Response(302, headers={"location": "https://evil.example/x.pdf"})},
              URL, tmp_path, seen)
    assert "https://evil.example/x.pdf" not in seen          # never requested


@pytest.mark.parametrize("resp, why", [
    (httpx.Response(200, text="<html>landing page</html>"), "not a PDF"),
    (httpx.Response(200, content=b"%PDF-1.4\n" + b"x" * 100), "no %%EOF"),
    (httpx.Response(200, content=PDF, headers={"content-length": str(10**9)}), "too large"),
    (httpx.Response(500), "HTTP 500"),
])
def test_bad_downloads_are_refused(tmp_path: Path, resp, why: str) -> None:
    with pytest.raises(FetchError, match=why):
        fetch({**ROBOTS_OK, URL: resp}, URL, tmp_path)
    assert not (tmp_path / "doc.pdf").exists() and not (tmp_path / "doc.pdf.part").exists()


LANDING = "https://sokotostate.gov.ng/documents/details/124425"
NO_EXT = "https://sokotostate.gov.ng/documents/download/124425"


def test_a_file_without_pdf_in_its_address_is_accepted_by_what_it_is(tmp_path: Path) -> None:
    d = fetch({**ROBOTS_OK, NO_EXT: httpx.Response(200, content=PDF, headers={"content-type": "application/pdf"})},
              NO_EXT, tmp_path)
    assert d.path.read_bytes() == PDF


def test_a_landing_page_is_followed_one_hop_to_its_own_sites_document(tmp_path: Path) -> None:
    page = ('<a href="https://evil.example/x.pdf">x</a> <a href="/about">about</a> '
            '<a href="/documents/download/124425">Download</a>')
    html = {"content-type": "text/html; charset=utf-8"}
    d = fetch({**ROBOTS_OK, LANDING: httpx.Response(200, text=page, headers=html),
               NO_EXT: httpx.Response(200, content=PDF)}, LANDING, tmp_path)
    assert d.final_url == NO_EXT and d.url == LANDING
    with pytest.raises(FetchError, match="landing page, not a document"):      # one hop only
        fetch({**ROBOTS_OK, LANDING: httpx.Response(200, text=page, headers=html),
               NO_EXT: httpx.Response(200, text="<html>again</html>", headers=html)}, LANDING, tmp_path)
    with pytest.raises(FetchError, match="no document link"):
        fetch({**ROBOTS_OK, LANDING: httpx.Response(200, text='<a href="https://evil.example/x.pdf">x</a>',
                                                    headers=html)}, LANDING, tmp_path)


def test_size_limit_while_streaming(tmp_path: Path) -> None:
    with pytest.raises(FetchError, match="too large"):
        fetch({**ROBOTS_OK, URL: httpx.Response(200, content=PDF)}, URL, tmp_path, max_bytes=500)


def test_sandbox_env_has_no_secrets(monkeypatch) -> None:
    monkeypatch.setenv("META_API_KEY", "secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://x")
    env = child_env()
    assert "META_API_KEY" not in env and "DATABASE_URL" not in env


def test_sandbox_rejects_a_broken_pdf(tmp_path: Path) -> None:
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(PDF)
    with pytest.raises(ParseError, match="unreadable"):
        asyncio.run(extract_pages_sandboxed(bad))


def test_sandbox_extracts_a_real_pdf() -> None:
    pdf = ROOT / "data" / "berap-2025.pdf"
    if not pdf.exists():
        pytest.skip("seed PDF not downloaded")
    pages, image_pages = asyncio.run(extract_pages_sandboxed(pdf))
    assert pages and any(len(p) > 100 for p in pages)


@pytest.mark.parametrize("title, url, out", [
    ("DTM Nigeria Flash Report: attack in Sabon Birni displaces 1,200", "https://dtm.iom.int/a.pdf", True),
    ("BudgIT State of States 2025", "https://unicef.org/s.pdf", True),
    ("Sokoto IDPs rise, says SEMA", "https://punchng.com/x", True),
    ("Nigeria North-West Mobility Tracking Round 18", "https://dtm.iom.int/r18.pdf", False),
])
def test_global_excludes_drop_search_results(title: str, url: str, out: bool) -> None:
    from app.acquisition.find import Candidate, excluded
    assert excluded(Candidate(url, title)) is out


def test_the_confirm_step_names_the_registrys_exclusions() -> None:
    from app.acquisition.library import CONFIRM_SYSTEM
    assert "BudgIT State of States" in CONFIRM_SYSTEM
