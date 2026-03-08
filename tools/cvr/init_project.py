#!/usr/bin/env python3
"""init_project.py - Bootstrap a new project in the clausidian-kit Silo.

Usage:
  python3 tools/cvr/init_project.py --name "My Project" --slug "my-project"

Creates workspace/<slug>/ (source code only — no ADK files).
Appends a row to PROJECTS.md and logs the action to the activity ledger.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.cvr import paths

SAFE_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9\-]*$')


def validate_slug(slug: str) -> None:
    if not slug:
        print("ERROR: --slug must not be empty.", file=sys.stderr)
        sys.exit(1)
    if not SAFE_SLUG_RE.match(slug):
        print(
            f"ERROR: Slug '{slug}' is invalid. Use lowercase letters, digits, and hyphens only.",
            file=sys.stderr,
        )
        sys.exit(1)


def append_to_projects_md(registry: Path, name: str, slug: str) -> None:
    content = registry.read_text(encoding="utf-8")
    new_row = f"| {name} | {slug} | active |\n"
    if not content.endswith("\n"):
        content += "\n"
    registry.write_text(content + new_row, encoding="utf-8")
    print(f"Updated {registry.name}: added '{name}' (slug: {slug})")


def create_workspace_dir(workspace_root: Path, slug: str) -> Path:
    project_dir = workspace_root / slug
    if project_dir.exists():
        print(f"ERROR: workspace/{slug}/ already exists.", file=sys.stderr)
        sys.exit(1)
    project_dir.mkdir(parents=True)
    (project_dir / ".gitkeep").touch()
    print(f"Created workspace/{slug}/")
    return project_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a new source project in the clausidian-kit Silo."
    )
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--slug", required=True, help="Directory name under workspace/")
    args = parser.parse_args()

    validate_slug(args.slug)

    registry = paths.PROJECTS_REGISTRY
    if not registry.exists():
        print(f"ERROR: {registry} not found. Run from the repo root.", file=sys.stderr)
        sys.exit(1)

    workspace_root = paths.WORKSPACE_ROOT
    if not workspace_root.exists():
        print(f"ERROR: {workspace_root}/ not found. Run from the repo root.", file=sys.stderr)
        sys.exit(1)

    create_workspace_dir(workspace_root, args.slug)
    append_to_projects_md(registry, args.name, args.slug)

    # Log action to activity ledger
    log_cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "log_action.py"),
        "--intent", "init-project",
        "--action", "project_initialized",
        "--scope", f"workspace/{args.slug}",
        "--result", "ok",
        "--evidence", str(registry),
    ]
    subprocess.run(log_cmd, check=True)

    print(f"\nProject '{args.name}' (slug: {args.slug}) is ready.")


if __name__ == "__main__":
    main()
