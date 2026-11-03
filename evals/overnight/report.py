"""docs/overnight-report.md from the state file and each round's results: scores per round (fix vs held-out), per
feature and per difficulty; each fix kept or reverted with its before/after; the final deployed-vs-branch table;
the top remaining failure causes with three examples each; the exact spend and every Meta attempt.

    python evals/overnight/report.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

from common import BASETEN_CAP_USD, ROOT, ROUNDS, load_state, read_jsonl  # noqa: E402

OUT = ROOT / "docs" / "overnight-report.md"


def pct(ok: int, n: int) -> str:
    return f"{ok}/{n} ({100 * ok / n:.0f}%)" if n else "–"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    s = load_state()
    lines = [f"# Overnight eval loop, {s.get('started', '')[:10]}", "",
             f"Branch `overnight-evals`, from the deployed commit `{s.get('base_commit', '?')}`. Muse Spark Open on Baseten "
             f"only; the Meta key in the environment was deliberately invalid and every Muse Spark client was served by "
             f"Muse Spark Open (`evals/overnight/common.py`, `meta_guard`). Caps in code: ${BASETEN_CAP_USD:.0f} Baseten, "
             f"stop 06:30.", "",
             f"**Spend:** ${s['spend_usd']:.2f} on Baseten (every model call priced from its token usage, "
             f"`kasafi_price_baseten_*`). **Meta attempts:** {len(s['meta_attempts'])}"
             + (" (" + "; ".join(f"{a['at']} {a['where']}" for a in s["meta_attempts"]) + ")" if s["meta_attempts"] else
                " (none: $0 Meta spend)") + ".", ""]
    all_rows: list[dict] = []
    lines += ["## Rounds", "", "| Round | Commit tested | Fix half | Held-out half | Notes |", "|---|---|---|---|---|"]
    for r in s["rounds"]:
        n = r["round"]
        rows = {w: read_jsonl(ROUNDS / f"r{n}" / f"results-{w}.jsonl") for w in ("fix", "heldout")}
        for w, rs in rows.items():
            for x in rs:
                x["round"] = n
            all_rows += rs
        f, h = rows["fix"], rows["heldout"]
        lines.append(f"| {n} | `{r.get('commit', '?')}` | {pct(sum(x['ok'] for x in f), len(f))} | "
                     f"{pct(sum(x['ok'] for x in h), len(h))} | {r.get('notes', '')} |")
    lines += ["", "### Per feature (all rounds, both halves)", "", "| Feature | Right | Direct | Combine | Multi |", "|---|---|---|---|---|"]
    by_feat = defaultdict(list)
    for x in all_rows:
        by_feat[x["feature"]].append(x)
    for feat, rs in sorted(by_feat.items()):
        cells = [pct(sum(x["ok"] for x in rs if x["difficulty"] == d), sum(1 for x in rs if x["difficulty"] == d))
                 for d in ("direct", "combine", "multi")]
        lines.append(f"| {feat} | {pct(sum(x['ok'] for x in rs), len(rs))} | " + " | ".join(cells) + " |")
    lines += ["", "### Per difficulty", "", "| Difficulty | Right |", "|---|---|"]
    for d in ("direct", "combine", "multi"):
        rs = [x for x in all_rows if x["difficulty"] == d]
        lines.append(f"| {d} | {pct(sum(x['ok'] for x in rs), len(rs))} |")
    lines += ["", "## Fixes", ""]
    if not s["fixes"]:
        lines.append("None made.")
    for fx in s["fixes"]:
        lines.append(f"- **{fx['kept'] and 'Kept' or 'Reverted'}** `{fx.get('commit', '')[:7]}`: {fx['what']} — "
                     f"held-out {fx.get('before', '?')} → {fx.get('after', '?')}; live-failures {fx.get('lf', '?')}, "
                     f"routing {fx.get('routing', '?')}, understanding {fx.get('understanding', '?')}.")
    lines += ["", "## Final comparison: deployed vs branch", ""]
    fin = s.get("final") or {}
    if fin:
        lines += ["| Set | Deployed | Branch | Changed |", "|---|---|---|---|"]
        for name, v in fin.items():
            lines.append(f"| {name} | {v.get('deployed', '–')} | {v.get('branch', '–')} | {v.get('changed', '')} |")
    else:
        lines.append("Not run (the night ended first).")
    lines += ["", "## Top remaining failures", ""]
    failed = [x for x in all_rows if not x["ok"]]
    for why, n in Counter(x["cause"] for x in failed).most_common(8):
        lines.append(f"### {why} ({n})")
        for x in [y for y in failed if y["cause"] == why][:3]:
            turns = " → ".join(t if isinstance(t, str) else "[pin]" for t in x["turns"])
            lines.append(f"- `{x['id']}` ({x['lang']}): {turns}\n  - expected: {str(x['expect'])[:160]}\n"
                         f"  - got: {x['reply'][:220].replace(chr(10), ' / ')}\n  - fails: {'; '.join(x['fails'])[:160]}")
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
