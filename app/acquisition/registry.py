"""The source registry (data/source_registry.yaml): for each topic, who publishes trustworthy figures for Sokoto,
on which domains, how to find their documents and how often they publish.

It is the single source of truth for the fetch allowlist (app/acquisition/policy.py adds every verified
publisher domain to the fixed base list), for topic detection (English and Hausa synonyms), and for multi-source
answers (app/agent/topics.py). A publisher marked `verified: "no"` was added from general knowledge: its domains
stay off the allowlist until a probe (scripts/probe_registry.py) and a person confirm them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "source_registry.yaml"

LEVEL_RANK = {"lga": 0, "town": 0, "state": 1, "zone": 2, "national": 3}


@dataclass(frozen=True)
class Publisher:
    id: str
    name: str
    domains: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()
    doc_types: tuple[str, ...] = ()
    level: str = ""                # lga | town | state | zone | national (finest geography it reports)
    tier: int = 3                  # 1 official / primary data, 2 analysis citing it, 3 related context
    cadence: str = ""
    latest_known: str = ""
    discovery: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    scope_note: str = ""           # e.g. "covers Sokoto town only": said whenever it is quoted
    definition_note: str = ""      # e.g. the NBS labour definitions: always shown with its figures
    note: str = ""
    verified: str = ""

    @property
    def is_verified(self) -> bool:
        return self.verified.lower() not in ("", "no")

    @property
    def level_rank(self) -> int:
        return LEVEL_RANK.get(self.level.split()[0].strip(" (;,").lower(), 4) if self.level else 4


@dataclass(frozen=True)
class Topic:
    id: str
    synonyms_en: tuple[str, ...]
    synonyms_ha: tuple[str, ...]
    answer_pattern: str
    publishers: tuple[Publisher, ...]
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class Channel:
    id: str
    what: str
    type: str = ""                 # catalog_crawl: list the publisher's own documents directly
    site: str = ""
    endpoint: str = ""
    download_pattern: str = ""
    auth: str = ""
    use_for: tuple[str, ...] = ()
    verified: str = ""


@dataclass(frozen=True)
class Registry:
    version: int
    topics: dict[str, Topic]
    channels: dict[str, Channel]
    global_exclude: tuple[str, ...] = ()
    _all: tuple[Publisher, ...] = field(default=(), repr=False)
    domain_checks: dict[str, str] = field(default_factory=dict)   # domain -> probe date | unreachable | disallowed

    def publishers(self) -> list[Publisher]:
        return list(self._all)

    def blocked(self) -> list[str]:
        """Domains probed as unreachable or disallowed by robots.txt: never fetched, even under an allowlisted
        parent (ilostat.ilo.org under ilo.org)."""
        return [d for d, v in self.domain_checks.items() if v in ("unreachable", "disallowed")]

    def domains(self, *, verified_only: bool = True) -> list[str]:
        """Every publisher's and catalog channel's domains (verified ones only, by default): a verified publisher's
        or a dated domain check's; blocked domains never."""
        checked = {d for d, v in self.domain_checks.items() if re.match(r"\d{4}-\d\d-\d\d", v)}
        out = [d for p in self._all if p.is_verified or not verified_only or set(p.domains) & checked
               for d in p.domains if not verified_only or p.is_verified or d in checked]
        out += [_host(c.site) for c in self.channels.values()
                if c.site and (c.verified.lower() not in ("", "no") or not verified_only)]
        blocked = set(self.blocked()) if verified_only else set()
        return list(dict.fromkeys(d.lower() for d in out if d and d.lower() not in blocked))

    def unverified_domains(self) -> list[str]:
        verified = set(self.domains())
        return [d for d in self.domains(verified_only=False) if d not in verified]

    def publisher_for(self, url: str) -> Publisher | None:
        """The registry publisher a document URL belongs to: its own listed URL first, then its domain (the
        most specific publisher wins: a primary source before a partner that shares its domain)."""
        if not url:
            return None
        for p in self._all:
            if url in p.urls:
                return p
        host = _host(url)
        hits = [p for p in self._all if any(host == d or host.endswith("." + d) for d in p.domains)]
        return min(hits, key=lambda p: (p.tier, len(p.domains))) if hits else None


def _host(url: str) -> str:
    return re.sub(r"^https?://", "", url or "").split("/")[0].lower()


def _t(v) -> tuple[str, ...]:
    if v is None:
        return ()
    return tuple(str(x) for x in v) if isinstance(v, list) else (str(v),)


def _publisher(d: dict) -> Publisher:
    return Publisher(id=str(d["id"]), name=str(d.get("name") or d["id"]), domains=_t(d.get("domains")),
                     urls=_t(d.get("urls")), doc_types=_t(d.get("doc_types")), level=str(d.get("level") or ""),
                     tier=int(d.get("tier") or 3), cadence=str(d.get("cadence") or ""),
                     latest_known=str(d.get("latest_known") or ""), discovery=_t(d.get("discovery")),
                     exclude=_t(d.get("exclude")), scope_note=str(d.get("scope_note") or ""),
                     definition_note=str(d.get("definition_note") or ""), note=str(d.get("note") or ""),
                     verified=str(d.get("verified") or ""))


def parse_registry(text: str) -> Registry:
    raw = yaml.safe_load(text) or {}
    topics, every = {}, {}
    for tid, t in (raw.get("topics") or {}).items():
        pubs = tuple(_publisher(p) for p in t.get("publishers") or [])
        for p in pubs:
            every.setdefault(p.id, p)
        topics[tid] = Topic(tid, _t(t.get("synonyms_en")), _t(t.get("synonyms_ha")),
                            str(t.get("answer_pattern") or ""), pubs, _t(t.get("exclude")))
    channels = {str(c["id"]): Channel(str(c["id"]), str(c.get("what") or ""), str(c.get("type") or ""),
                                      str(c.get("site") or ""), str(c.get("endpoint") or ""),
                                      str(c.get("download_pattern") or ""), str(c.get("auth") or ""),
                                      _t(c.get("use_for")), str(c.get("verified") or ""))
                for c in raw.get("discovery_channels") or []}
    checks = {str(d).lower(): str(v) for d, v in (raw.get("domain_checks") or {}).items()}
    return Registry(int(raw.get("version") or 0), topics, channels, _t(raw.get("global_exclude")),
                    tuple(every.values()), checks)


@lru_cache(maxsize=1)
def registry(path: str = str(REGISTRY_PATH)) -> Registry:
    """The registry, loaded once (an empty one if the file is missing, so the app still runs)."""
    p = Path(path)
    return parse_registry(p.read_text(encoding="utf-8")) if p.exists() else Registry(0, {}, {})


def _pattern(words: tuple[str, ...]) -> re.Pattern | None:
    words = tuple(w for w in words if w.strip())
    if not words:
        return None
    alts = "|".join(re.escape(w.lower()).replace("\\ ", r"\s+") for w in sorted(words, key=len, reverse=True))
    return re.compile(rf"(?<![\w'])(?:{alts})(?![\w])", re.I)


def detect_topic(text: str, reg: Registry | None = None) -> str:
    """The topic whose English or Hausa synonyms the text names, the one named most; '' for none (the planner's
    topic is the fallback). Apostrophes are normalised (’ and ' are one)."""
    reg = reg or registry()
    norm = text.replace("’", "'").replace("‘", "'")
    best, most = "", 0
    for t in reg.topics.values():
        pat = _pattern(t.synonyms_en + t.synonyms_ha)
        n = len(pat.findall(norm)) if pat else 0
        if n > most:
            best, most = t.id, n
    return best
