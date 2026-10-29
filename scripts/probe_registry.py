"""Probe the registry's unverified publisher domains once: does the site answer over https, and does its
robots.txt let KasafiBot in? Prints a table; nothing is allowlisted by this script (a person decides, then sets
`verified: <date>` in data/source_registry.yaml).

    uv run python scripts/probe_registry.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from app.acquisition.policy import USER_AGENT, Robots  # noqa: E402
from app.acquisition.registry import registry  # noqa: E402


async def probe(http: httpx.AsyncClient, robots: Robots, domain: str) -> tuple[str, str, str]:
    url = f"https://{domain}/"
    try:
        r = await http.head(url, follow_redirects=True, timeout=20)
        if r.status_code in (405, 501):          # some servers refuse HEAD
            r = await http.get(url, follow_redirects=True, timeout=20)
        site = f"HTTP {r.status_code}" + (f" -> {r.url.host}" if r.url.host != domain else "")
    except httpx.HTTPError as e:
        site = f"no answer ({type(e).__name__})"
    ok, why = await robots.allowed(url)
    return domain, site, "allowed" if ok else why


async def main() -> None:
    domains = registry().unverified_domains()
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as http:
        robots = Robots(http)
        rows = await asyncio.gather(*(probe(http, robots, d) for d in domains))
    print(f"{'domain':32} {'site':34} robots.txt")
    for d, site, rb in rows:
        print(f"{d:32} {site[:34]:34} {rb}")


if __name__ == "__main__":
    asyncio.run(main())
