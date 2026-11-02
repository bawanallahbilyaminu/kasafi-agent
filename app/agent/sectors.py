"""Sectors of the budget, matched in code (3 Nov 2026): "farming-related budgets in my area" means the agriculture
function and its ministries and agencies (the Ministry of Agriculture, the ADP, the fertilizer company, Fadama,
livestock, irrigation, the College of Agriculture), not project names that contain the word "farming".

A project line belongs to a sector by its function of government first (the budget's functional classification,
e.g. AGRICULTURE, PUBLIC HEALTH SERVICES), then by the ministry or agency that runs it, and only then by words in
its own name. The live test of 3 Nov ("What are the farming related budgets in my area?", a Wamakko pin) matched
project names only and found none; by function and agency the 2026 budget has five there.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Sector:
    key: str
    en: str
    ha: str
    asked: re.Pattern            # the question's words (English and Hausa)
    function: re.Pattern         # the function of government's printed name
    mda: re.Pattern              # the ministry or agency's printed name
    words: re.Pattern            # the project's own name (last resort)


def _rx(p: str) -> re.Pattern:
    return re.compile(p, re.I)


SECTORS = [
    Sector("agriculture", "agriculture", "noma",
           _rx(r"\b(?:farm\w*|agric\w*|crops?|irrigation|livestock|fadama|fertili[sz]er\w*|extension|agro\w*|"
               r"fish\w*|veterinar\w*|food\s+security|noma|manoma|gona(?:ki)?|dabbobi|taki|ban\s+ruwa)\b"),
           _rx(r"agricultur|forestry|fishing|hunting|livestock|irrigation"),
           _rx(r"agricult|livestock|animal|fertili|irrigat|fadama|agro|\bADP\b|agricultural\s+development|"
               r"international\s+fund\s+for\s+agric|fisher"),
           _rx(r"\b(?:farm\w*|agric\w*|irrigat\w*|livestock|fertili[sz]er|fadama|tractor\w*|grazing|veterinar\w*|"
               r"fish\s+pond\w*|dam\b|tube\s*wells?)")),
    Sector("health", "health", "lafiya",
           _rx(r"\b(?:health\w*|hospitals?|clinics?|phcs?|primary\s+health|medical|maternal|nursing|lafiya|asibiti\w*)\b"),
           _rx(r"health|hospital|medical"),
           _rx(r"health|hospital|medical|nursing|midwi|\bPHC|primary\s+health|drug|pharmac"),
           _rx(r"\b(?:hospital|clinic|health|PHC|medical|maternity|dispensar\w*)")),
    Sector("education", "education", "ilimi",
           _rx(r"\b(?:educat\w*|schools?|classrooms?|teachers?|universit\w*|colleges?|ilimi|makarant\w*|malamai)\b"),
           _rx(r"education|pre-primary|primary|secondary|tertiary"),
           _rx(r"educat|school|universit|college|SUBEB|polytechnic|scholarship|almajiri|tsangaya|nomadic"),
           _rx(r"\b(?:school|classroom|universit\w*|college|hostel|laborator\w*|library)")),
    Sector("water", "water and sanitation", "ruwa da tsafta",
           _rx(r"\b(?:water\s+supply|drinking\s+water|boreholes?|sanitation|wash|ruwan\s+sha|rijiy\w*|tsafta)\b"),
           _rx(r"water\s+supply|waste\s+water|sanitation"),
           _rx(r"water\s+(?:board|corporation|supply)|rural\s+water|RUWASA|sanitation|environmental\s+sanitation"),
           _rx(r"\b(?:boreholes?|water\s+supply|water\s+scheme|reticulation|toilets?|latrines?|sanitation)")),
    Sector("roads", "roads and transport", "hanyoyi da sufuri",
           _rx(r"\b(?:roads?|bridges?|transport\w*|highways?|flyovers?|hanya|hanyoyi|gada|sufuri)\b"),
           _rx(r"road\s+transport|transport"),
           _rx(r"works|highway|road|transport|rural\s+access"),
           _rx(r"\b(?:roads?|bridges?|dualizat\w*|flyover|culverts?|drainage|asphalt\w*|township\s+roads?)")),
]
BY_KEY = {s.key: s for s in SECTORS}


def sector_asked(*texts: str) -> Sector | None:
    """The sector a question asks about ('farming-related budgets', 'kasafin noma'), or None."""
    t = " ".join(x or "" for x in texts)
    return next((s for s in SECTORS if s.asked.search(t)), None)


def sector_of(function_name: str, mda_name: str, name: str = "") -> Sector | None:
    """The sector of one project line: its function, then its ministry or agency, then its own name."""
    for field_rx in ("function", "mda", "words"):
        text = {"function": function_name, "mda": mda_name, "words": name}[field_rx]
        hit = next((s for s in SECTORS if text and getattr(s, field_rx).search(text)), None)
        if hit:
            return hit
    return None


def sector_sql(s: Sector) -> tuple[str, list]:
    """The SQL condition on a projects row for a sector (function, then agency, then name), with its args."""
    return ("(p.function_name ~* %s OR p.mda_name ~* %s OR p.name ~* %s)",
            [_pg(s.function.pattern), _pg(s.mda.pattern), _pg(s.words.pattern)])


def _pg(pattern: str) -> str:
    """Python's \\b and (?:...) in a PostgreSQL regex: \\y is the word boundary there."""
    return pattern.replace(r"\b", r"\y")
