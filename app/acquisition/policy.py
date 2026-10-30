"""Where Kasafi may fetch documents from: the domain allowlist and robots.txt.

Only https URLs on allowlisted domains (or their subdomains) are fetched, and only when the
host's robots.txt allows our user agent. Some government sites also publish Cloudflare
Content-Signals (e.g. "search=yes, ai-train=no"); a host that says ai-input=no is refused,
because answering from a document is AI input. Kasafi never trains on documents.
"""

from __future__ import annotations

import logging
import urllib.parse
import urllib.robotparser

import httpx

from app.acquisition.registry import registry

log = logging.getLogger(__name__)

# Honest identification: robots.txt rules are matched on the "KasafiBot" token, and the URL explains who we are.
USER_AGENT = "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"

# The fixed base list; keep in sync with data/manifest.json "allowlist_domains" (tests check). sk.gov.ng covers
# the Sokoto State ministries' own sites (mof.sk.gov.ng, mbep.sk.gov.ng, ...).
BASE_ALLOWLIST = (
    "sokotostate.gov.ng", "sk.gov.ng", "mbep.sk.gov.ng", "mof.sk.gov.ng",
    "budgetoffice.gov.ng", "nigerianstat.gov.ng",
    "worldbank.org", "documents1.worldbank.org", "reliefweb.int",
    "unicef.org", "unfpa.org", "undp.org", "dhsprogram.com",
    # humanitarian partners: displacement tracking (IOM DTM), refugees (UNHCR), humanitarian coordination (OCHA)
    "iom.int", "dtm.iom.int", "unhcr.org", "unocha.org",
)
# ... plus every verified publisher domain in data/source_registry.yaml, loaded at startup (unverified ones stay
# off until a probe and a person confirm them: scripts/probe_registry.py)
ALLOWLIST = tuple(dict.fromkeys(BASE_ALLOWLIST + tuple(registry().domains())))
BLOCKED = tuple(registry().blocked())          # probed unreachable or disallowed: never fetched

# Open-web results (docs/question-planning.md §5) are fetched without review only from these patterns: Nigerian
# government (*.gov.ng), treaty organisations (*.int: who.int, iom.int, reliefweb.int ...), the UN system's own
# domains and the World Bank. Partner-hint websites join only once they have a dated check in the registry's
# domain_checks (trusted_hint_sites). Any other domain is queued for a person (app/acquisition/review.py).
TRUSTED_SUFFIXES = ("gov.ng", "int")
TRUSTED_DOMAINS = (
    "un.org", "undp.org", "mptf.undp.org", "jointsdgfund.org", "unicef.org", "wfp.org", "ilo.org", "fao.org",
    "unfpa.org", "unhcr.org", "unocha.org", "unwomen.org", "unesco.org", "unops.org", "worldbank.org",
)
APPROVED: set[str] = set()                     # approved on the admin page; loaded from domain_reviews at startup


def _host(url: str) -> str | None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.port not in (None, 443):
        return None
    return parts.hostname.lower().rstrip(".")


def _under(host: str, domains) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def host_allowed(url: str, allowlist: tuple[str, ...] = ALLOWLIST) -> bool:
    host = _host(url)
    if host is None or _under(host, BLOCKED):     # e.g. ilostat.ilo.org: robots.txt says no
        return False
    return _under(host, allowlist) or _under(host, APPROVED)


def trusted(url: str, hint_sites: tuple[str, ...] = ()) -> bool:
    """An open-web result we may fetch without review: allowlisted, approved, or on a trusted pattern."""
    host = _host(url)
    if host is None or _under(host, BLOCKED):
        return False
    return (host_allowed(url) or _under(host, TRUSTED_DOMAINS) or _under(host, hint_sites)
            or any(host.endswith("." + s) for s in TRUSTED_SUFFIXES))


def site_of(url: str) -> str:
    """The domain a person approves: the host without 'www.'."""
    host = _host(url) or ""
    return host[4:] if host.startswith("www.") else host


def https_url(url: str) -> str:
    """Search APIs often return http:// links (World Bank pdfurl); we only fetch over https."""
    return "https://" + url[len("http://"):] if url.lower().startswith("http://") else url


def content_signals(robots_txt: str, agent: str = "kasafibot") -> dict[str, str]:
    """Content-Signal values from the groups that apply to us (our agent name or *)."""
    signals: dict[str, str] = {}
    agents: list[str] = []
    in_rules = False
    for raw in robots_txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if in_rules:                       # a User-agent after rules starts a new group
                agents, in_rules = [], False
            agents.append(value.lower())
            continue
        in_rules = True
        if key == "content-signal" and any(a == "*" or a in agent for a in agents):
            for part in value.split(","):
                if "=" in part:
                    k, v = (s.strip().lower() for s in part.split("=", 1))
                    signals[k] = v
    return signals


class Robots:
    """robots.txt cache for one acquisition run."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http
        self._cache: dict[str, tuple[urllib.robotparser.RobotFileParser, dict[str, str]] | None] = {}

    async def allowed(self, url: str) -> tuple[bool, str]:
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._cache:
            self._cache[origin] = await self._load(origin)
        entry = self._cache[origin]
        if entry is None:      # robots.txt unreadable for a reason other than 4xx: be conservative
            return False, "robots.txt unreadable"
        parser, signals = entry
        if not parser.can_fetch(USER_AGENT, url):
            return False, "disallowed by robots.txt"
        if signals.get("ai-input") == "no":
            return False, "robots.txt Content-Signal ai-input=no"
        return True, ""

    async def _load(self, origin: str) -> tuple[urllib.robotparser.RobotFileParser, dict[str, str]] | None:
        parser = urllib.robotparser.RobotFileParser(origin + "/robots.txt")
        try:
            r = await self.http.get(origin + "/robots.txt", headers={"User-Agent": USER_AGENT},
                                    follow_redirects=True, timeout=20)
        except httpx.HTTPError as e:
            log.info("robots.txt fetch failed for %s: %s", origin, type(e).__name__)
            return None
        if r.status_code in (401, 403):     # same convention as urllib.robotparser
            parser.disallow_all = True
            return parser, {}
        if 400 <= r.status_code < 500:
            parser.allow_all = True
            return parser, {}
        if 200 <= r.status_code < 300 and not r.text.strip():
            # an empty robots.txt has no rules, so it disallows nothing (HDX answers 202 with no body)
            parser.allow_all = True
            return parser, {}
        if r.status_code != 200:
            return None
        text = r.text[:512 * 1024]
        parser.parse(text.splitlines())
        return parser, content_signals(text)
