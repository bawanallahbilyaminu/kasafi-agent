"""Probe the hazard and advisory sources (docs/hazard-and-services.md section 5) before they are allowlisted: does the
site answer over HTTPS, and does its robots.txt let KasafiBot fetch its home and report pages?

    uv run python scripts/probe_advisories.py
"""

from __future__ import annotations

import asyncio
from urllib.robotparser import RobotFileParser

import httpx

UA = "KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)"
CANDIDATES = {
    "NiMet": ["nimet.gov.ng"],
    "NIHSA": ["nihsa.gov.ng"],
    "NEMA": ["nema.gov.ng"],
    "NCDC": ["ncdc.gov.ng"],
    "Sokoto SEMA": ["sema.sk.gov.ng", "sema.sokotostate.gov.ng", "sokotostate.gov.ng"],
    "Sokoto MoH": ["health.sk.gov.ng", "moh.sk.gov.ng", "smoh.sk.gov.ng", "sokotostate.gov.ng"],
}
PATHS = ["/", "/reports", "/situation-report", "/wp-content/uploads/report.pdf", "/download"]


async def probe(http: httpx.AsyncClient, host: str) -> dict:
    out = {"host": host}
    try:
        r = await http.get(f"https://{host}/", timeout=25)
        out["home"] = f"{r.status_code}" + (f" -> {r.headers.get('location', '')[:60]}" if r.is_redirect else "")
        out["title"] = (r.text.split("<title>", 1)[1].split("</title>", 1)[0].strip()[:70]
                        if "<title>" in r.text else "")
    except httpx.HTTPError as e:
        out["home"] = type(e).__name__
        return out
    try:
        rb = await http.get(f"https://{host}/robots.txt", timeout=25)
        rp = RobotFileParser()
        rp.parse(rb.text.splitlines() if rb.status_code == 200 else [])
        out["robots"] = rb.status_code
        out["allowed"] = {p: rp.can_fetch(UA, f"https://{host}{p}") for p in PATHS}
    except httpx.HTTPError as e:
        out["robots"] = type(e).__name__
    return out


async def main() -> None:
    async with httpx.AsyncClient(headers={"User-Agent": UA}, follow_redirects=False) as http:
        for name, hosts in CANDIDATES.items():
            for host in hosts:
                r = await probe(http, host)
                allowed = r.get("allowed") or {}
                print(f"{name:12} {host:28} home {r.get('home', '-'):>18}  robots {r.get('robots', '-')}  "
                      f"all allowed: {all(allowed.values()) if allowed else '-'}  {r.get('title', '')}")


if __name__ == "__main__":
    asyncio.run(main())
