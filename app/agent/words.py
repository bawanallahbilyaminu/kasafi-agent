"""What the question's words settle on their own (docs/planner-variance.md, fix 1): the period and so the
report, the measures (spent / revised / approved / performance), the splits named (personnel, overhead,
capital), the publishers named with "according to" and a change asked, and a named budget line. Read in code,
in English, Hausa and code-switched wording, and enforced on the planner's plan only when a pattern is clear.
Absent patterns leave the plan as it is; patterns that contradict each other are *conflicts*, left to the
second-opinion plan (fix 5, app/agent/answer.py). Every override and every conflict is written to the plan's
`words` record (field names and values only, never the message text) and so to the trace.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.agent.periods import Period, asked_period, asked_quarters

# --- measures ----------------------------------------------------------------------------------------------------------
SPENT = re.compile(r"(?i)\b(?:spent|spend(?:ing)?\s+(?:so\s+far|to\s+date|by)|actual(?:ly)?\s+(?:spent|expend\w*)|"
                   r"actual\s+expenditure|expended|disbursed|utili[sz]ed|kashe\w*|aka\s+kashe|ta\s+kashe|ya\s+kashe|"
                   r"an\s+kashe|suka\s+kashe|kuɗin\s+da\s+aka\s+kashe)\b")
REVISED = re.compile(r"(?i)\b(?:revised|amended|supplementary|kasafin\s+da\s+aka\s+(?:sabunta|gyara)|"
                     r"(?:da\s+)?aka\s+(?:sabunta|gyara)|sabunta\w*|gyara\w*\s+kasafi)\b")
APPROVED = re.compile(r"(?i)\b(?:approved|budgeted|allocat\w*|appropriat\w*|aka\s+ware|an\s+ware|ware\s+wa|"
                      r"aka\s+amince|an\s+amince|amince\w*)\b")
PERFORMANCE = re.compile(r"(?i)\b(?:performance|percent(?:age)?\s+(?:spent|of|performance)|"
                         r"share\s+(?:spent|of\s+(?:the|its|their|his|her))|kashi\s+nawa|yawan\s+kashi|%\s*(?:of|na))\b|\b\d+\s*%")
AGAINST = re.compile(r"(?i)\b(?:against|compared?\s+(?:with|to)|versus|vs\.?|relative\s+to|out\s+of|idan\s+aka\s+"
                     r"(?:kwatanta|duba)\s+da|a\s+kan|daga\s+cikin)\b")
# --- splits --------------------------------------------------------------------------------------------------------------
SPLIT_WORDS = [
    ("personnel", re.compile(r"(?i)\b(?:personnel|salar(?:y|ies)|wages|staff\s+costs?|albashi|ma'?aikata|kuɗin\s+albashi)\b")),
    ("overhead", re.compile(r"(?i)\b(?:overheads?|running\s+costs?|gudanarwa|kuɗin\s+gudanarwa|tafiyar\s+da\s+aiki)\b")),
    ("capital", re.compile(r"(?i)\b(?:capital|projects?\s+spending|jari|kuɗin\s+jari|ayyukan\s+raya\s+ƙasa)\b")),
    ("debt", re.compile(r"(?i)\b(?:debt\s+(?:service|repayment|servicing)|bashi|biyan\s+bashi)\b")),
]
# --- publishers and change --------------------------------------------------------------------------------------------------
ACCORDING = re.compile(r"(?i)\b(?:according\s+to|as\s+(?:per|reported\s+by|stated\s+by|published\s+by)|per|from|"
                       r"compared\s+(?:with|to)|against|a\s+cewar|bisa\s+ga(?:\s+(?:rahoton|bayanin|alƙaluman|alkaluman))?|"
                       r"bisa\s+(?:rahoton|bayanin|alƙaluman|alkaluman)|daga\s+(?:rahoton|bayanin|alƙaluman|alkaluman)|"
                       r"idan\s+aka\s+kwatanta\s+da(?:\s+na)?|in\s+(?:the\s+)?words\s+of)\s+(?:the\s+)?"
                       r"([A-Z][A-Za-z&'’. -]{1,60}?|[A-Z]{2,6})"
                       r"(?=[,.;:?!]|\s+(?:menene|nawa|what|how|the|was|is|were|in|a|ya|ta|sun|suka|kuma|and|\d)|$)")
CHANGE = re.compile(r"(?i)\b(?:improv\w*|chang\w*|increas\w*|decreas\w*|fell|rose|risen|dropp?\w*|declin\w*|"
                    r"worsen\w*|better|worse|difference|differ\w*|ya\s+inganta|ta\s+inganta|sun\s+inganta|ya\s+ragu|"
                    r"ta\s+ragu|ya\s+ƙaru|ya\s+karu|ta\s+ƙaru|ya\s+canza|ta\s+canza|ya\s+tashi|ya\s+sauka|ya\s+gyaru|"
                    r"bambanci|an\s+samu\s+ci\s+gaba)\b")
PUBLISHER_ALIASES = {         # short name -> the registry publisher ids it may mean (app/acquisition/registry.py)
    "nbs": ("nbs_mpi", "nbs_nlfs", "nbs_nlss_poverty", "nbs_cpi"), "national bureau of statistics": ("nbs_mpi", "nbs_nlfs"),
    "sbs": ("sokoto_mpi", "sokoto_sbs"), "sokoto state bureau of statistics": ("sokoto_mpi", "sokoto_sbs"),
    "state bureau of statistics": ("sokoto_mpi", "sokoto_sbs"), "bureau of statistics": ("sokoto_mpi", "nbs_mpi"),
    "world bank": ("worldbank_poverty", "worldbank_labour"), "unicef": ("unicef_nutrition", "unicef_education"),
    "iom": ("iom_dtm",), "dtm": ("iom_dtm",), "unhcr": ("unhcr_dashboard",), "ophi": ("ophi",), "undp": ("ophi",),
    "nimet": ("nimet_scp",), "nihsa": ("nihsa_afo",), "ncdc": ("ncdc",), "who": ("who_afro",), "wfp": ("wfp",),
    "ocha": ("ocha_nigeria",), "nema": ("nema_floods",), "sema": ("sokoto_sema",), "ilo": ("ilo",), "fao": ("fao",),
}
TOPIC_WORDS = [               # a measure word that settles the registry topic
    ("poverty_welfare", re.compile(r"(?i)\b(?:mpi|multidimensional\s+poverty|poverty|poor|talauci|matalauta|headcount)\b")),
    ("displacement_humanitarian", re.compile(r"(?i)\b(?:idps?|displaced|displacement|returnees?|'?yan\s+gudun\s+hijira|"
                                             r"gudun\s+hijira)\b")),
    ("labour_employment", re.compile(r"(?i)\b(?:unemploy\w*|underemploy\w*|labou?r\s+force|jobs?|rashin\s+aikin\s+yi|"
                                     r"aikin\s+yi)\b")),
    ("nutrition_health", re.compile(r"(?i)\b(?:malnutrition|stunting|wasting|tamowa|ƙarancin\s+abinci|karancin\s+abinci)\b")),
]
# --- a named budget line ------------------------------------------------------------------------------------------------------
QUOTED = re.compile(r"[\"“«]([^\"”»]{8,120})[\"”»]")
LINE_LEAD = re.compile(r"(?i)\b(?:budgeted|allocated|approved|provided|set\s+aside|earmarked|aka\s+ware|an\s+ware)\s+"
                       r"(?:for|wa|ga|don)\s+(?:the\s+)?(.{12,120}?)\s+(?:in|for|a|na)\s+(?:the\s+)?(?:fy\s*)?(?:20\d\d)\b")
LINE_LEAD_HA = re.compile(r"(?i)\b(?:nawa\s+aka\s+ware\s+wa|me\s+aka\s+ware\s+wa|kuɗi\s+nawa\s+aka\s+ware\s+wa)\s+(.{12,120}?)\s+a\s+(?:20\d\d)\b")
GENERIC_LINE = re.compile(r"(?i)^(?:the\s+)?(?:ministry|office|agency|commission|board|bureau|department|hukuma|ma'aikat)")


@dataclass
class Facts:
    period: Period | None = None
    measures: list[str] = field(default_factory=list)
    splits: list[str] = field(default_factory=list)
    publishers: list[str] = field(default_factory=list)     # registry ids, in the order named
    compare: bool = False
    topic: str = ""
    line_name: str = ""
    conflicts: list[dict] = field(default_factory=list)      # patterns that contradict each other: fix 5 decides
    rules: list[str] = field(default_factory=list)           # the patterns that matched

    def as_record(self) -> dict:
        return {"period": self.period.label() if self.period else "", "measures": self.measures, "splits": self.splits,
                "publishers": self.publishers, "compare": self.compare, "topic": self.topic,
                "line_name": bool(self.line_name), "rules": self.rules, "conflicts": self.conflicts}


def facts_from(question: str, english: str = "") -> Facts:
    """What the words settle. Only clear patterns count; two patterns that pull different ways are a conflict."""
    text = " ".join(x for x in (question, english) if x)
    f = Facts()
    # the period (app/agent/periods.py knows the cumulative quarters): a conflict when two different quarters are named
    quarters = asked_quarters(question) | asked_quarters(english)
    if len(quarters) == 1:
        f.period = asked_period(question, english)
        f.rules.append("period")
    elif len(quarters) > 1:
        f.conflicts.append({"field": "time", "values": sorted(quarters)})
    # measures: every one the words name ("the approved and the revised budget" asks for both)
    if SPENT.search(text):
        f.measures.append("actual_ytd"); f.rules.append("spent")
    if REVISED.search(text):
        f.measures.append("revised"); f.rules.append("revised")
    if APPROVED.search(text):
        f.measures.append("approved"); f.rules.append("approved")
    if PERFORMANCE.search(text) and (SPENT.search(text) or REVISED.search(text)):
        f.measures.append("performance_pct"); f.rules.append("performance")
    # splits named
    for name, pat in SPLIT_WORDS:
        if pat.search(text):
            f.splits.append(name)
    if f.splits:
        f.rules.append("splits")
    # publishers named with "according to"; a change word with two publishers is a comparison of their figures
    for m in ACCORDING.finditer(text):
        name = m.group(1).strip(" .,'’").lower()
        ids = PUBLISHER_ALIASES.get(name) or PUBLISHER_ALIASES.get(name.replace("the ", ""))
        if ids and ids[0] not in f.publishers:
            f.publishers.append(ids[0])
    if f.publishers:
        f.rules.append("publishers")
    if CHANGE.search(text) and (len(f.publishers) >= 2 or re.search(r"(?i)\b(?:between|from)\s+20\d\d\b.*\b(?:and|to|zuwa)\s+20\d\d", text)):
        f.compare = True
        f.rules.append("compare")
    for topic, pat in TOPIC_WORDS:
        if pat.search(text):
            f.topic = topic
            f.rules.append("topic")
            break
    # a named line: quoted, or "budgeted for <a long name> in 2026"
    q = QUOTED.search(question or "")
    lead = LINE_LEAD.search(text) or LINE_LEAD_HA.search(question or "")
    name = (q.group(1) if q else lead.group(1) if lead else "").strip(" ,.")
    if name and len(name.split()) >= 5 and not GENERIC_LINE.match(name):
        f.line_name = name
        f.rules.append("line")
    return f


def enforce(plan, facts: Facts, docs_known: set[str] | None = None) -> list[dict]:
    """The plan corrected where the words are clear; the list of overrides ({field, from, to, rule}), also kept in
    `plan.words` with the facts and the conflicts. A field the words don't settle is left as the planner gave it."""
    overrides: list[dict] = []
    need = plan.need

    def note(fld: str, before, after, rule: str) -> None:
        overrides.append({"field": fld, "from": before, "to": after, "rule": rule})

    if facts.period and facts.period.year and need is not None:
        t = need.time or {}
        want = {"kind": "quarter", "year": facts.period.year, "quarter": facts.period.quarter}
        if t.get("kind") != "quarter" or t.get("quarter") != facts.period.quarter or t.get("year") != facts.period.year:
            note("time", dict(t), want, "period")
            need.time = want
        wanted_doc = f"bir-{facts.period.year}-q{facts.period.quarter}"
        others = [d for d in plan.doc_ids if re.fullmatch(rf"bir-{facts.period.year}-q[1-4]", d) and d != wanted_doc]
        if others:
            note("doc_ids", list(plan.doc_ids), [d for d in plan.doc_ids if d not in others], "period")
            plan.doc_ids = [d for d in plan.doc_ids if d not in others]
        if docs_known and wanted_doc in docs_known and wanted_doc not in plan.doc_ids:
            note("doc_ids", list(plan.doc_ids), [wanted_doc, *plan.doc_ids], "period")
            plan.doc_ids = [wanted_doc, *plan.doc_ids]
    if facts.measures and need is not None:
        missing = [m for m in facts.measures if m not in need.measures]
        if missing:
            note("measures", list(need.measures), [*need.measures, *missing], "measures")
            need.measures = [*need.measures, *missing]
    if facts.splits and need is not None:
        want = [s for s in ("personnel", "overhead", "capital", "debt") if s in facts.splits]
        if sorted(need.splits) != sorted(want):
            note("splits", list(need.splits), want, "splits")
            need.splits = want
    if facts.compare and need is not None and need.operation != "compare":
        note("operation", need.operation, "compare", "compare")
        need.operation = "compare"
    if facts.topic and need is not None and facts.topic not in list(getattr(need, "topics", []) or []):
        before = list(getattr(need, "topics", []) or [])
        note("topics", before, [facts.topic, *before], "topic")
        need.topics = [facts.topic, *before]
    if facts.line_name:
        terms = list((plan.line_search or {}).get("terms") or [])
        if facts.line_name.lower() not in {x.lower() for x in terms}:
            note("line_search.terms", terms[:4], [facts.line_name, *terms][:4], "line")
            plan.line_search = {**(plan.line_search or {}), "terms": [facts.line_name, *terms]}
            if "years" not in plan.line_search and (y := re.findall(r"\b20\d\d\b", facts.line_name + " " + (plan.english_question or ""))):
                plan.line_search["years"] = [int(y[0])]
        if plan.category:
            note("category", {k: plan.category.get(k) for k in ("scope", "year")}, {}, "line")
            plan.category = {}
    plan.words = {"facts": facts.as_record(), "overrides": overrides, "conflicts": facts.conflicts}
    return overrides


def disputed_fields(plan, facts: Facts) -> list[str]:
    """The fields the second opinion (fix 5) should settle: the words' conflicts."""
    return sorted({c["field"] for c in facts.conflicts})


def take_second_opinion(plan, second, facts: Facts, fields: list[str]) -> list[dict]:
    """Settle the disputed fields with the second plan: a field is taken from it only when the two plans differ and
    the second plan's value is consistent with the words' partial evidence; otherwise the first plan stands."""
    taken: list[dict] = []
    a, b = plan.need, second.need
    if a is None or b is None:
        return taken
    for fld in fields:
        if fld == "time" and b.time != a.time and b.time.get("kind") == "quarter":
            taken.append({"field": "time", "from": dict(a.time), "to": dict(b.time)})
            a.time = dict(b.time)
        elif fld == "measures" and set(b.measures) != set(a.measures) and set(b.measures) & {"approved", "revised"}:
            taken.append({"field": "measures", "from": list(a.measures), "to": list(b.measures)})
            a.measures = list(b.measures)
    return taken
