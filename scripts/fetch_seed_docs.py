"""Download the seed documents listed in data/manifest.json.

- Fetches only entries with "acquisition": "download".
- Every URL (including redirect targets) must be https and on the manifest's
  allowlist, and must be allowed by the host's robots.txt for our user agent.
- Enforces a size limit, checks the payload is a PDF, and rejects truncated downloads
  (size must match Content-Length and the file must end with %%EOF).
- Records SHA-256, size, final URL and fetch date in data/provenance.json.
- Lists the "local" entries whose PDFs still need to be placed in data/.

Standard library only. Usage:
    python scripts/fetch_seed_docs.py [--force] [--dry-run] [--only ID ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MANIFEST = DATA_DIR / "manifest.json"
PROVENANCE = DATA_DIR / "provenance.json"

USER_AGENT = "KasafiBot/0.1 (+https://github.com/bawanallahbilyaminu/kasafi-agent)"
MAX_BYTES = 100 * 1024 * 1024  # 100 MB per document
TIMEOUT = 60
DELAY_SECONDS = 2.0  # politeness delay between requests to the same host
CHUNK = 64 * 1024


class FetchError(Exception):
    pass


def host_allowed(url: str, allowlist: list[str]) -> bool:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        return False
    host = parts.hostname.lower()
    return any(host == d or host.endswith("." + d) for d in allowlist)


class Robots:
    """robots.txt cache, fetched with our own user agent."""

    def __init__(self) -> None:
        self._cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}

    def allowed(self, url: str) -> bool:
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._cache:
            self._cache[origin] = self._load(origin)
        parser = self._cache[origin]
        # None = robots.txt could not be read for a reason other than 4xx: be conservative.
        return parser is not None and parser.can_fetch(USER_AGENT, url)

    @staticmethod
    def _load(origin: str) -> urllib.robotparser.RobotFileParser | None:
        parser = urllib.robotparser.RobotFileParser(origin + "/robots.txt")
        req = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                parser.parse(resp.read(512 * 1024).decode("utf-8", errors="replace").splitlines())
        except urllib.error.HTTPError as e:
            # Same convention as urllib.robotparser: 401/403 = disallow all, other 4xx = allow all.
            if e.code in (401, 403):
                parser.disallow_all = True
            elif 400 <= e.code < 500:
                parser.allow_all = True
            else:
                return None
        except (urllib.error.URLError, TimeoutError, OSError):
            return None
        return parser


class GuardedRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse redirects that leave the allowlist or are disallowed by robots.txt."""

    def __init__(self, allowlist: list[str], robots: Robots) -> None:
        self.allowlist = allowlist
        self.robots = robots

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not host_allowed(newurl, self.allowlist):
            raise FetchError(f"redirect to non-allowlisted URL refused: {newurl}")
        if not self.robots.allowed(newurl):
            raise FetchError(f"redirect target disallowed by robots.txt: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(opener, url: str, dest: Path) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
    tmp = dest.with_suffix(dest.suffix + ".part")
    sha = hashlib.sha256()
    size = 0
    tail = b""
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            length = resp.headers.get("Content-Length")
            if length and length.isdigit() and int(length) > MAX_BYTES:
                raise FetchError(f"too large ({int(length)} bytes > {MAX_BYTES})")
            with tmp.open("wb") as f:
                first = True
                while chunk := resp.read(CHUNK):
                    if first and not chunk.startswith(b"%PDF-"):
                        raise FetchError(
                            f"not a PDF (Content-Type: {resp.headers.get('Content-Type')}); "
                            "probably a landing page, resolve the direct PDF link"
                        )
                    first = False
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise FetchError(f"too large (> {MAX_BYTES} bytes)")
                    sha.update(chunk)
                    f.write(chunk)
                    tail = (tail + chunk)[-2048:]
            final_url = resp.geturl()
        if size == 0:
            raise FetchError("empty response")
        if length and length.isdigit() and size != int(length):
            raise FetchError(f"truncated: got {size} of {int(length)} bytes")
        if b"%%EOF" not in tail:
            raise FetchError("truncated: no %%EOF at end of file")
        tmp.replace(dest)
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"network error: {e}") from e
    finally:
        tmp.unlink(missing_ok=True)
    return {
        "sha256": sha.hexdigest(),
        "bytes": size,
        "final_url": final_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            sha.update(chunk)
    return sha.hexdigest()


def normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_local_file(doc: dict) -> Path | None:
    """A local PDF may be named <id>.pdf or after its title (punctuation ignored)."""
    by_id = DATA_DIR / f"{doc['id']}.pdf"
    if by_id.exists():
        return by_id
    wanted = normalise(doc["title"])
    for pdf in DATA_DIR.glob("*.pdf"):
        if normalise(pdf.stem) == wanted:
            return pdf
    return None


def load_provenance() -> dict:
    if PROVENANCE.exists():
        return json.loads(PROVENANCE.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-download files that already exist")
    ap.add_argument("--dry-run", action="store_true", help="check allowlist/robots only, download nothing")
    ap.add_argument("--only", nargs="+", metavar="ID", help="only these document ids")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    allowlist = [d.lower() for d in manifest["allowlist_domains"]]
    docs = manifest["documents"]
    provenance = load_provenance()
    robots = Robots()
    opener = urllib.request.build_opener(GuardedRedirects(allowlist, robots))
    last_hit: dict[str, float] = {}

    ok, skipped, failed = [], [], []

    for doc in (d for d in docs if d["acquisition"] == "download" and (not args.only or d["id"] in args.only)):
        doc_id, url = doc["id"], doc.get("source_url")
        dest = DATA_DIR / f"{doc_id}.pdf"
        if not url:
            failed.append((doc_id, "no source_url"))
            continue
        if not host_allowed(url, allowlist):
            failed.append((doc_id, f"not on allowlist / not https: {url}"))
            continue
        if not robots.allowed(url):
            failed.append((doc_id, "disallowed by robots.txt (mark as 'local' and download manually)"))
            continue
        if dest.exists() and not args.force:
            if doc_id not in provenance:
                provenance[doc_id] = {"sha256": sha256_file(dest), "bytes": dest.stat().st_size,
                                      "final_url": None, "fetched_at": None, "source_url": url,
                                      "acquisition": "download"}
            skipped.append((doc_id, "already downloaded"))
            continue
        if args.dry_run:
            ok.append((doc_id, "would download"))
            continue

        host = urllib.parse.urlsplit(url).hostname
        wait = DELAY_SECONDS - (time.monotonic() - last_hit.get(host, 0.0))
        if wait > 0:
            time.sleep(wait)
        print(f"downloading {doc_id} ...", flush=True)
        try:
            info = download(opener, url, dest)
        except FetchError as e:
            failed.append((doc_id, str(e)))
        else:
            provenance[doc_id] = {**info, "source_url": url, "acquisition": "download"}
            ok.append((doc_id, f"{info['bytes'] / 1e6:.1f} MB"))
        finally:
            last_hit[host] = time.monotonic()

    missing_local = []
    for doc in (d for d in docs if d["acquisition"] == "local"):
        path = find_local_file(doc)
        if path is None:
            missing_local.append(doc)
            continue
        entry = provenance.get(doc["id"], {})
        digest = sha256_file(path)
        if entry.get("sha256") != digest:
            provenance[doc["id"]] = {
                "sha256": digest,
                "bytes": path.stat().st_size,
                "file": path.name,
                "source_url": doc.get("source_url"),
                "acquisition": "local",
                "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }

    if not args.dry_run:
        PROVENANCE.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def section(title: str, rows: list[tuple[str, str]]) -> None:
        print(f"\n{title} ({len(rows)})")
        for doc_id, note in rows:
            print(f"  - {doc_id}: {note}")

    section("Downloaded" if not args.dry_run else "Allowed", ok)
    section("Skipped", skipped)
    section("Failed", failed)
    print(f"\nLocal files still needed ({len(missing_local)})")
    for doc in missing_local:
        hint = f" (source: {doc['source_url']})" if doc.get("source_url") else ""
        print(f"  - {doc['id']}: save as data/{doc['id']}.pdf -- {doc['title']}{hint}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
