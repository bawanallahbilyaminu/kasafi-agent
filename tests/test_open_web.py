"""The open-web fallback (docs/question-planning.md §5): trusted patterns are fetched, other sites are queued."""

import asyncio

import pytest

from app.acquisition import library, policy, review
from app.acquisition.find import Candidate
from app.config import Settings


@pytest.mark.parametrize("url, ok", [
    ("https://mptf.undp.org/sites/default/files/documents/sp-nigeria-final-report.pdf", True),   # UN system
    ("https://www.jointsdgfund.org/sites/default/files/2022-03/report.pdf", True),
    ("https://www.who.int/docs/default-source/a.pdf", True),                                  # *.int
    ("https://nassp.gov.ng/wp-content/uploads/a.pdf", True),                                  # *.gov.ng
    ("https://openknowledge.worldbank.org/a.pdf", True),
    ("https://some-blog.com.ng/sokoto-budget.pdf", False),                                    # unknown: queued
    ("https://ncfrmi.gov.ng/a.pdf", False),          # the registry lists it as unverified: its own check first
    ("http://www.who.int/a.pdf", False),                                                      # https only
    ("https://who.int.evil.com/a.pdf", False),
    ("https://ilostat.ilo.org/a.pdf", False),         # blocked in domain_checks
])
def test_open_web_trust_patterns(url: str, ok: bool) -> None:
    assert review.open_web_trusted(url) is ok


def test_trust_patterns_do_not_widen_the_registry_allowlist() -> None:
    assert not policy.host_allowed("https://kebbistate.gov.ng/a.pdf")
    assert not policy.host_allowed("https://mptf.undp.org/a.pdf") or "undp.org" in policy.ALLOWLIST


def test_an_approved_domain_becomes_fetchable(monkeypatch) -> None:
    monkeypatch.setattr(policy, "APPROVED", {"budgetpartner.org"})
    assert policy.host_allowed("https://www.budgetpartner.org/x.pdf")
    assert review.open_web_trusted("https://budgetpartner.org/x.pdf")


class _Conn:
    def __init__(self) -> None:
        self.sql: list[tuple[str, tuple]] = []

    def execute(self, sql, params=()):
        self.sql.append((sql, params))
        return type("R", (), {"fetchone": lambda _s: (0,), "fetchall": lambda _s: []})()


def _run(monkeypatch, found: Candidate, fetched: list) -> library.Acquired:
    async def none(*a, **k):
        return []

    async def web(*a, **k):
        return [found]

    async def rank(description, cands, client, settings):
        return cands

    async def fetch(conn, url, description, **kw):
        fetched.append((url, kw["allowed"]))
        return library.Acquired("indexed", "doc-1", url=url)

    async def robots_ok(self, url):
        return True, ""
    monkeypatch.setattr(library, "search_candidates", none)
    monkeypatch.setattr(library, "open_web_candidates", web)
    monkeypatch.setattr(library, "rank_candidates", rank)
    monkeypatch.setattr(library, "registry_urls", lambda d: [])
    monkeypatch.setattr(library, "fetch_and_index", fetch)
    monkeypatch.setattr(library.Robots, "allowed", robots_ok)
    s = Settings(serper_api_key="k", kasafi_fetches_per_day=10)
    return asyncio.run(library.find_and_fetch(_Conn(), "UN joint programme on social protection Sokoto final report",
                                              settings=s, client=None, check_local=False, open_web=True,
                                              question="What did the UN social protection programme achieve?"))


def test_a_trusted_open_web_result_is_fetched_with_the_trust_check_on_every_hop(monkeypatch) -> None:
    fetched: list = []
    got = _run(monkeypatch, Candidate("https://mptf.undp.org/sites/default/files/final.pdf", "Final report"), fetched)
    assert got.status == "indexed" and fetched == [("https://mptf.undp.org/sites/default/files/final.pdf",
                                                    review.open_web_trusted)]


def test_an_unknown_site_is_queued_not_fetched(monkeypatch) -> None:
    fetched: list = []
    queued: list = []
    monkeypatch.setattr(library, "queue_domain", lambda conn, c, q: queued.append((policy.site_of(c.url), q))
                        or policy.site_of(c.url))
    got = _run(monkeypatch, Candidate("https://www.some-ngo.org/reports/sp-sokoto.pdf", "SP report"), fetched)
    assert got.status == "awaiting" and got.detail == "some-ngo.org" and not fetched
    assert queued == [("some-ngo.org", "What did the UN social protection programme achieve?")]


def test_the_user_is_told_the_site_awaits_approval() -> None:
    from app.agent import answer as ans
    plan = ans.Plan("q", ["q"], [])
    plan.missing_document = "SP final report"
    a = ans._not_found(None, plan, "en", library.Acquired("awaiting", detail="some-ngo.org"), {})
    assert "hasn't approved yet (some-ngo.org)" in a.text and not a.found


def test_the_registry_address_is_tried_before_any_search_and_judged_by_content(monkeypatch) -> None:
    order: list = []

    async def search(*a, **k):
        order.append("search")
        return []

    async def fetch(conn, url, description, **kw):
        order.append(url)
        return library.Acquired("indexed", "un-jp-eval", url=url)

    async def robots_ok(self, url):
        return True, ""
    monkeypatch.setattr(library, "search_candidates", search)
    monkeypatch.setattr(library, "fetch_and_index", fetch)
    monkeypatch.setattr(library.Robots, "allowed", robots_ok)
    got = asyncio.run(library.find_and_fetch(
        _Conn(), "Final Evaluation of the UN Joint Programme on Social Protection in Nigeria", settings=Settings(),
        client=None, check_local=False))
    assert got.doc_id == "un-jp-eval" and order == [
        "https://mptf.undp.org/sites/default/files/documents/2023-05/nigeria_final_evaluation_report.pdf"]
    assert library.registry_urls("NBS CPI September 2026") == []          # a shared year or month is no match
