#!/usr/bin/env python3
import sys
from pathlib import Path

# Import canonical paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from tools.cvr import paths

def die(msg: str) -> int:
  print(f"template_baseline_lint: ERROR: {msg}", file=sys.stderr)
  return 1

def main() -> int:
  req_ok = any(Path(p).exists() for p in ["requirements-verify.txt", "requirements.txt", "flake.nix"])
  if not req_ok:
    return die("missing verification requirements file: requirements-verify.txt, requirements.txt, or flake.nix")

  required = [
    Path(".gitignore"),
    Path(".agentsignore"),
    Path("CLAUDE.md"),
    Path("AGENDA.md"),
    Path(".claude"),
    paths.INTENT_DIR,
  ]
  missing = [str(p) for p in required if not p.exists()]
  if missing:
    return die("missing required template files/dirs: " + ", ".join(missing))

  print("template_baseline_lint: OK")
  return 0

if __name__ == "__main__":
  raise SystemExit(main())
