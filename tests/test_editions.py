import asyncio
import io
import zipfile
from datetime import date
from pathlib import Path

import pytest

from app.acquisition import editions as ed
from app.acquisition.editions import SERIES, editions_back, find_latest, label, parse_nbs_catalog, release_date
from app.acquisition.library import Acquired
from app.acquisition.parse_worker import unzip_pdf

TODAY = date(2026, 10, 28)


@pytest.mark.parametrize("series, newest, older", [
    ("nbs_cpi", "2026-09", "2026-08"),            # mid-October release of September's CPI is out
    ("sokoto_bir", "2026-Q3", "2026-Q2"),         # Q3 ended Sep 30; ~3 weeks later
    ("sokoto_budget", "2026", "2025"),            # the 2027 budget isn't out until about January 2027
    ("sokoto_audited_fs", "2025", "2024"),        # audited statements come ~7 months after the year
])
def test_expected_newest_edition_from_today(series: str, newest: str, older: str) -> None:
    eds = editions_back(SERIES[series], TODAY, 6)
    assert eds[0] == newest and eds[1] == older and len(eds) == 6


def test_before_mid_month_the_previous_cpi_is_newest() -> None:
    assert editions_back(SERIES["nbs_cpi"], date(2026, 10, 10), 1) == ["2026-08"]
    assert editions_back(SERIES["nbs_cpi"], date(2026, 1, 20), 3) == ["2025-12", "2025-11", "2025-10"]


def test_labels_and_release() -> None:
    assert label("2026-09") == "September 2026" and label("2026-09", "ha") == "Satumba 2026"
    assert label("2026-Q3") == "Q3 2026" and label("2026") == "2026"
    assert release_date(SERIES["nbs_cpi"], "2026-09") == date(2026, 10, 15)


CATALOG_HTML = """
<span class="resource-info" title="Click" alt="View" id="1440">
  <i class="far fa-plus-square icon-expand" aria-hidden="true"></i>
  <i class="far fa-minus-square icon-collapsed" aria-hidden="true"></i>
  September 2026 CPI Report
</span>
<span class="resource-info" id="1441"><i class="x"></i> September 2026 CPI Tables </span>
<span class="resource-info" id="1254"><i class="x"></i> June 2025 CPI Report </span>
"""


def test_nbs_catalog_listing_maps_editions_to_downloads() -> None:
    got = parse_nbs_catalog(CATALOG_HTML, "https://microdata.nigerianstat.gov.ng/index.php/catalog/154/related-materials")
    assert got == {"2026-09": "https://microdata.nigerianstat.gov.ng/index.php/catalog/154/download/1440",
                   "2025-06": "https://microdata.nigerianstat.gov.ng/index.php/catalog/154/download/1254"}


# --- find_latest with a fake library --------------------------------------------------------------

def run_latest(monkeypatch, series: str, local: dict, *, listing=None, online: dict | None = None, newer_than=None):
    monkeypatch.setattr(ed, "local_edition", lambda conn, s, e: local.get((s, e)))
    monkeypatch.setattr(ed, "newest_local", lambda conn, s, before=None: max(
        ((d, e) for (ss, e), d in local.items() if ss == s and (before is None or e < before)),
        key=lambda x: x[1], default=None))

    async def fake_listing(series, http, robots):
        return listing
    monkeypatch.setattr(ed, "fetch_listing", fake_listing)
    calls = []

    async def find_fn(conn, description, **kw):
        calls.append(("search", kw["edition"]))
        doc = (online or {}).get(kw["edition"])
        return Acquired("indexed", doc, url="https://x") if doc else Acquired("not_found")

    async def fetch_fn(conn, url, description, **kw):
        calls.append(("listing", kw["edition"]))
        return Acquired("indexed", f"cpi-{kw['edition']}", url=url)

    notes = []

    async def notify(text):
        notes.append(text)

    async def go():
        return await find_latest(None, SERIES[series], TODAY, find_fn=find_fn, fetch_fn=fetch_fn, notify=notify,
                                 notify_text="checking", http=object(), newer_than=newer_than)
    return asyncio.run(go()), calls, notes


def test_older_local_edition_does_not_answer_latest_before_checking_newer(monkeypatch) -> None:
    listing = {"2026-09": "https://n/1440", "2025-06": "https://n/1254"}
    res, calls, notes = run_latest(monkeypatch, "nbs_cpi", {("nbs_cpi", "2025-06"): "cpi-2025-06"}, listing=listing)
    assert calls == [("listing", "2026-09")] and res.doc_id == "cpi-2026-09"
    assert res.status == "newest" and res.fetched and notes == ["checking"]


def test_newest_edition_already_in_library_needs_no_web(monkeypatch) -> None:
    res, calls, notes = run_latest(monkeypatch, "nbs_cpi", {("nbs_cpi", "2026-09"): "cpi-2026-09"})
    assert calls == [] and notes == [] and res.status == "newest"


def test_listing_skips_unpublished_editions(monkeypatch) -> None:
    res, calls, _ = run_latest(monkeypatch, "nbs_cpi", {}, listing={"2026-07": "https://n/1"})
    assert calls == [("listing", "2026-07")] and res.edition == "2026-07" and res.status == "older"
    assert res.tried == ["2026-09", "2026-08", "2026-07"]


def test_without_a_listing_it_searches_back_one_period_at_a_time(monkeypatch) -> None:
    res, calls, _ = run_latest(monkeypatch, "sokoto_bir", {("sokoto_bir", "2026-Q2"): "bir-2026-q2"})
    assert calls == [("search", "2026-Q3")]                     # Q3 2026 looked for first, then Q2 found locally
    assert res.doc_id == "bir-2026-q2" and res.status == "older" and res.expected == "2026-Q3"


def test_falls_back_to_an_older_local_edition_after_max_steps(monkeypatch) -> None:
    res, calls, _ = run_latest(monkeypatch, "nbs_cpi", {("nbs_cpi", "2025-06"): "cpi-2025-06"}, listing={})
    assert calls == [] and res.doc_id == "cpi-2025-06" and res.status == "older" and len(res.tried) == 6


def test_recheck_only_looks_at_newer_editions(monkeypatch) -> None:
    res, calls, _ = run_latest(monkeypatch, "nbs_cpi", {("nbs_cpi", "2025-06"): "cpi-2025-06"},
                               listing={"2026-09": "https://n/1440"}, newer_than="2026-08")
    assert calls == [("listing", "2026-09")] and res.status == "newer_found"
    res, _, _ = run_latest(monkeypatch, "nbs_cpi", {}, listing={}, newer_than="2026-09")
    assert res.status == "none_newer" and res.doc_id is None


# --- ZIP downloads (NBS ships CPI reports as zips) -------------------------------------------------

def make_zip(path: Path, files: dict[str, bytes]) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    path.write_bytes(buf.getvalue())


def test_unzip_takes_the_pdf(tmp_path: Path) -> None:
    z = tmp_path / "a.zip"
    make_zip(z, {"CPI_SEPTEMBER_2026.pdf": b"%PDF-1.7 report", "tables.xlsx": b"x" * 100})
    out = unzip_pdf(z, tmp_path / "out.pdf", 10_000)
    assert out["name"] == "CPI_SEPTEMBER_2026.pdf" and (tmp_path / "out.pdf").read_bytes().startswith(b"%PDF")


@pytest.mark.parametrize("files, why", [
    ({"tables.xlsx": b"x"}, "no PDF"),
    ({"bomb.pdf": b"%PDF" + b"0" * 50_000}, "too large"),
    ({"fake.pdf": b"MZ not a pdf"}, "not a PDF"),
    ({f"f{i}.pdf": b"%PDF" for i in range(60)}, "too many entries"),
])
def test_unzip_refuses_bad_archives(tmp_path: Path, files: dict, why: str) -> None:
    z = tmp_path / "a.zip"
    make_zip(z, files)
    assert why in unzip_pdf(z, tmp_path / "out.pdf", 10_000)["error"]
    assert not (tmp_path / "out.pdf").exists()
