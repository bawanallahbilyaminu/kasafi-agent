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
        if out:
            return out.splitlines()[0][:80]
    except (OSError, subprocess.SubprocessError):
        pass
    ini = Path(exe).parent / "version.ini"           # Windows: soffice.exe prints nothing; the install says
    if ini.exists():
        for line in ini.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("ProductVersion=") or line.startswith("MsiProductVersion="):
                return f"LibreOffice {line.split('=', 1)[1].strip()}"[:80]
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


async def convert_to_pdf(src: Path, dest: Path, timeout: float = CONVERT_TIMEOUT_S,
                         strip: tuple | list = (), kind: str = "") -> Converted:
    """`src` (a DOCX, DOC, ODT or RTF file already checked by filetype) to `dest`, a PDF; `strip`: the inert
    embedded parts filetype found, removed from the copy that is converted; `kind`: what the bytes are, so the
    working copy carries the right extension whatever the file was called (LibreOffice picks its import filter
    by the name: a DOCX called .pdf fails to load). The work happens in a temporary directory that is deleted
    whether it succeeds or not."""
    import time
    from app.acquisition.filetype import EXTENSIONS
    t0 = time.perf_counter()
    tmp = Path(tempfile.mkdtemp(prefix="kasafi-convert-"))
    try:
        work = tmp / (src.stem + EXTENSIONS.get(kind, src.suffix or ".docx"))
        if strip:
            strip_parts(src, list(strip), work)
        else:
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


def strip_parts(src: Path, parts: list[tuple[str, str]], dest: Path) -> Path:
    """A copy of a DOCX without its inert embedded parts (chart workbooks: the chart keeps its cached values),
    their relationships and the charts' external-data pointers, so the converter never opens them. The original
    file is left as it is."""
    import re
    import zipfile
    names = {p for p, _ in parts}
    if not names:
        shutil.copyfile(src, dest)
        return dest
    targets = {Path(p).name.lower() for p in names}
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if info.filename in names:
                continue
            data = zin.read(info)
            low = info.filename.lower()
            if low.endswith(".rels"):
                xml = data.decode("utf-8", "replace")
                xml = re.sub(r'<Relationship\b[^>]*Target="[^"]*?([^"/]+)"[^>]*/>',
                             lambda m: "" if m.group(1).lower() in targets else m.group(0), xml)
                data = xml.encode("utf-8")
            elif low.startswith("word/charts/") and low.endswith(".xml"):
                data = re.sub(rb"<c:externalData\b[^>]*?(?:/>|>.*?</c:externalData>)", b"", data, flags=re.S)
            elif low == "[content_types].xml":
                xml = data.decode("utf-8", "replace")
                xml = re.sub(r'<Override\b[^>]*PartName="/([^"]+)"[^>]*/>',
                             lambda m: "" if m.group(1) in names else m.group(0), xml)
                data = xml.encode("utf-8")
            zout.writestr(info.filename, data)
    return dest


def convert_to_pdf_sync(src: Path, dest: Path, timeout: float = CONVERT_TIMEOUT_S, strip: tuple | list = (),
                        kind: str = "") -> Converted:
    """For the indexing scripts (no event loop)."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    return asyncio.run(convert_to_pdf(src, dest, timeout, strip, kind))
