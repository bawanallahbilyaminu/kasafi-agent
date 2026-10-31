"""The hazard answer's executive summary (app/hazards/summary.py): the scale owners' meaning quoted and credited,
guideline multiples instead of raw numbers, what drives it, comparisons, the official status last; and no sentence
of it repeated in the details, which say 'model forecasts, not official' once."""

import re
from datetime import date, datetime, timedelta, timezone

import pytest

from app.agent.summary import lead, split_quotes
from app.hazards import official, read
from app.hazards import summary as hs
from app.hazards.answer import hazard_answer

TODAY = date(2026, 10, 31)
NOW = datetime(2026, 10, 31, 10, 0, tzinfo=timezone.utc)
CHECKED = datetime(2026, 10, 31, 5, 3, tzinfo=timezone.utc)
LGAS = [(i, n) for i, n in enumerate(["Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", "Gudu", "Gwadabawa",
                                      "Illela", "Isa", "Kebbe", "Kware", "Rabah", "Sabon Birni", "Shagari", "Silame",
                                      "Sokoto North", "Sokoto South", "Tambuwal", "Tangaza", "Tureta", "Wamakko",
                                      "Wurno", "Yabo"], 1)]


def _air(pid, lga, day, aqi=150.0, cat_="unhealthy", pm25=87.0, pm10=124.0, by="PM2.5"):
    return read.AirDay(lga, day, pm10, pm25, 70.0, 1.1, aqi, cat_, NOW, by)


def _heat(pid, lga, day, t=38.0, hi=35.0, cat_="extreme_caution", basis="air_temperature"):
    return read.HeatDay(lga, day, t, t - 2, hi, cat_, 6, 15, 29, 0.0, 0.0, "none", 0.0, NOW, basis)


class Conn:
    """hazard_answer's few direct queries; the rest is patched."""
    def execute(self, sql, args=()):
        class R:
            def fetchone(self):
                return (CHECKED,)

            def fetchall(self):
                return []
        return R()


@pytest.fixture
def data(monkeypatch):
    state = {"air": {}, "heat": {}, "warnings": [], "checked": CHECKED}

    def point_ids(conn, where):
        if where.kind == "state":
            return LGAS
        return [p for p in LGAS if p[1] == (where.lga or "Wamakko")]

    def air_day(conn, pid, lga, day):
        return _air(pid, lga, day, **state["air"].get((lga, day), {"aqi": 120.0 + pid, "cat_": "unhealthy"}))

    def heat_day(conn, pid, lga, day):
        return _heat(pid, lga, day, **state["heat"].get((lga, day), {"t": 36.0 + pid * 0.1}))
    monkeypatch.setattr(read, "point_ids", point_ids)
    monkeypatch.setattr(read, "air_day", air_day)
    monkeypatch.setattr(read, "heat_day", heat_day)
    monkeypatch.setattr(read, "freshness", lambda conn, layer, now=None: read.Freshness(layer, NOW, False, 1.0))
    monkeypatch.setattr(official, "advisories_for", lambda conn, hazards, where, now=None, **kw:
                        (state["warnings"], None))
    monkeypatch.setattr(official, "last_checked", lambda conn, layer="advisories": state["checked"])
    return state


def _answer(layers, where, lang="en", question="dust today"):
    conn = Conn()
    ha = hazard_answer(conn, question, lang, layers, where, TODAY, None, status=False)
    s = hs.hazard_summary(conn, lang, ha.layers, ha.where, TODAY, TODAY, NOW)
    details, _ = split_quotes(ha.text)
    return s, details, lead(s, details)


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?”])\s+", text) if len(s.strip()) > 12]


WAMAKKO = read.Where("point", "NG034021", "Wamakko", 13.03, 5.2)


def test_air_summary_quotes_the_epa_gives_multiples_driver_comparison_and_status(data) -> None:
    s, details, _ = _answer(["air"], WAMAKKO)
    assert "*Unhealthy* on the US AQI, which the US EPA describes as “Some members of the general public" in s
    assert "Fine particles (PM2.5) set the AQI: PM2.5 is about 6 times and PM10 about 3 times the WHO daily " \
           "guideline" in s
    assert "87 µg" not in s and "124" not in s                                  # multiples, not raw numbers
    assert "tomorrow looks similar" in s
    assert s.endswith("No official warning is in force from NEMA, SEMA or the Ministry of Health (checked 06:03 "
                      "today).")
    assert len(sentences(s)) <= 4


def test_no_sentence_of_the_summary_appears_again_in_the_details(data) -> None:
    for layers, where, lang in ((["air"], WAMAKKO, "en"), (["air"], read.Where("state"), "ha"),
                                (["heat"], read.Where("lga", "NG034006", "Goronyo"), "en"),
                                (["heat"], read.Where("state"), "en"), (["air"], WAMAKKO, "ha")):
        s, details, _ = _answer(layers, where, lang)
        assert s
        for sentence in sentences(s):
            assert sentence not in details, sentence


def test_model_forecast_not_official_is_said_once(data) -> None:
    _, details, text = _answer(["air"], WAMAKKO)
    assert text.count("model forecasts, not official") + text.count("Model forecasts (not official)") == 1
    assert "No active alert" not in details                                     # the status is in the summary only


def test_a_warning_in_force_is_the_last_clause_and_quoted_in_the_details(data) -> None:
    data["warnings"] = [official.Adv("nema_alerts", "alert", NOW - timedelta(days=1), None,
                                     "Residents of Goronyo should be on the alert", "https://nema.gov.ng/x",
                                     ["NG034006"], False)]
    s, details, _ = _answer(["air"], WAMAKKO)
    assert s.endswith("An official NEMA warning is in force (issued 30 Oct), quoted below.")


def test_the_status_says_when_no_check_has_succeeded(data) -> None:
    data["checked"] = None
    s, _, _ = _answer(["air"], WAMAKKO)
    assert s.endswith("Kasafi hasn't yet been able to check NEMA, SEMA or Ministry of Health alerts.")


def test_heat_names_the_driver_the_trend_and_the_rank(data) -> None:
    data["heat"][("Goronyo", TODAY)] = {"t": 41.0, "hi": 37.0, "cat_": "danger"}
    data["heat"][("Goronyo", TODAY + timedelta(days=1))] = {"t": 38.0, "hi": 35.0, "cat_": "extreme_caution"}
    s, _, _ = _answer(["heat"], read.Where("lga", "NG034006", "Goronyo"), question="heat today")
    assert "reaches *Danger* on the US National Weather Service heat index scale, which the NWS describes as " \
           "“Sunstroke, muscle cramps, and/or heat exhaustion likely" in s
    assert "It comes from the air temperature itself" in s
    assert "tomorrow is cooler (*Extreme caution*)" in s and "Goronyo LGA is among the 5 worst of the 23 LGAs" in s


def test_hausa_quotes_are_marked_as_kasafis_translation(data) -> None:
    s, _, _ = _answer(["air"], WAMAKKO, "ha")
    assert "US EPA ta bayyana shi da “" in s and "(fassarar bayanin US EPA)" in s and "kusan ninki 6" in s


def test_state_summaries_name_the_lga_and_count_in_the_singular(data) -> None:
    data["air"][("Tureta", TODAY)] = {"aqi": 204.0, "cat_": "very_unhealthy", "pm25": 135.0, "pm10": 180.0}
    s, _, _ = _answer(["air"], read.Where("state"))
    assert "In Tureta, fine particles (PM2.5) set the AQI: PM2.5 is about 9 times" in s and " there" not in s
    data["heat"][("Gudu", TODAY)] = {"t": 41.0, "hi": 38.0, "cat_": "danger"}
    s, _, _ = _answer(["heat"], read.Where("state"), question="heat today")
    assert "1 of the 23 LGAs is at Danger or above" in s
    ha, _, _ = _answer(["heat"], read.Where("state"), "ha", question="heat today")
    assert "ƙaramar hukuma 1 cikin 23 ce ke matakin Haɗari ko sama" in ha and "(fassarar bayanin NWS)" in ha
    assert hs.counted(hs.W["en"]["wet_n"], 1) == "1 of the 23 LGAs expects rain"
    assert hs.counted(hs.W["en"]["wet_n"], 5) == "5 of the 23 LGAs expect rain"


@pytest.mark.parametrize("pm25,pm10,want", [(87, 124, "PM2.5 is about 6 times and PM10 about 3 times"),
                                            (20, 30, "PM2.5 is about 1.3 times the WHO daily guideline, PM10 within"),
                                            (10, 30, "PM2.5 and PM10 are within the WHO daily guidelines")])
def test_multiples_of_the_guideline(pm25, pm10, want) -> None:
    assert want in hs.multiples(pm25, pm10, "en")


def test_every_category_has_its_owners_meaning() -> None:
    from app.hazards.categories import AQI_CATEGORIES, HEAT_CATEGORIES
    assert {c for _, c in AQI_CATEGORIES} == set(hs.EPA) == set(hs.EPA_HA)
    assert {c for _, c in HEAT_CATEGORIES} == set(hs.NWS) == set(hs.NWS_HA)


@pytest.mark.parametrize("question,key", [
    ("Whats the dust and air quality today", "searching_forecasts"),
    ("Yaya zafin rana yake a Goronyo gobe?", "searching_forecasts"),
    ("Is the river high near Goronyo?", "searching_forecasts"),
    ("What is the 2026 budget for flood control?", "searching"),
    ("How much did Sokoto spend on health in 2025?", "searching")])
def test_hazard_questions_say_they_are_checking_forecasts(question, key) -> None:
    from app.whatsapp.conversation import searching_key
    from app.whatsapp.messages import t
    assert searching_key(question) == key
    assert t("searching_forecasts", "en") == "🌦️ Checking the latest forecasts…"


def test_a_named_layer_beats_an_overview_the_planner_adds() -> None:
    from app.hazards.answer import layers_asked
    assert layers_asked("Is there a flood warning for Goronyo?", ["hazard_overview", "river_discharge"]) == ["flood"]
    assert "overview" in layers_asked("What should we watch out for this week?", ["hazard_overview"])
    assert "overview" in layers_asked("Any hazards in Goronyo? heat too?", ["hazard_overview"])
