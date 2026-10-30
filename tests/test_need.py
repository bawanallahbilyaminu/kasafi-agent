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
