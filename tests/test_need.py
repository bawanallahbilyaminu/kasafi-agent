"""The information need (docs/question-planning.md §2): the planner's fields, checked by code."""

from app.agent.need import Entity, Names, parse_need, resolve

NAMES = Names(mdas=(("State Bureau of Statistics", "023800400100"),
                    ("Ministry of Budget and Economic Planning", "023800000000"),
                    ("Ministry of Budget and Economic Planning", "023800100100"),
                    ("Government House", "011100100100"), ("Government House", "011100000000")),
              programmes=("Information Communication and Technology",), lgas=("Sabon Birni", "Tambuwal", "Wamakko"))


def test_the_idp_follow_up_becomes_an_lga_rank_need() -> None:
    n = parse_need({"measures": ["idp_count"], "entities": [{"type": "state", "name": "Sokoto"}], "geo_level": "lga",
                    "time": {"kind": "latest"}, "operation": "rank", "output_shape": "table_top_n",
                    "topics": ["displacement_humanitarian"]},
                   "Which LGAs in Sokoto State have the most IDPs (latest figures)?", NAMES,
                   ("displacement_humanitarian", "labour_employment"))
    assert (n.measures, n.geo_level, n.operation, n.output_shape, n.top_n) == (["idp_count"], "lga", "rank",
                                                                              "table_top_n", 5)
    assert n.topics == ["displacement_humanitarian"] and not n.problems


def test_a_sub_agency_resolves_to_its_own_row_not_its_ministrys_total() -> None:
    n = parse_need({"measures": ["revised", "quarter_spent"], "splits": ["personnel", "overhead", "capital"],
                    "entities": [{"type": "sub_agency", "name": "Sokoto State Bureau of Statistics"}],
                    "time": {"kind": "quarter", "year": 2026, "quarter": 2}, "operation": "breakdown"},
                   "Personnel, overhead and capital of the State Bureau of Statistics and its Q2 2026 spending?", NAMES)
    e = n.entities[0]
    assert (e.resolved, e.code) == ("State Bureau of Statistics", "023800400100")
    assert n.splits == ["personnel", "overhead", "capital"] and n.time == {"kind": "quarter", "year": 2026, "quarter": 2}
    gh = resolve(Entity("sub_agency", "Government House"), NAMES)
    assert gh.code == "011100100100"                                     # not 011100000000 (with its agencies)
    assert resolve(Entity("mda", "Min. of Budget & Economic Planning"), NAMES).code == "023800000000"


def test_unknown_names_are_dropped_and_noted_never_guessed() -> None:
    n = parse_need({"measures": ["idp_count", "happiness"], "operation": "divine", "time": {"kind": "year", "year": 1066},
                    "entities": [{"type": "lga", "name": "Tambuwaal"}, {"type": "lga", "name": "Atlantis"}]},
                   "q", NAMES)
    assert n.measures == ["idp_count"] and n.operation == "lookup" and n.time == {"kind": "latest"}
    assert any("happiness" in p for p in n.problems) and any("1066" in p for p in n.problems)
    assert [e.resolved for e in n.entities] == ["Tambuwal", ""]          # a typo resolves; an unknown place doesn't


def test_no_need_is_an_empty_need() -> None:
    n = parse_need(None, "q")
    assert n.standalone_question == "q" and n.measures == [] and n.time == {"kind": "latest"}


def test_the_lgas_named_together_mean_every_lga_of_the_state() -> None:
    n = parse_need({"measures": ["idp_count"], "entities": [{"type": "lga", "name": "Sokoto State LGAs"}],
                    "geo_level": "state", "operation": "list"}, "List of LGAs and number of IDPs", NAMES)
    assert [(e.type, e.resolved) for e in n.entities] == [("state", "Sokoto")] and n.geo_level == "lga"
    one = parse_need({"measures": ["idp_count"], "entities": [{"type": "lga", "name": "Tambuwal"}]}, "q", NAMES)
    assert one.entities[0].resolved == "Tambuwal" and one.geo_level == "state"


def test_short_forms_misprints_and_sectors_resolve_to_the_printed_name() -> None:
    from app.agent.need import Entity, Names, resolve
    names = Names(mdas=(("Sokoto State Rima Televiosn (Rtv)", "012300300100"), ("Sokoto State Rima Radio", "012300200100"),
                        ("Social Sector", "050000000000"), ("Ministry of Budget and Economic Planning", "023800000000")))
    assert resolve(Entity("mda", "Rima Television"), names).code == "012300300100"
    assert resolve(Entity("sector", "Social Sector"), names).code == "050000000000"
    assert resolve(Entity("mda", "Budjet and Economic Planing"), names).code == "023800000000"
    assert resolve(Entity("mda", "Rima"), names).code == ""                  # two Rima agencies: not guessed


def test_a_time_keeps_only_its_kinds_fields() -> None:
    from app.agent.need import check_time
    p: list = []
    assert check_time({"kind": "year", "year": 2026, "from": 2026, "to": 2026, "quarter": 1}, p) == \
        {"kind": "year", "year": 2026}
    assert check_time({"kind": "range", "year": 2026, "from": 2025, "to": 2026}, p) == \
        {"kind": "range", "from": 2025, "to": 2026}
    assert check_time({"kind": "quarter", "year": 2026, "quarter": "2"}, p) == {"kind": "quarter", "year": 2026, "quarter": 2}


def test_an_agency_never_resolves_to_its_parent_ministry() -> None:
    from app.agent.need import Entity, Names, resolve, same_entity
    names = Names(mdas=(("Ministry of Education", "051700000000"), ("State Agency for Normadic Education1", "051701100100"),
                        ("Ministry of Health", "052100000000"),
                        ("Sokoto State contributory health care mgt agency", "052100200100")))
    e = resolve(Entity("sub_agency", "State Agency for Nomadic Education"), names)
    assert (e.resolved, e.code) == ("State Agency for Normadic Education1", "051701100100")
    assert resolve(Entity("mda", "Contributory Health Care Management Agency"), names).code == "052100200100"
    assert not same_entity("State Agency for Nomadic Education", "Ministry of Education")
    e = resolve(Entity("mda", "Agency for Adult Education"), names)        # not printed: not the ministry
    assert e.code == "" and "Ministry of Education" not in e.candidates[:0]


def test_two_printings_of_one_ministry_are_one_entity() -> None:
    from app.agent.need import Entity, Names, resolve
    names = Names(mdas=(("Min of Lands and Housing", "023500100100"), ("Ministry of Lands and Housing", "023500000000")))
    assert resolve(Entity("mda", "Ministry of Lands and Housing"), names).code == "023500000000"


def test_a_spelled_out_name_matches_the_acronym_the_budget_prints() -> None:
    names = Names(mdas=(("Office of the SSG", "016100000000"), ("SSG'S Office", "016100100100"),
                        ("Ministry of Health", "052100000000")))
    # the words in another order are one name printed two ways, not two agencies to ask between
    e = resolve(Entity("mda", "Office of the Secretary to the State Government"), names)
    assert (e.resolved, e.code, e.candidates) == ("Office of the SSG", "016100000000", [])
    assert resolve(Entity("sub_agency", "Office of the Secretary to the State Government"), names).code == \
        "016100100100"
    assert resolve(Entity("mda", "Secretary to the State Government"), names).code == "016100000000"   # 'Office'
    assert resolve(Entity("mda", "Ministry of Higher Education"), names).code == ""                   # tells none apart


def test_a_programme_printed_as_a_budget_unit_resolves_to_its_code() -> None:
    names = Names(mdas=(("Livestock Development Programme", "026800200100"),), programmes=("Rural Water Supply",))
    e = resolve(Entity("programme", "Livestock Development Programme"), names)
    assert (e.type, e.code) == ("sub_agency", "026800200100")
    e = resolve(Entity("programme", "Rural Water Supply"), names)         # a printed programme stays one
    assert (e.type, e.resolved) == ("programme", "Rural Water Supply")


def test_an_agency_the_user_named_settles_one_the_planner_renamed() -> None:
    names = Names(mdas=(("Ministry for Basic Education", "051700100100"), ("Ministry of Health", "052100000000")))
    d = {"measures": ["approved"], "entities": [{"type": "mda", "name": "Ministry of Basic and Secondary Education"}],
         "time": {"kind": "year", "year": 2026}}
    asked = "Ministry for Basic Education 2026 approved budget din, what share ne capital?"
    assert parse_need(d, "q", names, asked=asked).entities[0].code == "051700100100"
    assert parse_need(d, "q", names).entities[0].code == ""            # without the user's words: ask
