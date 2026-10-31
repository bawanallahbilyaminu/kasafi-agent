"""Verified facility corrections (data/geo/facility_corrections.yaml): validation, and answers saying when a
location was checked."""

from datetime import date

import pytest

from app.geo import corrections as fixes
from app.geo import facilities as fac
from app.geo import facility_info as fi


def test_a_valid_correction_records_what_was_fixed_and_who_checked() -> None:
    [c] = fixes.parse([{"nhfr_code": "33/21/1/1/1/0003", "lat": 13.034, "lon": 5.199, "kind": "Primary Health Center",
                        "verified_by": "Bilyaminu", "verified_on": "2026-11-01", "note": "site visit"}])
    assert c.match == {"nhfr_code": "33/21/1/1/1/0003"} and c.fields == ["location", "kind"]
    assert c.record() == {"fields": ["location", "kind"], "verified_by": "Bilyaminu", "verified_on": "2026-11-01",
                          "note": "site visit"}
    assert fixes.parse([{"registry_name": "Alheri Clinic", "lga": "Wamako", "name": "Alheri Clinic Arkilla",
                         "verified_by": "B", "verified_on": date(2026, 11, 1)}])[0].fields == ["name"]


@pytest.mark.parametrize("entry,problem", [
    ({"nhfr_code": "x", "lat": 13.0, "lon": 5.2}, "verified_by and verified_on"),
    ({"nhfr_code": "x", "lat": 13.0, "verified_by": "B", "verified_on": "2026-11-01"}, "lat and lon go together"),
    ({"nhfr_code": "x", "lat": 9.0, "lon": 7.4, "verified_by": "B", "verified_on": "2026-11-01"}, "outside Sokoto"),
    ({"lat": 13.0, "lon": 5.2, "verified_by": "B", "verified_on": "2026-11-01"}, "nhfr_code, fid or registry_name"),
    ({"nhfr_code": "x", "verified_by": "B", "verified_on": "2026-11-01"}, "nothing to correct"),
    ({"nhfr_code": "x", "level": "Big", "verified_by": "B", "verified_on": "2026-11-01"}, "level must be"),
    ({"nhfr_code": "x", "lat": 13.0, "lon": 5.2, "verified_by": "B", "verified_on": "1 Nov"}, "verified_on"),
])
def test_an_invalid_correction_stops_the_import(entry, problem) -> None:
    with pytest.raises(fixes.CorrectionError, match=problem):
        fixes.parse([entry])


def test_only_a_location_fix_is_mentioned_in_answers() -> None:
    assert fixes.checked_on({"fields": ["location"], "verified_on": "2026-11-01"}) == "2026-11-01"
    assert fixes.checked_on({"fields": ["name"], "verified_on": "2026-11-01"}) == ""
    assert fixes.checked_on(None) == ""


def test_facility_answers_say_when_a_location_was_checked() -> None:
    f = fac.Facility("a", "Arkilla PHC", "Primary", "Primary Health Center", "Public", "", 13.03, 5.2, "Wamakko",
                     "Wamako", 1.2, checked="2026-11-01")
    text = fac.facilities_text("en", [f], fac.Filters())
    assert "Arkilla PHC" in text and "(location checked 1 Nov 2026)" in text
    assert "an tabbatar da wurin 1 Nov 2026" in fac.route_text("ha", f, "car", False)
    r = fi.Registered("a", "Arkilla PHC", "Primary", "Primary Health Center", "Public", "Arkilla", "Wamakko",
                      "Wamako", 13.03, 5.2, checked="2026-11-01")
    assert "(location checked 1 Nov 2026)" in fi.card(r, "en")
    assert fi.as_facility(r).checked == "2026-11-01"
    plain = fac.Facility("b", "Salewa", "Primary", "", "Public", "", 13.0, 5.2, "Wamakko", "Wamako", 1.0)
    assert "checked" not in fac.facilities_text("en", [plain], fac.Filters())


def test_the_local_corrections_file_is_valid() -> None:
    from pathlib import Path
    p = Path("data/geo/facility_corrections.yaml")
    if not p.exists():
        pytest.skip("data/geo/ not present (not in git)")
    assert all(c.verified_by and c.verified_on for c in fixes.load(p))       # parse() raises on a bad entry


def test_remove_and_hide_entries() -> None:
    gone, held = fixes.parse([
        {"fid": "536eb69c", "remove": True, "verified_by": "B", "verified_on": "2026-10-31", "note": "not a facility"},
        {"nhfr_code": "33/21/1/2/2/0056", "hide": True, "verified_by": "B", "verified_on": "2026-10-31"}])
    assert gone.fields == ["removed"] and gone.remove and held.fields == ["hidden"] and held.hide
    with pytest.raises(fixes.CorrectionError, match="removal can't also change"):
        fixes.parse([{"fid": "x", "remove": True, "name": "Y", "verified_by": "B", "verified_on": "2026-10-31"}])


class _Conn:
    """Records the SQL an apply runs; `found` answers the facility lookup."""
    def __init__(self, found):
        self.found, self.sql = found, []

    def execute(self, sql, args=()):
        self.sql.append((sql, args))
        rows = self.found if sql.startswith("SELECT fid, name FROM facility") else []

        class R:
            def fetchall(self):
                return rows
        return R()


def test_apply_removes_hides_and_tolerates_an_earlier_removal() -> None:
    [gone] = fixes.parse([{"fid": "s1", "remove": True, "verified_by": "B", "verified_on": "2026-10-31"}])
    conn = _Conn([("s1", "Salewa Health Post")])
    assert fixes.apply(conn, [gone]) == ["- Salewa Health Post: removed (verified by B, 31 Oct 2026)"]
    assert any(s.startswith("DELETE FROM facility WHERE") for s, _ in conn.sql)
    assert any(s.startswith("DELETE FROM facility_capability") for s, _ in conn.sql)
    assert fixes.apply(_Conn([]), [gone]) == ["- {'fid': 's1'}: removed (already gone)"]       # a re-run
    [held] = fixes.parse([{"nhfr_code": "x", "hide": True, "verified_by": "B", "verified_on": "2026-10-31"}])
    conn = _Conn([("x1", "Sarda Quarters Health Clinic")])
    fixes.apply(conn, [held])
    assert conn.sql[0][0] == "UPDATE facility SET hidden = false WHERE hidden"            # reset first
    update = next((s, a) for s, a in conn.sql if s.startswith("UPDATE facility SET correction"))
    assert "hidden = %s" in update[0] and True in update[1]
