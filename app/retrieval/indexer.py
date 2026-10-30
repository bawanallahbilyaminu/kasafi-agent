"""Index PDFs into Postgres: one row per page (for citations) plus searchable chunks.

Document text is untrusted data (CLAUDE.md rule 6): it is stored and searched, never executed
or followed. Pages with no text layer are stored with source='none' and need OCR later.
Re-indexing is idempotent: a document whose SHA-256 hasn't changed is skipped, and OCR text
already stored for scanned pages is kept.

Budget tables run across many pages, and the same sector rows appear in several tables (total,
personnel, overhead, capital). So each chunk starts with the title of the table it sits in,
carried over from earlier pages, e.g. "[Table: ... Total Expenditure by Programme]".
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import psycopg
import pypdfium2 as pdfium

from app.retrieval import entities, line_meaning, quality, tables

log = logging.getLogger(__name__)

CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200
MIN_PAGE_CHARS = 40   # less than this is treated as "no text layer"
# A text layer whose font map drops a letter (IOM DTM flash report: "di placed", "hou ehold", no "s" at all) reads
# as text but can't be searched. On a page with enough English letters, each of these common ones is several per
# cent of them; one that is nearly absent means the layer is broken, and the page is OCR'd instead.
COMMON_LETTERS = "etaoinsr"          # not "h": budget line names barely use it (67 sound pages flagged)
MIN_LETTERS_CHECKED = 400
MISSING_LETTER_SHARE = 0.004


def broken_text_layer(text: str) -> bool:
    letters = [c for c in text.lower() if "a" <= c <= "z"]
    if len(letters) < MIN_LETTERS_CHECKED:
        return False
    return any(letters.count(c) < MISSING_LETTER_SHARE * len(letters) for c in COMMON_LETTERS)


def needs_ocr(page_no: int, text: str, image_pages: set[int]) -> bool:
    """No text layer, a picture of a table, or a text layer with letters missing."""
    return len(text) < MIN_PAGE_CHARS or page_no in image_pages or broken_text_layer(text)


@dataclass
class IndexResult:
    doc_id: str
    status: str          # "indexed" | "unchanged" | "missing" | "failed"
    pages: int = 0
    empty_pages: int = 0
    chunks: int = 0
    detail: str = ""


def normalise_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_file(doc: dict, data_dir: Path) -> Path | None:
    """The manifest's `file` (relative to data/, e.g. advisories/nihsa-afo-2026.pdf), <id>.pdf, or a local file
    named after the title (punctuation ignored), as in fetch_seed_docs.py."""
    if doc.get("file"):
        named = data_dir / doc["file"]
        return named if named.exists() else None
    by_id = data_dir / f"{doc['id']}.pdf"
    if by_id.exists():
        return by_id
    wanted = normalise_name(doc["title"])
    return next((p for p in data_dir.glob("*.pdf") if normalise_name(p.stem) == wanted), None)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 16):
            h.update(chunk)
    return h.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


TOP_OF_PAGE = 0.85   # a title whose text starts above 85% of the page height is printed at the top


def titles_first(page: pdfium.PdfPage, text: str) -> str:
    """Move table titles printed at the top of the page to the start of its text.

    PDFium returns text in the PDF's content order, and the budget PDFs store each table's title
    (printed at the top of the page) as the LAST line. A title carried forward from there landed on
    the next page's table, so the 2025 budget's total-expenditure rows were labelled with the
    previous table's title. Only title lines move; everything else keeps its order, because the
    content order is what keeps wrapped column headers intact (a full visual re-order scrambled them).
    """
    lines = text.splitlines()
    tail = [i for i in range(max(0, len(lines) - 3), len(lines)) if is_table_title(lines[i])]
    if not tail:
        return text
    textpage = page.get_textpage()
    height = page.get_height()
    move = []
    for i in tail:
        searcher = textpage.search(lines[i].strip()[:60], match_case=True)
        hit = searcher.get_next()
        if hit and textpage.get_charbox(hit[0])[3] >= TOP_OF_PAGE * height:
            move.append(i)
    if not move:
        return text
    return "\n".join([lines[i] for i in move] + [line for i, line in enumerate(lines) if i not in move])


IMAGE_PAGE_CHARS = 400   # a page with less text than this...
IMAGE_SHARE = 0.25       # ...and an image covering a quarter of it is a picture of a table: OCR it
DRAWN_PATHS = 40         # ...or this many vector paths: text turned into outlines, a map or a chart (L31)


def image_table_pages(path: Path) -> set[int]:
    """Pages (1-based) whose content is an image with only a short text layer, e.g. a title.

    The NBS CPI prints its state tables as images under a text title ("Combined Urban and Rural State
    Consumer Price Index (Base Period: 2024 = 100)", 92 characters): more than MIN_PAGE_CHARS, so the
    page counted as text and the table, with Sokoto's published year-on-year rate, was never OCR'd.
    NIHSA's 2026 Annual Flood Outlook draws its pages as vector outlines under a running footer ("NATIONAL
    SEASONAL FLOOD FORECAST AND ADVISORY 04", 48 characters) with no image at all; NiMet's 2026 SCP draws its
    state maps as paths. Many paths under a short text layer count as a picture too (L31).
    """
    pdf = pdfium.PdfDocument(str(path))
    out = set()
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            if len(page.get_textpage().get_text_range().strip()) >= IMAGE_PAGE_CHARS:
                continue
            w, h = page.get_size()
            paths = 0
            for obj in page.get_objects(max_depth=3):
                if obj.type == pdfium.raw.FPDF_PAGEOBJ_IMAGE:
                    left, bottom, right, top = obj.get_bounds()
                    if (right - left) * (top - bottom) >= IMAGE_SHARE * w * h:
                        out.add(i + 1)
                        break
                elif obj.type == pdfium.raw.FPDF_PAGEOBJ_PATH:
                    paths += 1
                    if paths >= DRAWN_PATHS:
                        out.add(i + 1)
                        break
    finally:
        pdf.close()
    return out


def extract_pages(path: Path, first: int = 1, last: int | None = None) -> list[str]:
    """Text of pages first..last (1-based, inclusive; all pages by default)."""
    pdf = pdfium.PdfDocument(str(path))
    try:
        pages = []
        for i in range(first - 1, min(last or len(pdf), len(pdf))):
            page = pdf[i]
            pages.append(clean_text(titles_first(page, page.get_textpage().get_text_range())))
        return pages
    finally:
        pdf.close()


# A title names a kind of statement ("budget" alone isn't enough: "Procurement of software for tracking of
# Budget" is a line item) and has a title shape ("... by Programme", "Summary of ...", "Total ...").
_TITLE_WORDS = re.compile(r"(?i)\b(expenditure|revenue|receipts|appropriation|financing|summary|statement|"
                          r"price index|indices)\b")
_TITLE_SHAPE = re.compile(r"(?i)(\bby\b|^summary\b|^total\b|\bsummary of\b|\bstatement of\b|\bprice index\b|"
                          r"\bindices\b)")
_HAS_AMOUNT = re.compile(r"\d{1,3}(,\d{3})+|\d+\.\d{2}\b")


def is_table_title(line: str) -> bool:
    """A heading such as 'Sokoto State Government 2026 Approved Budget - Total Expenditure by Programme'.

    Headings are mostly capitalised words; a prose sentence ("Consolidated Revenue Fund (CRF) to be
    maintained by the Government ...") isn't.
    """
    s = line.strip()
    if not (15 <= len(s) <= 160 and not s.endswith(".") and not _HAS_AMOUNT.search(s)
            and _TITLE_WORDS.search(s) and _TITLE_SHAPE.search(s) and s[:1].isupper()):
        return False
    long_words = [w for w in re.findall(r"[A-Za-z]+", s) if len(w) > 3]
    return bool(long_words) and sum(w[0].isupper() for w in long_words) / len(long_words) >= 0.7


# A table often opens with its own "Total <kind> Expenditure" row, and that row is a better guide to
# where the table starts than the title: some titles are drawn as images, and some are stored at the
# end of the page although printed mid-page (2026 budget p42: personnel rows start at line 28).
_TOTAL_ROW = re.compile(r"^\s*Total ((?:[A-Za-z\-]+ ){0,4}?Expenditure)\b.*\d")


def spend_kind(s: str) -> str | None:
    """'personnel' | 'overhead' | 'debt' | 'capital' | 'total' for a title or 'Total ...' row."""
    s = s.lower()
    if "non-debt recurrent" in s or "overhead" in s:
        return "overhead"
    for word, kind in (("personnel", "personnel"), ("debt service", "debt"), ("capital", "capital")):
        if word in s:
            return kind
    return "total" if "expenditure" in s else None


def next_title(line: str, title: str) -> str:
    """The table title in force after this line."""
    if is_table_title(line):
        return line.strip()
    m = _TOTAL_ROW.match(line)
    # Only a specific kind starts a new table. A plain "Total Expenditure" row is also each ministry's
    # subtotal in the amended budget; switching on it replaced real titles with a generic one.
    kind = spend_kind(m.group(1)) if m else None
    if kind and kind != "total" and kind != spend_kind(title):
        return f"{m.group(1)} (table starting at its Total row)"
    return title


# --- bracketed negatives ------------------------------------------------------------------------
# Financial statements write negatives the accounting way: "(56,893,525,653.90)". Only amounts in that
# shape (thousands separators and two decimals), or a two-decimal value in a labelled cell, are turned
# into "-56,893,525,653.90". Brackets in running text are just parentheses ("Sokoto (3.01%)" in the CPI
# is +3.01%; the same sentence writes "Adamawa (-6.10%)"), and "(25,000)" in a budget line is a quantity.
_ACCOUNTING_NEG = re.compile(r"(?<![\w-])\((\d{1,3}(?:,\d{3})+\.\d{2})\)(?![\w%])")
_CELL_NEG = re.compile(r"(?<=: )\((\d+\.\d{2})\)(?=\s*(?:\||$))", re.M)


def accounting_negatives(text: str) -> str:
    return _CELL_NEG.sub(r"-\1", _ACCOUNTING_NEG.sub(r"-\1", text))


# --- column labelling --------------------------------------------------------------------------
# Budget tables reach us as rows of bare numbers ("05 Education 8,139,687,377.37 80,287,... -"), and the
# column header ("Code Sector ... 2024 Full Year Actuals 2025 Revised Budget ... 2026 Approved Budget ...")
# is on an earlier line or page. A model counting positions picked the wrong column (eval 11), so rows
# are labelled in code: "05 Education | 2026 Approved Budget: 128,495,868,362.13 | ...". A row is only
# labelled when its value count matches the column count exactly; anything else stays as it was.
# Brackets must be balanced: "2201)" in "OTHER RECURRENT COSTS (EXCLUDING 2201)" is part of the name, and
# counting it as a value left the BIRs' "22" row unlabelled (found by the totals quality check).
_VALUE = re.compile(r"^(?:-|-?[\d,]+(?:\.\d+)?%?|\(-?[\d,]+(?:\.\d+)?%?\))$")
_COLUMN_SPLIT = re.compile(r"(?<!against)(?<!to)\s(?=20\d\d\b)|\s(?=%)|\s(?=Balance\b)")
# Detail tables start their header with "Code ..."; summary tables with "Item ..." (2024/2025 budgets).
_HEADER_START = re.compile(r"^(Code|Item)\b")
# A data row starts with a 2-digit sector code ("04 Health") or a 5+-digit code ("010101"); header
# lines may start with a 4-digit year ("2026 Approved"), which must not end the header.
_ROW_CODE = re.compile(r"^(\d{2}|\d{5,})\s")


def parse_columns(header: str) -> list[str]:
    """'Code Sector 2024 Full Year Actuals 2025 Revised Budget ...' -> ['2024 Full Year Actuals', ...]."""
    h = re.sub(r"\s+", " ", header).strip()
    m = re.search(r"\b20\d\d\b", h)
    if not _HEADER_START.match(h) or not m:
        return []
    cols = [c.strip() for c in _COLUMN_SPLIT.split(h[m.start():]) if c.strip()]
    return cols if len(cols) >= 2 else []


_BARE_CODE = re.compile(r"^\d{5,}$")


def label_row(line: str, columns: list[str]) -> str:
    tokens = line.split()
    values: list[str] = []
    while tokens and _VALUE.match(tokens[-1]):
        values.insert(0, tokens.pop())
    if not columns or not tokens or len(values) != len(columns) or not any(v != "-" for v in values):
        return line
    # A bare 5+-digit number is a budget code (economic code 23020105), not an amount: amounts have commas.
    # On the 2025 amended budget p114 a wrapped line put a code and a quantity "(25,000)" in value cells.
    if any(_BARE_CODE.match(v) for v in values):
        return line
    return " ".join(tokens) + " | " + " | ".join(f"{c}: {v}" for c, v in zip(columns, values))


# A header continuation line must look like header text. Without this, the next row's name ("Bureau for
# Public Procurement", no amount, no code) was swallowed into the last column's label.
_HEADER_WORDS = re.compile(
    r"(?i)\b(20\d\d|budget|actuals?|estimates?|performance|revised|approved|original|final|draft|adjustments?|"
    r"out-year|tagging|balance|against|january|september|q[1-4]|year|date|bi-lateral|post|mda|proposal|"
    r"executive|full|supplementary|virement)\b|%|\(")
MAX_HEADER_LINES = 14   # the 2024 budget wraps its header almost one word per line


def _is_header_line(line: str) -> bool:
    return not _HAS_AMOUNT.search(line) and not _ROW_CODE.match(line) and bool(_HEADER_WORDS.search(line))


def label_tables(text: str, columns: list[str], open_header: list[str] | None = None
                 ) -> tuple[str, list[str], list[str]]:
    """Label table rows on one page.

    Returns the new text, the columns in force at the end of the page, and any header still open
    at the end of the page: a header split by a page break continues on the next page.
    """
    lines, out, i = text.splitlines(), [], 0
    if open_header:                          # finish a header that started on the previous page
        j = 0
        while j < len(lines) and j <= MAX_HEADER_LINES and _is_header_line(lines[j]):
            j += 1
        if cols := parse_columns(" ".join(open_header + lines[:j])):
            columns = cols
        out.extend(lines[:j])
        i = j
    while i < len(lines):
        line = lines[i]
        if _HEADER_START.match(line) and not _HAS_AMOUNT.search(line):
            header, j = [line], i + 1
            while j < len(lines) and j - i <= MAX_HEADER_LINES and _is_header_line(lines[j]):
                header.append(lines[j])
                j += 1
            if j == len(lines):              # the page ended inside the header
                out.extend(lines[i:j])
                return chr(10).join(out), columns, header
            if cols := parse_columns(" ".join(header)):
                columns = cols
            out.extend(lines[i:j])
            i = j
            continue
        # Columns carry over a new title: budgets often print a table's header only once, and the
        # tables in one section share a layout. The exact value-count check guards the rest.
        out.append(label_row(line, columns))
        i += 1
    return chr(10).join(out), columns, []


# --- OCR'd tables ------------------------------------------------------------------------------
# OCR returns a table as "a | b | c" rows. Its header can take two lines, the first leaving a blank cell
# where a heading spans two columns: "State | Sep-25 | | Aug-26 | ..." over "State | Food | All Items | ...".
# Rows are labelled with the combined names ("Sokoto | Sep-25 Food: 127.0 | ... | YoY All Items: 8.0"),
# again only when the value count matches the header exactly. Without this the NBS state CPI table was
# bare numbers, and search for Sokoto's year-on-year rate never found it.
_PIPE_NUMBER = re.compile(r"^(?:-|-?\(?[\d,]+(?:\.\d+)?\)?%?)$")
_YEAR = re.compile(r"^(?:19|20)\d\d$")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.split("|")]


def _is_pipe_header(cells: list[str]) -> bool:
    rest = [c for c in cells[1:] if c]
    return len(cells) >= 3 and bool(rest) and not any(_PIPE_NUMBER.match(c) and not _YEAR.match(c) for c in rest)


def _combine_headers(rows: list[list[str]]) -> list[str]:
    width = max(len(r) for r in rows) - 1
    filled = []
    for r in rows:
        cells, last = (r[1:] + [""] * width)[:width], ""
        row = []
        for c in cells:
            last = c or last
            row.append(last)
        filled.append(row)
    names = []
    for parts in zip(*filled):
        name = []
        for p in parts:
            p = _ABBREVIATIONS.get(p, p)
            p = _MONTH_YY.sub(lambda m: f"{m.group(1)} 20{m.group(2)}", p)    # "Sep-25" -> "Sep 2025"
            if p and p not in name:
                name.append(p)
        names.append(" ".join(name))
    return names


# Spelled out so a question saying "year-on-year" finds a column headed "YoY"
_ABBREVIATIONS = {"YoY": "Year-on-Year", "MoM": "Month-on-Month"}
_MONTH_YY = re.compile(r"^([A-Z][a-z]{2,8})-(\d{2})$")


def label_pipe_tables(text: str) -> tuple[str, set[str]]:
    """Label OCR'd pipe tables. Returns the new text and the labelled rows (indexed as key rows)."""
    lines, out, labelled, columns, i = text.splitlines(), [], set(), [], 0
    while i < len(lines):
        line = lines[i]
        if "|" not in line:
            if line.strip():
                columns = []                       # a table ends at the first line of text
            out.append(line)
            i += 1
            continue
        cells = _cells(line)
        if _is_pipe_header(cells):
            header, j = [cells], i + 1
            while j < len(lines) and len(header) < 3 and "|" in lines[j] and _is_pipe_header(_cells(lines[j])):
                header.append(_cells(lines[j]))
                j += 1
            columns = _combine_headers(header)
            out.extend(lines[i:j])
            i = j
            continue
        values = cells[1:]
        while values and not values[-1] and len(values) > len(columns):
            values.pop()                           # a trailing "|" leaves an empty last cell
        if columns and cells[0] and len(values) == len(columns) and all(_PIPE_NUMBER.match(v) for v in values if v) \
                and any(values):
            row = cells[0] + " | " + " | ".join(f"{c}: {v}" for c, v in zip(columns, values) if v)
            out.append(row)
            labelled.add(row)
        else:
            out.append(line)
        i += 1
    return chr(10).join(out), labelled


def contextual_chunks(pages: list[str], labelled: list[str] | None = None,
                      line_titles: list[list[str]] | None = None) -> list[list[str]]:
    """Label table columns, chunk every page, and prefix each chunk with the table title in force at its start.

    `labelled`, if given, receives each page's labelled text (for the quality checks); `line_titles` the
    table title in force for each of its lines (for the structured budget rows)."""
    out, title, columns, open_header = [], "", [], []
    for text in pages:
        page_chunks = []
        text, pipe_rows = label_pipe_tables(text)
        text, columns, open_header = label_tables(text, columns, open_header)
        if labelled is not None:
            labelled.append(text)
        page_titles: list[str] = []
        # Sector-total rows ("04 Health"), ministry-total rows (12-digit codes ending in eight zeros, e.g.
        # "017200000000 Ministry for Religious Affairs") and "Total ..." rows also get their own one-row
        # chunk with the table title: in a big table they're outranked by the many rows below them that
        # repeat the same name.
        key_rows, row_title = [], title
        for line in text.splitlines():
            new_title = next_title(line, row_title)
            if new_title != row_title and is_table_title(line):
                row_title = new_title
                page_titles.append(row_title)
                continue
            row_title = new_title
            page_titles.append(row_title)
            if " | " in line and (re.match(r"^(\d{2}|\d{4}0{8})\s", line) or line.lower().startswith("total")
                                  or line in pipe_rows):
                key_rows.append((f"[Table: {row_title}]" + chr(10) if row_title else "") + line)
        for chunk in chunk_page(text) if len(text) >= MIN_PAGE_CHARS else []:
            lines = chunk.splitlines()
            prefix = f"[Table: {title}]" + chr(10) if title and not is_table_title(lines[0]) else ""
            page_chunks.append(prefix + chunk)
            for line in lines:
                title = next_title(line, title)
        out.append(page_chunks + key_rows)
        if line_titles is not None:
            line_titles.append(page_titles)
    return out


def ocr_page_chunks(text: str) -> list[str]:
    """Chunks for one page OCR'd after indexing: the same table labelling and key rows as any page."""
    return contextual_chunks([text])[0]


def chunk_page(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split on line boundaries into ~size-char pieces with ~overlap chars repeated between pieces."""
    if len(text) <= size:
        return [text] if text else []
    lines, chunks, cur = text.split("\n"), [], ""
    for line in lines:
        while len(line) > size:                    # a single huge line (rare): hard-split it
            head, line = line[:size], line[size:]
            if cur:
                chunks.append(cur)
            chunks.append(head)
            cur = ""
        if cur and len(cur) + 1 + len(line) > size:
            chunks.append(cur)
            cur = cur[-overlap:].split("\n", 1)[-1] if overlap else ""
        cur = f"{cur}\n{line}" if cur else line
    if cur.strip():
        chunks.append(cur)
    return chunks


def index_document(conn: psycopg.Connection, doc: dict, path: Path, *, force: bool = False,
                   pages: list[str] | None = None, sha: str | None = None,
                   image_pages: set[int] | None = None) -> IndexResult:
    """Index one PDF. `pages` (already extracted, e.g. by the sandbox for a fetched PDF) skips extraction;
    `image_pages` (pages that are pictures of tables) is computed from the file when not given."""
    sha = sha or sha256_file(path)
    if not force:
        row = conn.execute("SELECT sha256 FROM documents WHERE id = %s", (doc["id"],)).fetchone()
        if row and row[0] == sha:
            return IndexResult(doc["id"], "unchanged")
    pages = list(pages) if pages is not None else extract_pages(path)
    image_pages = image_pages if image_pages is not None else image_table_pages(path)
    # Keep OCR text from earlier runs for pages that still have no (useful) text layer.
    ocr = dict(conn.execute("SELECT page, text FROM pages WHERE doc_id = %s AND source = 'ocr'", (doc["id"],)).fetchall())
    sources = []
    for i, text in enumerate(pages):
        ocr_it = needs_ocr(i + 1, text, image_pages)
        if ocr_it and (i + 1) in ocr:
            pages[i] = ocr[i + 1]
            sources.append("ocr")
        else:
            sources.append("none" if ocr_it else "text")   # "none" keeps its title text until OCR'd
    empty = sources.count("none")
    pages = [accounting_negatives(p) for p in pages]
    labelled: list[str] = []
    line_titles: list[list[str]] = []
    chunked = contextual_chunks(pages, labelled, line_titles)
    rows = tables.extract_rows(labelled, line_titles) if doc.get("category") in tables.TABLE_CATEGORIES else []
    with conn.transaction():
        conn.execute("DELETE FROM documents WHERE id = %s", (doc["id"],))   # cascades to pages/chunks
        conn.execute(
            """INSERT INTO documents (id, title, category, year, publisher, source_url, acquisition, sha256, page_count,
                                      final_url, fetched_at, series, edition)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (doc["id"], doc["title"], doc.get("category"), doc.get("year"), doc.get("publisher"),
             doc.get("source_url"), doc.get("acquisition"), sha, len(pages), doc.get("final_url"),
             doc.get("fetched_at"), doc.get("series"), doc.get("edition")),
        )
        n_chunks = 0
        with conn.cursor() as cur:
            with cur.copy("COPY pages (doc_id, page, text, source) FROM STDIN") as cp:
                for i, (text, source) in enumerate(zip(pages, sources), start=1):
                    cp.write_row((doc["id"], i, text, source))
            with cur.copy("COPY chunks (doc_id, page, idx, text) FROM STDIN") as cp:
                for i, page_chunks in enumerate(chunked, start=1):
                    for j, chunk in enumerate(page_chunks):
                        cp.write_row((doc["id"], i, j, chunk))
                        n_chunks += 1
            # One searchable line per printed table row; each typed cell points back to its line
            line_ids = tables.line_ids(doc["id"], rows)
            with cur.copy("COPY budget_lines (id, doc_id, page, table_title, classification, spend_kind, code, name, "
                          "row_text) FROM STDIN") as cp:
                for (page, title, row_text), (lid, r) in line_ids.items():
                    cp.write_row((lid, doc["id"], page, title, r.classification, r.spend_kind, r.code, r.name, row_text))
            with cur.copy("COPY budget_rows (doc_id, page, table_title, classification, spend_kind, code, name, "
                          "column_label, year, measure, period, amount_naira, row_text, line_id) FROM STDIN") as cp:
                for r in rows:
                    cp.write_row((doc["id"], r.page, r.table_title, r.classification, r.spend_kind, r.code, r.name,
                                  r.column_label, r.year, r.measure, r.period, r.amount_naira, r.row_text,
                                  line_ids[(r.page, r.table_title, r.row_text)][0]))
    if rows:
        try:
            line_meaning.enrich(conn, doc["id"])
        except Exception as e:  # the embedding model can't load: keep the code descriptions, search by keyword
            conn.rollback()
            log.warning("%s: line vectors skipped: %s", doc["id"], e)
            line_meaning.enrich(conn, doc["id"], embed=False)
    quality.run(conn, doc["id"], doc.get("category"),
                [(i, text, src) for i, (text, src) in enumerate(zip(labelled, sources), start=1)])
    if rows:
        try:                    # the structured core the analysis tools query, with its reconciliation checks
            entities.build(conn, doc["id"], path)
        except Exception as e:  # never lose the index over it: search and model reading still work
            conn.rollback()
            log.warning("%s: entity build failed: %s", doc["id"], e)
    return IndexResult(doc["id"], "indexed", len(pages), empty, n_chunks)


def index_manifest(conn: psycopg.Connection, manifest_path: Path, *, only: list[str] | None = None,
                   force: bool = False) -> list[IndexResult]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []
    for doc in manifest["documents"]:
        if only and doc["id"] not in only:
            continue
        path = find_file(doc, manifest_path.parent)
        if path is None:
            results.append(IndexResult(doc["id"], "missing", detail="no local PDF"))
            continue
        try:
            results.append(index_document(conn, doc, path, force=force))
        except pdfium.PdfiumError as e:
            results.append(IndexResult(doc["id"], "failed", detail=f"unreadable PDF: {e}"))
    return results
