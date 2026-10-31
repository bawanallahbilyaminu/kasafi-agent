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


def test_the_template_file_parses_and_applies_nothing() -> None:
    from pathlib import Path
    p = Path("data/geo/facility_corrections.yaml")
    if p.exists():
        assert fixes.load(p) == []
