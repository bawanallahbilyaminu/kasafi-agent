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


async def _run_worker(args: list[str], timeout: float) -> dict:
    # -E -s: ignore PYTHON* variables and user site-packages; -m from ROOT finds the app package.
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-E", "-s", "-m", "app.acquisition.parse_worker", *args,
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
    return d


async def extract_pages_sandboxed(path: Path, timeout: float = TIMEOUT_S) -> tuple[list[str], set[int]]:
    """Page texts, and the pages that are pictures of tables (to OCR)."""
    d = await _run_worker(["text", str(path), str(MAX_PAGES)], timeout)
    return d["pages"], set(d.get("image_pages", []))


async def unzip_pdf_sandboxed(path: Path, out: Path, max_bytes: int, timeout: float = TIMEOUT_S) -> Path:
    """The PDF inside a downloaded ZIP (NBS ships reports that way), extracted in the sandbox."""
    d = await _run_worker(["unzip", str(path), str(out), str(max_bytes)], timeout)
    return Path(d["pdf"])


async def locate_sandboxed(path: Path, page: int, figure: str, out: Path, scale: float,
                           timeout: float = 30) -> dict:
    """Render a page and find a figure's row on it (pixels), in the sandbox: fetched PDFs are untrusted."""
    out.parent.mkdir(parents=True, exist_ok=True)
    return await _run_worker(["evidence", str(path), str(page), figure, str(out), str(scale)], timeout)


async def render_pages_sandboxed(path: Path, pages: list[int], out_dir: Path,
                                 timeout: float = TIMEOUT_S) -> dict[int, Path]:
    """Render pages (1-based) to JPEG files for OCR. Only the images leave the sandbox."""
    out_dir.mkdir(parents=True, exist_ok=True)
    files = (await _run_worker(["render", str(path), str(out_dir), *map(str, pages)], timeout))["files"]
    return {int(p): Path(f) for p, f in files.items()}
