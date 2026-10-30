"""IOM Displacement Tracking Matrix (DTM) API: read-only calls for Nigeria / Sokoto. Not wired into the agent yet.

Endpoints and parameters are those of IOM's own client, the `dtmapi` package (0.2.1: dtmapi/config.py,
dtmapi/hna/config.py); called here with httpx, which the app already uses (the package needs pandas and
requests). Each product has its own subscription key, sent in the Ocp-Apim-Subscription-Key header:
  - Baseline (displacement), v3: admin0 / admin1 (state) / admin2 (LGA) IDP figures, DTMAPI_SUBSCRIPTION_KEY;
  - Humanitarian Needs Assessment (HNA), v1: LGA level only, DTMHNA_SUBSCRIPTION_KEY.
Without a key a call returns None. Keys are never logged; responses are data, not instructions.

Displacement rows carry the round in `roundNumber` and the date in `reportingDate` (ISO, e.g.
2025-10-31T00:00:00; also `yearReportingDate` / `monthReportingDate`). One state and round has a row per
displacement reason (conflict, natural disaster ...), and a figure for a state is their sum (`numPresentIdpInd`).
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass

import httpx

from app.config import Settings

log = logging.getLogger(__name__)

BASE = "https://dtmapi.iom.int"
ADMIN1 = f"{BASE}/v3/displacement/admin1"
ADMIN2 = f"{BASE}/v3/displacement/admin2"
HNA_COUNTRIES = f"{BASE}/HNA/v1/country-list"
HNA_CATALOG = f"{BASE}/HNA/v1/catalog"
HNA_ADMIN2 = f"{BASE}/HNA/v1/admin2"
TIMEOUT = httpx.Timeout(60.0, connect=15.0)


class DtmError(Exception):
    pass


@dataclass
class RoundFigure:
    place: str                 # state or LGA
    round: int
    date: str                  # reporting date, YYYY-MM-DD
    idps: int                  # summed over displacement reasons
    reasons: dict[str, int]
    operation: str = ""
    pcode: str = ""            # the place's P-code (admin2Pcode / admin1Pcode): the join key with our LGAs


def _unwrap(body):
    """The gateway wraps results in result / isSuccess / errorMessages, sometimes more than once."""
    for _ in range(4):
        if not isinstance(body, dict):
            return body
        if body.get("exception"):
            raise DtmError(f"API exception: {str(body['exception'])[:200]}")
        if "isSuccess" in body and not body["isSuccess"]:
            raise DtmError(f"API error: {(body.get('errorMessages') or ['unknown'])[0]}")
        if "result" in body:
            body = body["result"]
        elif "data" in body:
            return body["data"]
        else:
            return body
    return body


async def _get(http: httpx.AsyncClient, url: str, key, params: dict | None = None):
    if key is None or not key.get_secret_value():
        return None
    r = await http.get(url, params=params or {}, headers={"Ocp-Apim-Subscription-Key": key.get_secret_value()},
                       timeout=TIMEOUT)
    if r.status_code in (401, 403):
        raise DtmError(f"HTTP {r.status_code}: the subscription key was refused for this product")
    if r.status_code == 429:
        raise DtmError(f"HTTP 429: rate limited (Retry-After: {r.headers.get('retry-after', '-')})")
    r.raise_for_status()
    return _unwrap(r.json())


def by_round(rows: list[dict], level: str = "admin1Name") -> list[RoundFigure]:
    """Rows -> one figure per place and round (displacement reasons summed), newest round first."""
    sums: dict[tuple, dict] = defaultdict(lambda: {"idps": 0, "reasons": defaultdict(int), "date": "", "op": "",
                                                   "pcode": ""})
    code = level.replace("Name", "Pcode")                   # admin2Name -> admin2Pcode
    for x in rows:
        try:
            rnd, n = int(x.get("roundNumber") or 0), int(float(x.get("numPresentIdpInd") or 0))
        except (TypeError, ValueError):
            continue
        k = (str(x.get(level) or ""), rnd)
        s = sums[k]
        s["idps"] += n
        s["reasons"][str(x.get("displacementReason") or "-")] += n
        s["date"] = max(s["date"], str(x.get("reportingDate") or "")[:10])
        s["op"] = s["op"] or str(x.get("operation") or "")
        s["pcode"] = s["pcode"] or str(x.get(code) or "")
    out = [RoundFigure(place, rnd, s["date"], s["idps"], dict(s["reasons"]), s["op"], s["pcode"])
           for (place, rnd), s in sums.items()]
    return sorted(out, key=lambda f: (f.date, f.round, f.idps), reverse=True)


async def state_rounds(http: httpx.AsyncClient, settings: Settings, state: str = "Sokoto") -> list[RoundFigure] | None:
    """Every round's state figure (Baseline, admin1), newest first; None without a key."""
    rows = await _get(http, ADMIN1, settings.dtmapi_subscription_key, {"CountryName": "Nigeria", "Admin1Name": state})
    return None if rows is None else by_round(list(rows or []))


async def lga_round(http: httpx.AsyncClient, settings: Settings, state: str = "Sokoto",
                    round_number: int | None = None) -> list[RoundFigure] | None:
    """The state's LGAs in one round (the newest if none given), most IDPs first; None without a key."""
    if not round_number:
        # without a round the LGA endpoint may answer with old rounds only (Oct 30: up to round 9), so the
        # newest round comes from the state figures and is asked for explicitly
        rounds = await state_rounds(http, settings, state)
        if not rounds:
            return rounds
        round_number = rounds[0].round
    params = {"CountryName": "Nigeria", "Admin1Name": state,
              "FromRoundNumber": round_number, "ToRoundNumber": round_number}
    rows = await _get(http, ADMIN2, settings.dtmapi_subscription_key, params)
    if rows is None:
        return None
    figs = by_round(list(rows or []), "admin2Name")
    newest = round_number or max((f.round for f in figs), default=0)
    return sorted((f for f in figs if f.round == newest), key=lambda f: f.idps, reverse=True)


async def hna_countries(http: httpx.AsyncClient, settings: Settings):
    return await _get(http, HNA_COUNTRIES, settings.dtmhna_subscription_key)


async def hna_catalog(http: httpx.AsyncClient, settings: Settings):
    return await _get(http, HNA_CATALOG, settings.dtmhna_subscription_key)


async def hna_admin2(http: httpx.AsyncClient, settings: Settings, year: int, country: str = "NGA", page: int = 1):
    """One page of HNA LGA rows for a country and assessment year (both required by the API)."""
    return await _get(http, HNA_ADMIN2, settings.dtmhna_subscription_key,
                      {"Admin0Pcode": country, "Year": year, "Page": page})
