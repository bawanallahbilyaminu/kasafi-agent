"""Fetch and index each multi-source topic's newest publisher documents ahead of time (no user waiting).

Some publishers' servers are too slow for a live answer's ~90 s budget (DTM's atlas PDFs can take minutes),
so this runs with long download timeouts and leaves the documents in the library; answers then use them.
Run it weekly (or after a publisher's release date). The daily fetch limit still applies.

    uv run python scripts/prefetch_topics.py [displacement_humanitarian labour_employment ...]
    uv run python scripts/prefetch_topics.py poverty_welfare:nbs_mpi       # one publisher of a topic only
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import psycopg  # noqa: E402

from app.acquisition.policy import USER_AGENT, Robots  # noqa: E402
from app.acquisition.registry import registry  # noqa: E402
from app.agent.topics import choose_publishers, get_document  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402

SLOW = httpx.Timeout(900.0, connect=30.0)


async def main(topic_ids: list[str]) -> None:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
    s = get_settings()
    reg = registry()
    only = {t.split(":", 1)[0]: t.split(":", 1)[1] for t in topic_ids if ":" in t}    # topic -> one publisher
    topic_ids = [t.split(":", 1)[0] for t in topic_ids]
    topics = [reg.topics[t] for t in topic_ids] if topic_ids else [t for t in reg.topics.values()
                                                                   if t.answer_pattern == "multi_source"]
    with psycopg.connect(s.db_url()) as conn:
        async with MetaClient(s, timeout=240) as client, httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as http:
            robots = Robots(http)
            for t in topics:
                primary, _ = choose_publishers(t)
                for p in primary:
                    if t.id in only and p.id != only[t.id]:
                        continue
                    if not p.domains or ("dtm_api" in p.discovery and s.dtmapi_subscription_key):
                        continue          # nothing to fetch, or its figures come from its API (DTM)
                    res = await get_document(conn, p, t, date.today(), http=http, robots=robots, client=client,
                                             settings=s, download_timeout=SLOW)
                    print(f"{t.id:28} {p.id:32} {res.status:10} {res.doc_id or '-':36} "
                          f"{'(older edition) ' if res.older else ''}{res.detail[:80]}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
