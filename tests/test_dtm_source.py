"""IOM DTM API client (app/sources/dtm.py): offline checks, and live calls that skip without the keys."""

import asyncio

import httpx
import pytest

from app.config import get_settings
from app.sources import dtm
from tests.helpers import make_settings

ROWS = [
    {"admin1Name": "Sokoto", "roundNumber": 18, "reportingDate": "2025-10-31T00:00:00", "numPresentIdpInd": 173004,
     "displacementReason": "Conflict/violence", "operation": "North Central and North West"},
    {"admin1Name": "Sokoto", "roundNumber": 18, "reportingDate": "2025-10-31T00:00:00", "numPresentIdpInd": 8522,
     "displacementReason": "Natural disaster"},
    {"admin1Name": "Sokoto", "roundNumber": 17, "reportingDate": "2025-05-31T00:00:00", "numPresentIdpInd": 88562,
     "displacementReason": "Conflict/violence"},
]


def test_a_rounds_state_figure_sums_its_displacement_reasons_newest_first() -> None:
    figs = dtm.by_round(ROWS)
    assert [(f.round, f.date, f.idps) for f in figs] == [(18, "2025-10-31", 181526), (17, "2025-05-31", 88562)]
    assert figs[0].reasons == {"Conflict/violence": 173004, "Natural disaster": 8522}


def test_the_gateway_wrapping_and_errors() -> None:
    assert dtm._unwrap({"isSuccess": True, "result": [1, 2]}) == [1, 2]
    assert dtm._unwrap({"result": {"result": {"data": [3], "pagination": {}}, "isSuccess": True}}) == [3]
    with pytest.raises(dtm.DtmError, match="no such state"):
        dtm._unwrap({"isSuccess": False, "errorMessages": ["no such state"]})


def test_no_key_no_call() -> None:
    def handler(req):
        raise AssertionError("called without a key")

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            return await dtm.state_rounds(http, make_settings()), await dtm.hna_catalog(http, make_settings())
    assert asyncio.run(go()) == (None, None)


def test_the_key_goes_in_the_subscription_header_only() -> None:
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json={"isSuccess": True, "result": ROWS})

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            return await dtm.state_rounds(http, make_settings(dtmapi_subscription_key="secret-k"))
    figs = asyncio.run(go())
    assert figs[0].idps == 181526 and seen[0].headers["Ocp-Apim-Subscription-Key"] == "secret-k"
    assert "secret-k" not in str(seen[0].url)


live = get_settings()


@pytest.mark.skipif(not live.dtmapi_subscription_key, reason="DTMAPI_SUBSCRIPTION_KEY not set")
def test_live_sokoto_state_rounds_and_lgas() -> None:
    async def go():
        async with httpx.AsyncClient() as http:
            return await dtm.state_rounds(http, live), await dtm.lga_round(http, live)
    rounds, lgas = asyncio.run(go())
    assert rounds and rounds[0].round >= 18 and rounds[0].date >= "2025-10-31"
    assert lgas and lgas[0].round == rounds[0].round and sum(f.idps for f in lgas) == rounds[0].idps


@pytest.mark.skipif(not live.dtmhna_subscription_key, reason="DTMHNA_SUBSCRIPTION_KEY not set")
def test_live_hna_lists_nigeria() -> None:
    async def go():
        async with httpx.AsyncClient() as http:
            return await dtm.hna_countries(http, live)
    assert any(c.get("admin0Pcode") == "NGA" for c in asyncio.run(go()))
