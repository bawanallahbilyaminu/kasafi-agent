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

log = logging.getLogger(__name__)

# Honest identification: robots.txt rules are matched on the "KasafiBot" token, and the URL explains who we are.
USER_AGENT = "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"

# Keep in sync with data/manifest.json "allowlist_domains" (tests check). sk.gov.ng covers the
# Sokoto State ministries' own sites (mof.sk.gov.ng, mbep.sk.gov.ng, ...).
ALLOWLIST = (
    "sokotostate.gov.ng", "sk.gov.ng", "mbep.sk.gov.ng", "mof.sk.gov.ng",
    "budgetoffice.gov.ng", "nigerianstat.gov.ng",
    "worldbank.org", "documents1.worldbank.org", "reliefweb.int",
    "unicef.org", "unfpa.org", "undp.org", "dhsprogram.com",
)


def host_allowed(url: str, allowlist: tuple[str, ...] = ALLOWLIST) -> bool:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.port not in (None, 443):
        return False
    host = parts.hostname.lower().rstrip(".")
    return any(host == d or host.endswith("." + d) for d in allowlist)


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
        if r.status_code != 200:
            return None
        text = r.text[:512 * 1024]
        parser.parse(text.splitlines())
        return parser, content_signals(text)
