"""The code-side exclusion screen after the confirm step and the security deny list (audit F1). Free: no model."""

import pytest

from app.acquisition.exclusion import screen
from app.acquisition.policy import host_allowed, trusted


@pytest.mark.parametrize("title", ["Report on banditry attacks in Isa and Sabon Birni",
                                   "Military operations in the North-West, 2025",
                                   "APC campaign manifesto for Sokoto 2027"])
def test_a_title_naming_conflict_or_partisan_material_is_excluded_whatever_the_model_said(title) -> None:
    assert screen(title, ["Introduction"])[0] == "excluded"


def test_first_pages_full_of_conflict_terms_are_held_for_review() -> None:
    pages = ["Gunmen and bandits carried out attacks on villages. Troops launched a military operation; "
             "kidnapping and reprisal attacks followed. Bandits returned."]
    verdict, why = screen("Situation report, October 2025", pages)
    assert verdict == "review" and "bandit" in why


@pytest.mark.parametrize("title, pages", [
    ("Sokoto State 2026 Approved Budget", ["Community Guard Corps 1,200,000,000.00 Security Trust Fund "
                                           "500,000,000.00 Ministry of Security Affairs"]),
    ("DTM Nigeria North-West: displacement baseline, Sokoto", ["IDPs displaced by banditry and attacks on "
                                                              "villages; bandits; kidnapping; armed men"]),
    ("Multiple Indicator Cluster Survey 2021", ["Conflict in the North-East is one of the reasons..."]),
])
def test_budgets_security_lines_displacement_statistics_and_passing_mentions_are_not_excluded(title, pages) -> None:
    assert screen(title, pages)[0] == ""


@pytest.mark.parametrize("url", ["https://defence.gov.ng/report.pdf", "https://army.mil.ng/a.pdf",
                                 "https://www.npf.gov.ng/x.pdf", "https://nato.int/doc.pdf"])
def test_defence_and_security_publishers_are_never_fetched(url) -> None:
    assert not host_allowed(url) and not trusted(url)


def test_ordinary_government_and_un_hosts_stay_trusted() -> None:
    assert trusted("https://mof.sk.gov.ng/a.pdf") and trusted("https://iom.int/a.pdf")
