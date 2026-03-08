#!/usr/bin/env python3
import sys
from pathlib import Path

# Import canonical paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from tools.cvr import paths

def die(msg: str) -> int:
  print(f"workflow_intent_lint: ERROR: {msg}", file=sys.stderr)
  return 1

def workflow_requires_intent(txt: str) -> bool:
  # Accept either:
  # - artifacts_required includes the project intent path
  # - or a Precondition section mentioning it
  return (str(paths.PROJECT_INTENT) in txt)

def main() -> int:
  wf_dir = Path(".claude/skills")
  if not wf_dir.exists():
    return die("missing .claude/skills directory")

  bad = []
  for p in sorted(wf_dir.glob("*/SKILL.md")):
    if p.parent.name == "establish-intent":
      continue
    txt = p.read_text(encoding="utf-8")
    if not workflow_requires_intent(txt):
      bad.append(p.as_posix())

  if bad:
    return die(f"workflows missing intent requirement (must mention {paths.PROJECT_INTENT}): " + ", ".join(bad))

  print("workflow_intent_lint: OK")
  return 0

if __name__ == "__main__":
  raise SystemExit(main())
