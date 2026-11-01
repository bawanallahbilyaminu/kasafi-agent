"""What a file really is, from its bytes (never its name or the server's Content-Type), and whether an Office
file is safe to convert (docs/architecture.md, "Office documents").

Kinds: pdf | docx | odt | doc | rtf | zip (a zip holding a PDF, as NBS ships reports) | unknown. A Word-type file
is untrusted input to LibreOffice: macro parts (DOCX `word/vbaProject.bin`, OLE `Macros`/`VBA` storages, ODT
`Basic/`), external targets (relationship `TargetMode="External"` for anything but a hyperlink, ODT `xlink:href`
to a URL) and embedded objects (`oleObject`, `package`, ODT `Object` parts, RTF `\\objdata`) are rejected before
anything is opened, and a zip is checked for bombs (declared size, ratio, member count) first.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

MAX_UNZIPPED = 300 * 1024 * 1024      # the declared size of every member together
MAX_MEMBERS = 3000
MAX_RATIO = 200                       # unzipped : zipped, a bomb's signature
OFFICE_KINDS = ("docx", "odt", "doc", "rtf")
EXTENSIONS = {"pdf": ".pdf", "docx": ".docx", "odt": ".odt", "doc": ".doc", "rtf": ".rtf", "zip": ".zip"}

_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _utf16(s: str) -> bytes:
    return s.encode("utf-16-le")


@dataclass(frozen=True)
class FileType:
    kind: str                 # pdf | docx | odt | doc | rtf | zip | unknown
    reason: str = ""          # why it is rejected ('' when it isn't)

    @property
    def office(self) -> bool:
        return self.kind in OFFICE_KINDS

    @property
    def rejected(self) -> bool:
        return bool(self.reason)


def sniff(path: Path) -> FileType:
    """The file's kind from its first bytes and, for a zip, its members."""
    with Path(path).open("rb") as f:
        head = f.read(8)
    if head.startswith(b"%PDF-"):
        return FileType("pdf")
    if head.startswith(b"PK\x03\x04"):
        return _sniff_zip(Path(path))
    if head.startswith(_OLE):
        return _sniff_ole(Path(path))
    if head.startswith(b"{\\rtf"):
        return _sniff_rtf(Path(path))
    return FileType("unknown", "not a PDF, Word, OpenDocument or RTF file")


def _sniff_zip(path: Path) -> FileType:
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return FileType("unknown", "a broken zip")
    with z:
        infos = z.infolist()
        bomb = zip_bomb(infos, path.stat().st_size)
        if bomb:
            return FileType("zip", bomb)
        names = [i.filename for i in infos]
        lower = [n.lower() for n in names]
        if any(n.startswith("word/vbaproject") or n.endswith("vbaproject.bin") for n in lower):
            return FileType("docx", "macro-enabled Word file (vbaProject)")
        if "word/document.xml" in lower:
            return FileType("docx", docx_problem(z, names))
        if "content.xml" in lower:
            mimetype = ""
            if "mimetype" in lower:
                mimetype = z.read(names[lower.index("mimetype")]).decode("ascii", "replace")
            if "opendocument.text" in mimetype or "content.xml" in lower and "styles.xml" in lower:
                return FileType("odt", odt_problem(z, names))
            return FileType("unknown", f"an OpenDocument file that is not text ({mimetype or 'no mimetype'})")
        if any(n.endswith(".pdf") for n in lower):
            return FileType("zip")                            # a zip holding the PDF: unpacked in the sandbox
    return FileType("unknown", "a zip with no PDF, Word or OpenDocument file")


def zip_bomb(infos: list[zipfile.ZipInfo], zipped: int) -> str:
    """Why a zip must not be opened: too many members, too much declared content, or a ratio only a bomb has."""
    if len(infos) > MAX_MEMBERS:
        return f"zip bomb check: {len(infos)} members (> {MAX_MEMBERS})"
    total = sum(max(i.file_size, 0) for i in infos)
    if total > MAX_UNZIPPED:
        return f"zip bomb check: {total} bytes declared (> {MAX_UNZIPPED})"
    if zipped > 0 and total / zipped > MAX_RATIO and total > 10 * 1024 * 1024:
        return f"zip bomb check: ratio {total // zipped}:1"
    return ""


_EXTERNAL = re.compile(r'(?is)<Relationship\b[^>]*TargetMode="External"[^>]*>')
_TYPE = re.compile(r'(?is)Type="[^"]*/relationships/([a-zA-Z]+)"')
_OBJECT_PART = re.compile(r"(?i)^word/(?:embeddings|activex)/|\.bin$|\.exe$|\.dll$|\.js$|\.vbs$")


def docx_problem(z: zipfile.ZipFile, names: list[str]) -> str:
    """A DOCX part that would run code or fetch content: embedded objects or ActiveX parts, and relationships with
    an external target other than a plain hyperlink (external images, templates, OLE links)."""
    for n in names:
        if _OBJECT_PART.search(n):
            return f"embedded object part ({n})"
    for n in names:
        if n.lower().startswith("word/") and n.lower().endswith(".rels"):
            xml = z.read(n).decode("utf-8", "replace")
            for rel in _EXTERNAL.finditer(xml):
                kind = (_TYPE.search(rel.group(0)) or [None, ""])[1]
                if kind.lower() != "hyperlink":
                    return f"external link ({kind or 'relationship'}) in {n}"
            if re.search(r'(?i)/relationships/(?:oleObject|package|externalLink|attachedTemplate|frame)"', xml):
                return f"embedded object or external part in {n}"
    return ""


def odt_problem(z: zipfile.ZipFile, names: list[str]) -> str:
    for n in names:
        low = n.lower()
        if low.startswith("basic/") or low.startswith("scripts/") or "/basic/" in low:
            return f"macro part ({n})"
        if low.startswith("object ") or low.startswith("object") and "/" in low:
            return f"embedded object ({n})"
    for n in ("content.xml", "styles.xml"):
        if n in [x.lower() for x in names]:
            xml = z.read(names[[x.lower() for x in names].index(n)]).decode("utf-8", "replace")
            if re.search(r'(?i)xlink:href="(?:https?|ftp|file)://', xml):
                return f"external link in {n}"
            if re.search(r"(?i)<draw:object\b|<draw:plugin\b|<office:script\b", xml):
                return f"embedded object or script in {n}"
    return ""


def _sniff_ole(path: Path) -> FileType:
    """An OLE compound file: a Word document when it has a 'WordDocument' stream; macros when it has a 'Macros'
    or 'VBA' storage (the directory entries are UTF-16LE names, found by a scan)."""
    data = Path(path).read_bytes()
    if _utf16("Macros") in data or _utf16("VBA") in data or _utf16("_VBA_PROJECT") in data:
        return FileType("doc", "macro-enabled Word file (VBA storage)")
    if _utf16("WordDocument") not in data:
        return FileType("unknown", "an OLE file that is not a Word document")
    if _utf16("ObjectPool") in data and _utf16("\x01Ole") in data:
        return FileType("doc", "embedded objects (ObjectPool)")
    return FileType("doc")


def _sniff_rtf(path: Path) -> FileType:
    text = Path(path).read_bytes()[:4 * 1024 * 1024].decode("latin-1", "replace")
    if re.search(r"\\objdata|\\objemb|\\objautlink|\\objlink", text):
        return FileType("rtf", "embedded object (\\objdata)")
    if re.search(r"(?i)INCLUDEPICTURE|INCLUDETEXT|\\field\{\\\*\\fldinst\s*\{?\s*HYPERLINK\s+\"?(?:https?|file)://[^\"}]*\\\\", text):
        return FileType("rtf", "a field that fetches content")
    return FileType("rtf")
