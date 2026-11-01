"""Charts on text pages (2 Nov 2026): detection in code, honest reading, storage, search, crops, and exact names.
Free: fixture PDFs drawn in code with matplotlib; the vision model is a fake that returns what a model would."""

import asyncio
import json
from pathlib import Path

import pytest

from app.agent.answer import Evidence, acronym_problems, unverified_numbers
from app.retrieval import chart_read as R
from app.retrieval.charts import detect_document


def make_pdf(path: Path, kind: str) -> Path:
    """One A4 page of running text with a chart (or a table) and its caption below it."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.08, 0.95, "Situation analysis. This page reviews the causes of maternal deaths in the state and the "
                         "\nresponse of primary health care facilities, as reported in the routine data.", fontsize=9)
    ax = fig.add_axes([0.12, 0.50, 0.76, 0.38])
    causes = ["Haemorrhage", "Eclampsia", "Sepsis", "Obstructed labour", "Anaemia", "Other causes"]
    shares = [34, 21, 12, 9, 7, 17]
    if kind in ("labelled", "unlabelled"):
        bars = ax.bar(causes, shares, color="#3a6ea5")
        if kind == "labelled":
            ax.bar_label(bars, labels=[f"{v}%" for v in shares])
        ax.set_ylabel("Percent of maternal deaths")
        caption = "Figure 3: Causes of maternal deaths, April-June 2022"
    elif kind == "pie":
        ax.pie(shares, labels=causes, autopct="%1.0f%%")
        caption = "Figure 4: Share of maternal deaths by cause"
    else:                                       # a table drawn with ruled cells: not a chart
        ax.axis("off")
        tab = ax.table(cellText=[[c, f"{v}%"] for c, v in zip(causes, shares)], colLabels=["Cause", "Share"],
                       loc="center", cellColours=[["#dddddd", "#ffffff"]] * 6)
        tab.scale(1, 2)
        caption = "Table 2: Causes of maternal deaths"
    fig.text(0.12, 0.45, caption, fontsize=11, weight="bold")
    fig.text(0.08, 0.30, "The chart above shows the leading causes recorded by the facilities in the quarter.", fontsize=9)
    fig.savefig(path, format="pdf")
    plt.close(fig)
    return path


# --- 1. detection (no model) -------------------------------------------------------------------------------------

def test_a_labelled_bar_chart_and_a_pie_are_found_with_their_captions(tmp_path) -> None:
    bar = detect_document(make_pdf(tmp_path / "bar.pdf", "labelled"))
    assert len(bar) == 1 and bar[0].label == "Figure 3" and bar[0].caption.startswith("Figure 3: Causes of maternal")
    pie = detect_document(make_pdf(tmp_path / "pie.pdf", "pie"))
    assert len(pie) == 1 and pie[0].label == "Figure 4"


def test_a_ruled_table_is_not_a_chart_and_pages_without_text_are_left_to_ocr(tmp_path) -> None:
    assert detect_document(make_pdf(tmp_path / "table.pdf", "table")) == []
    # a page without a text layer goes to page OCR, as before: the detector isn't run on it
    assert detect_document(make_pdf(tmp_path / "bar.pdf", "labelled"), text_pages=set()) == []


# --- 2. reading: printed values are figures, estimated ones never are -----------------------------------------------

class FakeVision:
    """Replies as a vision model would for the fixture charts; counts calls (one pass per chart, then cached)."""
    provider = "Fake"
    default_model = "fake-vision"

    def __init__(self, labelled: bool):
        self.labelled, self.calls = labelled, 0

    async def chat(self, messages, **kw):
        from app.providers.chat import ChatResult
        self.calls += 1
        assert any(p.get("type") == "image_url" for p in messages[0]["content"])        # the crop goes as an image
        values = [{"category": c, "series": "", "value": f"{v}%" if self.labelled else str(v + 1),
                   "printed": self.labelled}
                  for c, v in zip(["Haemorrhage", "Eclampsia", "Sepsis", "Obstructed labour", "Anaemia",
                                   "Other causes"], [34, 21, 12, 9, 7, 17])]
        return ChatResult(json.dumps({"is_chart": True, "title": "Causes of maternal deaths", "chart_type": "bar",
                                      "units": "percent", "values": values}), "fake", "stop")

    async def aclose(self):
        return None


def test_printed_values_become_searchable_figures_and_estimated_ones_only_an_order() -> None:
    labelled = asyncio.run(R.read_chart(FakeVision(True), b"jpeg"))
    text = R.chart_text("Figure 3", 16, labelled)
    assert labelled.value_source == "label" and "Haemorrhage: 34% (read from a chart label)" in text
    assert text.startswith("[Chart: Figure 3 (page 16)")
    shape = asyncio.run(R.read_chart(FakeVision(False), b"jpeg"))
    text = R.chart_text("Figure 3", 16, shape)
    assert shape.value_source == "estimated" and "estimated from the chart's shape" in text
    assert not any(ch.isdigit() for ch in text.split("\n", 2)[-1])        # no number from a bar height, ever
    assert text.index("Haemorrhage") < text.index("Eclampsia")             # only the order


def test_the_verifier_takes_chart_labels_like_table_values_and_never_an_estimate() -> None:
    text = R.chart_text("Figure 3", 16, asyncio.run(R.read_chart(FakeVision(True), b"jpeg")))
    ev = [Evidence(1, "plan", "Health Plan", 2023, 16, "text", text)]
    assert unverified_numbers("Haemorrhage caused 34% of maternal deaths, read from Figure 3 on page 16 [1].", ev) == []
    est = R.chart_text("Figure 3", 16, asyncio.run(R.read_chart(FakeVision(False), b"jpeg")))
    ev = [Evidence(1, "plan", "Health Plan", 2023, 16, "text", est)]
    assert unverified_numbers("Haemorrhage caused about 35% of maternal deaths [1].", ev) == ["35"]


def test_labels_are_snapped_to_the_printed_text_and_the_title_is_the_caption() -> None:
    d = R.ChartData(True, "Figure 7", "bar", values=[{"category": "PLATEEAU", "series": "", "value": "79.5",
                                                       "printed": True}])
    d = R.snap_labels(d, "BAUCHI KEBBI PLATEAU NIGER", "Figure 7: Employment to Population Ratio by State (%)")
    assert d.values[0]["category"] == "PLATEAU" and d.title.startswith("Figure 7: Employment")


def test_not_a_chart_reads_as_nothing() -> None:
    assert R.parse_chart({"is_chart": False}).values == [] and not R.parse_chart({}).is_chart


# --- 3. stored, searchable, cropped (dev database; rolled back) -----------------------------------------------------

DOC = "zz-fixture-chart-plan"


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM charts LIMIT 0")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database with charts (migration 0027): {e}")
    c.execute("INSERT INTO documents (id, title, category, year, publisher, acquisition, sha256, page_count) VALUES "
              "(%s, 'State Health Improvement Plan', 'sector_plan', 2023, 'Fixture Ministry of Health', 'local', "
              "'f', 16)", (DOC,))
    body = "Situation analysis. Figure 3: Causes of maternal deaths, April-June 2022."
    c.execute("INSERT INTO pages (doc_id, page, text, source) VALUES (%s, 16, %s, 'text')", (DOC, body))
    c.execute("INSERT INTO chunks (doc_id, page, idx, text) VALUES (%s, 16, 0, %s)", (DOC, body))
    yield c
    c.rollback()
    c.close()


def test_a_labelled_chart_is_stored_searchable_and_its_crop_is_the_evidence(conn) -> None:
    from app.agent.answer import Plan, gather_evidence
    from app.agent.need import Need
    from app.retrieval.chart_build import chart_crop, store_chart
    d = asyncio.run(R.read_chart(FakeVision(True), b"jpeg"))
    region = {"page": 16, "box": [80.0, 300.0, 520.0, 700.0], "kind": "vector", "label": "Figure 3",
              "caption": "Figure 3: Causes of maternal deaths, April-June 2022"}
    text = store_chart(conn, DOC, region, R.snap_labels(d, "", region["caption"]), b"\xff\xd8chart", "fake-vision")
    assert "(read from a chart label)" in text
    page = conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = 16", (DOC,)).fetchone()[0]
    assert "Haemorrhage: 34% (read from a chart label)" in page
    q = "What are the main causes of maternal deaths in the state health improvement plan?"
    ev = gather_evidence(conn, Plan(english_question=q, search_queries=["causes of maternal deaths haemorrhage"],
                                    doc_ids=[DOC], need=Need(q)))
    hit = next(e for e in ev if e.doc_id == DOC)
    assert hit.page == 16 and "Haemorrhage: 34% (read from a chart label)" in hit.text
    assert chart_crop(conn, DOC, 16, "34%") == b"\xff\xd8chart" and chart_crop(conn, DOC, 16, "35%") is None
    # read once: the same region again is skipped by the builder's cache key
    assert conn.execute("SELECT count(*) FROM charts WHERE doc_id = %s AND page = 16", (DOC,)).fetchone()[0] == 1


def test_an_unlabelled_chart_stores_no_figure(conn) -> None:
    from app.retrieval.chart_build import chart_crop, store_chart
    d = asyncio.run(R.read_chart(FakeVision(False), b"jpeg"))
    region = {"page": 16, "box": [80.0, 50.0, 520.0, 290.0], "kind": "vector", "label": "Figure 4", "caption": ""}
    text = store_chart(conn, DOC, region, d, b"\xff\xd8other", "fake-vision")
    assert "estimated from the chart's shape" in text and "35" not in text
    assert chart_crop(conn, DOC, 16, "35") is None


# --- 4. names and acronyms exactly as printed -----------------------------------------------------------------------

def test_every_acronym_in_an_answer_is_printed_in_its_cited_pages() -> None:
    ev = [Evidence(1, "plan", "Health Plan", 2023, 24, "text",
                   "from NGN1.29 billion (combined for NPHCDA, SOCHEMA, and SOSMEA) to NGN4 billion in 2023")]
    assert acronym_problems("₦1.29 billion for NPHCDA, SOCHEMA and SOSMEA in the 2022 budget [1].", ev) == []
    assert acronym_problems("₦1.29 billion for SPHCDA, SOCHEMA and SOSMEA [1].", ev) == ["SPHCDA"]
    assert acronym_problems("Each LGA reports in Q2; NGN figures [1].", ev) == []


# --- 5. routing and the primary-source note (2 Nov 2026) ------------------------------------------------------------

@pytest.mark.parametrize("q, other", [
    ("How many medical officers do Sokoto's primary health facilities need, and how many are there?", True),
    ("Likitoci nawa ne a asibitocin Sokoto?", True), ("Ma'aikatan lafiya nawa ake bukata a cibiyoyin lafiya?", True),
    ("How many health facilities have a functional ambulance?", True),
    ("How many primary health centres are there in Wamakko?", False), ("Asibitoci nawa ne a Kebbe?", False),
])
def test_staff_equipment_and_services_at_facilities_are_not_facility_counts(q, other) -> None:
    from app.agent.routing import other_subject
    assert other_subject(q) is other


def test_a_plan_is_the_primary_source_for_its_own_targets(conn) -> None:
    from app.agent.answer import own_commitments
    ev = [Evidence(1, "health-aop-2025", "2025 Health AOP", 2025, 40, "text", "Renovation of 50 PHCs")]
    assert own_commitments(conn, "How many PHCs does the 2025 health plan target for renovation?", ev)
    assert not own_commitments(conn, "What is the maternal mortality ratio in Sokoto?", ev)      # a statistic
    ev2 = [Evidence(1, "ndhs-2024", "NDHS 2024", 2024, 40, "text", "x")]
    assert not own_commitments(conn, "How many PHCs does the plan target for renovation?", ev2)
