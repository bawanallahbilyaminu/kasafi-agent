"""Place history step 3: the planner route and answer (the answer and the map against the dev database's
ward_history rows; skipped without them)."""

from __future__ import annotations

from datetime import date

import pytest

from app.place import planner as P

TODAY = date(2026, 10, 31)


@pytest.mark.parametrize("q,want", [
    ("Which wards of Wurno LGA were greenest in 2024?", ("lga", "NG034022")),
    ("Waɗanne gundumomin Ƙaramar Hukumar Wurno ne suka fi koriya a 2024?", ("lga", "NG034022")),
    ("Share of cropland flooded in 2022 across Sokoto State", ("state", "NG034")),
    ("Which LGAs had the most bare soil in the dry season?", ("state", "NG034")),
    ("Flood share by ward in Wamakko", ("lga", "NG034021")),
])
def test_area_questions_route_to_the_lga_or_the_state(q, want) -> None:
    assert P.area_route(q) == want


@pytest.mark.parametrize("q", [
    "How green was my farm in 2024?", "Was my plot in Wurno flooded?", "How much was budgeted for farms in Wurno?",
    "Will it rain in Wurno tomorrow?", "Nearest hospital in Wurno",
    # no satellite measure named: displacement, facilities and population rankings keep their own paths (the 1 Nov
    # fresh eval had 'which 10 LGAs get most IDPs?' answered with greenness)
    "How many IDPs ne a Gada LGA?", "Abeg, which 10 LGAs ne a Sokoto da get most IDPs?",
    "Which LGAs have the most people displaced?", "Which LGAs have the most health facilities?", "Rank LGAs by population",
    "Wadanne kananan hukumomi ne suka fi yawan 'yan gudun hijira?",
])
def test_pin_budget_weather_and_facility_questions_do_not_route_to_an_area(q) -> None:
    assert P.area_route(q) is None


def test_a_question_naming_no_measure_has_none() -> None:
    assert P.measure_word("which LGAs have most IDPs") is None and P.measure_asked("which LGAs have most IDPs") == "greenness"
    assert P.measure_word("greenest wards") == "greenness"


def test_the_measure_and_year_come_from_the_words() -> None:
    assert P.measure_asked("which wards flooded most in 2022") == "flood"
    assert P.measure_asked("wards inside the UN flood map") == "flood_map"
    assert P.measure_asked("bare soil spreading by ward") == "bare"
    assert P.measure_asked("wettest wards by rainfall") == "rain"
    assert P.measure_asked("vegetation decline by ward") == "greenness"
    assert P.measure_asked("ambaliya a gundumomin Goronyo") == "flood"
    assert P.year_asked("floods in 2022 across the state", TODAY) == 2022 and P.year_asked("which wards", TODAY) is None


def test_a_units_series_drops_its_low_data_years() -> None:
    rows = {y: (0.5, 18) for y in range(2017, 2025)}
    rows[2025] = (0.25, 5)                                  # five composites against a usual 18: out
    rows[2026] = (0.58, 18)
    s = P.drop_low_data(rows)
    assert 2025 not in s and 2026 in s and len(s) == 9
    assert P.drop_low_data({2022: (0.1, None), 2023: (0.2, None)}) == {2022: 0.1, 2023: 0.2}


def test_low_data_cut_is_relative_to_the_median_count() -> None:
    rows = [("a", "A", 0.5, 17), ("b", "B", 0.4, 16), ("c", "C", 0.3, 5), ("d", "D", 0.2, 18), ("e", "E", None, 0)]
    assert P.low_data_cut(rows, "modis_peak") == 10               # 60% of 16.5 -> 10: at or under 10 is low data
    assert P.low_data_cut(rows, "unosat_share") == -1


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT 1 FROM ward_history WHERE measure = 'modis_peak' AND year = 2024 LIMIT 1").fetchone():
            pytest.skip("ward_history not precomputed for 2024")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_versus_usual_and_the_plain_words() -> None:
    assert P.versus_usual(0.60, 0.52, "greenness") == "above" and P.versus_usual(0.55, 0.52, "greenness") == "near"
    assert P.versus_usual(0.40, 0.52, "greenness") == "below" and P.versus_usual(None, 0.5, "greenness") == ""
    assert P.versus_usual(600, 500, "rain") == "above" and P.versus_usual(520, 500, "rain") == "near"
    assert P.versus_usual(0.3, 0.5, "bare") == "below" and P.versus_usual(0.3, 0, "rain") == ""


def test_the_lga_answer_opens_in_plain_words_then_names_the_wards_and_ranks_them(conn) -> None:
    a = P.area_answer(conn, "Which wards of Wurno LGA were greenest in 2024?", "", "en", "lga", "NG034022", TODAY)
    assert a.found and a.year == 2024 and a.level == "ward"
    lines = a.text.split("\n\n")
    assert lines[1].startswith("Most of Wurno LGA's farmland was") and "least green ward" in lines[1]   # plain words first
    assert "its rain" in lines[1] and not any(ch.isdigit() for ch in lines[1].replace("2024", ""))
    assert "wards of Wurno LGA, 2024" in a.text and "Greenest:" in a.text and "Least green:" in a.text
    assert "*Ranking (" in a.text and "250 m" not in a.text                  # the technical description is in working
    assert "Kasafi reports what the satellite record shows" in a.text
    assert a.working.startswith("Measure: peak rainy-season greenness") and "Period 2001" in a.working and "250 m" in a.working
    assert "All wards, modis_peak, 2024" in a.working and a.specs[0]["kind"] == "area_map"
    ha = P.area_answer(conn, "Waɗanne gundumomin Wurno ne suka fi koriya a 2024?", "", "ha", "lga", "NG034022", TODAY)
    assert "gundumomin Ƙaramar Hukumar Wurno, 2024" in ha.text and "Mafi koriya:" in ha.text
    assert ha.text.split("\n\n")[1].startswith("Mafi yawan gonakin Ƙaramar Hukumar Wurno")


def test_no_budget_line_for_the_lga_gives_the_statewide_totals_never_just_no_line(conn) -> None:
    a = P.area_answer(conn, "Which wards of Wurno LGA were greenest in 2024?", "", "en", "lga", "NG034022", TODAY)
    if "budget lines for Wurno LGA" in a.text:
        pytest.skip("Wurno has its own lines in this budget")
    assert "No 2026 budget line names Wurno; statewide lines that may cover it:" in a.text
    assert "• Agriculture: ₦" in a.text and "statewide lines are not split by LGA" in a.text
    assert "matches agriculture" not in a.text
    totals = P.statewide_totals(conn)
    assert totals and totals[0]["agriculture"][0] > 0 and totals[2] == 2026


def test_flood_answers_lead_with_the_un_map_and_give_radar_as_a_lower_bound(conn) -> None:
    a = P.area_answer(conn, "Share of cropland flooded in 2022 across Sokoto State", "", "en", "state", "NG034", TODAY)
    assert a.found and a.level == "lga" and a.year == 2022
    assert a.text.startswith("*Share of cropland inside the UN flood map: the 23 LGAs of Sokoto State, 2022* — experimental")
    assert a.working.startswith("Measure: UN satellite flood map of 1–25 October 2022 (UNOSAT, VIIRS 375 m)")
    assert a.text.split("\n\n")[1].startswith("The UN satellite flood map of 1–25 October 2022 covered")
    assert "*Open floodwater seen by radar, a lower bound*" in a.text and "misses water under crops" in a.text
    assert "The two differ because" in a.text
    assert a.text.index("UN satellite flood map") < a.text.index("lower bound")
    assert [s["key"] for s in a.specs] == ["flood_map", "flood"] and a.measure == "unosat_share"
    assert "s1_flood_share" in a.working and "unosat_share" in a.working
    b = P.area_answer(conn, "Which LGAs flooded most in 2020?", "", "en", "state", "NG034", TODAY)
    assert b.text.startswith("*Open-floodwater share of normally dry cropland (radar): the 23 LGAs of Sokoto State, 2020*")
    assert "No UN satellite flood map covers Sokoto for 2020" in b.text and [s["key"] for s in b.specs] == ["flood"]
    c = P.area_answer(conn, "Which LGAs flood most?", "", "en", "state", "NG034", TODAY)
    assert c.year == 2024 and c.specs[0]["key"] == "flood_map"          # no year: the latest year with an official map


def test_rain_by_ward_says_the_wards_share_the_lga_figure(conn) -> None:
    a = P.area_answer(conn, "wettest wards of Wurno by rainfall in 2024", "", "en", "lga", "NG034022", TODAY)
    assert "for all of them, because the ~9 km rain grid" in a.text and "wettest ward" not in a.text


def test_the_state_answer_compares_lgas_and_a_missing_year_is_said(conn) -> None:
    a = P.area_answer(conn, "Share of cropland inside the UN flood map in 2022 across Sokoto State", "", "en", "state",
                      "NG034", TODAY)
    assert a.found and a.level == "lga" and a.year == 2022 and "the 23 LGAs of Sokoto State, 2022" in a.text
    assert "Budget lines are linked per LGA" in a.text and "lower bound" not in a.text
    b = P.area_answer(conn, "greenness by LGA in 1999", "", "en", "state", "NG034", TODAY)
    assert not b.found and "1999" in b.text


def test_the_area_map_draws(conn) -> None:
    from app.maps.render import MAX_BYTES
    from app.place.images import area_map
    img = area_map(conn, {"kind": "area_map", "measure": "modis_peak", "key": "greenness", "year": 2024, "level": "ward",
                          "unit": "NG034022"}, "en", TODAY)
    assert img is not None and len(img.jpeg) <= MAX_BYTES and "Wurno LGA, 2024" in img.caption
    img = area_map(conn, {"kind": "area_map", "measure": "unosat_share", "key": "flood_map", "year": 2022, "level": "lga",
                          "unit": "NG034"}, "ha", TODAY)
    assert img is not None and "Jihar Sokoto" in img.caption


# --- 'my ward … over the years' (the 1 Nov phone test answered a pin's ward question with a statewide 2025 ranking)

PIN = {"lat": 13.0, "lon": 5.2, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Bado", "wardcode": "62102", "ward_likely": True}


@pytest.mark.parametrize("q,want", [
    ("How has farming evolved in my ward over the years", ("ward", "62102")),
    ("How green was my area in 2024?", ("ward", "62102")),
    ("Is farmland around here getting greener?", ("ward", "62102")),
    ("Yaya noma ya canza a unguwata tun shekaru?", ("ward", "62102")),
    ("Koriyar gundumata tun 2015", ("ward", "62102")),
    ("How has farming evolved in my LGA over the years", ("lga", "NG034021")),
    ("Yaya koriyar gonaki ta canza a ƙaramar hukumata?", ("lga", "NG034021")),
    ("How has farming evolved across the state over the years", ("state", "NG034")),
    ("Which wards of Sokoto State were greenest in 2024?", ("state", "NG034")),
    ("Yaya noma ya canza a faɗin jihar Sokoto?", ("state", "NG034")),
    ("Which wards of Wurno LGA were greenest in 2024?", ("lga", "NG034022")),       # a named LGA beats the pin
])
def test_the_scope_comes_from_the_words_and_the_location(q, want) -> None:
    assert P.area_route(q, "", PIN) == want


def test_my_ward_with_only_an_lga_on_file_takes_the_lga_and_with_nothing_asks_for_the_pin() -> None:
    assert P.area_route("How has farming evolved in my ward over the years", "", {"lga_pcode": "NG034021"}) == ("lga", "NG034021")
    assert P.area_route("How has farming evolved in my ward over the years") == ("ward", "")
    assert P.area_route("Yaya noma ya canza a unguwata?") == ("ward", "")
    assert P.area_route("How green was my farm in 2024?", "", PIN) is None             # the pin's own record


def test_trend_words_in_both_languages() -> None:
    for q in ("over the years", "how has it evolved", "since 2015", "the last 10 years", "tun shekaru", "ya canza", "tarihin"):
        assert P.trend_asked(q), q
    assert not P.trend_asked("greenest wards in 2024")
    assert P.year_asked("since 2015 in my ward", TODAY) is None and P.year_asked("in 2024 since 2015", TODAY) == 2024


class _Counts:
    """A connection whose only answer is the median observation count per year."""

    def __init__(self, medians):
        self.medians = medians

    def execute(self, q, args):
        year = args[2]
        m = self.medians.get(year)
        return type("R", (), {"fetchone": staticmethod(lambda: (m,))})()


def test_the_headline_year_skips_thin_years_and_unfinished_seasons() -> None:
    medians = {y: 16.0 for y in range(2001, 2025)}
    medians[2025], medians[2026] = 5.0, 18.0
    loaded = sorted(medians)
    assert P.headline_year(_Counts(medians), "modis_peak", "ward", loaded, date(2026, 10, 31)) == (2024, [2025])
    assert P.headline_year(_Counts(medians), "modis_peak", "ward", loaded, date(2026, 11, 1)) == (2026, [])
    assert P.headline_year(_Counts(medians), "modis_peak", "ward", loaded, date(2025, 12, 1)) == (2024, [2025])


def test_the_plain_class_agrees_with_the_rain_check() -> None:
    spec = P.MEASURES["greenness"]
    rows = [("a", "A", 0.40, 16), ("b", "B", 0.42, 16), ("c", "C", 0.45, 16)]
    usual = {"a": 0.55, "b": 0.55, "c": 0.55}                    # all below their own usual …
    b = P.Block("greenness", spec, 2024, rows, rows, [], [], 9, 0.42, {"a": "normal", "b": "normal", "c": "normal"}, usual)
    assert P.plain_class(b) == "near"                            # … but the rain explains it: never 'less green than usual'
    b.flags = {"a": "below", "b": "below", "c": "normal"}
    assert P.plain_class(b) == "below"
    b.flags = {}
    assert P.plain_class(b) == "below"                           # no rain fit: the units' own usual


def test_the_ward_answer_names_the_ward_gives_the_trend_and_never_headlines_a_thin_year(conn) -> None:
    q = "How has farming evolved in my ward over the years"
    a = P.area_answer(conn, q, "", "en", "ward", "62102", TODAY, place=PIN)
    assert a.found and a.level == "ward" and a.unit == "62102"
    lines = a.text.split("\n\n")
    assert lines[0].startswith("*Peak greenness: Bado ward (likely), Wamakko LGA*")            # plain head first
    assert lines[1].startswith("Your pin is in Bado ward (likely) of Wamakko LGA")
    assert lines[2].startswith("Since 20") and "Bado's farmland greenness" in lines[2] and "Wamakko LGA's" in lines[2] \
        and "the state's" in lines[2]
    assert a.year == 2024 and "In 2024 Bado was" in a.text and "2025 has too few clear images so far" in a.text
    assert "232" not in a.text and "*Ranking" not in a.text and "MODIS NDVI" not in a.text     # technical words in working
    assert a.working.startswith("Measure: peak rainy-season greenness") and "Series (Bado" in a.working
    assert a.specs == [{"kind": "area_map", "measure": "modis_peak", "key": "greenness", "year": 2024, "level": "ward",
                        "unit": "NG034021", "highlight": "62102"}]
    later = P.area_answer(conn, q, "", "en", "ward", "62102", date(2026, 11, 1), place=PIN)
    assert later.year == 2026 and "too few clear images" not in later.text                   # the 2026 season is complete
    ha = P.area_answer(conn, "Yaya noma ya canza a unguwata tun shekaru?", "", "ha", "ward", "62102", TODAY, place=PIN)
    assert ha.text.startswith("*Koriyar ƙololuwa: gundumar Bado (wataƙila), Ƙaramar Hukumar Wamakko*")
    assert "Wurinka yana gundumar Bado" in ha.text and "Tun 20" in ha.text and " sun fi koriya" not in ha.text
    sure = P.area_answer(conn, q, "", "en", "ward", "62102", TODAY, place={**PIN, "ward_likely": False})
    assert "(likely)" not in sure.text
    year = P.area_answer(conn, "How green was my ward in 2024?", "", "en", "ward", "62102", TODAY, place=PIN)
    assert year.year == 2024 and "Since 20" not in year.text


def test_my_ward_without_a_location_asks_for_the_pin(conn) -> None:
    a = P.area_answer(conn, "How has farming evolved in my ward over the years", "", "en", "ward", "", TODAY)
    assert a.needs_pin and not a.found and a.text.startswith("To look at a place's history I need the spot itself")


def test_the_lga_and_state_answers_open_in_plain_words_then_the_trend_and_the_technical_label_is_in_working(conn) -> None:
    a = P.area_answer(conn, "How has farming evolved in my LGA over the years", "", "en", "lga", "NG034021", TODAY, place=PIN)
    lines = a.text.split("\n\n")
    assert lines[0] == "*Peak greenness: wards of Wamakko LGA, 2024* — experimental"
    assert lines[1].startswith("Most of Wamakko LGA's farmland was") and lines[2].startswith("Since 20")
    assert "Wamakko LGA's farmland greenness" in lines[2] and "NDVI" not in a.text and "Measure: " in a.working
    assert a.year == 2024 and "2025 has too few clear images so far" in a.text
    s = P.area_answer(conn, "How has farming evolved across the state over the years", "", "en", "state", "NG034", TODAY, place=PIN)
    assert s.text.startswith("*Peak greenness: the 23 LGAs of Sokoto State, 2024*") and "Sokoto State's farmland greenness" in s.text
    assert "each LGA's own years" in s.text and "each ward's" not in s.text
    w = P.area_answer(conn, "Which wards of Sokoto State were greenest in 2024?", "", "en", "state", "NG034", TODAY)
    assert "12 wards have no cropland in the 2021 land-cover map" in w.text and "Since 20" not in w.text


def test_the_map_caption_counts_match_the_answer_and_the_legend_has_no_nan(conn) -> None:
    from app.place.images import area_map
    img = area_map(conn, {"kind": "area_map", "measure": "modis_peak", "key": "greenness", "year": 2025, "level": "ward",
                          "unit": "NG034"}, "en", TODAY)
    assert "across 232 of 244 wards" in img.caption and "12 with no cropland" in img.caption and "nan" not in img.caption.lower()
    cov = P.coverage(conn, "ward", None, P.rows_for(conn, "modis_peak", "ward", 2025, None), -1)
    assert cov["total"] == 244 and cov["valued"] == 232 and cov["no_crop"] == 12 and cov["no_data"] == 0
    mine = area_map(conn, {"kind": "area_map", "measure": "modis_peak", "key": "greenness", "year": 2024, "level": "ward",
                           "unit": "NG034021", "highlight": "62102"}, "en", TODAY)
    assert mine is not None and "11 of 11 wards" in mine.caption
