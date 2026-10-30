"""The open-web fallback (docs/question-planning.md §5) and the domains awaiting approval.

When the registry's channels and allowlisted search find nothing, the open web is searched without site filters.
The pick step chooses the result that is the wanted document; if it is on a trusted pattern (policy.trusted) it
is fetched like any other, with robots.txt, size limits, sandboxed parsing and the global exclusions. If it is on
any other site, nothing is fetched: the domain is queued in domain_reviews with the question that needed it, and
the user is told the document is on a site Kasafi hasn't approved yet. Approving it on /admin/review makes it
fetchable (policy.APPROVED).
"""

from __future__ import annotations

import json
import logging
import re

import httpx
import psycopg

from app.acquisition import policy
from app.acquisition.find import Candidate, excluded, search_web
from app.acquisition.registry import registry

log = logging.getLogger(__name__)

REVIEW_RETENTION_DAYS = 90


def trusted_hint_sites() -> tuple[str, ...]:
    """Partner-hint websites that have a dated check in the registry's domain_checks (verified reachable and
    allowed). Only their domains are used; the hints file is never quoted or sent to a model."""
    from app.agent.topics import HINTS_PATH
    try:
        d = json.loads(HINTS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    checked = {k for k, v in registry().domain_checks.items() if re.match(r"\d{4}-\d\d-\d\d", v)}
    sites = {policy.site_of(w if w.startswith("https://") else f"https://{w}")
             for p in d.get("partners", []) if (w := str(p.get("website") or "").strip())}
    return tuple(sorted(s for s in sites if s and s in checked))


def open_web_trusted(url: str) -> bool:
    """Fetchable from an open-web result: allowlisted, approved, a trusted pattern or a verified partner site;
    never a domain the registry lists as unverified (awaiting its own check) or blocked."""
    host = policy.site_of(url)
    if any(host == d or host.endswith("." + d) for d in registry().unverified_domains()) \
            and not policy.host_allowed(url):
        return False
    return policy.trusted(url, trusted_hint_sites())


def open_web_queries(description: str) -> list[str]:
    return [f"{description} filetype:pdf", description]


async def open_web_candidates(http: httpx.AsyncClient, description: str, key: str) -> list[Candidate]:
    """Web search with no site filter; https results not caught by the global exclusions."""
    out, seen = [], set()
    for q in open_web_queries(description):
        try:
            found = await search_web(http, q, key)
        except httpx.HTTPError as e:
            log.info("open-web search failed: %s", type(e).__name__)
            continue
        for c in found:
            c.url = policy.https_url(c.url)
            if c.url not in seen and policy.site_of(c.url) and not excluded(c):
                seen.add(c.url)
                out.append(c)
    return out[:10]


def queue_domain(conn: psycopg.Connection, c: Candidate, question: str) -> str:
    """Queue the result's domain for a person (once per domain; later questions update it). Returns the domain."""
    domain = policy.site_of(c.url)
    conn.execute("DELETE FROM domain_reviews WHERE status <> 'approved' "
                 "AND last_seen < now() - make_interval(days => %s)", (REVIEW_RETENTION_DAYS,))
    conn.execute("""INSERT INTO domain_reviews (domain, question, url, title) VALUES (%s, %s, %s, %s)
                    ON CONFLICT (domain) DO UPDATE SET last_seen = now(), hits = domain_reviews.hits + 1,
                    question = EXCLUDED.question, url = EXCLUDED.url, title = EXCLUDED.title""",
                 (domain, question[:1000], c.url[:1000], c.title[:300]))
    log.info("domain queued for approval: %s", domain)
    return domain


def load_approved(conn: psycopg.Connection) -> set[str]:
    """Approved domains become fetchable (policy.APPROVED). Called at startup and after each approval."""
    try:
        rows = conn.execute("SELECT domain FROM domain_reviews WHERE status = 'approved'").fetchall()
    except psycopg.errors.UndefinedTable:          # before migration 0010
        conn.rollback()
        return set(policy.APPROVED)
    policy.APPROVED.clear()
    policy.APPROVED.update(r[0] for r in rows)
    return set(policy.APPROVED)
