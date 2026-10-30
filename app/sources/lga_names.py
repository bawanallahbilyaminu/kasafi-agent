"""Sokoto State's 23 LGAs and the spellings the sources use for them.

The budget prints capitals and spaces ("WAMAKKO", "DANGE SHUNI"), IOM DTM uses its own forms ("Wamako",
"Dange-Shuni"), and people type others ("Wamako", "Sabon-Birni", "Ilela", "Sokoto ta Arewa"). Every name is
matched through canonical(), so a question, a budget location and a DTM place meet on one key.

The crosswalk (hazard step 1): every LGA's identity is its OCHA COD-AB P-code (NG034001 ...), the join key for
IOM DTM and HDX data. Each canonical name maps to its P-code and to GRID3's own code (601 ...); every spelling
(COD-AB's 'Wamako' and 'Dange-Shuni', GRID3's 'Wamakko' and 'Dange Shuni', the facility file's, the budgets',
DTM's, typed ones) goes through canonical(), then pcode(). The same crosswalk is stored on the lga table
(scripts/import_geo.py) with the boundaries; tests/test_geo.py checks it against the COD-AB and GRID3 files.
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


# OCHA COD-AB (HDX, valid from 22 Feb 2017) P-codes and GRID3 operational-ward LGA codes, by canonical name
PCODES = {"Binji": "NG034001", "Bodinga": "NG034002", "Dange Shuni": "NG034003", "Gada": "NG034004",
          "Gwadabawa": "NG034005", "Goronyo": "NG034006", "Gudu": "NG034007", "Illela": "NG034008", "Isa": "NG034009",
          "Kebbe": "NG034010", "Kware": "NG034011", "Rabah": "NG034012", "Sabon Birni": "NG034013",
          "Shagari": "NG034014", "Silame": "NG034015", "Sokoto North": "NG034016", "Sokoto South": "NG034017",
          "Tambuwal": "NG034018", "Tangaza": "NG034019", "Tureta": "NG034020", "Wamakko": "NG034021",
          "Wurno": "NG034022", "Yabo": "NG034023"}
GRID3_CODES = {name: str(601 + i) for i, name in enumerate(CANONICAL)}      # Binji 601 ... Yabo 623
_BY_PCODE = {p: n for n, p in PCODES.items()}


def pcode(name: str) -> str:
    """The LGA's P-code for any spelling of its name, or its P-code in either form: COD-AB's NG034013 or the ISO3
    form NGA034013 that IOM DTM returns (both mean Sabon Birni); '' when it is none of them."""
    if name in _BY_PCODE:
        return name
    if (m := re.fullmatch(r"NGA?(\d{6})", (name or "").strip().upper())) and f"NG{m.group(1)}" in _BY_PCODE:
        return f"NG{m.group(1)}"
    return PCODES.get(canonical(name), "")


def name_of(code: str) -> str:
    """The canonical name for a P-code."""
    return _BY_PCODE.get(code, "")
