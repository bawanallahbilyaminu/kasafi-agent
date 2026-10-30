"""What the eval runners share so a run survives memory pressure.

- Checkpoint: each case's result goes to a JSON-lines file as soon as the case finishes (flushed and synced), with
  the run's settings in the first line and the cost counters so far in every line. `--resume` reads it back and runs
  only the cases not in it, so a killed run loses at most the cases in flight.
- run_each: cases one or two at a time (each worker its own DB connection), garbage collected after every case.
- warm: the embedding model loaded once, before the first case (every case then reuses it).
- peak_mb: the process's peak memory, printed at the end of a run.
"""

from __future__ import annotations

import asyncio
import gc
import json
import os
import sys
from pathlib import Path

import psycopg

from app import usage

CHECKPOINTS = Path(__file__).with_name(".checkpoints")      # not in git


class Checkpoint:
    def __init__(self, name: str, header: dict, *, resume: bool) -> None:
        self.path = CHECKPOINTS / f"{name}.jsonl"
        self.done: dict[str, dict] = {}
        if resume and self.path.exists():
            lines = [json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]
            self.header = lines[0]["header"]
            if diff := {k: (self.header.get(k), v) for k, v in header.items() if v is not None
                        and self.header.get(k) != v}:
                raise SystemExit(f"--resume: {self.path} was a different run ({diff}); drop --resume to start over")
            self.done = {r["key"]: r for r in lines[1:]}
            if lines[1:]:
                usage.restore(lines[-1]["usage"])
            print(f"resuming {self.path.name}: {len(self.done)} cases already done")
        else:
            self.header = header
            self.path.parent.mkdir(exist_ok=True)
            self.path.write_text(json.dumps({"header": header}, ensure_ascii=False) + "\n", encoding="utf-8")

    def add(self, key: str, record: dict) -> None:
        record = {"key": key, **record, "usage": usage.snapshot()}
        self.done[key] = record
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())


def warm() -> None:
    from app.retrieval.line_meaning import embed_queries
    embed_queries(["warm up"])        # loads the model once; it's cached for the process (line_meaning._model)


async def run_each(items: list, fn, db_url: str, concurrency: int = 1) -> None:
    """await fn(item, conn) for every item, `concurrency` (1-2) at a time."""
    queue = list(items)

    async def worker() -> None:
        with psycopg.connect(db_url) as conn:
            while queue:
                await fn(queue.pop(0), conn)
                gc.collect()            # free the case's evidence, pages and crops before the next one

    await asyncio.gather(*(worker() for _ in range(max(1, min(concurrency, 2, len(queue))))))


def peak_mb() -> float:
    """Peak resident memory of this process, in MB."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        c = Counters(cb=ctypes.sizeof(Counters))
        psapi = ctypes.WinDLL("psapi")
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        kernel = ctypes.WinDLL("kernel32")
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return c.PeakWorkingSetSize / 2**20
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 2**20 if sys.platform == "darwin" else peak / 2**10


def memory_line(resumed: int) -> str:
    return f"peak memory: {peak_mb():,.0f} MB" + (f" (this session; {resumed} cases were done before --resume)"
                                                  if resumed else "")
