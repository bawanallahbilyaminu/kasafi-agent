"""The topic-set fixes of Oct 31 2026 (t01, t08, t11), each on the real page or wording that went wrong."""

import psycopg
import pytest

from app.acquisition.registry import detect_topic
from app.agent import topics as T
from app.config import get_settings
from app.retrieval.search import printed_names, printed_query


def test_a_sokoto_row_with_a_negative_z_score_is_a_row() -> None:
    assert T.SOKOTO_ROW.search("Sokoto 14.8 42.8 −2.0 332 2.1 6.0 1.5 −0.7 332")        # NDHS 2024 p366
    assert T.SOKOTO_ROW.search("Sokoto 0.409 0.391 0.427 90.5")
    assert not T.SOKOTO_ROW.search("Sokoto State has 23 LGAs")


def test_a_sample_size_is_not_a_population_group() -> None:
    assert T.population_of("", "the 2022 national mpi, sampling over 56,000 households. in sokoto 91%") == "all"
    assert T.population_of("", "percentage of households with improved water") == "households"


def test_a_change_pairs_each_year_with_its_own_edition_first() -> None:
    from app.acquisition.registry import registry
    pub = registry().topics["poverty_welfare"].publishers[0]
    quoted = T.Card(pub, "d", "t", 36, "91%", "%", "headcount ratio, 2022 baseline", "2022", edition="2025 Profile")
    own = T.Card(pub, "e", "t", 123, "90.5%", "%", "incidence", "2022", edition="2022")
    assert T.quoted_earlier(quoted) and not T.quoted_earlier(own)


def test_a_printed_change_is_not_a_level() -> None:
    # SBS MPI 2025 p36: 'a reduction of 32 percentage points' became the 2025 headcount (90.5% -> 32-%)
    assert T.measure_of("32-", "percentage points", "headcount", "reduction in Headcount Ratio") == "other"
    assert T.measure_of("32", "%", "headcount", "decline in headcount ratio") == "other"
    assert T.measure_of("59.1%", "%", "headcount", "Headcount Ratio") == "headcount"


def test_a_title_that_spells_the_acronym_belongs_to_it() -> None:
    assert T.spelled_out("NDHS", "Nigeria Demographic and Health Survey 2024 Final Report")
    assert T.spelled_out("MICS", "Nigeria 2021 Multiple Indicator Cluster Survey (MICS)")
    assert not T.spelled_out("NDHS", "Nigeria Labour Force Survey Annual Report 2023")


def test_indicators_are_also_searched_by_their_printed_names() -> None:
    assert printed_names("What percentage of children are stunted?") == ["height-for-age"]
    assert printed_query("stunting in Sokoto") == "height-for-age or height in Sokoto"
    assert printed_query("unemployment in Sokoto") == ""


def test_the_topic_path_detects_only_multi_source_topics() -> None:
    q = "How many measles vaccination doses were given in Sokoto?"
    assert detect_topic(q, pattern="multi_source") == "health"
    assert T.other_topics("unemployment of IDPs in Sokoto town", "displacement_humanitarian")[0].id == \
        "labour_employment"


def _conn():
    s = get_settings()
    try:
        return psycopg.connect(s.db_url(), connect_timeout=3)
    except (psycopg.OperationalError, RuntimeError):
        pytest.skip("database not running")


def test_a_continued_table_page_carries_its_title() -> None:
    with _conn() as conn:
        row = conn.execute("SELECT text FROM pages WHERE doc_id = 'nbs-nlfs-2023' AND page = 51").fetchone()
        if not row:
            pytest.skip("NLFS 2023 not indexed")
        # NLFS 2023 p51 prints Sokoto's discouraged job seekers (0.3) under no title: read as unemployment
        assert T.continued_from(conn, "nbs-nlfs-2023", 51, row[0]) == \
            "(continues Table 14: Discouraged Job Seekers by State and Sex, from page 50)\n"
        p45 = conn.execute("SELECT text FROM pages WHERE doc_id = 'nbs-nlfs-2023' AND page = 45").fetchone()[0]
        assert T.continued_from(conn, "nbs-nlfs-2023", 45, p45) == ""


def test_a_scheduled_crawl_does_not_use_the_users_fetch_limit() -> None:
    from app.acquisition.library import fetches_today
    with _conn() as conn:
        before = fetches_today(conn)
        conn.execute("INSERT INTO documents (id, title, acquisition, sha256, page_count, fetched_at) VALUES "
                     "('test-scheduled', 't', 'scheduled', 'x', 1, now())")
        assert fetches_today(conn) == before
        conn.rollback()
