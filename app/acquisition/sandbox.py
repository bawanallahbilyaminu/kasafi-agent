"""Parse a fetched PDF in a separate, limited process (CLAUDE.md rule 6).

A PDF from the web is untrusted input to a C library (PDFium). The parse runs in a child
Python process with no secrets in its environment, a wall-clock timeout and, on Linux (the
server), memory and CPU limits. If it crashes or hangs, only the child dies.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_S = 120
MEMORY_BYTES = 1536 * 1024 * 1024
CPU_SECONDS = 120
MAX_PAGES = 800


class ParseError(Exception):
    pass


def _limits() -> None:   # runs in the child before exec (POSIX only)
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))


def child_env() -> dict[str, str]:
    """Only what Python needs to start: no API keys, tokens or database URLs."""
    keep = ("PATH", "SYSTEMROOT", "TEMP", "TMP", "LANG", "LC_ALL")
    return {k: os.environ[k] for k in keep if k in os.environ}


async def extract_pages_sandboxed(path: Path, timeout: float = TIMEOUT_S) -> list[str]:
    # -E -s: ignore PYTHON* variables and user site-packages; -m from ROOT finds the app package.
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-E", "-s", "-m", "app.acquisition.parse_worker", str(path), str(MAX_PAGES),
        cwd=str(ROOT), env=child_env(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        preexec_fn=_limits if os.name == "posix" else None,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise ParseError(f"parse timed out after {timeout:.0f} s") from None
    if proc.returncode != 0:
        raise ParseError(f"parse failed (exit {proc.returncode}): {err.decode(errors='replace')[-300:]}")
    d = json.loads(out)
    if "error" in d:
        raise ParseError(d["error"])
    return d["pages"]
