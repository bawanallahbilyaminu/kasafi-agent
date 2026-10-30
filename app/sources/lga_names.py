"""Sokoto State's 23 LGAs and the spellings the sources use for them.

The budget prints capitals and spaces ("WAMAKKO", "DANGE SHUNI"), IOM DTM uses its own forms ("Wamako",
"Dange-Shuni"), and people type others ("Wamako", "Sabon-Birni", "Ilela", "Sokoto ta Arewa"). Every name is
matched through canonical(), so a question, a budget location and a DTM place meet on one key.

An interim table: hazard step 1 replaces it with a full crosswalk joined by OCHA P-codes.
"""

from __future__ import annotations

import re

CANONICAL = ("Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", "Gudu", "Gwadabawa", "Illela", "Isa", "Kebbe",
             "Kware", "Rabah", "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South", "Tambuwal",
             "Tangaza", "Tureta", "Wamakko", "Wurno", "Yabo")

# other spellings -> canonical (compared after lower-casing and turning hyphens and repeated spaces into one space)
ALIASES = {
    "wamako": "Wamakko", "wamakko": "Wamakko",
    "dange-shuni": "Dange Shuni", "dange shuni": "Dange Shuni", "dangeshuni": "Dange Shuni",
    "sabon-birni": "Sabon Birni", "sabonbirni": "Sabon Birni", "sabon biri": "Sabon Birni",
    "ilela": "Illela", "illella": "Illela",
    "issa": "Isa",
    "raba": "Rabah",
    "silami": "Silame",
    "kwarre": "Kware",
    "gwadabawa": "Gwadabawa", "gwadabewa": "Gwadabawa",
    "sokoto ta arewa": "Sokoto North", "sokoto arewa": "Sokoto North", "north sokoto": "Sokoto North",
    "sokoto ta kudu": "Sokoto South", "sokoto kudu": "Sokoto South", "south sokoto": "Sokoto South",
    "goronye": "Goronyo",
    "tambuwal": "Tambuwal", "tanbuwal": "Tambuwal",
}


def _key(name: str) -> str:
    return " ".join(re.sub(r"[-_/]", " ", name.lower()).replace(" lga", " ").split())


_SPELLINGS = [(c, c) for c in CANONICAL] + list(ALIASES.items())
_BY_KEY = {k: c for s, c in _SPELLINGS for k in (_key(s), _key(s).replace(" ", ""))}


# Sokoto city, the state capital, is no LGA (it spans Sokoto North and South and parts of Wamakko and Dange
# Shuni): people say 'Sokoto city', 'birnin Sokoto', 'cikin garin Sokoto'; the budgets print 'Sokoto Metropolis'
# and 'Sokoto Township'
CITY = re.compile(r"(?i)\b(?:sokoto\s+(?:city|metropolis|township|town)|birnin\s+sokoto|garin\s+sokoto)\b")
CITY_PRINTED = ("Sokoto Metropolis", "Township")


def city_terms(text: str) -> list[str]:
    """The city's printed names when `text` names Sokoto city, else []."""
    return list(CITY_PRINTED) if CITY.search(text or "") else []


def canonical(name: str) -> str:
    """The LGA's canonical name for any known spelling (spaces optional), or '' if it isn't a Sokoto LGA."""
    k = _key(name)
    return _BY_KEY.get(k) or _BY_KEY.get(k.replace(" ", ""), "")
