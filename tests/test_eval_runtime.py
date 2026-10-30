"""Eval runs survive memory pressure: every case is on disk when it finishes, --resume runs only the rest (with the
cost so far), cases go one or two at a time, and the run reports its peak memory."""

import asyncio
import contextlib

import pytest

from app import usage
from evals import runtime
from evals.generated.run import pick_form


def test_a_killed_run_resumes_with_its_finished_cases_and_their_cost(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runtime, "CHECKPOINTS", tmp_path)
    usage.reset()
    c = runtime.Checkpoint("report_x", {"cases": "a.json", "seed": 1}, resume=False)
    usage.record_chat("Meta", {"prompt_tokens": 100, "completion_tokens": 10})
    c.add("lookup-01", {"why": "", "dt": 1.0})
    usage.record_chat("Meta", {"prompt_tokens": 100, "completion_tokens": 10})     # the case in flight when killed
    usage.reset()                                                                   # ... a new process
    again = runtime.Checkpoint("report_x", {"seed": 1}, resume=True)
    assert set(again.done) == {"lookup-01"} and again.header["cases"] == "a.json"
    assert usage.chat["Meta"].calls == 1 and usage.chat["Meta"].prompt == 100
    with pytest.raises(SystemExit):                                                 # another run's checkpoint
        runtime.Checkpoint("report_x", {"seed": 2}, resume=True)
    fresh = runtime.Checkpoint("report_x", {"seed": 1}, resume=False)               # no --resume: start over
    assert fresh.done == {}
    usage.reset()


def test_a_resumed_run_asks_each_case_in_the_same_form() -> None:
    case = {"id": "split-03", "forms": {"hausa": "?", "typo": "?", "followup": {}}}
    assert {pick_form(case, "all", 7) for _ in range(5)} == {pick_form(case, "all", 7)}
    assert pick_form(case, "template", 7) == "template"


def test_cases_run_at_most_two_at_a_time_each_with_its_own_connection(monkeypatch) -> None:
    conns, live, peak = [], [0], [0]

    @contextlib.contextmanager
    def connect(_url):
        conns.append(object())
        yield conns[-1]
    monkeypatch.setattr(runtime.psycopg, "connect", connect)

    async def fn(item, conn):
        live[0] += 1
        peak[0] = max(peak[0], live[0])
        await asyncio.sleep(0.01)
        live[0] -= 1

    asyncio.run(runtime.run_each(list(range(6)), fn, "db", concurrency=5))
    assert peak[0] == 2 and len(conns) == 2
    asyncio.run(runtime.run_each(list(range(3)), fn, "db"))
    assert len(conns) == 3


def test_the_run_reports_its_peak_memory() -> None:
    assert runtime.peak_mb() > 1
    assert runtime.memory_line(4).startswith("peak memory: ") and "4 cases were done before --resume" in \
        runtime.memory_line(4)
