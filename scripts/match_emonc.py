"""Link health facilities to EmONC capability from the UNFPA EmONC assessment in the library (doc emonc-sokoto,
Appendix 1 secondary and Appendix 2 primary facilities assessed: name, level, BEmONC / CEmONC, ward, LGA).

A link is made only on a confident name match inside the same LGA (COD-AB, from the facility's point): the names
agree once the report's abbreviations are spelled out (Gh, Phc, Hc, Hp, P., Mch), the score clears a bar, and it
clearly beats the next facility in that LGA. Every link is stored unconfirmed (facility_capability.confirmed =
false) and listed in data/geo/emonc_matches.md for Bilyaminu to confirm; nothing else is guessed.

    uv run python scripts/match_emonc.py
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.sources.lga_names import CANONICAL, canonical, pcode  # noqa: E402

DOC = "emonc-sokoto"
OUT = ROOT / "data" / "geo" / "emonc_matches.md"
BAR, MARGIN = 0.88, 0.06            # a confident match: score >= BAR and >= MARGIN above the next in the LGA

_LGA_TAIL = sorted({*CANONICAL, "Dange-Shuni", "Wamako", "Sabon-Birni"}, key=len, reverse=True)
ROW = re.compile(r"(?:^|\s)(\d{1,3})\s+(.+?)\s+(Primary|Secondary|Tertiary)\s+(BEmONC|CEmONC)\s+Sokoto\s+(.+?)"
                 r"(?=\s+\d{1,3}\s+\S.*?\s+(?:Primary|Secondary|Tertiary)\s+(?:BEmONC|CEmONC)\s|\s*$)")
ABBREV = [(r"\bgh\b", "general hospital"), (r"\bphc\b", "primary health centre"), (r"\bphcc\b", "primary health care centre"),
          (r"\bhc\b", "health clinic"), (r"\bhp\b", "health post"), (r"\bp\.?\s*health\b", "primary health"),
          (r"\bmch\b", "maternal and child health"), (r"\bcenter\b", "centre"), (r"\bclinc\b", "clinic"),
          (r"\bcomp(?:rehensive)?\b", "comprehensive")]
GENERIC = {"general", "hospital", "primary", "health", "centre", "care", "clinic", "post", "dispensary", "maternal",
           "and", "child", "comprehensive", "the", "of", "model", "town", "township", "specialist"}


def norm(name: str) -> str:
    s = name.lower().replace("’", "'")
    for pat, rep in ABBREV:
        s = re.sub(pat, rep, s)
    return " ".join(re.findall(r"[a-z0-9]+", s))


def score(a: str, b: str) -> float:
    """Name agreement on the facility's own words (its place: 'Margai' is not 'Rara', however alike 'Health Clinic'
    makes the whole names), less a little when the kind differs (Health Clinic / Health Post: perhaps upgraded,
    perhaps another facility, so it shows in the score for the person confirming)."""
    x, y = norm(a), norm(b)
    ox, oy = [w for w in x.split() if w not in GENERIC], [w for w in y.split() if w not in GENERIC]
    if not ox or not oy:
        return 0.0                   # a name with no place word ('Specialist Hospital') can't be matched by name
    own = difflib.SequenceMatcher(None, " ".join(sorted(ox)), " ".join(sorted(oy))).ratio()
    kind = 1.0 if (set(x.split()) & GENERIC) == (set(y.split()) & GENERIC) else 0.92
    return round(own * kind, 3)


def rows(conn) -> list[dict]:
    pages = conn.execute("SELECT page, text FROM pages WHERE doc_id = %s AND text ~ 'Appendix (1|2):' OR "
                         "(doc_id = %s AND page BETWEEN (SELECT min(page) FROM pages WHERE doc_id = %s AND text ~ "
                         "'Appendix 2:') AND (SELECT min(page) FROM pages WHERE doc_id = %s AND text ~ 'Appendix 3:') - 1) "
                         "ORDER BY page", (DOC, DOC, DOC, DOC)).fetchall()
    out = []
    for page, text in pages:
        flat = " ".join(text.split())
        flat = flat.split(" LGA ", 1)[1] if " S/N FACILITY NAME " in flat else flat     # past the table header
        for m in ROW.finditer(flat):
            tail = m.group(5)
            lga = next((n for n in _LGA_TAIL if tail.endswith(" " + n) or tail == n), "")
            out.append({"n": int(m.group(1)), "name": re.sub(r"^\d{1,3}\s+", "", m.group(2).strip()), "level": m.group(3), "service": m.group(4),
                        "ward": tail[: -len(lga)].strip() if lga else tail, "lga": canonical(lga), "page": page})
    return out


def main() -> None:
    global OUT
    if "--out" in sys.argv:                      # the list's place (the server: /data/geo/emonc_matches.md)
        OUT = Path(sys.argv[sys.argv.index("--out") + 1])
    with psycopg.connect(get_settings().db_url()) as conn:
        assessed = rows(conn)
        fac = defaultdict(list)
        for fid, name, lga, level in conn.execute("SELECT fid, name, lga_pcode, level FROM facility"):
            fac[lga].append((fid, name, level))
        conn.execute("DELETE FROM facility_capability WHERE doc_id = %s", (DOC,))
        made, unmatched, lines = [], [], []
        for r in assessed:
            cands = sorted(((score(r["name"], name), fid, name, level) for fid, name, level in fac[pcode(r["lga"])]),
                           reverse=True)
            best = cands[0] if cands else None
            second = cands[1][0] if len(cands) > 1 else 0.0
            if best and best[0] >= BAR and best[0] - second >= MARGIN:
                made.append((r, best))
                conn.execute("INSERT INTO facility_capability (fid, capability, doc_id, page, matched_name, score) "
                             "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                             (best[1], r["service"].lower(), DOC, r["page"], r["name"], best[0]))
            else:
                unmatched.append((r, best, second))
    by = defaultdict(int)
    for r, _ in made:
        by[r["service"]] += 1
    lines = [f"# EmONC capability links (UNFPA EmONC assessment, {DOC}, Appendices 1-2)", "",
             f"Facilities listed in the report: {len(assessed)} "
             f"({sum(r['service'] == 'CEmONC' for r in assessed)} CEmONC, "
             f"{sum(r['service'] == 'BEmONC' for r in assessed)} BEmONC). Linked on a confident name match in the "
             f"same LGA: {len(made)} ({by['CEmONC']} CEmONC, {by['BEmONC']} BEmONC); not linked: {len(unmatched)}.",
             f"Bar: score >= {BAR} and >= {MARGIN} above the next facility in the LGA. All links unconfirmed.", "",
             "## Links to confirm", "", "| report (page) | service | LGA | facility (GRID3/NHFR) | level | score |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {r['name']} (p{r['page']}) | {r['service']} | {r['lga']} | {b[2]} | {b[3]} | {b[0]:.2f} |"
              for r, b in sorted(made, key=lambda x: (x[0]["service"], x[0]["lga"], x[0]["name"]))]
    lines += ["", "## Not linked (best candidate, below the bar or too close to the next)", "",
              "| report | service | LGA | best candidate | score | next |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['name']} | {r['service']} | {r['lga'] or '?'} | {b[2] if b else '-'} | "
              f"{b[0] if b else 0:.2f} | {s:.2f} |" for r, b, s in sorted(unmatched, key=lambda x: (x[0]["service"],
                                                                                                       x[0]["lga"]))]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:5]))
    print("list:", OUT)


if __name__ == "__main__":
    main()
