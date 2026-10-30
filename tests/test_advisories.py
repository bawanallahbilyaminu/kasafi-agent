"""Official advisories and NCDC outbreak figures (app/hazards/advisories.py), on the real pages that went wrong."""

import asyncio
import json

from app.config import Settings
from app.hazards.advisories import advisory_of, excerpt, lgas_in, ncdc_listing, read_sokoto
from app.providers.chat import ChatResult


def post(title: str, body: str, date: str = "2026-08-13T10:00:00", link: str = "https://nema.gov.ng/a/") -> dict:
    return {"title": {"rendered": title}, "content": {"rendered": f"<p>{body}</p>"}, "date_gmt": date, "link": link}


def test_an_lga_name_alone_is_not_sokoto() -> None:
    # nema.gov.ng, Aug 2025: a Jimeta (Adamawa) alert naming "Gwadabawa secondary school" there
    p = post("Urgent Flood Alert: Rising Water Level at Jimeta (Bakin Kogi)",
             "Current discharge rates exceed 3,222 m³/s, posing a heightened risk of overbank flooding. Displaced "
             "persons have already sought refuge at Limawa and Gwadabawa secondary schools.")
    assert advisory_of("nema_alerts", p) is None


def test_a_sokoto_flood_alert_is_kept_with_its_lgas_and_verbatim_text() -> None:
    p = post("NIHSA Issues Flood Alert for Sokoto-Rima Basin",
             "Residents of Goronyo and Wamakko in Sokoto State are advised to move away from flood plains as "
             "the Rima river rises. The Agency will continue to monitor river levels.")
    a = advisory_of("nema_alerts", p)
    assert a and a.kind == "alert" and a.hazard == "flood" and a.lgas == ["NG034006", "NG034021"]
    assert a.text.startswith("Residents of Goronyo and Wamakko in Sokoto State are advised")
    assert not a.state_wide and a.issued_at.year == 2026


def test_a_past_fire_outbreak_is_not_an_advisory() -> None:
    p = post("Sokoto Government Assures Support Following Fire Outbreak at Jarma Academy",
             "The Sokoto State Government's delegation visited the academy, which was gutted by a fire outbreak.",
             link="https://sokotostate.gov.ng/x/")
    assert advisory_of("sokoto_sema", p) is None


def test_office_holders_are_kept_out() -> None:
    assert advisory_of("sokoto_sema", post("Gov. Aliyu Warns on Flood in Sokoto", "Flooding in Sokoto ...")) is None
    body = "The Governor said flooding in Sokoto is under control. Flood waters in Kebbe LGA, Sokoto, are rising."
    assert excerpt(body, "flood") == "Flood waters in Kebbe LGA, Sokoto, are rising."


def test_a_disease_outbreak_notice_is_kept() -> None:
    p = post("Ministry Confirms Cholera Outbreak in Sokoto",
             "Cholera cases have been recorded in Sokoto North and Sokoto South LGAs.",
             link="https://moh.sk.gov.ng/cholera/")
    a = advisory_of("sokoto_moh", p)
    assert a and a.hazard == "cholera" and a.kind == "notice" and len(a.lgas) == 2


def test_lga_spellings() -> None:
    assert lgas_in("floods in Sabon Birni and Kware") == ["NG034011", "NG034013"]
    assert lgas_in("nothing here") == []


def test_ncdc_listing_rows() -> None:
    html = ('<table><tr><td>1</td><td>for Week 40</td><td>03 October 2026</td><td>'
            '<a href="/themes/common/files/sitreps/5787.pdf">Download</a></td></tr>'
            '<tr><td>2</td><td>for Week 39</td><td>26 September 2026</td><td>'
            '<a href="/themes/common/files/sitreps/4658.pdf">Download</a></td></tr></table>')
    assert ncdc_listing(html) == [(40, "03 October 2026", "https://ncdc.gov.ng/themes/common/files/sitreps/5787.pdf"),
                                  (39, "26 September 2026", "https://ncdc.gov.ng/themes/common/files/sitreps/4658.pdf")]


class Conn:
    def __init__(self, pages):
        self.pages = pages

    def execute(self, sql, args=()):
        rows = self.pages
        return type("R", (), {"fetchall": lambda _: rows})()


class Client:
    def __init__(self, reply: dict):
        self.reply, self.calls = json.dumps(reply), 0

    async def chat(self, messages, **kw):
        self.calls += 1
        return ChatResult(content=self.reply, model="m", finish_reason="stop")


SETTINGS = Settings(_env_file=None)
DIPHTHERIA = ("Epi-Week 3 2026 • Kano (24,687), Yobe (3,159), Bauchi(4,139), Plateau (137), Sokoto (146) & "
              "Kaduna (156) accounted for 99.1% of confirmed cases. • Sokoto (481) accounted for suspected cases.")


def test_sokoto_from_a_sentence_every_number_printed() -> None:
    reply = {"listed": True, "suspected": 481, "confirmed": 146, "deaths": None, "page": 1,
             "period": "Epi-Week 19 2022 - Epi-Week 3 2026"}
    row = asyncio.run(read_sokoto(Conn([(1, DIPHTHERIA)]), "d", Client(reply), SETTINGS))
    assert row and (row["suspected"], row["confirmed"], row["deaths"], row["listed"]) == (481, 146, None, True)


def test_a_number_not_on_the_page_drops_the_row() -> None:
    reply = {"listed": True, "suspected": 482, "confirmed": 146, "page": 1, "period": "x"}
    assert asyncio.run(read_sokoto(Conn([(1, DIPHTHERIA)]), "d", Client(reply), SETTINGS)) is None


def test_not_listed_only_when_every_page_has_text() -> None:
    conn = Conn([(1, "Lassa fever situation report. Ondo 2500 406")])
    client = Client({})
    assert asyncio.run(read_sokoto(conn, "d", client, SETTINGS, waiting=2)) is None       # tables still images
    row = asyncio.run(read_sokoto(conn, "d", client, SETTINGS, waiting=0))
    assert row and row["listed"] is False and client.calls == 0
    said_no = Client({"listed": False, "page": 1})
    assert asyncio.run(read_sokoto(Conn([(1, "Sokoto | |")]), "d", said_no, SETTINGS, waiting=1)) is None
