"""deploy/deploy.sh's helper (scripts/deploykit.py): progress text, the uploader, the follower, packing, and the
checksum diff that makes --sync-pdfs incremental. No network, no server: a local Python stands in for ssh."""

import hashlib
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("deploykit", ROOT / "scripts" / "deploykit.py")
dk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dk)


def quiet(log=None) -> "dk.Screen":
    return dk.Screen(live_mode=False, err=io.StringIO(), log_path=str(log) if log else "")


def test_sizes_and_times_read_naturally() -> None:
    assert dk.fmt_bytes(415_200_000) == "415.2 MB" and dk.fmt_bytes(812_000) == "812 KB"
    assert dk.fmt_bytes(1_270_000_000) == "1.27 GB" and dk.fmt_bytes(12) == "12 B"
    assert dk.fmt_time(7) == "7s" and dk.fmt_time(102) == "1m 42s" and dk.fmt_time(3780) == "1h 03m"


def test_the_bar_shows_percent_done_total_speed_and_time_left() -> None:
    line = dk.bar_line("uploading", 100_000_000, 400_000_000, 20.0, width=20)
    assert line.startswith("uploading  [█████░░░░░░░░░░░░░░░]  25%")
    assert "100.0 MB/400.0 MB" in line and "5.0 MB/s" in line and "1m 00s left" in line
    assert "done in 20s" in dk.bar_line("x", 5, 5, 20.0)
    assert "0%" in dk.bar_line("x", 0, 0, 0.0) or "100%" in dk.bar_line("x", 0, 0, 0.0)   # empty file: no crash


def test_live_screen_redraws_one_status_line_and_prints_lines_above_it() -> None:
    err = io.StringIO()
    s = dk.Screen(live_mode=True, err=err, log_path="")
    s.draw("⠋ loading 3s")
    s.line("[remote] building abc1234")
    s.clear()
    out = err.getvalue()
    assert "\r\033[K⠋ loading 3s" in out and "\r\033[K[remote] building abc1234\n⠋ loading 3s" in out


def test_parse_sums_and_the_diff_never_deletes() -> None:
    a, b, c = "a" * 64, "b" * 64, "c" * 64
    server = dk.parse_sums(f"SUM {a}  budget-2026-approved.pdf\nSUM {b}  old.pdf\n{c} *extra.pdf\nnoise line\n")
    assert server == {"budget-2026-approved.pdf": a, "old.pdf": b, "extra.pdf": c}
    d = dk.diff({"budget-2026-approved.pdf": a, "old.pdf": c, "new.pdf": b}, server)
    assert d == {"new": ["new.pdf"], "changed": ["old.pdf"], "unchanged": ["budget-2026-approved.pdf"],
                 "server_only": ["extra.pdf"]}
    assert dk.diff_line(d) == "1 new, 1 changed, 1 unchanged (1 only on the server, kept)"
    assert dk.diff_line(dk.diff({"x.pdf": a}, {"x.pdf": a})) == "0 new, 0 changed, 1 unchanged"


def files(tmp_path: Path) -> dict[str, Path]:
    out = {}
    for name, body in {"a.pdf": b"%PDF-1 a" * 1000, "b.pdf": b"%PDF-1 b", "c.docx": b"PK\x03\x04 c"}.items():
        p = tmp_path / "src" / name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(body)
        out[name] = p
    return out


def test_pdfs_diff_packs_only_new_and_changed_files(tmp_path: Path) -> None:
    names = files(tmp_path)
    same = hashlib.sha256(names["a.pdf"].read_bytes()).hexdigest()
    sums = tmp_path / "sums.txt"
    sums.write_text(f"SUM {same}  a.pdf\nSUM {'0' * 64}  b.pdf\nSUM {'1' * 64}  server-only.pdf\n", encoding="utf-8")
    out = tmp_path / "out.tar"
    line = dk.pdfs_diff(sums, out, names=names, screen=quiet())
    assert line == "1 new, 1 changed, 1 unchanged (1 only on the server, kept)"
    with tarfile.open(out) as t:
        assert sorted(t.getnames()) == ["b.pdf", "c.docx"]
        assert t.extractfile("b.pdf").read() == b"%PDF-1 b"


def test_pdfs_diff_with_nothing_new_writes_no_tar(tmp_path: Path) -> None:
    names = files(tmp_path)
    sums = tmp_path / "sums.txt"
    sums.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {n}\n" for n, p in names.items()),
                    encoding="utf-8")
    out = tmp_path / "out.tar"
    out.write_bytes(b"stale")
    assert dk.pdfs_diff(sums, out, names=names, screen=quiet()) == "0 new, 0 changed, 3 unchanged"
    assert not out.exists()


def test_pack_names_members_relative_to_the_base_and_logs(tmp_path: Path) -> None:
    names = files(tmp_path)
    log = tmp_path / "run.log"
    out = tmp_path / "x.tar"
    dk.pack(out, [(f"geo/{n}", p) for n, p in names.items()], screen=quiet(log))
    with tarfile.open(out) as t:
        assert sorted(t.getnames()) == ["geo/a.pdf", "geo/b.pdf", "geo/c.docx"]
    assert "packing:" in log.read_text(encoding="utf-8")


def test_upload_streams_the_file_into_the_command_and_returns_its_exit_code(tmp_path: Path) -> None:
    src = tmp_path / "big.bin"
    src.write_bytes(bytes(range(256)) * 20_000)                       # 5 MB, several chunks
    dst = tmp_path / "landed.bin"
    fake_ssh = [sys.executable, "-c", f"import sys; open(r'{dst}', 'wb').write(sys.stdin.buffer.read())"]
    err = io.StringIO()
    assert dk.upload(src, fake_ssh, screen=dk.Screen(live_mode=False, err=err, log_path="")) == 0
    assert dst.read_bytes() == src.read_bytes()
    assert "uploading: 5.1 MB in" in err.getvalue() and "100%" in err.getvalue()   # plain lines every 10%
    failing = [sys.executable, "-c", "import sys; sys.stdin.buffer.read(); sys.exit(3)"]
    assert dk.upload(src, failing, screen=quiet()) == 3


def test_a_git_bash_program_path_is_run_in_its_windows_form(monkeypatch) -> None:
    monkeypatch.setattr(dk.os, "name", "nt")
    assert dk.native("/c/Windows/System32/OpenSSH/ssh.exe") == "C:/Windows/System32/OpenSSH/ssh.exe"
    assert dk.native("ssh") == "ssh" and dk.native("/usr/bin/ssh") == "/usr/bin/ssh"
    monkeypatch.setattr(dk.os, "name", "posix")
    assert dk.native("/c/Windows/ssh.exe") == "/c/Windows/ssh.exe"


def test_follow_echoes_every_line_for_parsing_and_hides_machine_lines_from_the_view(tmp_path: Path) -> None:
    log = tmp_path / "run.log"
    err = io.StringIO()
    out = io.StringIO()
    src = io.StringIO("[remote] loading index (6.4M compressed)\nSUM abc  x.pdf\nRESULT=ok COMMIT=abc123\n"
                      "SUMMARY=46 documents\n")
    screen = dk.Screen(live_mode=False, err=err, log_path=str(log))
    assert dk.follow("server", src=src, out=out, screen=screen) == 0
    assert out.getvalue().splitlines() == ["[remote] loading index (6.4M compressed)", "SUM abc  x.pdf",
                                           "RESULT=ok COMMIT=abc123", "SUMMARY=46 documents"]
    shown = err.getvalue()
    assert "[remote] loading index" in shown and "RESULT=" not in shown and "SUM abc" not in shown
    assert "RESULT=ok COMMIT=abc123" in log.read_text(encoding="utf-8")       # the log keeps everything


def test_meter_copies_stdin_to_the_file(tmp_path: Path) -> None:
    out = tmp_path / "dump.gz"
    assert dk.meter(out, "pg_dump", src=io.BytesIO(b"x" * 3_000_000), screen=quiet()) == 0
    assert out.stat().st_size == 3_000_000


def test_the_deploy_script_keeps_its_safety_steps() -> None:
    """The rewrite for progress must not drop a gate: tests before deploy, the migration check, rollback paths."""
    sh = (ROOT / "deploy" / "deploy.sh").read_text(encoding="utf-8")
    for must in ("KASAFI_E2E_REQUIRED=1 uv run pytest -q tests/test_e2e_conversation.py", "uv run pytest -q",
                 "uncommitted changes", "origin/main", "pf_migration", "remote \"server\" rollback",
                 "the server kept the previous index", "ALLOWED_KEYS", "set -euo pipefail"):
        assert must in sh, must
    remote = (ROOT / "deploy" / "remote.sh").read_text(encoding="utf-8")
    assert "predeploy.dump" in remote and "TRUNCATE documents CASCADE" in remote and "never deleted" in remote
    assert "\nsync-pdfs)" in remote.replace("\r", "") and "rm -f /data/pdfs" not in remote


@pytest.mark.skipif(sys.platform != "win32", reason="the PowerShell wrapper")
def test_the_powershell_wrapper_uses_gits_bash_in_the_same_window() -> None:
    ps = (ROOT / "deploy" / "deploy.ps1").read_text(encoding="utf-8")
    assert "bin\\bash.exe" in ps and "git-bash.exe\"" not in ps and "@args" in ps and "exit $code" in ps
