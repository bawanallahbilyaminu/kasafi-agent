"""One rule for every shortcut that answers before or instead of the planner (docs/routing.md): a shortcut fires
only on unambiguous intent for its own feature, and a question that names a publisher, a survey or a report goes
to the planner and the document path, whatever facility, place or hazard words it also contains. The planner may
then add facility, hazard or place data as a supplement; the report answers the question.

Two live misroutes on 1 Nov 2026 were of this class: "What did UNFPA find out about health facilities in Wamakko"
got a facility card for "Wamakko Primary Health Center" (the name lookup matched the LGA and a facility word), and
"which 10 LGAs get most IDPs" had earlier gone to ward greenness. The emergency fast path stays first, unchanged.
"""

from __future__ import annotations

import re
from functools import lru_cache

# publishers, surveys and reports a question can name; the registry's publisher names are added at import
_FIXED_SOURCES = {
    "unfpa", "unicef", "who", "undp", "unhcr", "unocha", "ocha", "iom", "dtm", "wfp", "fao", "usaid", "fcdo", "giz",
    "msf", "oxfam", "jips", "drc", "nrc", "reach", "world bank", "worldbank", "nbs", "sbs", "npc", "nphcda", "ncdc",
    "nimet", "nihsa", "nema", "sema", "ophi", "mics", "ndhs", "dhs", "nlfs", "nlss", "mpi", "cpi", "emonc", "sftas",
    "neiti", "ubec", "nmcp", "naca", "fews", "fewsnet", "iati", "ilo", "ifad", "grid3", "smart", "nassco", "nassp",
    "hukumar kididdiga", "hukumar ƙididdiga", "ma'aikatar lafiya ta duniya", "bankin duniya", "majalisar dinkin duniya",
    "majalisar ɗinkin duniya",
}
_NOT_SOURCES = {"net", "pres", "idp", "lga", "hiv", "asc", "aop", "fct", "education", "lga", "scp", "sdg", "pfm", "hac",
                "igr", "mof", "moh", "dmo", "impact", "smart", "ube", "mbep"}      # everyday words or too short

# "according to X", "what did X find / say / report / show", "the X report / survey / assessment / study"
SOURCE_PHRASE = re.compile(
    r"(?i)\b(?:according\s+to|as\s+per|per\s+the|based\s+on\s+the|a\s+cewar|bisa\s+ga|kamar\s+yadda)\b"
    r"|\bwhat\s+(?:did|does|do|has|have)\b.{0,60}\b(?:find|found|say|says|said|report|reported|show|shows|showed|"
    r"conclude|concluded|recommend|recommended|estimate|estimated|state|stated)\b"
    r"|\b(?:findings?|finding\s+out)\s+(?:of|from|by)\b"
    r"|\b(?:report|survey|assessment|study|bulletin|census|index|dashboard|factsheet|fact\s+sheet|situation\s+report|"
    r"sitrep|evaluation|audit|review)\b"
    r"|\b(?:rahoto\w*|bincike\w*|ƙidaya\w*|kidaya\w*|bayanan\s+hukuma|ya\s+ce|ta\s+ce|sun\s+ce|suka\s+ce|ya\s+gano|"
    r"ta\s+gano|sun\s+gano|suka\s+gano|ya\s+nuna|ta\s+nuna|sun\s+nuna)\b")

# the question's own words that make a facility shortcut unambiguous
NAMED_FACILITY_INTENT = re.compile(
    r"(?i)\b(?:where\s+is|where's|where\s+can\s+i\s+find|how\s+far|how\s+do\s+i\s+get\s+to|directions?\s+to|"
    r"route\s+to|go\s+to|get\s+to|going\s+to|take\s+me\s+to|is\s+.{1,60}\s+open|opening\s+hours|what\s+about|"
    r"tell\s+me\s+about|about\s+the|details\s+of|information\s+(?:on|about)|is\s+there\s+(?:a|an)|does\s+.{1,60}"
    r"\s+(?:have|offer|do)|ina\b|a\s+ina|yaya\s+nisan|nisan|zuwa|ina\s+son\s+zuwa|a\s+buɗe|a\s+bude|game\s+da|"
    r"akwai|shin\s+.{1,60}\s+(?:na|tana|yana))\b")


@lru_cache(maxsize=1)
def source_names() -> tuple[str, ...]:
    """Every publisher name the registry and the fixed list know, longest first."""
    names = set(_FIXED_SOURCES)
    try:
        from app.acquisition.registry import registry
        from app.agent.topics import publisher_names
        for t in registry().topics.values():
            for p in t.publishers:
                names |= {n for n in publisher_names(p) if n not in _NOT_SOURCES and len(n) >= 3}
    except Exception:              # noqa: BLE001 - the registry file missing (tests): the fixed list serves
        pass
    return tuple(sorted(names, key=len, reverse=True))


@lru_cache(maxsize=1)
def _source_re() -> re.Pattern:
    alts = "|".join(re.escape(n) for n in source_names())
    return re.compile(rf"(?i)(?<![\w'ƙɓɗƴ])(?:{alts})(?![\w'ƙɓɗƴ])")


def names_a_source(text: str) -> str:
    """The publisher, survey or report the text names ('UNFPA', 'MICS', 'World Bank'), or ''. Short names count
    only in capitals ('WHO' is a publisher; 'who' is a question word)."""
    for m in _source_re().finditer(text or ""):
        word = m.group(0)
        if len(word) <= 4 and " " not in word and not word.isupper() and word.lower() not in ("mics", "ndhs", "nlfs"):
            continue
        return word
    return ""


def document_question(text: str) -> bool:
    """A question that goes to the planner and the document path whatever else it contains: it names a publisher,
    a survey or a report, or asks what one found, says or reports."""
    t = text or ""
    return bool(names_a_source(t) or SOURCE_PHRASE.search(t))


def own_source(text: str, own: tuple[str, ...]) -> bool:
    """The only source the text names is the route's own data source (NCDC for outbreak tables, NiMet and NIHSA
    for the outlooks): the route may still answer."""
    found = {m.group(0).lower() for m in _source_re().finditer(text or "")}
    found = {f for f in found if len(f) > 4 or " " in f or f in ("mics", "ndhs", "nlfs") or f.upper() in (text or "")}
    return bool(found) and found <= {o.lower() for o in own}


def facility_intent(text: str) -> bool:
    """A named-facility shortcut (the registry card or the route to it) needs the question's own words to ask
    about a place: where it is, how far, directions, is it open, what about it."""
    return bool(NAMED_FACILITY_INTENT.search(text or ""))
