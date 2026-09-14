"""Make the repo-owned CI scripts in ``.github/scripts`` importable from unit tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".github" / "scripts"))
