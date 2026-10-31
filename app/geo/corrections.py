"""Verified fixes that override the GRID3 / NHFR facility registry at import (scripts/import_geo.py).

The file is data/geo/facility_corrections.yaml (outside git, like the registry). Each entry names one facility by
its NHFR code (preferred), its registry id (fid), or its registry name and LGA, and gives any of: `lat` and `lon`
together (a checked location), `name`, `level` (Primary / Secondary / Tertiary) and `kind` (the facility type, e.g.
"Primary Health Center"); or `remove: true` (not a health facility: deleted from the table, with its EmONC links)
or `hide: true` (held back from every answer until confirmed; deleting the entry shows it again on the next
apply). Every entry needs `verified_by` and `verified_on` (a date); an entry without them, or with a location
outside Sokoto State's box, is refused, and the import stops so nothing half-applies. Name an entry by nhfr_code or
fid so it still matches after a rename; a removal that no longer matches is reported as already done.

    corrections:
      - nhfr_code: "33/21/1/1/1/0003"
        lat: 13.0339
        lon: 5.1993
        verified_by: Bilyaminu (site visit)
        verified_on: 2026-11-01
        note: the registry point is 600 m off

What was fixed is stored on the facility (`correction`), and facility answers say "location checked <date>" for a
corrected location.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

PATH = Path("data/geo/facility_corrections.yaml")
BOX = (12.0, 14.1, 3.4, 6.9)                # Sokoto State, lat and lon bounds, with a margin
LEVELS = ("Primary", "Secondary", "Tertiary")


class CorrectionError(ValueError):
    pass


@dataclass
class Correction:
    match: dict                              # nhfr_code | fid | name + lga
    verified_by: str
    verified_on: date
    lat: float | None = None
    lon: float | None = None
    name: str = ""
    level: str = ""
    kind: str = ""
    note: str = ""
    remove: bool = False
    hide: bool = False
    fields: list[str] = field(default_factory=list)

    def record(self) -> dict:
        return {"fields": self.fields, "verified_by": self.verified_by, "verified_on": self.verified_on.isoformat(),
                "note": self.note}


def parse(entries: list[dict]) -> list[Correction]:
    out, problems = [], []
    for i, e in enumerate(entries or [], 1):
        match = ({"nhfr_code": str(e["nhfr_code"])} if e.get("nhfr_code") else {"fid": str(e["fid"])} if e.get("fid")
                 else {"name": e["registry_name"], "lga": e.get("lga", "")} if e.get("registry_name") else {})
        on = e.get("verified_on")
        if isinstance(on, str):
            try:
                on = date.fromisoformat(on)
            except ValueError:
                on = None
        c = Correction(match, str(e.get("verified_by") or "").strip(), on, e.get("lat"), e.get("lon"),
                       str(e.get("name") or "").strip(), str(e.get("level") or "").strip(),
                       str(e.get("kind") or "").strip(), str(e.get("note") or "").strip(), bool(e.get("remove")),
                       bool(e.get("hide")))
        c.fields = [f for f, there in (("location", c.lat is not None), ("name", c.name), ("level", c.level),
                                       ("kind", c.kind), ("removed", c.remove), ("hidden", c.hide)) if there]
        if c.remove and len(c.fields) > 1:
            problems.append(f"entry {i}: a removal can't also change the facility")
        if not match:
            problems.append(f"entry {i}: name it by nhfr_code, fid or registry_name")
        if not c.verified_by or not isinstance(on, date):
            problems.append(f"entry {i}: verified_by and verified_on (YYYY-MM-DD) are required")
        if (c.lat is None) != (c.lon is None):
            problems.append(f"entry {i}: lat and lon go together")
        if c.lat is not None and c.lon is not None and not (BOX[0] <= float(c.lat) <= BOX[1] and BOX[2] <= float(c.lon) <= BOX[3]):
            problems.append(f"entry {i}: {c.lat}, {c.lon} is outside Sokoto State")
        if c.level and c.level not in LEVELS:
            problems.append(f"entry {i}: level must be one of {', '.join(LEVELS)}")
        if not c.fields:
            problems.append(f"entry {i}: nothing to correct")
        out.append(c)
    if problems:
        raise CorrectionError("; ".join(problems))
    return out


def load(path: Path = PATH) -> list[Correction]:
    if not path.exists():
        return []
    return parse((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("corrections") or [])


def _where(c: Correction) -> tuple[str, tuple]:
    if "nhfr_code" in c.match:
        return "nhfr_code = %s", (c.match["nhfr_code"],)
    if "fid" in c.match:
        return "fid = %s", (c.match["fid"],)
    return "lower(name) = lower(%s) AND (%s = '' OR lower(lga_attr) = lower(%s))", (
        c.match["name"], c.match["lga"], c.match["lga"])


def apply(conn, corrections: list[Correction]) -> list[str]:
    """Apply each correction (exactly one facility must match), then place moved facilities in their LGA and ward
    again. Hidden flags are set afresh each time (an entry taken out of the file shows its facility again). Returns
    one line per correction for the import report."""
    lines = []
    conn.execute("UPDATE facility SET hidden = false WHERE hidden")
    for c in corrections:
        where, args = _where(c)
        found = conn.execute(f"SELECT fid, name FROM facility WHERE {where}", args).fetchall()
        if c.remove and not found:
            lines.append(f"- {c.match}: removed (already gone)")
            continue
        if len(found) != 1:
            raise CorrectionError(f"{c.match}: {len(found)} facilities match (exactly one must)")
        fid, was = found[0]
        stamp = f"(verified by {c.verified_by}, {c.verified_on:%d %b %Y})"
        if c.remove:
            conn.execute("DELETE FROM facility_capability WHERE fid = %s", (fid,))
            conn.execute("DELETE FROM facility WHERE fid = %s", (fid,))
            lines.append(f"- {was}: removed {stamp}")
            continue
        sets, vals = ["correction = %s", "hidden = %s"], [json.dumps(c.record()), c.hide]
        if c.lat is not None:
            sets.append("geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326)")
            vals += [float(c.lon), float(c.lat)]
        for col, v in (("name", c.name), ("level", c.level), ("level_option", c.kind)):
            if v:
                sets.append(f"{col} = %s")
                vals.append(v)
        conn.execute(f"UPDATE facility SET {', '.join(sets)} WHERE fid = %s", (*vals, fid))
        lines.append(f"- {was}: {', '.join(c.fields)} {stamp}")
    if any(c.lat is not None for c in corrections):
        conn.execute("UPDATE facility f SET lga_pcode = l.pcode FROM lga l WHERE f.correction IS NOT NULL "
                     "AND ST_Within(f.geom, l.geom)")
        conn.execute("UPDATE facility f SET ward_code = (SELECT w.wardcode FROM ward w WHERE ST_Within(f.geom, w.geom) "
                     "AND w.lga_pcode = f.lga_pcode LIMIT 1) WHERE f.correction IS NOT NULL")
    return lines


def checked_on(correction: dict | None) -> str:
    """The date a corrected location was checked ('' when the location is the registry's)."""
    c = correction or {}
    return c.get("verified_on", "") if "location" in (c.get("fields") or []) else ""
