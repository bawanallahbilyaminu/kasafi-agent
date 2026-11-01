"""Word-type files (DOCX, DOC, ODT, RTF) to PDF with LibreOffice headless, in a limited child process, so the
PDF is indexed exactly like any other (pages, crops, page citations, OCR). docs/architecture.md, "Office documents".

The child gets the parser's limits (app/acquisition/sandbox.py: a stripped environment with no secrets, memory and
CPU limits on Linux, a wall-clock timeout), its own throwaway LibreOffice profile and a temporary directory that is
deleted afterwards. There is no network namespace in the container, so external links and embedded objects are
rejected before conversion (app/acquisition/filetype.py). A failed or timed-out conversion raises ConversionError
with the reason; nothing retries it.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.acquisition.sandbox import _limits, child_env

CONVERT_TIMEOUT_S = 120
WINDOWS_PATHS = (r"C:\Program Files\LibreOffice\program\soffice.exe", r"C:\Program Files (x86)\LibreOffice\program\soffice.exe")


class ConversionError(Exception):
    pass


@dataclass
class Converted:
    pdf: Path
    sha256: str
    converter: str            # 'LibreOffice 7.4.7.2' (soffice --version)
    seconds: float


def soffice_path() -> str | None:
    for name in ("soffice", "libreoffice"):
        if found := shutil.which(name):
            return found
    return next((p for p in WINDOWS_PATHS if Path(p).exists()), None)


def available() -> bool:
    return CONVERTER is not _libreoffice or soffice_path() is not None


@lru_cache(maxsize=1)
def converter_version() -> str:
    exe = soffice_path()
    if not exe:
        return "none"
    try:
        out = subprocess.run([exe, "--headless", "--version"], capture_output=True, text=True, timeout=60,
                             env=child_env()).stdout.strip()
        return out.splitlines()[0][:80] if out else "LibreOffice"
    except (OSError, subprocess.SubprocessError):
        return "LibreOffice"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 16):
            h.update(chunk)
    return h.hexdigest()


async def _libreoffice(src: Path, out_dir: Path, timeout: float) -> Path:
    """soffice --headless --convert-to pdf, with its profile and temp files under `out_dir`."""
    exe = soffice_path()
    if not exe:
        raise ConversionError("LibreOffice is not installed (soffice not found)")
    profile = out_dir / "profile"
    profile.mkdir(parents=True, exist_ok=True)
    env = child_env() | {"HOME": str(out_dir), "TMPDIR": str(out_dir), "TEMP": str(out_dir), "TMP": str(out_dir)}
    args = [exe, "--headless", "--norestore", "--nologo", "--nodefault", "--nolockcheck",
            f"-env:UserInstallation={profile.resolve().as_uri()}", "--convert-to", "pdf",
            "--outdir", str(out_dir), str(src)]
    proc = await asyncio.create_subprocess_exec(*args, cwd=str(out_dir), env=env, stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE,
                                                preexec_fn=_limits if os.name == "posix" else None)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise ConversionError(f"conversion timed out after {timeout:.0f} s") from None
    pdf = out_dir / (src.stem + ".pdf")
    if proc.returncode != 0 or not pdf.exists():
        detail = (err or out).decode(errors="replace")[-300:].strip()
        raise ConversionError(f"conversion failed (exit {proc.returncode}): {detail or 'no PDF produced'}")
    return pdf


CONVERTER = _libreoffice        # replaced in tests without LibreOffice


async def convert_to_pdf(src: Path, dest: Path, timeout: float = CONVERT_TIMEOUT_S) -> Converted:
    """`src` (a DOCX, DOC, ODT or RTF file already checked by filetype) to `dest`, a PDF. The work happens in a
    temporary directory that is deleted whether it succeeds or not."""
    import time
    t0 = time.perf_counter()
    tmp = Path(tempfile.mkdtemp(prefix="kasafi-convert-"))
    try:
        work = tmp / src.name
        shutil.copyfile(src, work)
        try:                                   # the wall clock holds for any converter, LibreOffice or a stand-in
            pdf = await asyncio.wait_for(CONVERTER(work, tmp, timeout), timeout + 1)
        except asyncio.TimeoutError:
            raise ConversionError(f"conversion timed out after {timeout:.0f} s") from None
        with pdf.open("rb") as f:
            head = f.read(5)
        if not head.startswith(b"%PDF-"):
            raise ConversionError("the converter did not produce a PDF")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return Converted(dest, _sha256(dest), converter_version() if CONVERTER is _libreoffice else "fake converter",
                     time.perf_counter() - t0)


def convert_to_pdf_sync(src: Path, dest: Path, timeout: float = CONVERT_TIMEOUT_S) -> Converted:
    """For the indexing scripts (no event loop)."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    return asyncio.run(convert_to_pdf(src, dest, timeout))
