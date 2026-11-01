"""Progress, uploads and the PDF checksum diff for deploy/deploy.sh (stdlib only; no model calls).

deploy.sh runs these as `python scripts/deploykit.py <command> ...`:

  upload LOCAL -- CMD...        stream LOCAL into CMD's stdin (an `ssh host "cat > file"`) with a progress bar:
                                MB done/total, speed and time left. Exit code: CMD's.
  meter OUT --label TEXT        copy stdin to OUT (a pg_dump | gzip), with a spinner, MB written and speed.
  follow --label TEXT           run beside a long command (`cmd 2>&1 | follow`): its lines are printed above a
                                spinner with the elapsed time; the spinner's text is the latest "[remote] ..." step.
                                The lines are also written to stdout, so the caller can capture and parse them.
  pack OUT --base DIR FILES...  a tar of FILES (names relative to DIR), with a progress bar.
  pdfs-diff SUMS OUT            hash the local source PDFs, compare with the server's `sha256sum` lines in SUMS,
                                pack only the new and changed ones into OUT (no OUT when nothing changed), print
                                "DIFF: 3 new, 0 changed, 44 unchanged".

Progress is drawn on stderr when KASAFI_PROGRESS=1 (deploy.sh sets it when stderr is a terminal: Python can't tell
a mintty terminal from a pipe) or stderr is a console; otherwise a plain line every 10%, so logs stay readable.
Every line also goes to the run's log (KASAFI_DEPLOY_LOG) when set.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time
from pathlib import Path

CHUNK = 1 << 20
SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


# --- formatting --------------------------------------------------------------------------------------------------

def fmt_bytes(n: float) -> str:
    """'415.2 MB', '812 KB', '1.27 GB'."""
    if n >= 1e9:
        return f"{n / 1e9:.2f} GB"
    if n >= 1e6:
        return f"{n / 1e6:.1f} MB"
    if n >= 1e3:
        return f"{n / 1e3:.0f} KB"
    return f"{int(n)} B"


def fmt_time(s: float) -> str:
    """'7s', '1m 42s', '1h 03m'."""
    s = max(0, int(round(s)))
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60:02d}s"
    return f"{s // 3600}h {s % 3600 // 60:02d}m"


def bar_line(label: str, done: int, total: int, elapsed: float, width: int = 24) -> str:
    """'uploading  [██████████░░░░░░░░░░░░░░]  42%  174.3/415.2 MB  5.1 MB/s  47s left'."""
    frac = min(1.0, done / total) if total else 1.0
    fill = int(round(frac * width))
    speed = done / elapsed if elapsed > 0 else 0.0
    left = (total - done) / speed if speed > 0 and total else 0.0
    eta = f"{fmt_time(left)} left" if done < total else f"done in {fmt_time(elapsed)}"
    return (f"{label}  [{'█' * fill}{'░' * (width - fill)}] {frac * 100:3.0f}%  "
            f"{fmt_bytes(done)}/{fmt_bytes(total)}  {fmt_bytes(speed)}/s  {eta}")


# --- the terminal ------------------------------------------------------------------------------------------------

def _enable_vt() -> None:
    """ANSI escapes in a Windows console (PowerShell, cmd): virtual terminal processing on stderr."""
    if os.name != "nt":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-12)                     # STD_ERROR_HANDLE
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:                               # noqa: BLE001
        pass


def live() -> bool:
    flag = os.environ.get("KASAFI_PROGRESS")
    if flag is not None:
        return flag == "1"
    return sys.stderr.isatty()


class Screen:
    """One redrawn status line under printed lines; plain lines when not live. Thread-safe."""

    def __init__(self, live_mode: bool | None = None, err=None, log_path: str | None = None):
        self.live = live() if live_mode is None else live_mode
        self.err = err or sys.stderr
        self.lock = threading.Lock()
        self.status = ""
        self.log_path = log_path if log_path is not None else os.environ.get("KASAFI_DEPLOY_LOG", "")
        if self.live:
            _enable_vt()

    def _cols(self) -> int:
        return max(40, shutil.get_terminal_size((110, 20)).columns - 1)

    def log(self, text: str) -> None:
        if self.log_path:
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(text.rstrip("\n") + "\n")
            except OSError:
                pass

    def line(self, text: str) -> None:
        """A permanent line (above the status line when live)."""
        with self.lock:
            if self.live:
                self.err.write("\r\033[K" + text + "\n")
                if self.status:
                    self.err.write(self.status[: self._cols()])
            else:
                self.err.write(text + "\n")
            self.err.flush()
        self.log(text)

    def draw(self, status: str) -> None:
        """Redraw the status line (live only)."""
        if not self.live:
            return
        with self.lock:
            self.status = status
            self.err.write("\r\033[K" + status[: self._cols()])
            self.err.flush()

    def clear(self) -> None:
        if not self.live:
            return
        with self.lock:
            self.status = ""
            self.err.write("\r\033[K")
            self.err.flush()


class Progress:
    """A byte counter drawn as a bar (total known) or a spinner (total unknown), at most 10 times a second; when
    not live, one plain line per 10% (or per 25 MB without a total)."""

    def __init__(self, screen: Screen, label: str, total: int = 0):
        self.screen, self.label, self.total = screen, label, total
        self.done, self.t0, self.last = 0, time.monotonic(), 0.0
        self.step = 0                       # the last 10% (or 25 MB) reported in plain mode
        self.i = 0

    def text(self) -> str:
        el = time.monotonic() - self.t0
        if self.total:
            return bar_line(self.label, self.done, self.total, el)
        self.i += 1
        speed = self.done / el if el > 0 else 0
        return f"{SPIN[self.i % len(SPIN)]} {self.label}  {fmt_bytes(self.done)}  {fmt_bytes(speed)}/s  {fmt_time(el)}"

    def add(self, n: int) -> None:
        self.done += n
        now = time.monotonic()
        if self.screen.live:
            if now - self.last >= 0.1:
                self.last = now
                self.screen.draw(self.text())
            return
        mark = int(self.done * 10 / self.total) if self.total else int(self.done / 25e6)
        if mark > self.step:
            self.step = mark
            self.screen.line(self.text())

    def finish(self) -> str:
        el = time.monotonic() - self.t0
        self.screen.clear()
        speed = f" ({fmt_bytes(self.done / el)}/s)" if el >= 0.5 else ""      # too quick for a speed to mean much
        msg = f"  {self.label}: {fmt_bytes(self.done)} in {fmt_time(el)}{speed}"
        self.screen.line(msg)
        return msg


# --- commands ----------------------------------------------------------------------------------------------------

def native(program: str) -> str:
    """A Git Bash path ('/c/Windows/System32/OpenSSH/ssh.exe') as Windows runs it ('C:/Windows/...'); deploy.sh
    turns MSYS path rewriting off, so the program path arrives in bash's form."""
    if os.name == "nt" and len(program) > 3 and program[0] == "/" and program[2] == "/" and program[1].isalpha():
        return f"{program[1].upper()}:{program[2:]}"
    return program


def upload(local: str | Path, cmd: list[str], label: str = "uploading", screen: Screen | None = None) -> int:
    """Stream a file into cmd's stdin with a progress bar. Returns cmd's exit code (a broken pipe is a failure)."""
    screen = screen or Screen()
    total = Path(local).stat().st_size
    prog = Progress(screen, label, total)
    proc = subprocess.Popen([native(cmd[0]), *cmd[1:]], stdin=subprocess.PIPE)
    try:
        with open(local, "rb") as f:
            while chunk := f.read(CHUNK):
                proc.stdin.write(chunk)
                prog.add(len(chunk))
        proc.stdin.close()
    except (BrokenPipeError, OSError) as e:
        screen.clear()
        screen.line(f"  upload interrupted: {e}")
        proc.kill()
        proc.wait()
        return proc.returncode or 1
    rc = proc.wait()
    if rc == 0:
        prog.finish()
    else:
        screen.clear()
    return rc


def meter(out: str | Path, label: str, src=None, screen: Screen | None = None) -> int:
    """Copy src (stdin) to out with a spinner and the bytes written."""
    screen = screen or Screen()
    src = src or sys.stdin.buffer
    prog = Progress(screen, label)
    with open(out, "wb") as f:
        while chunk := src.read(CHUNK):
            f.write(chunk)
            prog.add(len(chunk))
    prog.finish()
    return 0


def follow(label: str, src=None, out=None, screen: Screen | None = None, tick: float = 0.1) -> int:
    """Print src's lines above a spinner with the elapsed time; echo them to out for the caller to parse."""
    screen = screen or Screen()
    src = src or sys.stdin
    out = out or sys.stdout
    t0 = time.monotonic()
    state = {"step": label, "done": False}

    def spin() -> None:
        i = 0
        while not state["done"]:
            i += 1
            screen.draw(f"{SPIN[i % len(SPIN)]} {state['step']}  {fmt_time(time.monotonic() - t0)}")
            time.sleep(tick)

    th = threading.Thread(target=spin, daemon=True)
    if screen.live:
        th.start()
    try:
        for raw in src:
            text = raw.rstrip("\r\n")
            out.write(text + "\n")
            out.flush()
            if text.startswith(("RESULT=", "SUMMARY=", "REVISION=", "FREE=", "SUM ")):
                screen.log(text)                     # machine lines: parsed by deploy.sh, kept out of the view
                continue
            screen.line(text)
            if text.startswith("[remote] "):
                state["step"] = f"{label}: {text[9:].strip()[:70]}"
    finally:
        state["done"] = True
        if screen.live:
            th.join(timeout=1)
        screen.clear()
    screen.line(f"  {label}: {fmt_time(time.monotonic() - t0)}")
    return 0


class _Counting:
    """A file wrapper that reports bytes read (tarfile reads members through it)."""

    def __init__(self, f, prog: Progress):
        self.f, self.prog = f, prog

    def read(self, n: int = -1) -> bytes:
        b = self.f.read(n)
        self.prog.add(len(b))
        return b


def pack(out: str | Path, members: list[tuple[str, Path]], label: str = "packing",
         screen: Screen | None = None) -> int:
    """A tar of (name in archive, path) members with a progress bar over their total size."""
    screen = screen or Screen()
    total = sum(p.stat().st_size for _, p in members)
    prog = Progress(screen, label, total)
    with tarfile.open(out, "w") as tar:
        for name, path in members:
            info = tar.gettarinfo(str(path), arcname=name)
            with open(path, "rb") as f:
                tar.addfile(info, _Counting(f, prog))
    prog.finish()
    return 0


def sha256(path: Path, prog: Progress | None = None) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
            if prog:
                prog.add(len(chunk))
    return h.hexdigest()


def parse_sums(text: str) -> dict[str, str]:
    """`sha256sum` output ('<hex>  name' or '<hex> *name', optionally prefixed 'SUM ') -> {name: hex}."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("SUM "):
            line = line[4:]
        parts = line.split(None, 1)
        if len(parts) == 2 and len(parts[0]) == 64 and all(c in "0123456789abcdef" for c in parts[0]):
            out[parts[1].lstrip("*").strip()] = parts[0]
    return out


def diff(local: dict[str, str], server: dict[str, str]) -> dict[str, list[str]]:
    """{new, changed, unchanged, server_only}: names, sorted. Nothing is ever deleted on the server."""
    return {"new": sorted(n for n in local if n not in server),
            "changed": sorted(n for n in local if n in server and server[n] != local[n]),
            "unchanged": sorted(n for n in local if server.get(n) == local[n]),
            "server_only": sorted(n for n in server if n not in local)}


def diff_line(d: dict[str, list[str]]) -> str:
    s = f"{len(d['new'])} new, {len(d['changed'])} changed, {len(d['unchanged'])} unchanged"
    return s + (f" ({len(d['server_only'])} only on the server, kept)" if d["server_only"] else "")


def pdfs_diff(sums_path: str | Path, out: str | Path, names: dict[str, Path] | None = None,
              screen: Screen | None = None) -> str:
    screen = screen or Screen()
    if names is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from pack_pdfs import collect
        names = collect()
    total = sum(p.stat().st_size for p in names.values())
    prog = Progress(screen, f"hashing {len(names)} local files", total)
    local = {n: sha256(p, prog) for n, p in sorted(names.items())}
    prog.finish()
    d = diff(local, parse_sums(Path(sums_path).read_text(encoding="utf-8", errors="replace")))
    send = d["new"] + d["changed"]
    for n in d["new"]:
        screen.line(f"  new:     {n}")
    for n in d["changed"]:
        screen.line(f"  changed: {n}")
    Path(out).unlink(missing_ok=True)
    if send:
        pack(out, [(n, names[n]) for n in send], label=f"packing {len(send)} file(s)", screen=screen)
    return diff_line(d)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]

    def opt(name: str, default: str = "") -> str:
        if name in rest:
            i = rest.index(name)
            val = rest[i + 1]
            del rest[i:i + 2]
            return val
        return default

    if cmd == "upload":
        label = opt("--label", "uploading")
        i = rest.index("--")
        return upload(rest[0], rest[i + 1:], label)
    if cmd == "meter":
        return meter(rest[0], opt("--label", "writing"))
    if cmd == "follow":
        return follow(opt("--label", "working"))
    if cmd == "pack":
        label, base = opt("--label", "packing"), Path(opt("--base", "."))
        out, files = rest[0], [Path(f) for f in rest[1:]]
        return pack(out, [(f.resolve().relative_to(base.resolve()).as_posix(), f) for f in files], label)
    if cmd == "pdfs-diff":
        print("DIFF: " + pdfs_diff(rest[0], rest[1]))
        return 0
    print(f"unknown command {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
