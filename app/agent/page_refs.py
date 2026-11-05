"""Every page number a model writes into an answer is the page code verified the figure on (5 Nov 2026).

Citations use the page of the PDF, and code binds a figure to its page. But a writer also puts page numbers in its own
sentences, and it reads them off the page: the census's PDF page 22 prints '4' at its top, and lfB (trace 659) said
'123 primary … (p. 4)'. Here each page number in the text is tested against the pages the answer cites: the figures it
stands beside must be printed on that page. If not, it becomes the cited page that does print them; if none does, the
number goes. A sentence with no figure is left as it is: nothing in it can be verified on a page.

Applies to text a model wrote. Sources lines, and lines written in code from checked rows, have their pages from code.
"""

from __future__ import annotations

import re

_LIST = r"\d{1,4}(?:\s*(?:,|and|da|&|[–-])\s*\d{1,4})+(?=\s*[)\].;:]|\s*$)"
REF = re.compile(rf"(?i)(?<![\w])(?P<word>pp?\.|pages?|shafi(?:\s+na)?)\s*(?P<nums>{_LIST}|\d{{1,4}})(?![\d,]*\d)", re.M)
_NOT_WRITTEN = ("📄", "📎", "ℹ️", "⏳", "_Reply", "_Ku rubuta")
_YEARS = re.compile(r"(?<![\d,.])(?:19|20)\d\d(?:[/–-]\d{2,4})?(?![\d,]|\.\d)")
_SENTENCE = re.compile(r"(?<!\bp\.)(?<=[.!?;])\s+")


def printed(segment: str, page_text: str, extra: list[str] | None = None) -> bool:
    """Every figure of two or more digits in this piece of text is printed on the page (a year isn't a figure)."""
    from app.agent.answer import Evidence, unverified_numbers
    bad = unverified_numbers(_YEARS.sub(" ", segment), [Evidence(1, "d", "d", None, 0, "text", page_text)], extra or [])
    return not [b for b in bad if len(re.sub(r"\D", "", str(b))) >= 2]


def _has_figures(segment: str) -> bool:
    from app.agent.answer_check import figures_in
    return bool(figures_in(_YEARS.sub(" ", segment)))


def _gone(text: str, start: int, end: int) -> str:
    """The text without this page reference, and without the brackets or comma it leaves behind."""
    before, after = text[:start], text[end:]
    if before.rstrip().endswith("(") and after.lstrip().startswith(")"):
        before, after = before.rstrip()[:-1].rstrip(), after.lstrip()[1:]
    elif before.rstrip().endswith(","):
        before = before.rstrip()[:-1]
    else:
        before = before.rstrip()
    return before + after


def _key(title: str) -> str:
    return re.sub(r"\W+", " ", title or "").strip().lower()[:25]


def _named_document(before_ref: str, pages: list[tuple]) -> tuple[str, list[tuple]]:
    """A reference written as '(<document title>, p. 22)': the title's own digits ('Census 23-24 Report') are not figures,
    and the page belongs to that document. Returns (the text before the reference without the title, the pages to judge
    it on). 5 Nov 2026: trace 96's right 'p. 22' was first moved to p. 23 of another cited document."""
    start = before_ref.rfind("(")
    if start < 0 or ")" in before_ref[start:]:
        return before_ref, pages
    inside = _key(before_ref[start + 1:])
    own = [x for x in pages if len(x) > 2 and _key(x[2]) and (inside.startswith(_key(x[2])) or _key(x[2]).startswith(inside))
           and inside]
    return (before_ref[:start], own) if own else (before_ref, pages)


def verified(text: str, pages: list[tuple], extra: list[str] | None = None) -> tuple[str, list[dict]]:
    """(the text with each page number verified, what was changed). `pages`: (page number, its text[, its document's
    title]), in the order cited. `extra`: what code computed (a calculated figure is printed on no page: its page number
    stays only if that page is cited)."""
    if not text or not pages:
        return text, []
    changes: list[dict] = []
    out: list[str] = []
    cited = {x[0] for x in pages}
    for line in text.split("\n"):
        if line.lstrip().startswith(_NOT_WRITTEN) or not REF.search(line):
            out.append(line)
            continue
        edits = []
        last = 0
        for m in REF.finditer(line):
            boundary = [b.end() for b in _SENTENCE.finditer(line, last, m.start())]
            segment, pool = _named_document(line[boundary[-1] if boundary else last:m.start()], pages)
            last = m.end()
            if not _has_figures(segment):
                continue
            said = [int(n) for n in re.findall(r"\d+", m.group("nums"))]
            good = [x[0] for x in pool if printed(segment, x[1])]
            if any(n in good for n in said):
                keep = [n for n in said if n in good]
                if keep != said:
                    edits.append((m, ", ".join(str(n) for n in keep)))
                    changes.append({"said": said, "now": keep, "around": segment[-80:]})
            elif good:
                edits.append((m, str(good[0])))
                changes.append({"said": said, "now": [good[0]], "around": segment[-80:]})
            elif extra and any(n in cited for n in said) and any(printed(segment, x[1], extra) for x in pool):
                continue
            else:
                edits.append((m, None))
                changes.append({"said": said, "now": [], "around": segment[-80:]})
        for m, new in reversed(edits):
            if new is None:
                line = _gone(line, m.start(), m.end())
            else:
                line = line[:m.start("nums")] + new + line[m.end("nums"):]
        out.append(line)
    return "\n".join(out), changes


def cited_pages(conn, cited: list) -> list[tuple[int, str, str]]:
    """The cited pages (page, whole text, document title), in the order cited: from the library (an evidence's text may
    be an extract); its own text when the library can't be read."""
    want = list(dict.fromkeys((e.doc_id, e.page) for e in cited or [] if e.doc_id and e.page))
    loaded: dict[tuple[str, int], str] = {}
    if want and conn is not None:
        try:
            for doc, page, text in conn.execute("SELECT doc_id, page, text FROM pages WHERE (doc_id, page) IN "
                                                "(SELECT unnest(%s::text[]), unnest(%s::int[]))",
                                                ([d for d, _ in want], [p for _, p in want])).fetchall():
                loaded[(doc, page)] = text or ""
        except Exception:                # noqa: BLE001 - the extracts then
            loaded = {}
    extracts = {(e.doc_id, e.page): e.text or "" for e in cited or []}
    titles = {(e.doc_id, e.page): e.title or "" for e in cited or []}
    return [(page, t, titles[(doc, page)]) for doc, page in want
            if (t := loaded.get((doc, page)) or extracts.get((doc, page), ""))]
