"""The 3 Nov live failures (A-E) as structure, not as questions: a not-found answer never turns into a budget note
for a schools question; one document's figures aren't labelled 'Newest' or 'By source'; the progress line never
claims several sources publish figures."""

from app.acquisition.registry import Publisher, registry
from app.agent import answer as ans
from app.agent import topics as tp

ASC = Publisher("sokoto_asc", "Sokoto State Annual School Census 23-24 Report", ("sokotoeducation.gov.ng",),
                level="lga", tier=1)


def _plan(q: str) -> ans.Plan:
    return ans.Plan(english_question=q, search_queries=[], doc_ids=[], original=q)


def test_a_schools_question_that_nothing_answers_never_gets_the_lga_budget_note() -> None:
    q = "How many total primary, junior secondary, senior secondary and IQS schools are in Dange Shuni LGA?"
    a = ans._not_found(None, _plan(q), "en", None, {}, gap=False)
    assert "budget" not in a.text.lower() and "Dange Shuni" not in a.text
    money = ans._not_found(None, _plan("How much did the state budget give Dange Shuni LGA in 2025?"), "en", None,
                           {}, gap=False)
    assert money.text.startswith("The state budget doesn't show money allocated directly to Dange Shuni")


def test_one_documents_figures_are_not_newest_or_by_source() -> None:
    cards = [tp.Card(ASC, "asc", ASC.name, 19, "91", "schools", "public primary schools", "2023/2024 ASC",
                     "Dange Shuni LGA"),
             tp.Card(ASC, "asc", ASC.name, 26, "20", "schools", "public pre-primary schools", "2023/2024 ASC",
                     "Dange Shuni LGA")]
    text, _ = tp.compose(registry().topics["education"], [tp.SourceResult(ASC, "asc", status="ok", cards=cards)],
                         [], "en")
    assert text.startswith("📊 *91 schools* – public primary schools, Dange Shuni LGA")
    assert "Newest" not in text and "By source" not in text and "In this document:" in text


P31 = ("SOKOTO State ASC Report; 2023/2024\n13\nTable 3.6: Public and Private Primary school enrolment by gender and "
       "LGA\nLGA\nPublic Private Total\nNumber\nof Schools Pupils Girls % girls\nNumber\nof Schools Pupils Girls % girls "
       "Pupils % girls\nBINJI 70 38,271 19,360 51% 2 246 80 33% 38,517 50%\nBODINGA 105 60,116 28,901 48% 4 784 325 41% "
       "60,900 48%\nDANGE SHUNI 91 40,089 17,615 44% 28 2,837 1,251 44% 42,926 44%\nGADA 120 57,916 24,228 42% 2 534 "
       "201 38% 58,450 42%\nTotal 2,203 1,122,151 508,746 45% 141 30,123 14,229 47% 1,152,274 45%")
P44 = ("SOKOTO State ASC Report; 2023/2024\n26\nTable 3.10: Public and private junior secondary school enrolment by "
       "gender and LGA\nLGA\nPublic Private Total\nNumber\nof Schools Pupils Girls % girls\nNumber\nof Schools Pupils "
       "Girls % girls Pupils % girls\nBINJI 5 2,105 963 46% - - - - 2,105 46%\nDANGE SHUNI 18 9,447 3,916 41% 17 980 "
       "469 48% 10,427 42%")
P26 = "Table 3.3 pre-primary schools\nLGA\nDANGE SHUNI 20 2,117 979 46% 28 1,733 845 49%"


def test_a_place_is_matched_however_the_document_prints_it() -> None:
    assert ans.place_pattern("Illela").search("ILELA 12 7,855") and ans.place_pattern("Dange Shuni").search("DANGE-SHUNI")
    assert not ans.place_pattern("Gada").search("GADABAWA 5") and not ans.place_pattern("Isa").search("Isah")


def test_reading_wide_keeps_the_tables_title_headers_the_places_row_and_the_total() -> None:
    ex = ans.place_excerpt(P31, [ans.place_pattern("Dange Shuni")])
    assert "Table 3.6" in ex and "of Schools Pupils" in ex and "DANGE SHUNI 91 40,089" in ex and ex.count("Total") >= 1
    assert "BODINGA" not in ex and "GADA 120" not in ex
    assert ans.place_excerpt("Table 9: Wards\nLGA\nBINJI 3 4", [ans.place_pattern("Dange Shuni")]) == ""


def _evidence():
    return {n: ans.Evidence(n, "asc-sokoto-2023-2024", ASC.name, 2024, p, "text", t)
            for n, (p, t) in enumerate(((31, P31), (44, P44), (26, P26)), start=1)}


def test_parts_are_added_up_in_code_and_pre_primary_is_shown_not_added() -> None:
    d = {"total_of": "schools in Dange Shuni LGA", "parts": [
        {"label": "public pre-primary schools", "value": "20", "cited": 3},
        {"label": "public primary schools", "value": "91", "cited": 1},
        {"label": "private primary schools", "value": "28", "cited": 1},
        {"label": "public junior secondary schools", "value": "18", "cited": 2},
        {"label": "private junior secondary schools", "value": "17", "cited": 2}]}
    text, working, plain = ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")
    assert text.startswith("Total (schools in Dange Shuni LGA): *154*, added up by Kasafi from the 4 parts below.")
    assert "Not added (counted with primary: not added):\n• public pre-primary schools: 20 (page 26)" in text
    assert working == "Total, calculated in code: 91 + 28 + 18 + 17 = 154" and plain.endswith("total 154")
    d["parts"][1]["label"] = "public primary schools (includes pre-primary)"        # a note, not a pre-primary part
    assert "*154*" in ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")[0]
    d["parts"][1]["label"] = "public pre-primary and primary schools"
    assert "*154*" in ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")[0]
    d["parts"][1]["label"] = "makarantun gwamnati na pre-primary da firamare"          # Hausa: still primary
    assert "*154*" in ans.parts_block(d, _evidence(), ["Dange Shuni"], "ha")[0]


def test_the_documents_own_per_level_note_keeps_private_parts_out_of_the_sum_whatever_the_writer_said() -> None:
    ev = _evidence()
    ev[4] = ans.Evidence(4, "asc-sokoto-2023-2024", ASC.name, 2024, 21, "text",
                         "Table 2.2: Number of Private schools by level\nSchools with primary classes 203\n"
                         "Schools with junior secondary classes 116")
    d = {"parts": [{"label": "public primary schools", "value": "91", "cited": 1},
                   {"label": "private primary schools", "value": "28", "cited": 1},
                   {"label": "public junior secondary schools", "value": "18", "cited": 2},
                   {"label": "private junior secondary schools", "value": "17", "cited": 2}]}
    text, working, _ = ans.parts_block(d, ev, ["Dange Shuni"], "en")
    assert working == "Total, calculated in code: 91 + 18 = 109"
    assert "Not added (the census counts a private school at each level it offers):\n• private primary schools: 28 (page 31)\n" in text
    assert text.count("counts a private school") == 1                 # the reason once, not on every line
    del ev[4]                                       # no such note in the evidence: the writer's parts are added
    assert ans.parts_block(d, ev, ["Dange Shuni"], "en")[1].endswith("= 154")


def test_the_same_school_counted_at_each_level_is_shown_not_added() -> None:
    d = {"total_of": "public schools in Dange Shuni LGA", "parts": [
        {"label": "public primary schools", "value": "91", "cited": 1},
        {"label": "public junior secondary schools", "value": "18", "cited": 2},
        {"label": "private schools with primary classes", "value": "28", "cited": 1, "add": False,
         "why": "a private school offering several levels is counted at each"},
        {"label": "private schools with junior secondary classes", "value": "17", "cited": 2, "add": False,
         "why": "a private school offering several levels is counted at each"}]}
    text, working, _ = ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")
    assert text.startswith("Total (public schools in Dange Shuni LGA): *109*, added up by Kasafi from the 2 parts below.")
    assert "Not added (a private school offering several levels is counted at each):\n• private schools with primary classes: 28" in text
    assert working == "Total, calculated in code: 91 + 18 = 109"


def test_a_part_not_in_the_places_row_stops_the_total() -> None:
    d = {"parts": [{"label": "public primary schools", "value": "70", "cited": 1},     # Binji's row, not Dange Shuni's
                   {"label": "public junior secondary schools", "value": "18", "cited": 2}]}
    text, working, _ = ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")
    assert "No total: public primary schools could not be found in the cited row" in text and working == ""


def test_a_count_is_an_answer_so_no_didnt_find_note_goes_under_it() -> None:
    from app.agent import answer_check
    assert answer_check.figures_in("Dange Shuni has 91 public primary schools (page 31).") == ["91"]


def test_a_numbered_table_row_and_a_dashboard_row_are_labelled_by_their_place() -> None:
    from app.agent import attribution as A
    assert A._survey_label("26 | Sokoto | 7 | 8 | 15,675 | 4,566 | 19") == "Sokoto"
    assert A.row_geo(A._survey_label("Sokoto: DISPLACED PERSONS 4,566 (printed on the page)")) == "sokoto"
    assert not A._prose_line("Nigeria: States Affected 28 (printed on the page)")
    ev = [ans.Evidence(4, "nema-flood-sitrep-2025-09-26", "2025 Floods NEOC Situation Report", 2025, 3, "ocr",
                       "26 | Sokoto | 7 | 8 | 15,675 | 4,566 | 19 | 3 | 1,161 | 6,572\nTotal | 25 | 89 | 325,321\n"
                       "[Table printed on page 3: NEMA 2025 FLOOD DASHBOARD]\nas of 24/09/25\n"
                       "Nigeria: States Affected 28 (printed on the page)\n"
                       "Sokoto: DISPLACED PERSONS 4,566 (printed on the page)")]
    att = A.bind("Sokoto State, as of 24/09/25: 4,566 displaced persons [4]", ev, [["Sokoto"]])
    assert att.ok and not any("national" in p for p in att.problems)


def test_a_year_asked_matches_any_year_a_figure_is_for() -> None:
    def card(ref):
        return tp.Card(ASC, "d", "t", 1, "22.5", "%", "w", ref, "Sokoto")
    assert tp.card_years(card("2021/22")) == {2021, 2022}            # 'MICS 2021' keeps Sokoto's 2021/22 card
    assert tp.card_years(card("17/08/25")) == {2025}                 # a dashboard's date
    assert tp.card_years(card("October 2024")) == {2024}


def test_each_change_has_its_own_switch(monkeypatch) -> None:
    from app.agent import understand as U
    from tests.helpers import make_settings
    off = make_settings(kasafi_followup_rules=False, kasafi_read_wide=False)
    monkeypatch.setattr(ans, "get_settings", lambda: off)
    q = "How many total primary, junior secondary, senior secondary and IQS schools are in Dange Shuni LGA?"
    assert ans._not_found(None, _plan(q), "en", None, {}, gap=False).text.startswith("The state budget doesn't show")
    assert "X not Y" not in U.system_prompt(off) and "X not Y" in U.system_prompt(make_settings())
    assert "rain fell in a past season" not in U.system_prompt(make_settings(kasafi_past_rain_rule=False))
    assert "rain fell in a past season" in U.system_prompt(make_settings())
    assert "6o." in ans.ANSWER_SYSTEM and "6o." not in ans.RULE_6O.sub("", ans.ANSWER_SYSTEM)
    assert make_settings().kasafi_past_rain_rule and make_settings().kasafi_answer_check


def test_counts_by_category_lead_with_the_total_in_the_writers_sentence_with_codes_figure() -> None:
    sn = "Table 3.6\nLGA\nSOKOTO NORTH 23 45,939 23,652 51% 14 1,759 787 45% 47,698 51%"
    jss = "Table 3.10\nLGA\nSOKOTO NORTH 23 30,866 17,914 58% 8 642 327 51% 31,508 58%"
    sss = "Table 3.14\nLGA\nSOKOTO NORTH 14 26,096 14,784 57% 6 459 170 37%"
    note = "Table 2.2: Number of Private schools by level\nSchools with primary classes 203"
    ev = {n: ans.Evidence(n, "asc", ASC.name, 2024, p, "text", t)
          for n, (p, t) in enumerate(((31, sn), (44, jss), (53, sss), (21, note)), start=1)}
    d = {"total_of": "public schools", "total_sentence": "Sokoto North had {total} public schools in 2023/24.",
         "parts": [{"label": "public primary", "value": "23", "cited": 1},
                   {"label": "public junior secondary", "value": "23", "cited": 2},
                   {"label": "public senior secondary", "value": "14", "cited": 3},
                   {"label": "private primary", "value": "14", "cited": 1},
                   {"label": "private junior secondary", "value": "8", "cited": 2},
                   {"label": "private senior secondary", "value": "6", "cited": 3}]}
    text, working, _ = ans.parts_block(d, ev, ["Sokoto North"], "en")
    lines = text.splitlines()
    assert lines[0] == "Sokoto North had *60* public schools in 2023/24." and lines[2].startswith("• public primary: 23")
    assert text.index("public senior secondary: 14") < text.index("Not added") < text.index("private primary: 14")
    assert text.count("counts a private school") == 1 and working.endswith("23 + 23 + 14 = 60")


def test_the_progress_line_names_what_is_checked_never_several_sources() -> None:
    for lang in ("en", "ha"):
        line = tp.PROGRESS[lang].format(n=2, names="ASC, NBS")
        assert "Several sources" not in line and "majiyoyi da yawa" not in line and "2" in line


def test_a_part_without_a_number_never_blocks_the_total_and_the_double_count_is_dropped_from_the_summary() -> None:
    d = {"total_sentence": "Dange Shuni had {total} public schools [1][2].", "parts": [
        {"label": "public primary", "value": "91", "cited": 1}, {"label": "public junior secondary", "value": "18", "cited": 2},
        {"label": "IQS", "value": "isn't published by LGA", "cited": 1}]}
    text, working, _ = ans.parts_block(d, _evidence(), ["Dange Shuni"], "en")
    assert text.startswith("Dange Shuni had *109* public schools.") and working.endswith("= 109")
    assert "• IQS: isn't published by LGA" in text
    parts = [ans.Part("public primary", "91", None, True), ans.Part("public JSS", "18", None, True),
             ans.Part("private primary", "28", None, True, False, "the census counts a private school at each level it offers")]
    assert ans.restates_parts("Dange Shuni has 137 schools when public and private are added.", parts)
    assert ans.restates_parts("Private schools are counted at each level they offer, so they can't be added.", parts)
    assert not ans.restates_parts("The census gives IQS only for the whole state: 123 (p. 22).", parts)
