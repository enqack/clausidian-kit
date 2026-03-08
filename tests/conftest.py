import sys
from pathlib import Path


# Ensure lint scripts and utilities under tools/ are importable in tests.
ROOT = Path(__file__).resolve().parents[1]
for rel in ("tools", "tools/linters"):
  path = ROOT / rel
  path_str = str(path)
  if path_str not in sys.path:
    sys.path.insert(0, path_str)
