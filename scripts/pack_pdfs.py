"""Pack the source PDFs for the server's evidence crops: deploy/deploy.sh --sync-pdfs.

Each seed document in data/manifest.json is stored as <id>.pdf (local files may be named after their
title), plus everything in data/fetched/. Public documents only. Usage: python scripts/pack_pdfs.py <out.tar>
"""

import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.retrieval.indexer import find_file  # noqa: E402


def main() -> int:
    out = Path(sys.argv[1])
    data = ROOT / "data"
    manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    names: dict[str, Path] = {}
    for doc in manifest["documents"]:
        if path := find_file(doc, data):
            names[f"{doc['id']}.pdf"] = path
    for path in sorted((data / "fetched").glob("*.pdf")):
        if not path.name.startswith("incoming-"):
            names.setdefault(path.name, path)
    with tarfile.open(out, "w") as tar:
        for name, path in sorted(names.items()):
            tar.add(path, arcname=name)
    size = sum(p.stat().st_size for p in names.values())
    print(f"packed {len(names)} PDFs, {size / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
