"""Sokoto LGA spellings meet on one canonical name (interim table, until the P-code crosswalk)."""

import pytest

from app.agent.need import Entity, Names, resolve
from app.sources.lga_names import CANONICAL, canonical


@pytest.mark.parametrize("spelling, name", [
    ("Wamako", "Wamakko"), ("WAMAKKO", "Wamakko"), ("Dange-Shuni", "Dange Shuni"), ("DANGE SHUNI", "Dange Shuni"),
    ("Sabon-Birni", "Sabon Birni"), ("Sabonbirni", "Sabon Birni"), ("Ilela", "Illela"), ("Sokoto ta Arewa", "Sokoto North"),
    ("Wamako LGA", "Wamakko"), ("Kano", ""),
])
def test_spellings_of_one_lga_meet(spelling: str, name: str) -> None:
    assert canonical(spelling) == name


def test_all_23_and_the_question_resolves_to_the_canonical_name() -> None:
    assert len(CANONICAL) == 23 and all(canonical(c) == c for c in CANONICAL)
    assert resolve(Entity("lga", "Wamako"), Names(lgas=("Wamakko",))).resolved == "Wamakko"


def test_dtm_places_are_matched_through_the_canonical_name(monkeypatch) -> None:
    import asyncio

    from app.agent import tools
    from app.agent.capabilities import Cell
    from app.agent.need import Need
    from app.sources.dtm import RoundFigure

    rounds = [RoundFigure("Sokoto", 18, "2025-10-31", 181526, {})]
    lgas = [RoundFigure("Wamako", 18, "2025-10-31", 4026, {})]

    async def state(*a, **k):
        return rounds

    async def lga(*a, **k):
        return lgas
    monkeypatch.setattr(tools.dtm_api, "state_rounds", state)
    monkeypatch.setattr(tools.dtm_api, "lga_round", lga)
    monkeypatch.setattr("app.agent.topics._save", lambda *a, **k: None)
    cell = Cell("idp_count", Entity("lga", "Wamako", "Wamakko"), "lga")
    s = type("S", (), {"dtmapi_subscription_key": "k", "kasafi_fetch_dir": "."})()
    asyncio.run(tools.dtm_fill(None, s, Need("q", measures=["idp_count"]), [cell]))
    assert cell.value == 4026


def test_sokoto_city_is_searched_by_the_names_the_budget_prints() -> None:
    from app.sources.lga_names import city_terms
    assert city_terms("funds for piped water in Sokoto city in 2026?") == ["Sokoto Metropolis", "Township"]
    assert city_terms("ruwan famfo a cikin birnin Sokoto") == ["Sokoto Metropolis", "Township"]
    assert city_terms("Sokoto State budget for water") == [] and canonical("Sokoto city") == ""
