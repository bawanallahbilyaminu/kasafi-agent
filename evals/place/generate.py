"""Generated eval families for the planner's place-history answers (docs/place-history.md §9): measure x unit x
language, with the expected values read from ward_history itself (so the eval checks the answer's wording and
ranking against the table, not the table against the sky), plus rain-adjustment and low-data cases.

Writes evals/place/cases.json. Run: uv run python evals/place/generate.py [--lgas 6] [--seed 7]
Then: uv run python evals/place/run.py (in code, no model) or run.py --full (through answer_question).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place import planner as P  # noqa: E402
from app.sources.lga_names import name_of  # noqa: E402

QUESTIONS = {
    "greenness": {"en": "Which wards of {lga} LGA were greenest in {year}?",
                  "ha": "Waɗanne gundumomin Ƙaramar Hukumar {lga} ne suka fi koriya a {year}?"},
    "flood": {"en": "Which wards of {lga} LGA flooded most in {year}?",
              "ha": "Waɗanne gundumomin Ƙaramar Hukumar {lga} ne ambaliya ta fi rufewa a {year}?"},
    "flood_map": {"en": "Share of cropland inside the UN flood map by ward in {lga} LGA, {year}",
                  "ha": "Kashin gonaki a cikin taswirar ambaliya ta MDD a gundumomin Ƙaramar Hukumar {lga}, {year}"},
    "bare": {"en": "Which wards of {lga} LGA had the most bare soil in the {year} dry season?",
             "ha": "Waɗanne gundumomin Ƙaramar Hukumar {lga} ne suka fi ƙasa mara ciyayi a ranin {year}?"},
    "rain": {"en": "Which wards of {lga} LGA got the most June–October rain in {year}?",
             "ha": "Waɗanne gundumomin Ƙaramar Hukumar {lga} ne suka fi samun ruwan sama na Yuni–Oktoba a {year}?"},
    "water": {"en": "Which wards of {lga} LGA have cropland that is often under water (JRC)?",
              "ha": "Waɗanne gundumomin Ƙaramar Hukumar {lga} ne gonakinsu ruwa ke yawan rufewa (JRC)?"},
}
STATE_QUESTIONS = {
    "flood_map": {"en": "Share of cropland inside the UN flood map in {year} across Sokoto State",
                  "ha": "Kashin gonaki a cikin taswirar ambaliya ta MDD a {year} a faɗin Jihar Sokoto"},
    "flood": {"en": "Which LGAs had the largest share of land flooded in {year}?",
              "ha": "Waɗanne ƙananan hukumomi ne suka fi kashin ƙasar da ambaliya ta rufe a {year}?"},
    "greenness": {"en": "Which LGAs were greenest in the {year} rainy season?",
                  "ha": "Waɗanne ƙananan hukumomi ne suka fi koriya a daminar {year}?"},
}


def flood_spec(key: str, spec: dict) -> dict:
    """Flood questions are answered from Copernicus GFM (app/place/flood_record.py): the ranking is its measure."""
    return P.MEASURES["gfm"] if key == "flood" else spec


def latest_flood_year(years: list[int], today: date) -> int:
    """The radar season rule, not MODIS's: the latest season whose floods are in (flood_record.complete)."""
    from app.place.flood_record import complete
    done = [y for y in years if complete(y, today)]
    return max(done) if done else max(years)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lgas", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=str(ROOT / "evals/place/cases.json"))
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    today = date.today()
    cases = []
    with psycopg.connect(get_settings().db_url()) as conn:
        lgas = [r[0] for r in conn.execute("SELECT DISTINCT unit FROM ward_history WHERE level = 'lga' ORDER BY unit")]
        picked = rnd.sample(lgas, min(a.lgas, len(lgas)))
        n = 0
        for key, spec in P.MEASURES.items():
            if key == "gfm":
                continue
            spec = flood_spec(key, spec)
            years = P.years_loaded(conn, spec["measure"], "ward")
            if not years:
                continue
            for pcode in picked:
                year = 0 if spec["first"] == 0 else latest_flood_year(years, today) if key == "flood" else \
                    P.headline_year(conn, spec["measure"], "ward", years, today)[0]
                rows = P.rows_for(conn, spec["measure"], "ward", year, pcode)
                cut = P.low_data_cut(rows, spec["measure"])
                ranked = sorted([r for r in rows if r[2] is not None and (r[3] is None or r[3] > cut)], key=lambda r: -r[2])
                if len(ranked) < 4:
                    continue
                low = [r[1] for r in rows if r[2] is not None and r[3] is not None and r[3] <= cut]
                for lang in ("en", "ha"):
                    n += 1
                    q = QUESTIONS[key][lang].format(lga=name_of(pcode), year=year or "")
                    cases.append({"id": f"a{n:03d}", "family": key, "lang": lang, "level": "lga", "unit": pcode,
                                  "year": year, "question": q.replace(" in ?", "?").replace(", ?", "?").strip(),
                                  "expect": {"top": ranked[0][1], "bottom": ranked[-1][1],
                                             "top_value": spec["fmt"].format(ranked[0][2]),
                                             "n_ranked": len(ranked), "low_data": low[:3],
                                             "must_have": ["Kasafi" if lang == "en" else "Kasafi"],
                                             "must_not": ["never flooded", "ba ta taɓa", "NDVI index"]}})
        # the state: LGAs compared
        for key, qs in STATE_QUESTIONS.items():
            spec = flood_spec(key, P.MEASURES[key])
            years = P.years_loaded(conn, spec["measure"], "lga")
            for year in [y for y in (2022, 2024) if y in years][:2]:
                rows = P.rows_for(conn, spec["measure"], "lga", year, None)
                ranked = sorted([r for r in rows if r[2] is not None], key=lambda r: -r[2])
                for lang in ("en", "ha"):
                    n += 1
                    cases.append({"id": f"a{n:03d}", "family": f"state_{key}", "lang": lang, "level": "state", "unit": "NG034",
                                  "year": year, "question": qs[lang].format(year=year),
                                  "expect": {"top": ranked[0][1], "bottom": ranked[-1][1], "top_value": spec["fmt"].format(ranked[0][2]),
                                             "n_ranked": len(ranked), "low_data": [], "must_have": [],
                                             "must_not": ["never flooded"]}})
        # rain adjustment: wards flagged below or above the rain in a year with a fit
        years = P.years_loaded(conn, "modis_peak", "ward")
        for pcode in picked:
            for year in reversed([y for y in years if y < today.year][-3:]):
                rows = P.rows_for(conn, "modis_peak", "ward", year, pcode)
                flags = P.rain_flags(conn, "ward", [r[0] for r in rows if r[2] is not None], year)
                names = {r[0]: r[1] for r in rows}
                below = [names[u] for u, f in flags.items() if f == "below"]
                above = [names[u] for u, f in flags.items() if f == "above"]
                if below or above:
                    n += 1
                    cases.append({"id": f"a{n:03d}", "family": "rain_adjusted", "lang": "en", "level": "lga", "unit": pcode,
                                  "year": year, "question": QUESTIONS["greenness"]["en"].format(lga=name_of(pcode), year=year),
                                  "expect": {"below": below, "above": above, "must_have": ["less green than the rain would suggest"]
                                             if below else ["greener than usual for the rain"], "must_not": []}})
                    break
        # low data: a measure-year where some wards fall under the cut
        for key in ("greenness", "flood", "bare"):
            spec = flood_spec(key, P.MEASURES[key])
            for year in P.years_loaded(conn, spec["measure"], "ward"):
                for pcode in picked:
                    rows = P.rows_for(conn, spec["measure"], "ward", year, pcode)
                    cut = P.low_data_cut(rows, spec["measure"])
                    low = [r[1] for r in rows if r[2] is not None and r[3] is not None and r[3] <= cut]
                    if low:
                        n += 1
                        cases.append({"id": f"a{n:03d}", "family": "low_data", "lang": "en", "level": "lga", "unit": pcode,
                                      "year": year, "question": QUESTIONS[key]["en"].format(lga=name_of(pcode), year=year),
                                      "expect": {"low_data": low[:3], "must_have": ["Low data:"], "must_not": []}})
                        break
                else:
                    continue
                break
        # scope: 'my ward / my LGA / the state' with a location on file (the 1 Nov phone test), and with none
        year = P.headline_year(conn, "modis_peak", "ward", P.years_loaded(conn, "modis_peak", "ward"), today)[0]
        for pcode in picked[:4]:
            rows = P.rows_for(conn, "modis_peak", "ward", year, pcode)
            ranked = sorted([r for r in rows if r[2] is not None], key=lambda r: -r[2])
            if not ranked:
                continue
            code, ward = ranked[len(ranked) // 2][0], ranked[len(ranked) // 2][1]
            place = {"lga_pcode": pcode, "lga": name_of(pcode), "ward": ward, "wardcode": code, "ward_likely": False}
            for lang, q, must in (("en", "How has farming evolved in my ward over the years",
                                   [f"{ward} ward, {name_of(pcode)} LGA", f"Your pin is in {ward} ward", "Since 20", f"In {year} {ward} was"]),
                                  ("ha", "Yaya noma ya canza a unguwata tun shekaru?",
                                   [f"gundumar {ward}", "Wurinku yana gundumar", "Tun 20"])):
                n += 1
                cases.append({"id": f"a{n:03d}", "family": "scope_ward", "lang": lang, "level": "ward", "unit": code, "year": year,
                              "question": q, "place": place,
                              "expect": {"must_have": must, "must_not": ["*Ranking", "232 wards", "244 wards", "sun fi koriya"],
                                         "text_must_not": ["NDVI", "90th percentile"]}})
            n += 1
            cases.append({"id": f"a{n:03d}", "family": "scope_lga", "lang": "en", "level": "lga", "unit": pcode, "year": year,
                          "question": "How has farming evolved in my LGA over the years", "place": place,
                          "expect": {"top": ranked[0][1], "must_have": [f"wards of {name_of(pcode)} LGA, {year}", f"Since 20"],
                                     "must_not": [], "text_must_not": ["NDVI", "90th percentile"]}})
        n += 1
        cases.append({"id": f"a{n:03d}", "family": "scope_state", "lang": "en", "level": "state", "unit": "NG034", "year": year,
                      "question": "How has farming evolved across the state over the years", "place": place,
                      "expect": {"must_have": [f"the 23 LGAs of Sokoto State, {year}", "Sokoto State's farmland greenness"],
                                 "must_not": [], "text_must_not": ["NDVI", "90th percentile"]}})
        n += 1
        cases.append({"id": f"a{n:03d}", "family": "scope_none", "lang": "en", "level": "ward", "unit": "", "year": year,
                      "question": "How has farming evolved in my ward over the years",
                      "expect": {"must_have": ["I need the spot itself"], "must_not": ["Ranking"]}})
    out = {"_about": "Generated planner place-history cases: expected values from ward_history (evals/place/generate.py). "
                     "Checked in code by evals/place/run.py; --full runs them through answer_question.",
           "generated": today.isoformat(), "cases": cases}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    fams = {}
    for c in cases:
        fams[c["family"]] = fams.get(c["family"], 0) + 1
    print(f"{len(cases)} cases -> {a.out}: {fams}")


if __name__ == "__main__":
    main()
