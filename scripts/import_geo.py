"""Import the geo foundation into Postgres/PostGIS and write the facility data-quality report
(docs/hazard-and-services.md section 2).

Reads data/geo/ (not in git: the facility file's licence isn't confirmed):
- sokoto_lga_codab.geojson     OCHA COD-AB LGAs: admin2Name, admin2Pcod (NG034xxx), CRS84 -> lga
- sokoto_wards_grid3.geojson   GRID3 operational wards: wardname, wardcode, lganame, lgacode -> ward
- health_facilities_nga.geojson  national GRID3 + NHFR 2024 file, filtered to state == "Sokoto" -> facility
- osm_places_sokoto.geojson, grid3_settlements_sokoto.geojson (optional) -> place (with LGA and ward names)

The LGA crosswalk (app/sources/lga_names.py) gives every layer's spelling one P-code. The COD-AB polygon decides a
facility's LGA; its ward is kept only when the ward's own LGA agrees. Re-running replaces the tables' rows.

    uv run python scripts/import_geo.py            -> tables filled, report at data/geo/quality_report.md
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.sources.lga_names import ALIASES, CANONICAL, GRID3_CODES, PCODES, canonical, pcode  # noqa: E402

GEO = ROOT / "data" / "geo"
REPORT = GEO / "quality_report.md"
FACILITY_SOURCE = "GRID3 Nigeria / NHFR (health_facilities_nga, updated Nov 2024)"
KEEP = ("globalid", "nhfr_uid", "nhfr_facility_code", "facility_name", "lga", "ward", "lga_name_disagreement",
        "ward_name_disagreement", "ownership", "ownership_type", "facility_level", "facility_level_option",
        "latitude", "longitude", "geocoordinates_source", "last_updated")


def name_key(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (s or "").lower().replace("'", "")))


def same_ward(a: str, b: str) -> bool:
    """One ward written two ways: a bracketed LGA ('Tudun Wada B (Sokoto South)'), a doubled letter ('Addar'),
    an 'h' ('Rarah'), 'E'/'I' ('Egwai' / 'Igwai'), a slash list that includes the other ('Basansan/Lemi')."""
    def k(s: str) -> str:
        return name_key(re.sub(r"\([^)]*\)", " ", s))
    x, y = k(a), k(b)
    if x == y or y in [k(p) for p in a.split("/")] or x in [k(p) for p in b.split("/")]:
        return True
    return difflib.SequenceMatcher(None, x.replace(" ", ""), y.replace(" ", "")).ratio() >= 0.85


def load(name: str) -> list[dict]:
    p = GEO / name
    return json.loads(p.read_text(encoding="utf-8"))["features"] if p.exists() else []


def import_lgas(conn, codab: list[dict], wards: list[dict], facilities: list[dict]) -> None:
    grid3 = {canonical(w["properties"]["lganame"]): (w["properties"]["lgacode"], w["properties"]["lganame"])
             for w in wards}
    fac_names = {canonical(f["properties"]["lga"]): f["properties"]["lga"] for f in facilities}
    conn.execute("DELETE FROM facility_capability; DELETE FROM facility; DELETE FROM place; DELETE FROM ward; "
                 "DELETE FROM lga")
    for f in codab:
        p = f["properties"]
        name = canonical(p["admin2Name"])
        if not name or PCODES[name] != p["admin2Pcod"]:
            raise SystemExit(f"crosswalk: COD-AB {p['admin2Name']} {p['admin2Pcod']} doesn't match lga_names.py")
        code, g3name = grid3.get(name, ("", ""))
        if code and code != GRID3_CODES[name]:
            raise SystemExit(f"crosswalk: GRID3 {g3name} {code} doesn't match lga_names.py")
        spellings = {p["admin2Name"], name, g3name, fac_names.get(name, "")} | \
            {k.title() for k, v in ALIASES.items() if v == name}
        conn.execute(
            "INSERT INTO lga (pcode, name, grid3_code, grid3_name, facility_name, aliases, geom, source, valid_on) "
            "VALUES (%s, %s, %s, %s, %s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)), %s, %s)",
            (p["admin2Pcod"], name, code, g3name, fac_names.get(name), sorted(s for s in spellings if s),
             json.dumps(f["geometry"]), "OCHA COD-AB (HDX)", (p.get("validOn") or "").replace("/", "-") or None))


def import_wards(conn, wards: list[dict]) -> None:
    for w in wards:
        p = w["properties"]
        conn.execute(
            "INSERT INTO ward (wardcode, name, grid3_lga_code, grid3_lga_name, lga_pcode, urban, geom, source) "
            "VALUES (%s, %s, %s, %s, %s, %s, ST_Multi(ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))), %s)",
            (p["wardcode"], p["wardname"], p["lgacode"], p["lganame"], pcode(p["lganame"]) or None,
             (p.get("urban") or "").lower() == "yes", json.dumps(w["geometry"]), "GRID3 operational wards (INEC, 2019)"))


def import_facilities(conn, facilities: list[dict]) -> None:
    for f in facilities:
        p = {k: f["properties"].get(k) for k in KEEP}
        lon, lat = (f.get("geometry") or {}).get("coordinates", [None, None])[:2]
        conn.execute(
            "INSERT INTO facility (fid, nhfr_uid, nhfr_code, name, lga_attr, ward_attr, lga_flag, ward_flag, ownership, "
            "ownership_type, level, level_option, geom, coord_source, last_updated, source) VALUES (%s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, %s, %s, CASE WHEN %s::float8 IS NULL OR %s::float8 IS NULL THEN NULL ELSE "
            "ST_SetSRID(ST_MakePoint(%s, %s), 4326) END, %s, %s, %s) ON CONFLICT (fid) DO NOTHING",
            (str(p["nhfr_uid"] or p["globalid"]), p["nhfr_uid"], p["nhfr_facility_code"] or None, (p["facility_name"] or "").strip(), p["lga"], p["ward"],
             p["lga_name_disagreement"], p["ward_name_disagreement"], p["ownership"], p["ownership_type"],
             p["facility_level"], p["facility_level_option"], lon, lat, lon, lat, p["geocoordinates_source"],
             p["last_updated"] or None, FACILITY_SOURCE))
    # the COD-AB polygon decides the LGA; the ward only when the ward's own LGA is that one
    conn.execute("UPDATE facility f SET lga_pcode = l.pcode FROM lga l WHERE ST_Within(f.geom, l.geom)")
    conn.execute("UPDATE facility f SET ward_code = w.wardcode FROM ward w WHERE ST_Within(f.geom, w.geom) "
                 "AND w.lga_pcode = f.lga_pcode")


def import_places(conn) -> Counter:
    n: Counter = Counter()
    for kind, sql in (("lga", "SELECT name, pcode, ST_PointOnSurface(geom) FROM lga"),
                      ("ward", "SELECT name, lga_pcode, ST_PointOnSurface(geom) FROM ward")):
        for name, lga, pt in conn.execute(sql).fetchall():
            conn.execute("INSERT INTO place (name, name_key, kind, lga_pcode, geom, source) VALUES (%s, %s, %s, %s, "
                         "%s, %s)", (name, name_key(name), kind, lga, pt, "COD-AB" if kind == "lga" else "GRID3"))
            n[kind] += 1
    for alias, name in ALIASES.items():                    # other spellings of an LGA find it too
        conn.execute("INSERT INTO place (name, name_key, kind, lga_pcode, geom, source) SELECT %s, %s, 'lga', pcode, "
                     "ST_PointOnSurface(geom), 'alias' FROM lga WHERE pcode = %s", (name, name_key(alias), PCODES[name]))
    for file, source, name_field in (("osm_places_sokoto.geojson", "OpenStreetMap", "name"),
                                     ("grid3_settlements_sokoto.geojson", "GRID3 settlement names", "set_name")):
        for f in load(file):
            p, g = f["properties"], f.get("geometry") or {}
            name = p.get(name_field) or p.get("name") or p.get("name:ha")
            if not name or g.get("type") != "Point":
                continue
            kind = p.get("place") or "settlement"
            # only places inside Sokoto, with the LGA their point falls in
            conn.execute("INSERT INTO place (name, name_key, kind, lga_pcode, geom, source) SELECT %s, %s, %s, l.pcode, "
                         "ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s FROM lga l WHERE ST_Within(ST_SetSRID("
                         "ST_MakePoint(%s, %s), 4326), l.geom)",
                         (name, name_key(name), kind, *g["coordinates"][:2], source, *g["coordinates"][:2]))
            n[source] += 1
    return n


def quality_report(conn, national: int, places: Counter) -> str:
    q = lambda sql, *a: conn.execute(sql, a).fetchall()        # noqa: E731
    total = q("SELECT count(*) FROM facility")[0][0]
    out = ["# Facility data-quality report", "",
           f"Source: {FACILITY_SOURCE}. National file: {national:,} facilities; Sokoto (state == \"Sokoto\"): "
           f"{total:,}.", ""]
    out += ["## By level and ownership", "", "| level | public | private | other | total |", "|---|---|---|---|---|"]
    for lvl, pub, pri, oth, tot in q("SELECT coalesce(level, '(none)'), count(*) FILTER (WHERE ownership = 'Public'), "
                                     "count(*) FILTER (WHERE ownership = 'Private'), count(*) FILTER (WHERE ownership "
                                     "NOT IN ('Public', 'Private') OR ownership IS NULL), count(*) FROM facility "
                                     "GROUP BY 1 ORDER BY 5 DESC"):
        out.append(f"| {lvl} | {pub} | {pri} | {oth} | {tot} |")
    out += ["", "Ownership types: " + ", ".join(f"{t or '(none)'} {n}" for t, n in q(
        "SELECT ownership_type, count(*) FROM facility GROUP BY 1 ORDER BY 2 DESC"))]
    out += ["", "Coordinates from: " + ", ".join(f"{t or '(none)'} {n}" for t, n in q(
        "SELECT coord_source, count(*) FROM facility GROUP BY 1 ORDER BY 2 DESC")), ""]
    outside = q("SELECT name, lga_attr, ST_X(geom), ST_Y(geom) FROM facility WHERE geom IS NULL OR lga_pcode IS NULL "
                "OR (ST_X(geom) = 0 AND ST_Y(geom) = 0) ORDER BY name")
    out += [f"## Outside Sokoto's boundary, 0/0 or no coordinates: {len(outside)}", ""]
    out += [f"- {n} (file LGA {lga}): {'no point' if x is None else f'{y:.5f}, {x:.5f}'}" for n, lga, x, y in outside[:40]]
    rows = q("SELECT f.name, f.lga_attr, l.name, f.lga_flag FROM facility f JOIN lga l ON l.pcode = f.lga_pcode")
    lga_off = [(n, a, b, flag) for n, a, b, flag in rows if pcode(a or "") != pcode(b)]
    flagged = sum(1 for *_, flag in rows if flag)
    out += ["", f"## LGA from the point vs the file's own lga: {len(lga_off)} disagree "
            f"(the file flags {flagged} with lga_name_disagreement; "
            f"{sum(1 for *_, f in lga_off if f)} of the {len(lga_off)} are among them)", ""]
    out += [f"- {n}: file {a}, point in {b}{' (flagged)' if flag else ''}" for n, a, b, flag in lga_off[:40]]
    wards = q("SELECT f.name, f.ward_attr, w.name, f.ward_flag FROM facility f JOIN ward w ON w.wardcode = f.ward_code")
    ward_off = [(n, a, b, flag) for n, a, b, flag in wards if not same_ward(a or "", b)]
    spelling = sum(1 for _, a, b, _ in wards if name_key(a or "") != name_key(b) and same_ward(a or "", b))
    out += ["", f"## Ward from the point vs the file's own ward: {len(ward_off)} of {len(wards)} are a different ward "
            f"(and {spelling} more differ only in spelling: Rara / Rarah, 'Tudun Wada B (Sokoto South)'); the file "
            f"flags {sum(1 for *_, f in wards if f)} with ward_name_disagreement, "
            f"{sum(1 for *_, f in ward_off if f)} of these among them", ""]
    out += [f"- {n}: file {a}, point in {b}{' (flagged)' if flag else ''}" for n, a, b, flag in ward_off[:25]]
    border = q("SELECT f.name, l.name, w.name, w.grid3_lga_name FROM facility f JOIN lga l ON l.pcode = f.lga_pcode "
               "JOIN ward w ON ST_Within(f.geom, w.geom) WHERE w.lga_pcode IS DISTINCT FROM f.lga_pcode ORDER BY 1")
    out += ["", f"## Border mismatches between the layers: {len(border)} facilities inside a GRID3 ward of one LGA "
            "but the COD-AB polygon of another (COD-AB decides the LGA; the ward is not used for them)", ""]
    out += [f"- {n}: COD-AB {lga}; GRID3 ward {w} of {wl}" for n, lga, w, wl in border[:25]]
    no_ward = q("SELECT count(*) FROM facility WHERE lga_pcode IS NOT NULL AND ward_code IS NULL")[0][0]
    out += [f"", f"Inside an LGA but in no ward of that LGA (gaps or border): {no_ward}"]
    dups = q("SELECT a.name, b.name, a.lga_attr, round(ST_Distance(a.geom::geography, b.geom::geography)) FROM facility a "
             "JOIN facility b ON a.fid < b.fid AND ST_DWithin(a.geom::geography, b.geom::geography, 200) "
             "WHERE regexp_replace(lower(a.name), '[^a-z0-9]', '', 'g') = regexp_replace(lower(b.name), '[^a-z0-9]', "
             "'', 'g') ORDER BY 1")
    same_point = q("SELECT count(*) FROM (SELECT geom FROM facility WHERE geom IS NOT NULL GROUP BY geom "
                   "HAVING count(*) > 1) x")[0][0]
    out += ["", f"## Duplicates: {len(dups)} pairs with the same name within 200 m; {same_point} points shared by "
            "more than one facility", ""]
    out += [f"- {a} / {b} ({lga}, {d:.0f} m apart)" for a, b, lga, d in dups[:25]]
    out += [f"- same point: {names} ({lga})" for names, lga in q(
        "SELECT string_agg(name, ' / ' ORDER BY name), min(lga_attr) FROM facility WHERE geom IS NOT NULL "
        "GROUP BY geom HAVING count(*) > 1")]
    miss = q("SELECT count(*) FILTER (WHERE coalesce(name, '') = ''), count(*) FILTER (WHERE level IS NULL), "
             "count(*) FILTER (WHERE level_option IS NULL), count(*) FILTER (WHERE ownership IS NULL), "
             "count(*) FILTER (WHERE lga_attr IS NULL), count(*) FILTER (WHERE ward_attr IS NULL), "
             "count(*) FILTER (WHERE nhfr_code IS NULL), count(*) FILTER (WHERE last_updated IS NULL) FROM facility")[0]
    out += ["", "## Missing fields", "", "| name | level | level option | ownership | lga | ward | NHFR code | "
            "last updated |", "|---|---|---|---|---|---|---|---|", "| " + " | ".join(map(str, miss)) + " |"]
    out += ["", "Functional status: not in this file (no field); phone numbers: none.",
            "", "## Gazetteer (places inside Sokoto, by source)", "",
            ", ".join(f"{s}: {n:,}" for s, n in q("SELECT source, count(*) FROM place GROUP BY 1 ORDER BY 2 DESC")),
            "", "GRID3 settlement names: no file in data/geo/ yet (grid3_settlements_sokoto.geojson is read when "
            "present)." if not places.get("GRID3 settlement names") else ""]
    return "\n".join(out) + "\n"


def main() -> None:
    codab, wards = load("sokoto_lga_codab.geojson"), load("sokoto_wards_grid3.geojson")
    national = load("health_facilities_nga.geojson")
    if not codab or not wards:
        raise SystemExit("data/geo/ needs sokoto_lga_codab.geojson and sokoto_wards_grid3.geojson")
    facilities = [f for f in national if (f["properties"].get("state") or "") == "Sokoto"]
    unknown = sorted({f["properties"].get("lga") for f in facilities if not pcode(f["properties"].get("lga") or "")}
                     - {None})
    if unknown or len(CANONICAL) != len(codab):
        raise SystemExit(f"crosswalk: LGA names it doesn't know: {unknown}")
    with psycopg.connect(get_settings().db_url()) as conn:
        import_lgas(conn, codab, wards, facilities)
        import_wards(conn, wards)
        import_facilities(conn, facilities)
        places = import_places(conn)
        report = quality_report(conn, len(national), places)
    REPORT.write_text(report, encoding="utf-8")
    print(report)
    print("report:", REPORT)


if __name__ == "__main__":
    main()
