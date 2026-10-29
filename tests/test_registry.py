"""The source registry: it parses, detects topics from English and Hausa synonyms, and maps URLs to publishers."""

import pytest

from app.acquisition.registry import detect_topic, parse_registry, registry

MINI = """
version: 1
discovery_channels:
  - id: cat
    what: a state library
    site: https://stats.example.gov.ng
    type: catalog_crawl
    verified: 2026-10-29
topics:
  displacement_humanitarian:
    synonyms_en: [IDP, IDPs, displaced persons]
    synonyms_ha: ["'yan gudun hijira"]
    answer_pattern: multi_source
    publishers:
      - {id: a, name: A, domains: [a.org], level: lga, tier: 1, verified: 2026-10-29}
      - {id: b, name: B, domains: [b.org], level: state, tier: 2, verified: "no"}
global_exclude: [flash reports]
"""


def test_a_small_registry_parses() -> None:
    r = parse_registry(MINI)
    t = r.topics["displacement_humanitarian"]
    assert t.answer_pattern == "multi_source" and [p.id for p in t.publishers] == ["a", "b"]
    assert r.domains() == ["a.org", "stats.example.gov.ng"] and r.unverified_domains() == ["b.org"]
    assert r.global_exclude == ("flash reports",) and r.channels["cat"].type == "catalog_crawl"
    assert t.publishers[0].level_rank < t.publishers[1].level_rank


def test_the_real_registry_parses_and_every_publisher_has_a_tier() -> None:
    r = registry()
    assert len(r.topics) >= 10 and all(1 <= p.tier <= 3 for p in r.publishers())
    assert r.topics["labour_employment"].publishers[0].definition_note
    assert r.publisher_for("https://sbs.sk.gov.ng/api/documents/durable-solutions-report-jips-drc-sbs/download"
                           ).scope_note


@pytest.mark.parametrize("q, topic", [
    ("current state of IDPs in Sokoto", "displacement_humanitarian"),
    ("Yaya halin ’yan gudun hijira a Sokoto?", "displacement_humanitarian"),
    ("employment statistics for Sokoto", "labour_employment"),
    ("Menene adadin rashin aikin yi a Sokoto?", "labour_employment"),
    ("which partners publish nutrition data for Sokoto", "nutrition_food_security"),
    ("What is the weather like?", ""),
])
def test_topics_are_detected_from_synonyms(q: str, topic: str) -> None:
    assert detect_topic(q) == topic
