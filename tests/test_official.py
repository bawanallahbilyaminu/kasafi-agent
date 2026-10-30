"""Official sources in answers (app/hazards/official.py): advisories lead verbatim, expired ones are marked, NCDC
outbreak rows give their epi week and period, official outlooks are never replaced by a forecast."""

from datetime import date, datetime, timedelta, timezone

import pytest

from app.hazards import official
from app.hazards.read import Where

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
GORONYO = Where("lga", "NG034006", "Goronyo")


class Conn:
    """Answers the selects official.py makes, from lists given per table."""

    def __init__(self, advisories=(), outbreaks=None, checked=NOW - timedelta(hours=2), library=False):
        self.advisories, self.outbreaks, self.checked, self.library = list(advisories), outbreaks or {}, checked, library

    def execute(self, sql, args=()):
        if sql.startswith("SELECT max(started_at)"):
            rows = [(self.checked,)]
        elif "FROM advisories" in sql:
            rows = [r for r in self.advisories if r[8] in args[0]]
            rows = [r[:8] for r in rows]
        elif "FROM outbreak_cases" in sql:
            rows = [self.outbreaks[args[0]]] if args[0] in self.outbreaks else []
        elif "FROM documents" in sql:
            rows = [(1,)] if self.library else []
        else:
            rows = []
        return type("R", (), {"fetchall": lambda _: rows, "fetchone": lambda _: rows[0] if rows else None})()


def adv(days_ago, text, lgas=("NG034006",), kind="alert", hazard="flood", source="nema_alerts", until=None,
        state_wide=False):
    return (source, kind, NOW - timedelta(days=days_ago), until, text, f"https://nema.gov.ng/{days_ago}/",
            list(lgas), state_wide, hazard)


def test_current_rules() -> None:
    assert official.current("alert", NOW - timedelta(days=9), None, NOW)
    assert not official.current("alert", NOW - timedelta(days=11), None, NOW)
    assert not official.current("alert", NOW - timedelta(days=1), NOW - timedelta(hours=1), NOW)   # its end date
    assert official.current("outlook", datetime(2026, 4, 15, tzinfo=timezone.utc), None, NOW)
    assert not official.current("outlook", datetime(2025, 4, 15, tzinfo=timezone.utc), None, NOW)


def test_a_current_warning_leads_verbatim_with_its_issue_date() -> None:
    conn = Conn([adv(2, "Residents of Goronyo are advised to move away from the Rima flood plain."),
                 adv(1, "Flooding expected in Kebbe.", lgas=("NG034012",))])
    lines = official.official_lines(conn, "en", ["flood"], GORONYO, NOW)
    assert lines[0] == "⚠️ *Official warnings*"
    assert lines[1].startswith("NEMA, issued 28 Oct 2026: “Residents of Goronyo are advised to move away")
    assert not any("Kebbe" in x for x in lines)                    # another LGA's warning
    assert lines[-1] == "*Model forecasts (not official):*"


def test_an_expired_warning_is_marked_and_older_ones_dropped() -> None:
    conn = Conn([adv(30, "The Rima will overflow its banks at Goronyo."), adv(200, "An old alert.")])
    text = "\n".join(official.official_lines(conn, "en", ["flood"], GORONYO, NOW))
    assert "(*expired*): “The Rima will overflow" in text and "An old alert" not in text
    assert "No current official warning for Goronyo LGA" in text


def test_state_wide_warnings_reach_every_lga_and_unchecked_says_so() -> None:
    conn = Conn([adv(1, "Sokoto State residents should expect heavy rainfall.", lgas=(), state_wide=True,
                     hazard="rain")])
    assert "heavy rainfall" in "\n".join(official.official_lines(conn, "en", ["rain"], GORONYO, NOW))
    assert official.official_lines(Conn(checked=None), "ha", ["heat"], GORONYO, NOW) == \
        ["⚠️ *Gargaɗin hukuma*", "Ba a duba gargaɗin hukuma ba tukuna."]


@pytest.mark.parametrize("q, want", [
    ("Any meningitis in Sokoto now?", "outbreaks"),
    ("Akwai sankarau a Sokoto yanzu?", "outbreaks"),
    ("Is there a cholera outbreak in Sokoto?", "outbreaks"),
    ("What did NiMet predict for Sokoto's rainy season?", "outlook_climate"),
    ("What does the NIHSA flood outlook say for Sokoto?", "outlook_flood"),
    ("Is there a flood warning for Goronyo?", ""),                   # the flood layer, with official warnings first
    ("What is the measles vaccination coverage in Sokoto?", ""),     # a document question
    ("How much is budgeted for cholera response?", ""),              # a budget question
    ("Did NiMet issue a heat warning?", ""),
])
def test_route(q, want) -> None:
    assert official.route(q) == want


def test_route_by_the_planner_measure() -> None:
    assert official.route("Yaya lamarin yake?", ["outbreak_cases"]) == "outbreaks"
    assert official.route("Yaya lamarin yake?", ["seasonal_outlook"]) == "outlook_climate"


CSM = (2025, 14, date(2025, 4, 5), "from Epi week 40 2024, - week 13 2025", 450, 41, 47, True, 4, NOW)
LASSA_NOT = (2026, 40, date(2026, 10, 3), "week 40", None, None, None, False, None, NOW)


def test_an_outbreak_row_gives_its_epi_week_period_and_page() -> None:
    a = official.outbreak_answer(Conn(outbreaks={"csm": CSM}), "Any meningitis in Sokoto now?", "en",
                                 date(2026, 10, 30))
    assert a.found and "*Meningitis (CSM)*: NCDC report for epi week 14 2025 (05 Apr 2025): Sokoto 450 suspected, " \
                       "41 confirmed, 47 deaths (period in the report: “from Epi week 40 2024, - week 13 2025”)." in a.text
    assert "81 weeks old, so it doesn't show the situation now" in a.text
    assert "please see a health worker" in a.text and "page 4" in a.text
    assert "Lassa" not in a.text                                      # only the disease asked


def test_not_listed_and_never_read() -> None:
    a = official.outbreak_answer(Conn(outbreaks={"lassa": LASSA_NOT}), "Is there a disease outbreak in Sokoto?",
                                 "en", date(2026, 10, 30))
    assert "*Lassa fever*: Sokoto isn't listed in NCDC's report for epi week 40 2026 (03 Oct 2026)." in a.text
    assert "*Cholera*: no NCDC report read yet." in a.text and "weeks old" not in a.text.split("Lassa")[1][:200]


def test_only_official_guidance_is_quoted() -> None:
    notice = adv(3, "Report any case of stiff neck and fever to the nearest health facility.", lgas=(),
                 kind="notice", hazard="csm", source="sokoto_moh", state_wide=True)
    news = adv(2, "A columnist says everyone should take antibiotics.", lgas=(), kind="notice", hazard="csm",
               source="nema_alerts", state_wide=True)
    a = official.outbreak_answer(Conn([notice, news], outbreaks={"csm": CSM}), "any meningitis now?", "en",
                                 date(2026, 10, 30))
    assert "Official guidance, Sokoto State Ministry of Health, issued 27 Oct 2026: “Report any case" in a.text
    assert "antibiotics" not in a.text


def test_an_official_outlook_is_never_replaced_by_a_forecast() -> None:
    a = official.outlook_answer(Conn(), "climate", "en", Where("state"), NOW)
    assert not a.found and "isn't available to Kasafi yet" in a.text and "not NiMet's prediction" in a.text
    assert official.outlook_answer(Conn(library=True), "flood", "en", GORONYO, NOW) is None   # the document path
    afo = adv(198, "Goronyo: High flood risk.", kind="outlook", source="nihsa_afo")
    b = official.outlook_answer(Conn([afo]), "flood", "en", GORONYO, NOW)
    assert b.found and "NIHSA, issued 15 Apr 2026: “Goronyo: High flood risk.”" in b.text


def test_the_eval_checks_hold_on_the_code_built_answers() -> None:
    """evals/topics/advisories_checks.json against the answers built from the crawled rows (no planner, no model)."""
    import json
    from pathlib import Path
    from types import SimpleNamespace

    from evals.complex.run_open import wrong
    checks = json.loads((Path(__file__).parents[1] / "evals/topics/advisories_checks.json").read_text("utf-8"))["checks"]
    conn = Conn(outbreaks={"csm": CSM})
    for cid, q, lang in [("a02", "Any meningitis in Sokoto now?", "en"), ("a04", "Akwai sankarau a Sokoto yanzu?", "ha")]:
        text = official.outbreak_answer(conn, q, lang, date(2026, 10, 30)).text
        assert wrong(checks[cid], SimpleNamespace(text=text, exact=text)) == "", cid
    text = official.outlook_answer(conn, "climate", "en", Where("state"), NOW).text
    assert wrong(checks["a03"], SimpleNamespace(text=text, exact=text)) == ""
    for cid, lang in [("a01", "en"), ("a05", "ha")]:
        text = "\n".join(official.official_lines(conn, lang, ["flood"], GORONYO, NOW)) + "\nRima near Goronyo"
        assert wrong(checks[cid], SimpleNamespace(text=text, exact=text)) == "", cid
