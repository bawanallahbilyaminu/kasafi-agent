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


def test_runs_stop_when_the_days_eval_budget_is_spent(tmp_path, monkeypatch) -> None:
    from tests.helpers import make_settings
    monkeypatch.setattr(runtime, "CHECKPOINTS", tmp_path)

    @contextlib.contextmanager
    def connect(_url):
        yield object()
    monkeypatch.setattr(runtime.psycopg, "connect", connect)
    usage.reset()
    ran = []

    async def fn(item, conn):                       # each case costs $1.25 (1M prompt tokens on Meta)
        ran.append(item)
        usage.record_chat("Meta", {"prompt_tokens": 1_000_000, "completion_tokens": 0})
    s = make_settings(eval_daily_usd=3.0)
    assert asyncio.run(runtime.run_each(list(range(5)), fn, "db", settings=s)) is False
    assert ran == [0, 1, 2]                         # $3.75 >= $3: stopped before the fourth
    assert runtime.DailyBudget(s).over()            # a later run today stops at once
    usage.reset()


def test_about_50_fresh_cases_in_development_155_before_a_deploy() -> None:
    from evals.generated.run import per_family
    assert (per_family(50), per_family(155)) == (6, 19)


def test_each_case_prints_and_logs_a_progress_line(tmp_path, monkeypatch, capsys) -> None:
    from tests.helpers import make_settings
    monkeypatch.setattr(runtime, "PROGRESS", tmp_path / "progress.log")
    usage.reset()
    p = runtime.Progress("plan11", 39, make_settings(), done=11, wrong=0)
    p.case("m12", "", 11.2)
    p.case("m13", "missing ['2.69']", 8.8)
    lines = (tmp_path / "progress.log").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "plan11: 39 cases, 11 done before --resume"
    assert lines[1] == "[12/39] m12 ok 11.2s | wrong so far 0 | spent $0.00 | ~5 min left"
    assert lines[2].startswith("[13/39] m13 WRONG missing ['2.69'] 8.8s | wrong so far 1")
    assert "[12/39] m12 ok" in capsys.readouterr().out


def test_the_run_reports_its_peak_memory() -> None:
    assert runtime.peak_mb() > 1
    assert runtime.memory_line(4).startswith("peak memory: ") and "4 cases were done before --resume" in \
        runtime.memory_line(4)
