"""Local shortcut for app/acquisition/forget.py (the server runs the module directly, since the image has no
scripts/ folder). Usage: python scripts/forget_document.py bir-2025-q3 [--yes --reason "demo reset"]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.acquisition.forget import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
