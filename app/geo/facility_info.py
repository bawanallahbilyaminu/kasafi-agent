"""Health facilities as a capability every question can use (docs/hazard-and-services.md section 6), from the GRID3 /
NHFR registry in PostGIS:

- count and list by type, ownership, level, LGA or ward ("How many PHCs are in Sokoto?": the registry's figure; the
  UNFPA EmONC assessment's is offered as the facilities it assessed, a different thing);
- look a facility up by name, fuzzily ("What about Arkilla PHC"): its type, level, ownership, ward and LGA, and its
  EmONC status (a link used only when exact or confirmed, as decided);
- the facility a question is about, for "I want to go to Arkilla PHC" / "How far is it from me?" (the route itself
  is app/geo/facilities.py).
No model is used.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from app.geo import WARD_EDGE_M
from app.geo.corrections import checked_on
from app.sources.lga_names import name_of

ABBREV = [(r"\bphcs?\b", "primary health centre"), (r"\bphcc\b", "primary health care centre"),
          (r"\bghs?\b", "general hospital"), (r"\bhc\b", "health clinic"), (r"\bhps?\b", "health post"),
          (r"\bmch\b", "maternal and child health"), (r"\bcenter\b", "centre"), (r"\bclinc\b", "clinic"),
          (r"\basibitin\b", "hospital"), (r"\basibiti\b", "hospital")]
GENERIC = {"general", "hospital", "primary", "health", "centre", "care", "clinic", "post", "dispensary", "maternal",
           "and", "child", "comprehensive", "the", "of", "model", "town", "township", "specialist", "upgraded",
           "federal", "state", "lowcost", "low", "cost", "teaching", "specialized", "centres"}
# words of the question that aren't the facility's name
ASKING = re.compile(r"(?i)\b(?:what|about|tell|me|where|is|the|a|an|i|want|to|go|going|get|take|how|far|it|from|"
                    r"which|in|at|of|info|information|details|show|directions?|route|distance|near|ina|son|zuwa|"
                    r"yaya|nisan|nisa|game|da|gaya|min|mini|kai|ni|a|ta|ga|lga|ward|sokoto)\b")
ROUTE_TO = re.compile(r"(?i)\b(?:go to|get to|going to|take me|directions? to|route to|how far|distance to|"
                      r"from me|zuwa|ina son zuwa|yaya nisan|nisan)\b")


def norm(name: str) -> str:
    s = (name or "").lower().replace("’", "'")
    for pat, rep in ABBREV:
        s = re.sub(pat, rep, s)
    return " ".join(re.findall(r"[a-z0-9]+", s))


def own_words(name: str) -> list[str]:
    """The facility's own place words ('Arkilla'), without its kind ('Primary Health Centre')."""
    return [w for w in norm(name).split() if w not in GENERIC and len(w) > 2]


@dataclass
class Registered:
    fid: str
    name: str
    level: str
    kind: str
    ownership: str
    ward: str
    lga: str                # from the point (COD-AB)
    lga_attr: str           # the file's own
    lat: float
    lon: float
    emonc: str = ""         # cemonc | bemonc, when the link is exact or confirmed
    score: float = 0.0
    checked: str = ""       # the date a person checked its location (app/geo/corrections.py)
    ward_likely: bool = False   # within ~300 m of its ward's border (app/geo.WARD_EDGE_M): "likely ... ward"


def _rows(conn, where: str = "TRUE", args: tuple = ()) -> list[Registered]:
    return [Registered(r[0], r[1], r[2] or "", (r[3] or "").replace("\xa0", " "), r[4] or "", r[5] or "", r[6] or "",
                       r[7] or "", r[8], r[9], r[10] or "", checked=checked_on(r[11]),
                       ward_likely=r[12] is not None and r[12] < WARD_EDGE_M) for r in conn.execute(
        "SELECT f.fid, f.name, f.level, f.level_option, f.ownership, coalesce(w.name, f.ward_attr), l.name, "
        "f.lga_attr, ST_Y(f.geom), ST_X(f.geom), (SELECT CASE WHEN bool_or(c.capability = 'cemonc') THEN 'cemonc' "
        "ELSE 'bemonc' END FROM facility_capability c WHERE c.fid = f.fid AND (c.confirmed OR c.score >= 1.0)), "
        "f.correction, ST_Distance(ST_Boundary(w.geom)::geography, f.geom::geography) "
        "FROM facility f LEFT JOIN lga l ON l.pcode = f.lga_pcode LEFT JOIN ward w ON w.wardcode = f.ward_code "
        f"WHERE f.geom IS NOT NULL AND NOT f.hidden AND {where}", args).fetchall()]


def find_by_name(conn, text: str, lga_pcodes: list[str] | None = None) -> list[Registered]:
    """The facilities the text names, best first (empty when none fits): every one of a facility's own place words
    is in the text (allowing small misspellings), the kind the text says ('PHC') breaking ties."""
    said = norm(ASKING.sub(" ", text or ""))
    words = said.split()
    if not words:
        return []
    kinds = {w for w in words if w in GENERIC}
    out = []
    where, args = ("f.lga_pcode = ANY(%s)", (lga_pcodes,)) if lga_pcodes else ("TRUE", ())
    for f in _rows(conn, where, args):
        own = own_words(f.name)
        if not own:
            continue
        hits = [max((difflib.SequenceMatcher(None, o, w).ratio() for w in words), default=0) for o in own]
        if min(hits) < 0.85:
            continue
        kind_fit = len(kinds & set(norm(f.name).split())) / max(len(kinds), 1) if kinds else 0.5
        f.score = round(sum(hits) / len(hits) * 0.8 + kind_fit * 0.2, 3)
        out.append(f)
    return sorted(out, key=lambda f: -f.score)


# --- counts ----------------------------------------------------------------------------------------------------

COUNT_Q = re.compile(r"(?i)\b(?:how many|number of|count of|nawa|guda nawa|adadin|list (?:all|the)?)\b")
KINDS = (  # (pattern, label key, SQL condition)
    (r"\b(?:phcs?|primary health cent(?:er|re)s?)\b", "phc", "f.level_option = 'Primary Health Center'"),
    (r"\bhealth posts?\b", "post", "f.level_option = 'Health Post'"),
    (r"\b(?:primary health )?clinics?\b", "clinic", "f.level_option = 'Primary Health Clinic'"),
    (r"\bgeneral hospitals?\b", "general", "f.level_option = 'General Hospital'"),
    (r"\b(?:hospitals?|asibitoci|asibiti)\b", "hospital",
     "(f.level IN ('Secondary', 'Tertiary') OR f.level_option ILIKE '%%hospital%%')"),
    (r"\b(?:health facilit\w*|facilit\w*|cibiyoyin lafiya|cibiyar lafiya)\b", "all", "TRUE"),
)
OWNERSHIP = ((r"\b(?:government|public|gwamnati)\b", "Public"), (r"\b(?:private|masu zaman kansu)\b", "Private"))

W = {
    "en": {"phc": "Primary Health Centres", "post": "health posts", "clinic": "primary health clinics",
           "general": "general hospitals", "hospital": "hospitals (general, specialist and teaching)",
           "all": "health facilities", "Public": "government", "Private": "private",
           "count": "{place} has *{n:,} {own}{what}* in the facility registry.",
           "also": "All primary-level facilities (health posts, clinics and centres): {n:,}.",
           "by_lga": "Most in: {top}.",
           "emonc": "The UNFPA EmONC assessment gives a different figure: the facilities it assessed, not all of "
                    "them. Reply “EmONC” to see it.",
           "source": "📄 GRID3 Nigeria / NHFR facility registry (updated Nov 2024)",
           "state": "Sokoto State", "lga": "{lga} LGA", "ward": "{ward} ward ({lga} LGA)",
           "card": "*{name}*: {kind}, {level} level, {own}; {likely}in {ward} ward, {lga} LGA{differs}.",
           "likely": "likely ",
           "differs": " (the registry lists it under {attr})",
           "emonc_yes": "In the UNFPA EmONC assessment: {cap}.",
           "emonc_no": "Not linked to the UNFPA EmONC assessment's list.",
           "caps": {"cemonc": "comprehensive emergency obstetric and newborn care (CEmONC)",
                    "bemonc": "basic emergency obstetric and newborn care (BEmONC)"},
           "levels": {"Primary": "primary", "Secondary": "secondary", "Tertiary": "tertiary"},
           "own_kinds": {"Public": "government", "Private": "private", "Unknown": "ownership not recorded",
                         "": "ownership not recorded"},
           "more": "Others with that name: {names}.",
           "caution": "Kasafi can't confirm opening hours or services; call ahead if you can.",
           "go": "Reply “how far is it” for the road distance and directions."},
    "ha": {"phc": "Cibiyoyin Kiwon Lafiya na Farko (PHC)", "post": "ƙananan cibiyoyi (health posts)",
           "clinic": "asibitocin shan magani na farko", "general": "manyan asibitoci (general hospitals)",
           "hospital": "asibitoci (manyan asibitoci, na ƙwararru da na koyarwa)", "all": "cibiyoyin lafiya",
           "Public": "na gwamnati", "Private": "masu zaman kansu",
           "count": "{place} tana da *{what}{own} {n:,}* a rajistar cibiyoyin lafiya.",
           "also": "Duka cibiyoyin matakin farko (health posts, clinics da centres): {n:,}.",
           "by_lga": "Mafi yawa a: {top}.",
           "emonc": "Binciken EmONC na UNFPA yana da wani adadi daban: cibiyoyin da ya bincika, ba duka ba. "
                    "Rubuta “EmONC” don gani.",
           "source": "📄 Rajistar cibiyoyin lafiya ta GRID3 Nigeria / NHFR (an sabunta Nuwamba 2024)",
           "state": "Jihar Sokoto", "lga": "Ƙaramar Hukumar {lga}", "ward": "Mazaɓar {ward} (Ƙaramar Hukumar {lga})",
           "card": "*{name}*: {kind}, matakin {level}, {own}; {likely}a mazaɓar {ward}, Ƙaramar Hukumar {lga}{differs}.",
           "likely": "wataƙila ",
           "differs": " (rajistar ta sanya ta a {attr})",
           "emonc_yes": "A binciken EmONC na UNFPA: {cap}.",
           "emonc_no": "Ba a haɗa ta da jerin binciken EmONC na UNFPA ba.",
           "caps": {"cemonc": "cikakkiyar kulawar gaggawa ta haihuwa da jarirai (CEmONC)",
                    "bemonc": "kulawar gaggawa ta haihuwa da jarirai ta asali (BEmONC)"},
           "levels": {"Primary": "farko", "Secondary": "na biyu", "Tertiary": "na uku"},
           "own_kinds": {"Public": "ta gwamnati", "Private": "mai zaman kanta", "Unknown": "ba a rubuta mallaka ba",
                         "": "ba a rubuta mallaka ba"},
           "more": "Wasu masu wannan suna: {names}.",
           "caution": "Kasafi ba zai iya tabbatar da lokutan buɗewa ko ayyuka ba; ka kira kafin ka je idan za ka iya.",
           "go": "Rubuta “yaya nisanta” don nisan hanya da kwatance."},
}


PROJECT = re.compile(r"(?i)\b(?:buil[dt]\w*|construct\w*|renovat\w*|upgrad\w*|equip\w*|projects?|budget\w*|"
                     r"allocat\w*|spen[dt]\w*|naira|kasafi\w*|kuɗi|kudi|gina|20\d\d)\b")


def is_count(text: str) -> bool:
    """'How many PHCs are in Sokoto?': a count from the registry; 'how many hospitals were built in 2025?' is a
    projects question, not this."""
    t = text or ""
    return bool(COUNT_Q.search(t) and any(re.search(rf"(?i){p}", t) for p, _, _ in KINDS) and not PROJECT.search(t))


def count_answer(conn, text: str, lang: str = "en") -> str:
    """How many facilities of a kind (and ownership) in the state, an LGA or a ward, from the registry."""
    from app.hazards.advisories import lgas_in
    w = W.get(lang, W["en"])
    key, cond = next(((k, c) for p, k, c in KINDS if re.search(rf"(?i){p}", text)), ("all", "TRUE"))
    own = next((o for p, o in OWNERSHIP if re.search(rf"(?i){p}", text)), "")
    where, args, place = [cond, "NOT f.hidden"], [], w["state"]
    if own:
        where.append("f.ownership = %s")
        args.append(own)
    ward = next((r for r in conn.execute("SELECT wardcode, name, lga_pcode FROM ward").fetchall()
                 if re.search(rf"(?i)\b{re.escape(r[1])}\b\s+ward|\bmazaɓar\s+{re.escape(r[1])}\b", text)), None)
    lgas = lgas_in(text)
    if ward:
        where.append("f.ward_code = %s")
        args.append(ward[0])
        place = w["ward"].format(ward=ward[1], lga=name_of(ward[2]))
    elif lgas:
        where.append("f.lga_pcode = ANY(%s)")
        args.append(lgas)
        place = ", ".join(w["lga"].format(lga=name_of(c)) for c in lgas)
    sql = " AND ".join(where)
    n = conn.execute(f"SELECT count(*) FROM facility f WHERE {sql}", tuple(args)).fetchone()[0]
    own_word = (f"{w[own]} " if lang != "ha" else f" {w[own]}") if own else ""
    lines = [w["count"].format(place=place, n=n, what=w[key], own=own_word)]
    if key == "phc":
        prim = conn.execute("SELECT count(*) FROM facility f WHERE f.level = 'Primary' AND NOT f.hidden AND "
                            + " AND ".join(where[1:] or ["TRUE"]), tuple(args)).fetchone()[0]
        lines.append(w["also"].format(n=prim))
    if not lgas and not ward and n:
        top = conn.execute(f"SELECT l.name, count(*) FROM facility f JOIN lga l ON l.pcode = f.lga_pcode WHERE {sql} "
                           "GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 3", tuple(args)).fetchall()
        lines.append(w["by_lga"].format(top=", ".join(f"{name} ({k})" for name, k in top)))
    lines += ["", w["emonc"], "", w["source"]]
    return "\n".join(lines)


def lookup(settings, text: str) -> list[Registered]:
    """find_by_name from its own connection (for the conversation, in a thread)."""
    import psycopg

    from app.hazards.advisories import lgas_in
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        return find_by_name(conn, text, lgas_in(text) or None)


def counted(settings, text: str, lang: str) -> str:
    import psycopg
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        return count_answer(conn, text, lang)


def as_facility(r: Registered, lat: float | None = None, lon: float | None = None):
    """The registry row as app.geo.facilities.Facility (for routes and maps), its straight-line km from a point."""
    from app.geo.facilities import Facility, _sphere_km
    km = round(_sphere_km(lat, lon, r.lat, r.lon), 2) if lat is not None else 0.0
    return Facility(r.fid, r.name, r.level, r.kind, r.ownership, "", r.lat, r.lon, r.lga, r.lga_attr, km, r.emonc,
                    checked=r.checked)


NAMED = 0.9               # a lookup this sure is the facility the question names


def card(f: Registered, lang: str = "en", others: list[Registered] | None = None) -> str:
    """One facility from the registry: kind, level, ownership, ward and LGA, and its EmONC status."""
    from app.sources.lga_names import canonical
    w = W.get(lang, W["en"])
    differs = w["differs"].format(attr=f.lga_attr) if f.lga_attr and canonical(f.lga_attr) != canonical(f.lga) else ""
    from app.geo.facilities import checked_text
    lines = [w["card"].format(name=f.name, kind=f.kind or "-", level=w["levels"].get(f.level, f.level.lower()),
                              own=w["own_kinds"].get(f.ownership, f.ownership), ward=f.ward or "-", lga=f.lga,
                              differs=differs, likely=w["likely"] if f.ward_likely else "") + checked_text(lang if lang in ("en", "ha") else "en", f),
             w["emonc_yes"].format(cap=w["caps"][f.emonc]) if f.emonc else w["emonc_no"]]
    if others:
        lines.append(w["more"].format(names="; ".join(f"{o.name} ({o.lga})" for o in others[:3])))
    lines += ["", w["go"], w["caution"], "", w["source"]]
    return "\n".join(lines)
