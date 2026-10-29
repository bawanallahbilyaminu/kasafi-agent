"""Code descriptions and meaning search for budget lines (app/retrieval/line_meaning.py, line_search.fuse)."""

from app.retrieval import line_meaning as lm
from app.retrieval.line_search import Line, asked_kind, cover, fuse, lift_kind, own_name

ECON = "Sokoto State Government 2026 Approved Budget - Total Expenditure by Economic Classification"
FUNC = "Sokoto State Government 2026 Approved Budget - Total Expenditure by Functional Classification"
ADMIN = "Sokoto State Government 2026 Approved Budget - Total Expenditure by Administrative Classification"
PROJECT = "Sokoto State Government 2026 Approved Budget - Capital Expenditure by Project"
TRYCLE = ("Purchase of 300 Trycle bicycle for disable for ease transportation 051300300100 - Agency for Persons Living "
          "With Disabilities 23010104 - PURCHASE MOTOR CYCLES 71012 - DISABILITY 33342400 - State Wide | 2026 "
          "Approved Budget: 140,000,000.00")
ROWS = [
    (ECON, "23", "CAPITAL EXPENDITURE", "23 CAPITAL EXPENDITURE | 2026 Approved Budget: 1.00"),
    (ECON, "2301", "FIXED ASSETS PURCHASED", "2301 FIXED ASSETS PURCHASED | 2026 Approved Budget: 1.00"),
    (ECON, "230101", "PURCHASE OF FIXED ASSETS - GENERAL", "230101 PURCHASE OF FIXED ASSETS - GENERAL | x: 1.00"),
    (FUNC, "710", "SOCIAL PROTECTION", "710 SOCIAL PROTECTION | 2026 Approved Budget: 1.00"),
    (FUNC, "7101", "SICKNESS AND DISABILITY", "7101 SICKNESS AND DISABILITY | 2026 Approved Budget: 1.00"),
    (ADMIN, "050000000000", "Social Sector", "050000000000 Social Sector | 2026 Approved Budget: 1.00"),
    (ADMIN, "11010101", "STATUTORY ALLOCATION", "11010101 STATUTORY ALLOCATION | 2026 Approved Budget: 1.00"),
    (PROJECT, "", "Purchase of 300 Trycle", TRYCLE),
]


def test_code_families_from_their_shape() -> None:
    assert lm.kind_of_code("051300300100") == "admin"
    assert lm.kind_of_code("23010104") == "economic"
    assert lm.kind_of_code("33342400") is None          # a place, not an item
    assert lm.kind_of_code("71012") == "function"
    assert lm.kind_in_table(ADMIN, "11010101") == "economic"   # revenue codes inside an administrative table


def test_parents_nearest_first() -> None:
    assert lm.parents("economic", "23010104") == ["230101", "2301", "23"]
    assert lm.parents("function", "71012") == ["7101", "710"]
    assert lm.parents("admin", "051300300100") == ["050000000000"]


def test_a_project_line_gets_its_codes_parent_categories_but_not_what_it_already_prints() -> None:
    names = lm.build_names(ROWS)
    assert names["economic"]["23010104"] == "PURCHASE MOTOR CYCLES"      # learned from the project row itself
    ctx = lm.context_of(PROJECT, "", TRYCLE, names)
    for d in ("Social Sector", "PURCHASE OF FIXED ASSETS - GENERAL", "FIXED ASSETS PURCHASED", "CAPITAL EXPENDITURE",
              "SICKNESS AND DISABILITY", "SOCIAL PROTECTION"):
        assert d in ctx
    assert not {"PURCHASE MOTOR CYCLES", "DISABILITY"} & set(ctx.split("; "))    # already printed on the row
    assert lm.context_of(PROJECT, "", TRYCLE, names, depth=1).count(";") < ctx.count(";")


def test_meaning_text_drops_codes() -> None:
    text = lm.meaning_text(TRYCLE, "SICKNESS AND DISABILITY")
    assert "051300300100" not in text and "Trycle bicycle" in text and text.endswith("SICKNESS AND DISABILITY")


def _l(i: str, name: str) -> Line:
    return Line(i, "t", "d", 1, "T", name, name, "project", "", "", 1.0)


def test_fuse_lifts_keyword_hits_near_in_meaning_and_adds_a_few_meaning_only_names() -> None:
    kw = [_l("a", "alpha"), _l("b", "beta"), _l("c", "gamma")]
    out = fuse(kw, [[_l("c2", "gamma"), _l("z", "zeta")]], window=3, meaning_only=1)
    assert [x.id for x in out] == ["c", "a", "z", "b"]    # gamma lifted; zeta inside the window of 3


def test_cover_reads_every_terms_best_names_first_then_meaning_only_lines() -> None:
    broad = [_l(f"w{i}", f"welfare {i}") for i in range(5)]
    trycle = _l("t", "Purchase of 300 Trycle bicycle")
    trycle.context = "SICKNESS AND DISABILITY"
    meaning_only = _l("m", "THERAPEUTIC APPLIANCES")
    meaning_only.score = 0.0
    out = cover([*broad, meaning_only, trycle], ["welfare", "disability"], per_term=2)
    assert [x.id for x in out][:4] == ["w0", "w1", "t", "m"]    # matched by its code description


def test_cover_reads_the_projects_a_broad_term_names_not_only_its_summary_rows() -> None:
    """m14: "housing" matched ~150 sector / ministry total rows before "Construction of 500 Housing Estate at
    Wajekke"; a project line whose name only carries the term in its agency's name isn't named by it."""
    codes = " 025300100100 - Min of Lands and Housing 23020104 - CONSTRUCTION / PROVISION OF HOUSING"
    summary = [_l(f"s{i}", n) for i, n in enumerate(["HOUSING", "Ministry of Lands and Housing", "HOUSING",
                                                      "HOUSING DEVELOPMENT"] * 3)]
    server = _l("srv", "Server Upgrade" + codes)
    heading = _l("hd", "HOUSING 33312100 - WAMAKKO 33312100 - x")
    programme = _l("pg", "06100126001300 - Housing and Urban Development - General Server Upgrade" + codes)
    estate = _l("est", "Construction of 500 Housing Estate at Wajekke, Wamakko" + codes)
    for x in (server, heading, programme, estate):
        x.row_text = x.name
    out = [x.id for x in cover([*summary, server, heading, programme, estate], ["housing"], per_term=2)]
    assert out[:3] == ["s0", "s1", "est"]
    assert own_name(estate) == "Construction of 500 Housing Estate at Wajekke, Wamakko"


def test_the_asked_kinds_copy_of_a_name_moves_up_so_the_copy_cap_keeps_it() -> None:
    """m19: Government House is printed in the total, personnel and overhead tables under one name."""
    gh = [_l(f"g{i}", "Government House") for i in range(3)]
    for x, k in zip(gh, ("total", "personnel", "overhead")):
        x.spend_kind = k
    other = _l("o", "OVERHEAD COST")
    assert asked_kind("office running costs and overhead for the Governor") == "overhead"
    assert asked_kind("salaries and capital expenditure") == ""            # two kinds: none lifted
    assert [x.id for x in lift_kind([gh[0], other, gh[1], gh[2]], "overhead")] == ["g2", "g0", "o", "g1"]


def test_fuse_without_meaning_keeps_the_keyword_order() -> None:
    kw = [_l("a", "alpha"), _l("b", "beta")]
    assert fuse(kw, []) == kw
