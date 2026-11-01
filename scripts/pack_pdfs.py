"""The source PDFs for the server's evidence crops: deploy/deploy.sh --sync-pdfs.

Each seed document in data/manifest.json is stored as <id>.pdf (local files may be named after their
title), its Word-type original beside it, plus everything in data/fetched/. Public documents only.
`collect()` lists them; deploy.sh compares their checksums with the server's and packs only the new and
changed ones (scripts/deploykit.py pdfs-diff). Run directly, this packs them all:
python scripts/pack_pdfs.py <out.tar>
"""

import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OFFICE_EXTS = (".docx", ".doc", ".odt", ".rtf")


def collect(data: Path | None = None) -> dict[str, Path]:
    """{name on the server: local path}."""
    from app.retrieval.indexer import find_file
    data = data or ROOT / "data"
    manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    names: dict[str, Path] = {}
    for doc in manifest["documents"]:
        if path := find_file(doc, data):
            names[f"{doc['id']}.pdf"] = path
            for ext in OFFICE_EXTS:                      # the Word-type original kept beside its converted PDF
                if (orig := path.with_suffix(ext)).exists():
                    names[f"{doc['id']}{ext}"] = orig
    for path in sorted((data / "fetched").glob("*")):
        if path.suffix in (".pdf", *OFFICE_EXTS) and not path.name.startswith("incoming-"):
            names.setdefault(path.name, path)
    return names


def main() -> int:
    out = Path(sys.argv[1])
    names = collect()
    with tarfile.open(out, "w") as tar:
        for name, path in sorted(names.items()):
            tar.add(path, arcname=name)
    size = sum(p.stat().st_size for p in names.values())
    print(f"packed {len(names)} PDFs, {size / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
