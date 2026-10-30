"""Admin pages: the agent trace of each answer and the human review queue.

- /admin/traces            recent answers; ?flagged=1 shows only those a person should check
- /admin/traces/{id}       one answer step by step: plan, search, the two model readings side by side, what code
                           verified and kept, citations, timings and the reply
- /admin/review            the review queue: open gaps (questions Kasafi couldn't answer or documents it couldn't
                           find), domains awaiting approval (open-web results on sites outside the allowlist and
                           the trusted patterns) and flagged answers, each with a button to close it

HTTP basic auth with ADMIN_USER / ADMIN_PASSWORD; without both the pages don't exist (404). Traces and gaps hold
no phone number or user key. Every value shown is escaped (questions and document text are untrusted), and form
posts must come from this site (basic-auth credentials are sent cross-site too).
"""

from __future__ import annotations

import html
import json
import secrets
from urllib.parse import urlsplit

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import Settings, get_settings

router = APIRouter(prefix="/admin")
_basic = HTTPBasic(auto_error=False)

HEADERS = {"Cache-Control": "no-store", "X-Frame-Options": "DENY", "X-Robots-Tag": "noindex",
           "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'"}
OPEN_MODEL = "muse-spark-open"


def admin(creds: HTTPBasicCredentials | None = Depends(_basic), settings: Settings = Depends(get_settings)) -> None:
    if not (settings.admin_user and settings.admin_password):
        raise HTTPException(404)
    ok = creds is not None and secrets.compare_digest(creds.username.encode(), settings.admin_user.encode()) and \
        secrets.compare_digest(creds.password.encode(), settings.admin_password.get_secret_value().encode())
    if not ok:
        raise HTTPException(401, headers={"WWW-Authenticate": 'Basic realm="Kasafi admin"'})


def same_site(request: Request) -> None:
    origin = request.headers.get("origin") or request.headers.get("referer") or ""
    if urlsplit(origin).netloc != request.headers.get("host", ""):
        raise HTTPException(403, "cross-site form post")


def _conn(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(settings.db_url(), connect_timeout=5)


e = html.escape

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1b1d1f;--mute:#5d6369;--line:#e2e2de;--accent:#0b6e4f;--open:#7b3fb3;
--warn:#a15c00;--bad:#b42318;--ok:#0b6e4f;--chip:#efefeb}
@media (prefers-color-scheme:dark){:root{--bg:#121416;--card:#1b1e21;--ink:#e8e8e6;--mute:#a0a6ab;--line:#2c3135;
--accent:#3fbf8f;--open:#b98be0;--warn:#e0a24a;--bad:#f07167;--ok:#3fbf8f;--chip:#262a2e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,
"Segoe UI",sans-serif}main{max-width:1100px;margin:0 auto;padding:20px 16px 60px}
header.top{display:flex;gap:18px;align-items:baseline;flex-wrap:wrap;margin-bottom:18px}
header.top b{font-size:18px}nav a{color:var(--mute);margin-right:14px;text-decoration:none}nav a.on{color:var(--ink);
font-weight:600}a{color:var(--accent)}h1{font-size:20px;margin:0 0 6px}h2{font-size:15px;margin:0 0 10px;
text-transform:uppercase;letter-spacing:.04em;color:var(--mute)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);
vertical-align:top}th{font-size:12px;color:var(--mute);font-weight:600;text-transform:uppercase}
.chip{display:inline-block;padding:1px 8px;border-radius:999px;background:var(--chip);font-size:12px;margin:0 4px 4px 0}
.answered{color:var(--ok)}.partial,.unverified,.clarify{color:var(--warn)}.notfound,.wrong{color:var(--bad)}
.mute{color:var(--mute)}.small{font-size:13px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:760px){.grid{grid-template-columns:1fr}td.q{min-width:180px}}
.reader{border-top:4px solid var(--accent)}.reader.open{border-top-color:var(--open)}
ul.picks{margin:0;padding-left:18px}ul.picks li{margin:4px 0}.agree{color:var(--ok);font-weight:700}
.only{color:var(--warn);font-weight:700}pre{white-space:pre-wrap;word-break:break-word;margin:0;
font:13px/1.45 ui-monospace,Consolas,monospace}.steps{display:flex;gap:8px;flex-wrap:wrap}
.step{background:var(--chip);border-radius:8px;padding:6px 10px;font-size:13px}.step b{display:block;font-size:16px}
form.inline{display:inline}button{font:inherit;padding:5px 12px;border-radius:7px;border:1px solid var(--line);
background:var(--card);color:var(--ink);cursor:pointer}button.good{border-color:var(--ok);color:var(--ok)}
button.bad{border-color:var(--bad);color:var(--bad)}.scroll{overflow-x:auto}details summary{cursor:pointer}
"""


def page(title: str, body: str, on: str = "") -> HTMLResponse:
    nav = "".join(f'<a href="/admin/{p}" class="{"on" if p == on else ""}">{n}</a>'
                  for p, n in (("traces", "Traces"), ("traces?flagged=1", "Flagged"), ("review", "Review queue")))
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
           f'content="width=device-width,initial-scale=1"><title>{e(title)} · Kasafi admin</title>'
           f'<style>{CSS}</style></head><body><main><header class="top"><b>Kasafi admin</b><nav>{nav}</nav>'
           f'</header>{body}</main></body></html>')
    return HTMLResponse(doc, headers=HEADERS)


def _cls(outcome: str) -> str:
    return outcome.replace(" ", "")


def _model_label(model: str) -> str:
    if OPEN_MODEL in model:
        return "Muse Spark Open · Baseten" + (" (fell back)" if "fallback" in model else "")
    return "Muse Spark · Meta Model API" + (" (fallback for Open)" if "fallback" in model else "")


@router.get("", include_in_schema=False)
def home(_: None = Depends(admin)) -> RedirectResponse:
    return RedirectResponse("/admin/traces", 303)


@router.get("/traces", response_class=HTMLResponse)
def traces(flagged: int = 0, _: None = Depends(admin), settings: Settings = Depends(get_settings)) -> HTMLResponse:
    with _conn(settings) as conn:
        rows = conn.execute(
            "SELECT id, created_at, lang, question, outcome, path, seconds, trace->'flags', "
            "trace->'lines'->'readers', review FROM traces "
            "WHERE NOT %s OR jsonb_array_length(trace->'flags') > 0 ORDER BY id DESC LIMIT 200",
            (bool(flagged),)).fetchall()
    trs = "".join(
        f'<tr><td class="small mute">{c:%b %d %H:%M}</td><td class="q"><a href="/admin/traces/{i}">{e(q)}</a>'
        f'<div class="small mute">{e(lang)} · {e(p)}</div></td>'
        f'<td class="{_cls(o)}">{e(o)}</td><td>{s:.1f}s</td>'
        f'<td>{"".join(f"<span class=chip>{e(f)}</span>" for f in (fl or []))}'
        f'{"".join(f"<span class=chip>{e(_model_label(r).split(" ·")[0])}</span>" for r in (rd or []))}</td>'
        f'<td class="{e(rv)}">{e(rv)}</td></tr>'
        for i, c, lang, q, o, p, s, fl, rd, rv in rows)
    body = (f'<h1>{"Flagged answers" if flagged else "Agent traces"}</h1><p class="mute small">One record per '
            f'answered question: the English wording only, no phone number or user ID. Kept 30 days.</p>'
            f'<div class="card scroll"><table><tr><th>When</th><th>Question</th><th>Outcome</th><th>Time</th>'
            f'<th>Readings / flags</th><th>Review</th></tr>{trs or "<tr><td colspan=6>No traces yet.</td></tr>"}'
            f'</table></div>')
    return page("Traces", body, "traces?flagged=1" if flagged else "traces")


def _readings(lines: dict) -> str:
    uncertain = set(lines.get("uncertain") or [])

    def agreed(p: str) -> bool:
        name, _, rest = p.partition(" | ")
        return f"{name} ({rest.rsplit(': ', 1)[0]})" not in uncertain

    cards = []
    for n, (model, picks) in enumerate(zip(lines.get("readers") or [], lines.get("picks") or []), 1):
        items = "".join(f'<li><span class="{"agree" if agreed(p) else "only"}">{"✓" if agreed(p) else "?"}</span> '
                        f'{e(p)}</li>' for p in picks) or "<li class=mute>chose no rows</li>"
        cards.append(f'<div class="card reader {"open" if OPEN_MODEL in model else ""}"><h2>Reading {n} · '
                     f'{e(_model_label(model))}</h2><div class="small mute">{e(model)}</div>'
                     f'<ul class="picks">{items}</ul></div>')
    return f'<div class="grid">{"".join(cards)}</div>'


@router.get("/traces/{tid}", response_class=HTMLResponse)
def trace_page(tid: int, _: None = Depends(admin), settings: Settings = Depends(get_settings)) -> HTMLResponse:
    with _conn(settings) as conn:
        row = conn.execute("SELECT created_at, lang, question, outcome, path, seconds, trace, answer, review "
                           "FROM traces WHERE id = %s", (tid,)).fetchone()
    if not row:
        raise HTTPException(404)
    created, lang, question, out, path, seconds, t, answer, review = row
    plan, tm, lines = t.get("plan") or {}, t.get("timings") or {}, t.get("lines")
    steps = "".join(f'<div class="step">{e(k)}<b>{v:.1f}s</b></div>' for k, v in tm.items())
    terms = (plan.get("line_search") or {}).get("terms") or []
    plan_html = (f'<div class="small">Documents: {"".join(f"<span class=chip>{e(d)}</span>" for d in plan.get("doc_ids") or []) or "-"}</div>'
                 f'<div class="small">Line search terms: {"".join(f"<span class=chip>{e(x)}</span>" for x in terms) or "-"}</div>'
                 f'<div class="small">Page search: {e("; ".join(plan.get("search_queries") or [])) or "-"}</div>'
                 + (f'<div class="small">Assumption: {e(plan["assumption"])}</div>' if plan.get("assumption") else "")
                 + (f'<div class="small">Fetched: {e(json.dumps(t["acquired"]))}</div>' if t.get("acquired") else ""))
    verify = ""
    if lines:
        computed = "".join(f"<span class=chip>{e(k)} = {e(v)}</span>" for k, v in (lines.get("computed") or {}).items())
        kept = "".join(f"<li>{e(k)}</li>" for k in lines.get("kept") or []) or "<li class=mute>none</li>"
        unc = "".join(f"<li>{e(u)}</li>" for u in lines.get("uncertain") or [])
        verify = (f'<div class="card"><h2>3 · Code checks and keeps</h2><p class="small mute">Rows both readings chose '
                  f'are answered; every figure is matched against the printed row; totals and percentages are '
                  f'computed by code.</p><div class="small">Operation: <b>{e(lines.get("operation", ""))}</b> '
                  f'{computed}{" · <b class=wrong>readings disagreed: no total computed</b>" if lines.get("disputed") else ""}'
                  f'</div><ul class="picks">{kept}</ul>'
                  + (f'<div class="small mute" style="margin-top:8px">Only one reading chose (shown as possibly '
                     f'relevant, not counted):</div><ul class="picks">{unc}</ul>' if unc else "")
                  + (f'<div class="small">Missing: {e(lines["missing"])}</div>' if lines.get("missing") else "")
                  + "</div>")
        readings = f'<h2 style="margin-top:18px">2 · Two independent readings</h2>{_readings(lines)}'
    else:
        readings = (f'<div class="card"><h2>2 · Evidence</h2><div class="small">Path: {e(path)} (page search and '
                    f'the composer, or the budget-query tool)</div></div>')
    cited = "".join(f'<li>[{c["n"]}] {e(c["title"])}, page {c["page"]} <span class="mute small">({e(c["doc"])}, '
                    f'{e(c["source"])})</span></li>' for c in t.get("cited") or []) or "<li class=mute>none</li>"
    buttons = "".join(f'<form class="inline" method="post" action="/admin/traces/{tid}/review?review={v}">'
                      f'<button class="{c}">{n}</button></form> '
                      for v, n, c in (("ok", "Mark correct", "good"), ("wrong", "Mark wrong", "bad"),
                                      ("open", "Reopen", "")))
    body = (f'<p class="small mute"><a href="/admin/traces">← traces</a> · #{tid} · {created:%Y-%m-%d %H:%M} UTC · '
            f'{e(lang)}</p><h1>{e(question)}</h1>'
            f'<p><span class="{_cls(out)}"><b>{e(out)}</b></span> · {e(path)} · {seconds:.1f}s · review: '
            f'<b class="{e(review)}">{e(review)}</b> · '
            f'{"".join(f"<span class=chip>{e(f)}</span>" for f in t.get("flags") or [])}</p>'
            f'<div class="steps">{steps}</div>'
            f'<div class="card"><h2>1 · Plan (Muse Spark)</h2>{plan_html}</div>{readings}{verify}'
            f'<div class="card"><h2>4 · Citations</h2><ul class="picks">{cited}</ul></div>'
            f'<div class="card"><h2>5 · Reply sent</h2><pre>{e(answer)}</pre></div>'
            f'<div class="card">{buttons}</div>'
            f'<details class="card"><summary class="small">Raw trace JSON</summary><pre>'
            f'{e(json.dumps(t, ensure_ascii=False, indent=1))}</pre></details>')
    return page(f"Trace {tid}", body, "traces")


@router.post("/traces/{tid}/review")
def review_trace(tid: int, request: Request, review: str, _: None = Depends(admin),
                 settings: Settings = Depends(get_settings)) -> RedirectResponse:
    same_site(request)
    if review not in ("open", "ok", "wrong"):
        raise HTTPException(400)
    with _conn(settings) as conn:
        conn.execute("UPDATE traces SET review = %s WHERE id = %s", (review, tid))
    return RedirectResponse(f"/admin/traces/{tid}", 303)


@router.get("/review", response_class=HTMLResponse)
def review_queue(_: None = Depends(admin), settings: Settings = Depends(get_settings)) -> HTMLResponse:
    with _conn(settings) as conn:
        gaps = conn.execute("SELECT id, created_at, question, missing_doc, reason, detail FROM gaps "
                            "WHERE status = 'open' ORDER BY id DESC LIMIT 200").fetchall()
        flagged = conn.execute("SELECT id, created_at, question, outcome, trace->'flags' FROM traces "
                               "WHERE review = 'open' AND jsonb_array_length(trace->'flags') > 0 "
                               "ORDER BY id DESC LIMIT 200").fetchall()
        try:
            domains = conn.execute("SELECT domain, last_seen, hits, question, url, title FROM domain_reviews "
                                   "WHERE status = 'awaiting' ORDER BY last_seen DESC LIMIT 200").fetchall()
        except psycopg.errors.UndefinedTable:          # before migration 0010
            domains = []
    domain_rows = "".join(
        f'<tr><td><b>{e(d)}</b><div class="small mute">{hits}× · last {c:%b %d %H:%M}</div></td>'
        f'<td class="q">{e(q)}</td><td class="small">{e(t or "-")}<div class="mute">{e(u)}</div></td><td>'
        + "".join(f'<form class="inline" method="post" action="/admin/domains/{e(d)}?status={v}">'
                  f'<button class="{k}">{n}</button></form> '
                  for v, n, k in (("approved", "Approve", "good"), ("rejected", "Reject", "")))
        + "</td></tr>" for d, c, hits, q, u, t in domains)
    gap_rows = "".join(
        f'<tr><td class="small mute">{c:%b %d %H:%M}</td><td class="q">{e(q)}'
        f'<div class="small mute">{e(json.dumps(d, ensure_ascii=False)[:300]) if d else ""}</div></td>'
        f'<td>{e(r)}</td><td>{e(m or "-")}</td><td>'
        + "".join(f'<form class="inline" method="post" action="/admin/gaps/{i}?status={v}">'
                  f'<button class="{k}">{n}</button></form> '
                  for v, n, k in (("resolved", "Resolved", "good"), ("dismissed", "Dismiss", "")))
        + "</td></tr>" for i, c, q, m, r, d in gaps)
    trace_rows = "".join(
        f'<tr><td class="small mute">{c:%b %d %H:%M}</td><td class="q"><a href="/admin/traces/{i}">{e(q)}</a></td>'
        f'<td class="{_cls(o)}">{e(o)}</td><td>{"".join(f"<span class=chip>{e(f)}</span>" for f in fl or [])}</td></tr>'
        for i, c, q, o, fl in flagged)
    body = (f'<h1>Review queue</h1><p class="mute small">What a person should look at: questions Kasafi couldn\'t '
            f'answer or documents it couldn\'t find (kept 90 days), and answers that were partial, unverified, '
            f'disputed between the two readings, or where Muse Spark Open fell back.</p>'
            f'<div class="card scroll"><h2>Gaps ({len(gaps)} open)</h2><table><tr><th>When</th><th>Question</th>'
            f'<th>Reason</th><th>Missing document</th><th></th></tr>'
            f'{gap_rows or "<tr><td colspan=5>No open gaps.</td></tr>"}</table></div>'
            f'<div class="card scroll"><h2>Domains awaiting approval ({len(domains)})</h2><p class="mute small">'
            f'Open-web results on sites outside the allowlist and the trusted patterns (*.gov.ng, *.int, UN '
            f'domains, the World Bank): nothing was fetched from them. Approving makes the domain fetchable now; '
            f'add it to data/source_registry.yaml too so it survives a fresh database.</p><table><tr><th>Domain</th>'
            f'<th>Question that needed it</th><th>Document found</th><th></th></tr>'
            f'{domain_rows or "<tr><td colspan=4>Nothing awaiting.</td></tr>"}</table></div>'
            f'<div class="card scroll"><h2>Flagged answers ({len(flagged)} to check)</h2><table><tr><th>When</th>'
            f'<th>Question</th><th>Outcome</th><th>Why</th></tr>'
            f'{trace_rows or "<tr><td colspan=4>Nothing flagged.</td></tr>"}</table></div>')
    return page("Review queue", body, "review")


@router.post("/gaps/{gid}")
def close_gap(gid: int, request: Request, status: str, _: None = Depends(admin),
              settings: Settings = Depends(get_settings)) -> RedirectResponse:
    same_site(request)
    if status not in ("resolved", "dismissed"):
        raise HTTPException(400)
    with _conn(settings) as conn:
        conn.execute("UPDATE gaps SET status = %s WHERE id = %s", (status, gid))
    return RedirectResponse("/admin/review", 303)


@router.post("/domains/{domain}")
def review_domain(domain: str, request: Request, status: str, _: None = Depends(admin),
                  settings: Settings = Depends(get_settings)) -> RedirectResponse:
    """Approve (fetchable from now on) or reject a domain an open-web result was on."""
    same_site(request)
    if status not in ("approved", "rejected"):
        raise HTTPException(400)
    from app.acquisition.review import load_approved
    with _conn(settings) as conn:
        conn.execute("UPDATE domain_reviews SET status = %s WHERE domain = %s", (status, domain))
        load_approved(conn)
    return RedirectResponse("/admin/review", 303)
