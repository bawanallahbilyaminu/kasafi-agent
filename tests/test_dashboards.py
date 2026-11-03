"""Dashboard pages read as labelled tables (app/retrieval/dashboards.py, 3 Nov): which pages qualify, the model's
rows as stored text, never a person's name; the progress line follows the reading; one satellite sentence after a
report's answer when the reading asks for it."""

from datetime import date
from types import SimpleNamespace

from app.retrieval.chart_read import chart_text
from app.retrieval.dashboards import numeric_page, parse_rows
from app.whatsapp.conversation import searching_key

GRID = ("1 Adamawa 9 21 49,617 30,206 28 2 10,511 5,917 2 Akwa Ibom 7 9 40,824 9,416 0 0 7,166 3,005 3 Bauchi 4 4 "
        "2,322 0 3 0 241 145 22 Sokoto 3 3 1,916 626 8 0 175 396 23 Taraba 1 1 3,111 0 28 0 923 536 Total 65 122 "
        "182,381 63,608 420 220 15,011 15,454 Sunday, 17 August 2025")
PROSE = ("NEMA Operations Offices nationwide remain on high alert. Rainstorms destroyed clay homes in Sokoto and "
         "Zamfara States. Displaced persons were absorbed by relatives. Structured shelter is required. In 2025, 12 "
         "states reported 3 deaths and 19 injuries.")


def test_a_grid_of_numbers_is_a_dashboard_page_and_running_text_is_not() -> None:
    assert numeric_page(GRID)
    assert not numeric_page(PROSE)
    assert not numeric_page("Table 3: 2024 2025")                 # too few numbers


def test_rows_become_labelled_text_with_place_measure_value_and_date() -> None:
    d = parse_rows({"is_table": True, "title": "Flood dashboard 2025", "date": "17/08/25",
                    "rows": [{"place": "Sokoto", "measure": "AFFECTED PERSONS", "value": "1,916"},
                             {"place": "Sokoto", "measure": "LIVES LOST", "value": "0", "date": ""},
                             {"place": "Nigeria", "measure": "AFFECTED PERSONS", "value": "182,381"},
                             {"place": "Sokoto", "measure": "x", "value": ""}]})
    assert d.is_chart and len(d.values) == 3 and all(v["printed"] for v in d.values)
    text = chart_text("Table on page 2", 2, d, "dashboard")
    assert text.splitlines()[0] == "[Table printed on page 2: Flood dashboard 2025]"
    assert "as of 17/08/25" in text and "Sokoto: AFFECTED PERSONS 1,916 (printed on the page)" in text
    assert "chart label" not in text
    assert not parse_rows({"is_table": False}).is_chart and not parse_rows("not json").is_chart


def test_the_prompt_never_asks_for_names() -> None:
    from app.retrieval.dashboards import PROMPT
    assert "Never copy a person's name, phone number or e-mail" in PROMPT and "ignore them" in PROMPT


def test_the_progress_line_follows_the_reading_not_the_words() -> None:
    q = "Was Wamakko LGA affected by floods in 2025, according to NEMA?"
    assert searching_key(q, SimpleNamespace(capability="statistics")) == "searching"
    assert searching_key("Will it rain tomorrow?", SimpleNamespace(capability="hazard")) == "searching_forecasts"
    assert searching_key("Has my farm ever flooded?", SimpleNamespace(capability="place_history")) == "searching_satellite"
    assert searching_key("Will it rain tomorrow in Wamakko?") == "searching_forecasts"        # no reading: the words


def test_one_satellite_sentence_after_the_reports_when_asked(monkeypatch) -> None:
    import app.place.flood_record as F
    rec = {2024: {"gfm_union_ha": (26000.0, 11), "unosat_ha": (123414.0, None)}}
    monkeypatch.setattr(F, "record", lambda conn, level, unit: rec)
    s = F.context_sentence(object(), "en", None, 2024, date(2026, 11, 3))
    assert s == ("Satellite radar (Copernicus GFM) saw 26,000 ha of Sokoto State under water at some point in 2024; "
                 "UNOSAT's event map, built over several days, shows 123,410 ha.")
    assert F.context_sentence(object(), "ha", None, 2024, date(2026, 11, 3)).startswith("Radar ta tauraron ɗan adam")


def test_an_acronym_the_user_wrote_or_the_publisher_carries_is_not_flagged() -> None:
    from types import SimpleNamespace as N
    from app.agent.answer import acronym_problems
    cited = [N(text="National Emergency Management Agency situation report: Sokoto 15,675", title="2025 Floods NEOC")]
    text = "According to NEMA, 15,675 people were affected in Sokoto."
    assert acronym_problems(text, cited) == ["NEMA"]
    assert acronym_problems(text, cited, ("Was Wamakko affected, according to NEMA?",)) == []
    assert acronym_problems(text, cited, ("National Emergency Management Agency (NEMA)",)) == []


def test_a_publishers_documents_are_newest_edition_first_within_a_year() -> None:
    import inspect
    from app.agent import topics
    assert "edition DESC NULLS LAST, fetched_at DESC" in inspect.getsource(topics.local_documents)


def test_a_year_asked_keeps_only_that_years_figures_in_the_topic_sweep() -> None:
    import inspect
    from app.agent import topics
    src = inspect.getsource(topics.topic_answer)
    assert "card_year(c) in asked" in src and "the document path answers" in src
