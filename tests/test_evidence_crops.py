"""Evidence images: planning, SAM 3.1 protocol, and crops of the real pages."""

import asyncio
import io
import json
from pathlib import Path

import httpx
import pytest
from PIL import Image

from app.agent.answer import Answer, Evidence
from app.evidence import crops
from app.evidence.crops import CropRequest, make_crop, plan_crops
from app.providers.sam import Box, SamError, box_prompt, parse_boxes, segment
from app.users import UserStore
from tests.helpers import make_settings

DATA = Path(__file__).resolve().parents[1] / "data"
STORE = UserStore(":memory:")

E1 = Evidence(1, "budget-2025-approved", "Sokoto State Government 2025 Approved Budget", 2025, 11, "text",
              "[Table: Total Expenditure by Administrative Classification]\n017200000000 Ministry for Religious Affairs | "
              "2024 Revised Budget: 16,585,051,495.96 | 2025 Approved Budget: 11,255,447,389.16")
E2 = Evidence(2, "bir-2025-q4", "Budget Implementation Report Q4 2025", 2025, 17, "text",
              "017200000000 Ministry for Religious Affairs | 2025 Final Budget: 12,477,910,002.01 | "
              "2025 Performance Year to Date (Q1-Q4): 8,457,842,546.60 | % Performance: 67.8%")
E3 = Evidence(3, "bir-2025-q4", "Budget Implementation Report Q4 2025", 2025, 17, "text", "same page again 67.8%")


def answer(exact: str, cited: list[Evidence]) -> Answer:
    return Answer("text", True, True, cited, exact=exact)


def test_plan_takes_the_first_answer_figure_in_each_cited_page_best_first() -> None:
    a = answer("Allocated 11,255,447,389.16 [1]; spent 8,457,842,546.60 (67.8%) [2][3].", [E1, E2, E3])
    got = plan_crops(a, max_images=2)
    assert [(c.doc_id, c.page, c.figure, c.label) for c in got] == [
        ("budget-2025-approved", 11, "11,255,447,389.16", "2025 Approved Budget"),
        ("bir-2025-q4", 17, "8,457,842,546.60", "2025 Performance Year to Date (Q1-Q4)")]
    assert got[0].caption("ha") == ("2025 Approved Budget: 11,255,447,389.16\n"
                                    "[1] Sokoto State Government 2025 Approved Budget, shafi 11")


def test_plan_limits_and_skips_evidence_without_an_answer_figure() -> None:
    a = answer("Allocated 11,255,447,389.16 [1].", [E1, E2])
    assert [c.n for c in plan_crops(a, max_images=2)] == [1]           # nothing from E2 is in the answer
    assert plan_crops(answer("It is 2025 [1].", [E1]), 2) == []          # a year alone isn't evidence to show
    assert plan_crops("plain text, no answer object", 2) == []


def test_sam_prompt_and_output_parsing() -> None:
    assert box_prompt(10, 5, 20, 9, 100, 50) == "<0f>1<|box;x1=10;y1=5;x2=20;y2=9;w=100;h=50|>"
    assert box_prompt(-5, -1, 500, 80, 100, 50) == "<0f>1<|box;x1=0;y1=0;x2=99;y2=49;w=100;h=50|>"    # clamped
    out = "<0f>1<|box;x1=806;y1=754;x2=883;y2=765;w=1224;h=1584|><|mask;x=0;y=0;data=1,2,~ab|>,2<|box;x1=1;y1=2;x2=3;y2=4;w=9;h=9|><|mask;x|>"
    assert parse_boxes(out) == [Box(1, 806, 754, 883, 765), Box(2, 1, 2, 3, 4)]
    assert parse_boxes("") == []


def sam_stream(text: str, status: int = 200):
    events = [{"type": "response.created"}, {"type": "response.output_text.delta", "delta": text},
              {"type": "response.completed"}]
    body = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events)

    def handler(req: httpx.Request) -> httpx.Response:
        sent = json.loads(req.content)
        assert sent["model"] == "sam-3.1" and sent["stream"] is True
        content = sent["input"][0]["content"]
        assert content[0]["type"] == "input_text" and content[1]["image_url"].startswith("data:image/jpeg;base64,")
        return httpx.Response(status, text=body)
    return httpx.MockTransport(handler)


def test_segment_streams_boxes_and_treats_no_match_as_empty() -> None:
    s = make_settings()
    got = asyncio.run(segment(b"jpeg", "table", settings=s, transport=sam_stream("<0f>1<|box;x1=1;y1=2;x2=3;y2=4;w=9;h=9|>")))
    assert got == [Box(1, 1, 2, 3, 4)]
    assert asyncio.run(segment(b"jpeg", "table", settings=s, transport=sam_stream(""))) == []
    with pytest.raises(SamError, match="HTTP 401"):
        asyncio.run(segment(b"jpeg", "table", settings=s, transport=sam_stream("", 401)))


# --- the real pages (skipped without data/) -----------------------------------------------------

def real(name: str) -> None:
    if not (DATA / name).exists():
        pytest.skip(f"{name} not downloaded")


def run_crop(monkeypatch, req: CropRequest, sam_boxes=None, sam_error=None):
    crops._cache.clear()                     # each test renders afresh: no crop from an earlier test
    calls = []

    async def fake_segment(jpeg, prompt, *, settings, timeout):
        calls.append(prompt)
        if sam_error:
            raise sam_error
        return sam_boxes(prompt) if callable(sam_boxes) else (sam_boxes or [])
    monkeypatch.setattr(crops, "segment", fake_segment)
    monkeypatch.setattr(crops, "get_store", lambda: STORE)
    jpg = asyncio.run(make_crop(req, make_settings(kasafi_pdf_dir=str(DATA))))
    return (Image.open(io.BytesIO(jpg)) if jpg else None), calls


REQ = CropRequest(1, "budget-2025-approved", "Sokoto State Government 2025 Approved Budget", 11, "11,255,447,389.16")


def test_real_row_crop_is_one_row_high_with_context(monkeypatch) -> None:
    real("budget-2025-approved.pdf")

    def same_box(prompt):            # SAM returns the row it was given
        nums = dict(p.split("=") for p in prompt.split("<|box;")[1].rstrip("|>").split(";"))
        return [Box(1, int(nums["x1"]), int(nums["y1"]), int(nums["x2"]), int(nums["y2"]))]
    img, calls = run_crop(monkeypatch, REQ, same_box)
    assert calls and calls[0].startswith("<0f>1<|box;")              # SAM 3.1 got the row as a box prompt
    assert img.width > 1000 and 40 < img.height < 400                 # a row band, not the whole page


def test_real_row_crop_survives_a_failing_sam(monkeypatch) -> None:
    real("budget-2025-approved.pdf")
    img, _ = run_crop(monkeypatch, REQ, sam_error=SamError("HTTP 503"))
    assert img is not None and img.height < 400                       # our own row box is used


def test_figure_not_on_the_page_falls_back_to_the_table(monkeypatch) -> None:
    real("budget-2025-approved.pdf")
    req = CropRequest(1, "budget-2025-approved", "t", 11, "999,999,999.99")
    img, calls = run_crop(monkeypatch, req, [Box(1, 10, 10, 400, 300)])
    assert calls == ["table"] and img is not None
    img, _ = run_crop(monkeypatch, req, [])                           # no table found: no image
    assert img is None


def test_missing_pdf_gives_no_image(monkeypatch) -> None:
    img, calls = run_crop(monkeypatch, CropRequest(1, "no-such-doc", "No such document", 1, "1,000.00"))
    assert img is None and calls == []


def test_each_page_shows_the_figure_the_answer_cites_to_it() -> None:
    e1 = Evidence(1, "budget-2025-approved", "Budget", 2025, 12, "text", "Ministry of Health | 2025 Approved Budget: 52,179,252,082.91")
    e4 = Evidence(4, "bir-2025-q4", "BIR Q4", 2025, 19, "text",
                  "Ministry of Health | 2025 Original Budget: 52,179,252,082.91 | 2025 Final Budget: 41,869,252,082.91 | "
                  "2025 Performance Year to Date (Q1-Q4): 17,506,884,680.90")
    exact = ("Allocated 52,179,252,082.91 and spent 17,506,884,680.90 [1][4].\n"
             "2025 approved budget: 52,179,252,082.91 [1]\n2025 final budget: 41,869,252,082.91 [4]")
    got = plan_crops(answer(exact, [e1, e4]), 2)
    assert [(c.n, c.figure, c.label) for c in got] == [(1, "52,179,252,082.91", "2025 Approved Budget"),
                                                       (4, "41,869,252,082.91", "2025 Final Budget")]


def test_each_sam_call_is_counted_per_day_and_added_to_spend(monkeypatch) -> None:
    real("budget-2025-approved.pdf")
    before = STORE._exec("SELECT COALESCE(SUM(n), 0) FROM api_calls WHERE name = 'sam'").fetchone()[0]
    spent = STORE.spent_today()
    run_crop(monkeypatch, REQ, [Box(1, 10, 10, 20, 20)])
    assert STORE._exec("SELECT SUM(n) FROM api_calls WHERE name = 'sam'").fetchone()[0] == before + 1
    assert abs(STORE.spent_today() - spent - 0.0025) < 1e-9
    run_crop(monkeypatch, REQ, sam_error=SamError("HTTP 503"))          # a failed call isn't billed or counted
    assert STORE._exec("SELECT SUM(n) FROM api_calls WHERE name = 'sam'").fetchone()[0] == before + 1
