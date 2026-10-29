"""(Re)build the structured budget core (budget_items, projects, perf_items) and print the reconciliation report.

Usage:  uv run python scripts/build_entities.py [--only ID ...] [--examples]
Without --only: every budget and implementation-report document. Reads only what is already indexed.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.retrieval.entities import BUDGET_CATEGORIES, PERF_CATEGORIES, build  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", metavar="ID")
    ap.add_argument("--examples", action="store_true", help="print examples of failed checks")
    args = ap.parse_args()
    with psycopg.connect(get_settings().db_url(), connect_timeout=10) as conn:
        ids = args.only or [r[0] for r in conn.execute(
            "SELECT id FROM documents WHERE category = ANY(%s) ORDER BY id",
            (sorted(BUDGET_CATEGORIES | PERF_CATEGORIES),))]
        for doc_id in ids:
            b = build(conn, doc_id)
            if b is None:
                print(f"{doc_id}: not a budget or implementation report")
                continue
            print(f"\n{doc_id}  " + "  ".join(f"{k}={v}" for k, v in b.counts.items()))
            for check, r in sorted(b.checks.results.items()):
                print(f"  {check:<28} {r['passed']:>6} passed {r['failed']:>5} failed")
                if args.examples:
                    for e in r["examples"]:
                        print(f"      {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
