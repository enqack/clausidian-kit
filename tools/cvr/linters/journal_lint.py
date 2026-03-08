#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

# Import canonical paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from tools.cvr import paths
from typing import List

"""Lint journal files for policy compliance.

Enforces:
- Required header
- Disclaimer presence
- Path hygiene (no absolute paths or file URLs)
"""

from lint_common import validate_paths

HEADER_REQ = "### Deep Thoughts, by an Agent"
DISCLAIMER_REQ = "*Editor’s note: This entry is a dramatized reconstruction of a deterministic decision process, derived from run artifacts.*"


def format_error(path: Path, msg: str) -> str:
    return f"journal_lint: ERROR: {path.name}: {msg}"


def lint_file(path: Path) -> List[str]:
    errors: List[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 1. Header Logic
    # We expect the header to be near the top.
    found_header = False
    for line in lines[:5]:
        if HEADER_REQ in line:
            found_header = True
            break
    if not found_header:
        errors.append(format_error(path, f"missing required header: '{HEADER_REQ}'"))

    # 2. Disclaimer Logic
    # We expect the disclaimer near the bottom.
    found_disclaimer = False
    for line in lines[-5:]:
        if DISCLAIMER_REQ in line:
            found_disclaimer = True
            break
    if not found_disclaimer:
        errors.append(format_error(path, "missing required editor disclaimer"))

    # 3. Path Safety
    path_error = validate_paths(text)
    if path_error:
        errors.append(format_error(path, path_error))
    
    return errors


def main() -> int:
    journal_dir = paths.JOURNAL_DIR
    if not journal_dir.exists():
        # No journals to lint
        print(f"journal_lint: no {paths.JOURNAL_DIR} directory; skipping")
        return 0

    all_errors: List[str] = []
    
    for journal_file in sorted(journal_dir.glob("*.md")):
        all_errors.extend(lint_file(journal_file))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1

    print("journal_lint: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
