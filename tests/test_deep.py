"""Deep analysis for broad questions (app/agent/deep.py): detection, dimension planning, sources, claim checks, the
cost and time caps, neutral synthesis, the brief. Free: the model clients are stubs."""

import asyncio
import json
import re
import time

import pytest

from app.agent import deep as D
from app.providers.chat import ChatResult
from tests.helpers import make_settings


class StubModel:
    """Plans dimensions, reads pages (a claim per page: the first number the page prints, so the code check
    passes), and writes a synthesis citing the claims; counts calls."""
    provider = "Stub"
    default_model = "stub"

    def __init__(self, delay: float = 0.0, bad_figure: bool = False):
        self.calls, self.delay, self.bad_figure = [], delay, bad_figure

    async def chat(self, messages, **kw):
        system = messages[0]["content"]
        user = messages[-1]["content"]
        self.calls.append(system[:30])
        if self.delay:
            await asyncio.sleep(self.delay)
        if system.startswith("You plan an analysis"):
            body = {"subject": "primary health care", "dimensions": [
                {"name": "facilities and infrastructure", "queries": ["PHC facilities", "renovation"]},
                {"name": "staffing", "queries": ["health workers", "nurses midwives"]},
                {"name": "funding and spending", "queries": ["budget", "expenditure"], "money": True},
                {"name": "plans and targets", "queries": ["targets", "plan"]}]}
        elif system.startswith("You read pages"):
            claims = []
            for m in re.finditer(r"--- page (\d+) ---\n(.*?)(?=\n--- page |\Z)", user, re.S):
                num = re.search(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+(?:\.\d+)?%", m.group(2))
                if num:
                    claims.append({"dimension": "facilities and infrastructure", "statement": "A figure printed",
                                   "value": num.group(0), "unit": "", "year": "2024", "entity": "Sokoto",
                                   "page": int(m.group(1))})
            claims.append({"dimension": "staffing", "statement": "invented", "value": "987,654,321", "page": 1})
            body = {"claims": claims}
        else:
            first = re.search(r"\[C1\] .*?\| value (\S+)", user)
            v = first.group(1) if first else "0"
            extra = " The rate was 77.7% in 2025 [C1]." if self.bad_figure else ""
            body = {"summary": f"The library holds figures on primary health care. One reads {v} [C1].{extra} "
                               "Facilities are poor in some LGAs.",
                    "sections": [{"dimension": "facilities and infrastructure", "text": f"{v} [C1]."}],
                    "differ": "Sources cover different years.", "missing": "No staffing figures by LGA."}
        return ChatResult(json.dumps(body), "stub", "stop")

    async def aclose(self):
        return None


# --- detection and planning -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("q, deep", [
    ("Whats the state of PHCs in sokoto state", True), ("Give me an overview of primary health care", True),
    ("How is basic education doing in Sokoto?", True), ("Yaya yanayin cibiyoyin kiwon lafiya a Sokoto?", True),
    ("Ina son bayani dalla-dalla kan ilimi", True), ("How many PHCs are in Sokoto State?", False),
    ("What is the 2026 health budget?", False),
])
def test_broad_questions_are_detected(q, deep) -> None:
    assert D.deep_question(q) is deep


def test_dimensions_come_from_the_model_or_the_fixed_list() -> None:
    subject, dims = asyncio.run(D.plan_dimensions(StubModel(), "state of PHCs", "What is the state of PHCs?"))
    assert subject == "primary health care" and [d.name for d in dims][:2] == ["facilities and infrastructure",
                                                                                "staffing"]
    assert next(d for d in dims if d.name == "funding and spending").money

    class Broken(StubModel):
        async def chat(self, messages, **kw):
            raise RuntimeError("down")
    _, dims = asyncio.run(D.plan_dimensions(Broken(), "q", "q"))
    assert len(dims) == len(D.DEFAULT_DIMENSIONS)


# --- claims, caps, synthesis --------------------------------------------------------------------------------------

def test_a_claim_counts_only_when_its_value_is_printed_on_its_page() -> None:
    pages = {7: "Total cost N15,900,000,000.", 13: "Coverage 61%."}
    assert D.verify_claim({"value": "N15,900,000,000", "page": 7}, pages)
    assert D.verify_claim({"value": "₦15.9 billion", "page": 7}, pages)
    assert not D.verify_claim({"value": "61%", "page": 7}, pages)
    assert not D.verify_claim({"value": "987,654,321", "page": 13}, pages) and not D.verify_claim({"value": "x"}, pages)


def readings(n):
    return [D.Reading(f"doc{i}", f"Doc {i}", 2024, [(1, f"Page {i} prints 1,234 facilities.")], ["staffing"])
            for i in range(n)]


def test_reading_stops_at_the_cost_cap() -> None:
    spend = {"usd": 0.0}
    model = StubModel()
    orig = model.chat

    async def costly(messages, **kw):
        spend["usd"] += 0.05
        return await orig(messages, **kw)
    model.chat = costly
    dims = [D.Dimension("staffing", ["x"])]
    claims, stopped = asyncio.run(D.read_all(model, readings(12), "PHC", dims, make_settings(), cost_cap=0.20,
                                             spent=lambda: spend["usd"]))
    assert "cost cap" in stopped and 4 <= len(model.calls) <= 4 + D.CONCURRENT
    assert all(c.value == "1,234" for c in claims)                        # the invented figure never passes


def test_reading_stops_at_the_deadline() -> None:
    dims = [D.Dimension("staffing", ["x"])]
    t0 = time.perf_counter()
    claims, stopped = asyncio.run(D.read_all(StubModel(delay=2.0), readings(3), "PHC", dims, make_settings(),
                                             deadline_s=0.3, spent=lambda: 0.0))
    assert time.perf_counter() - t0 < 1.5 and claims == [] and "time" in stopped


def test_the_synthesis_keeps_only_verified_figures_and_no_verdict_words() -> None:
    claims = [D.Claim("facilities and infrastructure", "PHCs in the registry", "1,234", "", "2024", "Sokoto",
                      "doc0", "Doc 0", 1)]
    text = D.keep_verified("There are 1,234 PHCs [C1]. The rate was 77.7% in 2025 [C1]. Facilities are poor.", claims)
    assert "1,234" in text and "77.7" not in text and "poor" not in text
    assert D.cite("There are 1,234 PHCs [C1].", claims) == "There are 1,234 PHCs (Doc 0, p. 1)."


def test_render_gives_a_summary_then_a_message_per_dimension_and_the_brief_offer() -> None:
    r = D.DeepResult("Summary.", [("facilities", "1,234 PHCs."), ("staffing", "500 nurses.")], "Different years.",
                     "No LGA data.", [], ["doc0"], 0.05, 40.0)
    summary, parts = D.render(r, "en")
    assert summary == "Summary." and parts[0].startswith("*facilities*") and parts[1].startswith("*staffing*")
    assert "Where sources differ" in parts[2] and "full brief" in parts[2]


def test_the_full_brief_is_a_pdf_with_every_claim() -> None:
    claims = [D.Claim("staffing", "Nurses in PHCs", "500", "", "2024", "Sokoto", "doc0", "Doc 0", 3)]
    pdf = D.brief_pdf("State of PHCs?", D.DeepResult("Summary.", [("staffing", "500 nurses.")], "", "", claims,
                                                      ["doc0"], 0.0, 1.0))
    assert pdf[:4] == b"%PDF" and len(pdf) > 1000


# --- the whole analysis on the dev library (stubbed models) ----------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM doc_cards LIMIT 1")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database: {e}")
    yield c
    c.close()


def test_a_deep_analysis_reads_across_the_library_within_its_limits(conn) -> None:
    notes = []

    async def notify(text):
        notes.append(text)
    r = asyncio.run(D.deep_answer(conn, "Whats the state of PHCs in sokoto state",
                                  "What is the state of primary health care centres in Sokoto State?", "en",
                                  client=StubModel(bad_figure=True), open_client=StubModel(), settings=make_settings(),
                                  notify=notify))
    assert 3 <= len(r.documents) <= D.MAX_DOCS + 1 and r.claims
    assert "registry:facilities" in r.documents                           # the registry counts for facilities
    assert all(c.value != "987,654,321" for c in r.claims)                # invented figures never pass the check
    assert "77.7" not in r.summary and "poor" not in r.summary            # unverified figure and verdict word gone
    assert notes[0].startswith("🧭") and notes[1].startswith("📚 Reading") and notes[2].startswith("✍️")


def test_citations_are_given_once_per_message_without_a_page_for_the_registry_and_amounts_in_house_style() -> None:
    claims = [D.Claim("f", "s", "15,000,000.00", "", "2025", "", "budget-2025", "Sokoto State Government 2025 Approved "
                      "Budget", 45),
              D.Claim("f", "s", "934", "", "2024", "", "registry:facilities", "Health facility registry (NHFR / GRID3)",
                      0),
              D.Claim("f", "s", "1", "", "", "", "rop", "State Health Resource Optimization Plan (ROP) to Improve "
                      "Healthcare Services in Sokoto", 9)]
    text = D.cite("15,000,000.00 NGN for renovation [C1]. 150,000,000.00 NGN for solar [C1]. 934 facilities [C2]. "
                  "Readiness [C3].", claims)
    assert text.count("(Sokoto State Government 2025 Approved Budget, p. 45)") == 1
    assert "(Health facility registry (NHFR / GRID3))" in text and "p. 0" not in text
    assert "₦15.00 million" in text and "NGN" not in text
    assert "Improve Healthcare…" in text or "Improve…" in text and "Hea," not in text
