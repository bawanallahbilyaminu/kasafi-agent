"""Publishers' own document listings: parsed from their pages, matched to a query, dates read."""

import pytest

from app.acquisition import channels as ch
from app.config import get_settings

NBS_ROW = """<tbody id="tabledata"><tr>
<!-- <td><div class="avatar"><img src="x.png"></div></td> -->
<td>Nigeria Labour Force Survey Annual Report 2023</td>
<td style="display:none">Social Statistics</td><td style="display:none">Labour</td>
<td style="display:none">Labour Force</td><td style="display:none">nlfs,unemployment,underemployment,neet</td>
<td>Tue Sep 24 2024</td><td><i class="glyphicon"></i> 11567</td>
<td> <a class="btn" href="https://nigerianstat.gov.ng/elibrary/read/1241561"><i></i></a></td></tr></tbody>"""

UNHCR_PAGE = """<a class='searchResultItem_download_link' href='https://data.unhcr.org/en/documents/download/124425'
 data-title="UNHCR Nigeria Forcibly Displaced Populations Dashboard - 1 October 2026" title="Download">Download</a>
 View 1.1 MB Download Count: 20 Displacement Overview Publish date: <b>1 October 2026</b> &#40;28 days ago&#41;"""


def test_the_nbs_library_table_gives_download_links_without_pdf() -> None:
    [e] = ch.parse_nbs_library(NBS_ROW)
    assert e.title == "Nigeria Labour Force Survey Annual Report 2023"
    assert e.url == "https://nigerianstat.gov.ng/download/1241561" and e.date == "2024-09-24" and "neet" in e.text


def test_the_unhcr_country_page_gives_each_dashboard_and_its_date() -> None:
    [e] = ch.parse_unhcr_country(UNHCR_PAGE)
    assert e.url.endswith("/documents/download/124425") and e.date == "2026-10-01"


def test_listed_documents_are_matched_by_words_newest_first_on_ties() -> None:
    entries = [ch.Entry("Nigeria Labour Force Survey Q2 2024", "u1", "2024-11-25", "labour nlfs"),
               ch.Entry("Nigeria Labour Force Survey Annual Report 2023", "u2", "2024-09-24", "labour nlfs neet"),
               ch.Entry("PSWG Nigeria Annual Report 2016", "u3", "2017-05-05")]
    got = [e.url for e in ch.best_entries(entries, "NLFS labour force annual report")]
    assert got[0] == "u2" and "u3" not in got                 # one shared word ("annual") isn't a match


def test_dates_in_the_listings_formats() -> None:
    assert ch.iso_date("Tue Sep 24 2024") == "2024-09-24" and ch.iso_date("1 October 2026") == "2026-10-01"
    assert ch.iso_date("2026-09-25T15:21:01.917Z") == "2026-09-25" and ch.iso_date("soon") == ""


def test_the_state_statistics_bureau_is_a_crawled_library() -> None:
    from app.acquisition.crawl import crawled_sites
    assert crawled_sites() == ["sbs.sk.gov.ng"] and "sbs.sk.gov.ng" in ch.LISTINGS


RW_REPLY = {"data": [
    {"fields": {"title": "Nigeria: North-West Flash Update (Sokoto)", "date": {"original": "2026-10-20T00:00:00+00:00"},
                "source": [{"shortname": "OCHA"}],
                "file": [{"url": "https://reliefweb.int/attachments/1/nw-flash.pdf"}]}},
    {"fields": {"title": "UNICEF Nigeria Humanitarian Situation Report", "date": {"original": "2026-09-30"},
                "source": [{"shortname": "UNICEF"}], "file": [{"url": "https://reliefweb.int/attachments/2/x.docx"}]}},
]}


def test_reliefweb_asks_for_nigeria_and_sokoto_newest_first_and_keeps_pdfs() -> None:
    params = dict(ch.reliefweb_params("APP", ""))
    assert params["query[value]"] == "Sokoto" and params["filter[field]"] == "country.name"
    assert params["filter[value]"] == "Nigeria" and params["sort[]"] == "date.created:desc"
    [c] = ch.parse_reliefweb(RW_REPLY)
    assert c.url.endswith("nw-flash.pdf") and c.date == "2026-10-20" and c.source == "reliefweb"
    assert ch.from_publisher(c, "UN OCHA Nigeria (North-West Operational Response Plan)")
    assert not ch.from_publisher(c, "UNICEF Nigeria Humanitarian Situation Reports")


def test_the_registry_never_holds_the_reliefweb_appname() -> None:
    from app.acquisition.registry import registry
    auth = registry().channels["reliefweb_api"].auth
    app = get_settings().reliefweb_appname
    assert "RELIEFWEB_APPNAME" in auth and (not app or app not in auth)


@pytest.mark.skipif(not get_settings().reliefweb_appname, reason="RELIEFWEB_APPNAME not set")
def test_live_reliefweb_lists_sokoto_reports() -> None:
    import asyncio

    import httpx

    async def go():
        ch._rw_cache.clear()
        async with httpx.AsyncClient() as http:
            return await ch.reliefweb_reports(http, get_settings().reliefweb_appname, "", rows=20)
    got = asyncio.run(go())
    assert got and all(c.url.startswith("https://") for c in got)
    assert max(c.date for c in got) >= "2026"            # newest posted first: this year's reports come back
