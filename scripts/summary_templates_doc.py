"""Write docs/hazard-summaries-ha.md: every Hausa template of the code-written hazard summaries
(app/hazards/summary.py), the US EPA and NWS category meanings in Hausa (marked as translations), and the Hausa
category names (app/hazards/categories.py), each beside its English, for Bilyaminu to correct.

    uv run python scripts/summary_templates_doc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.hazards import categories as cat  # noqa: E402
from app.hazards import summary as hs  # noqa: E402

OUT = Path("docs/hazard-summaries-ha.md")
GROUPS = [
    ("Places and days", ["place_state", "place_lga", "place_named", "today", "tomorrow", "in_lga"]),
    ("Dust and air quality", ["air", "air_state", "air_driver", "air_mult", "both", "one", "neither"]),
    ("Heat", ["heat", "heat_below", "heat_state", "danger_n", "heat_driver"]),
    ("Rain", ["rain", "rain_none", "rain_state", "wet_n", "rain_state_none"]),
    ("Rivers", ["river", "river_none", "levels", "parts", "months"]),
    ("Fires", ["fires", "fires_none"]),
    ("Comparisons and rank", ["trend", "trend_cat", "rank_top", "rank_low"]),
    ("Official warning status (the last sentence)", ["status_none", "status_stale", "status_unchecked",
                                                     "status_live", "when_today", "when_yesterday"]),
]


def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def rows(key: str, ha, en) -> list[str]:
    if isinstance(ha, dict):
        return [r for k in ha for r in rows(f"{key}.{k}", ha[k], en.get(k, "") if isinstance(en, dict) else "")]
    if isinstance(ha, (list, tuple)):
        return [f"| `{key}` | {cell(', '.join(ha))} | {cell(', '.join(en))} |"]
    return [f"| `{key}` | {cell(ha)} | {cell(en)} |"]


def main() -> None:
    ha, en = hs.W["ha"], hs.W["en"]
    out = ["# Hazard summaries in Hausa: every template, for correction",
           "",
           "Generated from `app/hazards/summary.py` and `app/hazards/categories.py` by "
           "`scripts/summary_templates_doc.py`. Correct the Hausa column here; Kasafi copies the corrections into the "
           "code and regenerates this file.",
           "",
           "- `{...}` are filled in by the code: `{place}`, `{day}`, `{cat}` (a category name, below), `{meaning}` "
           "(an official meaning, below), `{lga}`, `{worst}`, `{n}`, `{a}` / `{b}` / `{x}` (multiples), `{other}` "
           "(today / tomorrow), `{when}`, `{src}`, `{date}`, `{point}`, `{period}`, `{level}`.",
           "- A summary is 2-3 sentences: the meaning sentence, then the driver with the comparisons (joined with "
           "“; ”), then the official warning status.",
           "- Text marked *(fassarar bayanin US EPA)* or *(fassarar bayanin NWS)* is Kasafi's translation of the "
           "official English wording, shown as such in every answer.",
           ""]
    for title, keys in GROUPS:
        out += [f"## {title}", "", "| Key | Hausa | English |", "|---|---|---|"]
        for k in keys:
            out += rows(k, ha[k], en[k])
        out.append("")
    out += ["## US EPA: what each AQI category means (fassarar bayanin US EPA)", "",
            "Quoted in English from AirNow “AQI Basics”; the Hausa is Kasafi's translation.", "",
            "| Category | Hausa name | Hausa meaning (translation) | Official English |", "|---|---|---|---|"]
    out += [f"| `{c}` | {cell(cat.label(c, 'ha'))} | {cell(hs.EPA_HA[c])} | {cell(hs.EPA[c])} |" for c in hs.EPA]
    out += ["", "## US National Weather Service: what each heat index category means (fassarar bayanin NWS)", "",
            "Quoted in English from the NWS heat index chart; the Hausa is Kasafi's translation.", "",
            "| Category | Hausa name | Hausa meaning (translation) | Official English |", "|---|---|---|---|"]
    out += [f"| `{c}` | {cell(cat.label(c, 'ha'))} | {cell(hs.NWS_HA[c])} | {cell(hs.NWS[c])} |" for c in hs.NWS]
    out += ["", "## Other category names", "", "| Key | Hausa | English |", "|---|---|---|"]
    out += [f"| `{k}` | {cell(cat.LABELS['ha'][k])} | {cell(cat.LABELS['en'][k])} |"
            for k in cat.LABELS["ha"] if k not in hs.EPA and k not in hs.NWS]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("written", OUT)


if __name__ == "__main__":
    main()
