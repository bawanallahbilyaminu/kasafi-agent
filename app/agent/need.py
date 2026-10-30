"""The information need: what data a question asks for, as structured fields (docs/question-planning.md §2).

The planner's one call rewrites the message into a standalone question (using the last turns) and fills a
`need`: measures, entities, geographic level, time, operation, output shape, premises, topics. The model fills
the fields; code checks them: measure, operation and shape names from fixed lists, entities resolved against
the budget's own MDA, programme and LGA names, and a valid time. What doesn't check out is dropped and noted,
never guessed.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from app.sources.lga_names import canonical

MEASURES = (
    # budget core (approved / revised budgets, spending from the implementation reports)
    "approved", "revised", "original", "actual", "actual_ytd", "quarter_spent", "performance_pct",
    "revenue_budget", "revenue_actual", "share_of_budget", "project_count",
    # displacement (IOM DTM, UNHCR, surveys)
    "idp_count", "returnee_count", "idp_households",
    # other statistics (registry topics)
    "unemployment_rate", "underemployment_rate", "poverty_rate", "malnutrition_rate", "population",
    "other",
)
OPERATIONS = ("lookup", "breakdown", "compare", "rank", "share", "trend", "list", "explain", "verify_claim")
SHAPES = ("value", "table", "table_top_n", "text")
ENTITY_TYPES = ("state", "lga", "mda", "sub_agency", "programme", "project", "function", "economic_item",
                "revenue_line", "sector", "publisher", "other")
GEO_LEVELS = ("state", "lga", "town", "zone", "national")
SPLITS = ("personnel", "overhead", "capital", "debt", "total")
TIME_KINDS = ("latest", "year", "quarter", "range", "none")

NEED_PROMPT = (
    "NEED: also add \"need\", what data the question asks for (english_question is its standalone form): "
    "{\"measures\": [<from: " + ", ".join(MEASURES) + ">], "
    "\"entities\": [{\"type\": \"<" + "|".join(ENTITY_TYPES) + ">\", \"name\": \"<as budgets or the source "
    "print it, in English>\"}], \"geo_level\": \"<" + "|".join(GEO_LEVELS) + ">\" (the level of the figures "
    "asked for: 'which LGAs ...' is lga), \"splits\": [<" + "|".join(SPLITS) + ", for a ministry or agency's "
    "personnel / overhead / capital>], \"time\": {\"kind\": \"" + "|".join(TIME_KINDS) + "\", \"year\": YYYY, "
    "\"quarter\": 1-4, \"from\": YYYY, \"to\": YYYY}, \"operation\": \"<" + "|".join(OPERATIONS) + ">\", "
    "\"output_shape\": \"<" + "|".join(SHAPES) + ">\", \"top_n\": N, \"premises\": [\"<claims the question "
    "takes for granted, to check, e.g. 'health got more in 2026 than 2025'>\"], \"topics\": [<registry topic "
    "ids>]}. A unit inside a ministry (a board, bureau, agency, department, Government House) is a "
    "sub_agency. "
)


COLLECTIVE_LGA = re.compile(r"(?i)\b(?:lgas|local governments|local government areas|all|every|each|kananan "
                            r"hukumomi|ƙananan hukumomi)\b")


@dataclass
class Entity:
    type: str
    name: str
    resolved: str = ""        # the name as the data prints it, when found
    code: str = ""
    candidates: list[str] = field(default_factory=list)   # unresolved agency: the printed names it may be (to ask)


@dataclass
class Need:
    standalone_question: str
    measures: list[str] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    geo_level: str = "state"
    splits: list[str] = field(default_factory=list)
    time: dict = field(default_factory=lambda: {"kind": "latest"})
    operation: str = "lookup"
    output_shape: str = "value"
    top_n: int = 0
    premises: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)   # what the checks dropped (for the trace)

    def years(self) -> list[int]:
        t = self.time
        if t.get("kind") == "range" and t.get("from") and t.get("to"):
            return list(range(int(t["from"]), int(t["to"]) + 1))
        return [int(t["year"])] if t.get("year") else []


def _year(v) -> int | None:
    try:
        y = int(v)
    except (TypeError, ValueError):
        return None
    return y if 2000 <= y <= 2035 else None


def check_time(t, problems: list[str]) -> dict:
    if not isinstance(t, dict) or t.get("kind") not in TIME_KINDS:
        if t:
            problems.append(f"time {t!r} not understood; latest used")
        return {"kind": "latest"}
    out = {"kind": t["kind"]}
    if out["kind"] in ("latest", "none"):         # a year or quarter given with "latest" means nothing
        return out
    for k in ("year", "from", "to"):
        if k in t and t[k] is not None:
            if (y := _year(t[k])) is None:
                problems.append(f"time {k}={t[k]!r} is not a year")
            else:
                out[k] = y
    if t.get("quarter") is not None:
        if str(t["quarter"]).strip() in ("1", "2", "3", "4"):
            out["quarter"] = int(str(t["quarter"]).strip())
        else:
            problems.append(f"quarter {t['quarter']!r} dropped")
    if out["kind"] == "year" and "year" not in out:
        out["kind"] = "latest"
    if out["kind"] == "quarter" and "quarter" not in out:
        problems.append("a quarter without its number; latest used")
        out["kind"] = "latest"
    if out["kind"] == "range" and not ("from" in out and "to" in out and out["from"] <= out["to"]):
        problems.append("a range without both ends; latest used")
        out = {"kind": "latest"}
    # each kind keeps only its own fields: the planner sometimes fills them all ('year' with quarter 1 and
    # from/to), and a stray quarter turns an approved budget into a quarter's figure
    keep = {"year": ("year",), "quarter": ("year", "quarter"), "range": ("from", "to")}.get(out["kind"], ())
    return {"kind": out["kind"], **{k: out[k] for k in keep if k in out}}


@dataclass(frozen=True)
class Names:
    """The names entities are resolved against: the budget's MDAs and sub-agencies (with codes), programmes,
    and LGAs (budget locations and DTM's)."""
    mdas: tuple[tuple[str, str], ...] = ()          # (name, 12-digit code)
    programmes: tuple[str, ...] = ()
    lgas: tuple[str, ...] = ()


def load_names(conn) -> Names:
    mdas = conn.execute("SELECT DISTINCT name, code FROM budget_items WHERE classification IN "
                        "('administrative', 'other') AND code ~ '^[0-9]{12}$'").fetchall()
    progs = conn.execute("SELECT DISTINCT name FROM budget_items WHERE classification = 'programme'").fetchall()
    lgas = conn.execute("SELECT DISTINCT location_name FROM projects WHERE location_name NOT ILIKE '%%state wide%%'"
                        ).fetchall()
    return Names(tuple((r[0], r[1]) for r in mdas), tuple(r[0] for r in progs),
                 tuple(sorted({r[0].title() for r in lgas} | set(SOKOTO_LGAS))))


# Sokoto State's 23 LGAs (the budget prints some in capitals or with variants; DTM uses these forms)
SOKOTO_LGAS = ("Binji", "Bodinga", "Dange-Shuni", "Gada", "Goronyo", "Gudu", "Gwadabawa", "Illela", "Isa",
               "Kebbe", "Kware", "Rabah", "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South",
               "Tambuwal", "Tangaza", "Tureta", "Wamakko", "Wurno", "Yabo")


def _norm(s: str) -> str:
    """Words that tell agencies apart: no 'Ministry of', 'State', 'Sokoto', 'the', 'of', 'and', and no digits
    stuck to a word by a misprint ('Normadic Education1' -> 'normadic education'), no bracketed acronym ('(Rtv)')."""
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"(?i)\b(min(istry)?\.?( of)?|the|state|sokoto|of|for|and|affairs|&)\b", " ", s.replace("'", ""))
    s = re.sub(r"(?<=[a-z])\d+\b", "", s.lower())
    return " ".join(re.findall(r"[a-z0-9]+", s))


def _word_near(w: str, x: str) -> bool:
    """Two words of one name: equal, a misprint (normadic / nomadic), or an abbreviation (mgt / management, and a
    printed initial: 'W& Child.' / 'Women and Children')."""
    if w == x:
        return True
    if len(w) > 3 and len(x) > 3 and difflib.SequenceMatcher(None, w, x).ratio() >= 0.8:
        return True
    short, long_ = sorted((w, x), key=len)
    it = iter(long_)
    return 1 <= len(short) < len(long_) and short[0] == long_[0] and all(ch in it for ch in short)


def same_entity(asked: str, printed: str) -> bool:
    """Every word of each name matches a word of the other: the printed row is the agency asked about, not its
    parent ministry ('Agency for Nomadic Education' is not 'Ministry of Education') or a sibling."""
    a, p = _norm(asked).split(), _norm(printed).split()
    return bool(a and p) and all(any(_word_near(w, x) for x in p) for w in a) \
        and all(any(_word_near(x, w) for w in a) for x in p)


def _agency(name: str, choices: list[str]) -> tuple[str, list[str]]:
    """The one printed agency name that is the same entity as `name`, or '' and the near candidates (to ask)."""
    n = _norm(name)
    if not n:
        return "", []
    hits = sorted({c for c in choices if same_entity(name, c)})
    exact = [c for c in hits if _norm(c) == n]
    if exact or len(hits) == 1:          # one entity, perhaps printed two ways ('Min of' / 'Ministry of')
        return (exact or hits)[0], []
    if hits:
        return "", hits[:3]
    # nothing is the same agency: the closest names, only to offer them as choices
    by_norm = {_norm(c): c for c in choices}
    return "", [by_norm[k] for k in difflib.get_close_matches(n, list(by_norm), n=3, cutoff=0.75)]


def _best(name: str, choices: list[str], cutoff: float = 0.82) -> str:
    n = _norm(name)
    if not n:
        return ""
    by_norm = {_norm(c): c for c in choices}
    if n in by_norm:
        return by_norm[n]
    contains = [c for k, c in by_norm.items() if k and len(n) > 6 and n in k]     # the asked name inside a longer one
    if len(contains) == 1:
        return contains[0]
    close = difflib.get_close_matches(n, list(by_norm), n=1, cutoff=cutoff)
    return by_norm[close[0]] if close else ""


def resolve(e: Entity, names: Names) -> Entity:
    """The entity as the data prints it (or unresolved: the planner's name stays, for search)."""
    # a sector total is an administrative line too; a 'publisher' (UNDP) may be a budget unit: the strict
    # same-entity match decides
    if e.type in ("mda", "sub_agency", "sector") or (e.type == "publisher" and names.mdas):
        hit, e.candidates = _agency(e.name, sorted({m for m, _ in names.mdas}))
        if e.type == "publisher":
            e.candidates = []                # not asked about: a publisher that isn't a budget unit stays one
            e.type = "mda" if hit else e.type
        if hit:
            e.resolved = hit
            codes = sorted({c for m, c in names.mdas if _norm(m) == _norm(hit)})
            # a sub-agency's own row, not its ministry's "with its agencies" total (codes ending 00000000)
            own = [c for c in codes if not c.endswith("00000000")] if e.type == "sub_agency" else codes
            e.code = (own or codes)[0]
    elif e.type == "programme":
        e.resolved = _best(e.name, list(names.programmes))
    elif e.type == "lga":          # a known spelling first (Wamako, Sabon-Birni, Sokoto ta Arewa), then fuzzy
        e.resolved = canonical(e.name) or canonical(_best(e.name, list(names.lgas), cutoff=0.75)) \
            or _best(e.name, list(names.lgas), cutoff=0.75)
    return e


def parse_need(d, standalone: str, names: Names | None = None, topics: tuple[str, ...] = ()) -> Need:
    """The planner's `need`, checked: unknown names dropped (and noted), entities resolved, time validated."""
    problems: list[str] = []
    if not isinstance(d, dict):
        return Need(standalone, problems=["no need given"] if d else [])

    def listed(key: str, allowed) -> list[str]:
        vals = d.get(key) or []
        vals = vals if isinstance(vals, list) else [vals]
        bad = [str(v) for v in vals if str(v) not in allowed]
        if bad:
            problems.append(f"{key}: dropped {bad}")
        return list(dict.fromkeys(str(v) for v in vals if str(v) in allowed))
    entities = []
    for e in d.get("entities") or []:
        if isinstance(e, dict) and str(e.get("name") or "").strip():
            t = e.get("type") if e.get("type") in ENTITY_TYPES else "other"
            ent = Entity(t, str(e["name"]).strip()[:120])
            entities.append(resolve(ent, names) if names else ent)
    geo = d.get("geo_level") if d.get("geo_level") in GEO_LEVELS else "state"
    # "Sokoto State LGAs", "all LGAs", "local governments": every LGA of the state, not one LGA
    collective = [e for e in entities if e.type == "lga" and not e.resolved and COLLECTIVE_LGA.search(e.name)]
    if collective:
        entities = [e for e in entities if e not in collective]
        if not any(e.type == "state" for e in entities):
            entities.insert(0, Entity("state", "Sokoto", "Sokoto"))
        geo = "lga"
    op = d.get("operation") if d.get("operation") in OPERATIONS else "lookup"
    shape = d.get("output_shape") if d.get("output_shape") in SHAPES else ("table_top_n" if op == "rank" else "value")
    try:
        top_n = max(0, min(int(d.get("top_n") or 0), 50))
    except (TypeError, ValueError):
        top_n = 0
    if op == "rank" and not top_n:
        top_n = 5
    return Need(standalone, measures=listed("measures", MEASURES), entities=entities, geo_level=geo,
                splits=listed("splits", SPLITS), time=check_time(d.get("time"), problems), operation=op,
                output_shape=shape, top_n=top_n,
                premises=[str(p)[:200] for p in (d.get("premises") or []) if str(p).strip()][:3],
                topics=listed("topics", topics) if topics else [], problems=problems)


_names: Names | None = None


def names_for(conn) -> Names:
    """The entity names, loaded once per process from the open connection (they change only when a budget is
    indexed)."""
    global _names
    if _names is None:
        try:
            _names = load_names(conn)
        except Exception:        # no database (tests) or a query problem: no resolution, try again next time
            conn.rollback() if hasattr(conn, "rollback") else None
            return Names()
    return _names
