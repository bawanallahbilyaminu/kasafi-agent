"""Flood answers over the whole record (app/place/flood_record.py): GFM first, UNOSAT quoted beside it with the
reason, never averaged; the share radar can't judge always said; the floodplain apart from farmland; our radar as
the check; plain words, no 'x% against its usual x%'."""

from __future__ import annotations

from datetime import date

from app.place import flood_record as F

TODAY = date(2026, 11, 3)


def season(union=0.0, mx=0.0, doy=None, crop=0.0, plain=0.0, excl=0.45, passes=20, unosat=None, s1=None):
    r = {"gfm_union_ha": (union, passes), "gfm_max_ha": (mx, passes), "gfm_max_doy": (doy, passes),
         "gfm_crop_ha": (crop, passes), "gfm_plain_ha": (plain, passes), "gfm_excluded_share": (excl, passes)}
    if unosat is not None:
        r["unosat_ha"] = (unosat, None)
    if s1 is not None:
        r["s1_flood_share"] = (s1, 13)
    return r


DRY = {2015: season(), 2022: season(unosat=0.0, s1=0.0), 2024: season(unosat=52.0, s1=0.0), 2026: season()}
WET = {2015: season(1070, 1060, 239, 640, 200), 2022: season(0, unosat=1610, s1=0.023),
       2024: season(370, 260, 240, 210, 110, unosat=1040, s1=0.028), 2026: season(5, 3, 250, 5, 0)}


def test_a_dry_ward_says_no_floodwater_seen_with_the_seasons_and_passes_never_never_flooded() -> None:
    s = F.record_line(DRY, "Bado", "en", TODAY)
    assert s.startswith("No floodwater was seen in Bado on any satellite radar pass in the rainy seasons 2015–2026")
    assert "4 seasons, 80 passes" in s and "never" not in s and "(2026 so far)" not in s


def test_the_largest_season_and_where_farmland_floodplain_other() -> None:
    s = F.record_line(WET, "Gidan Bubu", "en", TODAY)
    assert "in 3 of the 4 rainy seasons 2015–2026: 2015, 2024, 2026" in s
    assert "The largest was in 2015: about 1,060 ha on its biggest pass (27 August 2015)" in s
    assert "(640 ha on farmland, 200 ha in the river floodplain, 230 ha on other land)" in s


def test_radar_and_unosat_quoted_side_by_side_with_the_reason_never_averaged() -> None:
    lines = F.compare_lines(DRY, "en")
    assert len(lines) == 1 and lines[0].startswith("In 2024, radar passes saw no floodwater; UNOSAT's event map of ")
    assert "shows 52 ha. UNOSAT's map covers several days, so it catches more of the flood than single passes." in lines[0]
    wet = F.compare_lines(WET, "en")
    assert [x[:8] for x in wet] == ["In 2022,", "In 2024,"]          # 2022: radar saw none, UNOSAT 1,610 ha: both said
    assert F.compare_lines(WET, "en", [2022])[0].startswith("In 2022, radar passes saw no floodwater")


def test_a_map_year_without_radar_passes_is_never_radar_saw_nothing() -> None:
    rec = {2022: {"unosat_ha": (1610.0, None), "s1_flood_share": (0.023, 14)}}
    assert F.compare_lines(rec, "en")[0].startswith("In 2022, no radar passes are on file;")
    assert F.compare_lines(DRY, "ha")[0].startswith("A 2024, hotunan radar ba su ga ruwan ambaliya ba;")


def test_a_ward_flooded_every_season_says_every_season_not_a_list_of_years() -> None:
    every = {y: season(50, 40, 250, 30, 20) for y in range(2015, 2027)}
    s = F.record_line(every, "Gidan Bubu", "en", TODAY)
    assert s.startswith("Satellite radar saw floodwater in Gidan Bubu in every rainy season 2015–2026 (12 seasons).")


def test_the_share_radar_cant_judge_is_always_said() -> None:
    s = F.excluded_line(DRY, {"land_ha": 3133.0}, "Bado", "en")
    assert s.startswith("Radar can't judge 45% of Bado (about 1,410 ha: built-up land")
    assert "for built-up parts, flood reports are the source" in s


def test_the_floodplain_and_the_check() -> None:
    assert F.plain_line({"jrc_plain_ha": 0.0}, "Bado", "en").startswith("No part of Bado was under water in any year")
    assert "water covered 280 ha of Gidan Bubu in some years" in F.plain_line({"jrc_plain_ha": 280, "jrc_often_ha": 12},
                                                                              "Gidan Bubu", "en")
    assert F.check_line(DRY, "en").startswith("Kasafi's own radar check (Sentinel-1, 2022–2024) agrees")
    assert "found floodwater in 2022, 2024; the most in 2024 (2.8% of that farmland)" in F.check_line(WET, "en")


def test_a_year_asked_leads_in_plain_words() -> None:
    assert F.year_line(DRY, "Bado", 2024, "en") == "No floodwater was seen on Bado's land in 2024 on any of its 20 radar passes."
    assert F.year_line(DRY, "Bado", 2019, "en").startswith("No radar season is on file for 2019")
    lines = F.unit_lines(None, DRY, {"land_ha": 3133.0}, "Bado", "en", TODAY, 2024)
    assert lines[0].startswith("No floodwater was seen on Bado's land in 2024") and "against its usual" not in " ".join(lines)


def test_the_map_year_is_the_year_asked_or_none_else_the_largest_season() -> None:
    assert F.map_year(WET, 2024, TODAY) == 2024 and F.map_year(WET, 2019, TODAY) is None
    assert F.map_year(WET, None, TODAY) == 2015 and F.map_year(DRY, None, TODAY) == 2026   # dry: the latest complete
    assert F.map_year(DRY, None, date(2026, 9, 1)) == 2024


def test_the_current_season_is_so_far_until_october_ends() -> None:
    assert F.record_line(DRY, "Bado", "en", date(2026, 9, 20)).endswith("(2026 so far)")
    assert not F.complete(2026, date(2026, 10, 31)) and F.complete(2026, date(2026, 11, 1))


def test_hausa_uses_the_same_figures_and_the_respectful_plural() -> None:
    s = F.record_line(DRY, "Bado", "ha", TODAY)
    assert s.startswith("Ba a ga ruwan ambaliya a Bado ba") and "hotuna 80" in s
    assert "hekta 52" in F.compare_lines(DRY, "ha")[0]
    assert F.T["ha"]["scope"].startswith("Wurinku")
