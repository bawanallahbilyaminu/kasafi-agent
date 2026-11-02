"""The code-side exclusion screen after the confirm step (audit F1, 3 Nov 2026; CLAUDE.md hard rule 5).

The confirm step is a model reading untrusted text: a document could tell it "excluded=false". So code checks too:
- the title naming attacks, banditry, insurgency, security operations or partisan election material forces
  excluded, whatever the model said;
- several such terms on the first pages hold the document for a person (not indexed; listed for review);
- displacement and humanitarian statistics (DTM, IDP counts, needs overviews) are not excluded: they count people,
  and the confirm rule already allows them. A budget's security lines are not conflict content
  (KASAFI_ALLOW_SECURITY_BUDGET).
"""

from __future__ import annotations

import re

CONFLICT = re.compile(r"(?i)\b(?:bandit\w*|insurgen\w*|kidnap\w*|terroris\w*|jihad\w*|boko\s+haram|ISWAP|"
                      r"lakurawa|armed\s+(?:attack|conflict|group|men)|attacks?\s+on|military\s+operation\w*|"
                      r"security\s+operation\w*|counter[\s-]?insurgency|troops|airstrike\w*|gunmen|"
                      r"cattle\s+rustl\w*|reprisal)")
ELECTION = re.compile(r"(?i)\b(?:election\s+campaign|campaign\s+(?:rally|manifesto|council|office)|manifesto|"
                      r"political\s+part(?:y|ies)|party\s+primar(?:y|ies)|polling\s+units?|INEC|"
                      r"(?:APC|PDP|NNPP|LP)\s+(?:candidate|chairman|campaign|ward|primaries))\b")
DISPLACEMENT = re.compile(r"(?i)\b(?:displacement\s+tracking|DTM|IDPs?|internally\s+displaced|mobility\s+tracking|"
                          r"humanitarian\s+needs|needs\s+overview|returnees)\b")
PAGE_TERMS = 2          # distinct terms on the first pages that hold a document for review
PAGE_HITS = 4           # and their occurrences


def screen(title: str, pages: list[str], first: int = 3) -> tuple[str, str]:
    """('excluded' | 'review' | '', why)."""
    t = title or ""
    if (m := CONFLICT.search(t) or ELECTION.search(t)) and not DISPLACEMENT.search(t):
        return "excluded", f"the title names '{m.group(0)}'"
    head = "\n".join(pages[:first])
    if DISPLACEMENT.search(f"{t} {head[:3000]}"):
        return "", ""
    hits = [m.group(0).lower() for rx in (CONFLICT, ELECTION) for m in rx.finditer(head)]
    distinct = sorted(set(hits))
    if len(distinct) >= PAGE_TERMS and len(hits) >= PAGE_HITS:
        return "review", f"its first pages name {', '.join(distinct[:5])} ({len(hits)} times)"
    return "", ""
