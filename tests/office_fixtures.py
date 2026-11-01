"""Office-document fixtures built in the tests (no real documents): DOCX, ODT, RTF, a fake legacy DOC, a
macro-enabled DOCX, a DOCX with an external link, a zip bomb; and a fake converter (a minimal PDF writer) for
machines without LibreOffice (docs/architecture.md, "Office documents")."""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="xml" ContentType="application/xml"/>'
                 '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.'
                 'wordprocessingml.document.main+xml"/></Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>')
DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{extra}</Relationships>')
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _p(text: str) -> str:
    return f"<w:p><w:r><w:t xml:space=\"preserve\">{text}</w:t></w:r></w:p>"


def docx_bytes(paragraphs: list[str], table: list[list[str]] | None = None, *, macro: bool = False,
               external_image: bool = False) -> bytes:
    body = "".join(_p(t) for t in paragraphs)
    if table:
        rows = "".join("<w:tr>" + "".join(f"<w:tc>{_p(c)}</w:tc>" for c in row) + "</w:tr>" for row in table)
        body += f"<w:tbl>{rows}</w:tbl>"
    document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W}><w:body>{body}</w:body></w:document>'
    extra = ('<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
             'Target="https://evil.example/tracker.png" TargetMode="External"/>' if external_image else "")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS.format(extra=extra))
        if macro:
            z.writestr("word/vbaProject.bin", b"\xd0\xcf\x11\xe0" + b"\x00" * 64)
    return buf.getvalue()


def odt_bytes(paragraphs: list[str], *, macro: bool = False, external_link: bool = False) -> bytes:
    text = "".join(f"<text:p>{t}</text:p>" for t in paragraphs)
    if external_link:
        text += '<draw:frame><draw:image xlink:href="https://evil.example/x.png"/></draw:frame>'
    content = ('<?xml version="1.0" encoding="UTF-8"?><office:document-content '
               'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
               'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
               'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
               'xmlns:xlink="http://www.w3.org/1999/xlink" office:version="1.2">'
               f'<office:body><office:text>{text}</office:text></office:body></office:document-content>')
    manifest = ('<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:'
                'xmlns:manifest:1.0" manifest:version="1.2"><manifest:file-entry manifest:full-path="/" '
                'manifest:media-type="application/vnd.oasis.opendocument.text"/><manifest:file-entry '
                'manifest:full-path="content.xml" manifest:media-type="text/xml"/></manifest:manifest>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.text", compress_type=zipfile.ZIP_STORED)
        z.writestr("content.xml", content, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("styles.xml", '<?xml version="1.0" encoding="UTF-8"?><office:document-styles '
                   'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>', compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("META-INF/manifest.xml", manifest, compress_type=zipfile.ZIP_DEFLATED)
        if macro:
            z.writestr("Basic/Standard/Module1.xml", "<script/>", compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def rtf_bytes(paragraphs: list[str], *, embedded_object: bool = False) -> bytes:
    body = "\\par ".join(paragraphs)
    obj = "{\\object\\objemb{\\*\\objdata 0105}}" if embedded_object else ""
    return ("{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Helvetica;}}\\f0\\fs24 " + body + obj + "\\par }").encode("latin-1", "replace")


def fake_doc_bytes(*, macro: bool = False) -> bytes:
    """An OLE compound file header with a 'WordDocument' directory entry name: enough for the sniffer; not a real
    document LibreOffice can open."""
    data = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 504
    data += "WordDocument".encode("utf-16-le") + b"\x00" * 100
    if macro:
        data += "Macros".encode("utf-16-le") + b"\x00" * 100
    return data + b"\x00" * 512


def zip_bomb_bytes() -> bytes:
    """A small zip declaring 40 MB of zeros (ratio over 1,000:1)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("word/document.xml", b"\x00" * (40 * 1024 * 1024))
    return buf.getvalue()


def pdf_bytes(lines: list[str]) -> bytes:
    """A minimal one-page PDF with the lines in Helvetica (ASCII; the fake converter's output)."""
    def esc(s: str) -> str:
        return s.encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = "BT /F1 11 Tf 40 780 Td 14 TL " + " T* ".join(f"({esc(l)}) Tj" for l in lines) + " ET"
    objs = ["<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    out = "%PDF-1.4\n"
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out.encode("latin-1")))
        out += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(out.encode("latin-1"))
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


def text_of(path: Path) -> list[str]:
    """The paragraphs of a DOCX, ODT or RTF fixture (for the fake converter)."""
    raw = path.read_bytes()
    if raw.startswith(b"PK"):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            xml = z.read("word/document.xml" if "word/document.xml" in names else "content.xml").decode("utf-8", "replace")
        if "word/document.xml" in names:
            rows = [" | ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", tr)) for tr in re.findall(r"<w:tr>.*?</w:tr>", xml)]
            paras = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", re.sub(r"<w:tbl>.*?</w:tbl>", "", xml))
            return paras + rows
        return re.findall(r"<text:p>([^<]*)</text:p>", xml)
    if raw.startswith(b"{\\rtf"):
        body = raw.decode("latin-1").split("\\fs24 ", 1)[-1]
        return [p.strip(" }") for p in body.split("\\par") if p.strip(" }")]
    return ["(a legacy DOC fixture: no text)"]


async def fake_converter(src: Path, out_dir: Path, timeout: float) -> Path:
    """Stands in for LibreOffice on a machine without it: the fixture's text as a one-page PDF."""
    pdf = out_dir / (src.stem + ".pdf")
    pdf.write_bytes(pdf_bytes(text_of(src)))
    return pdf
