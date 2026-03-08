#!/usr/bin/env python3
"""verify_silo.py - Audit the health of the clausidian-kit Multi-Project Silo.

Reads PROJECTS.md and verifies that all registered non-root projects have a
corresponding directory under workspace/. Exits non-zero on any failure.

Usage:
  python3 tools/cvr/verify_silo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.cvr import paths


def parse_projects_md(registry: Path) -> list[dict]:
    """Parse PROJECTS.md table rows into dicts with keys: name, slug, status."""
    projects = []
    content = registry.read_text(encoding="utf-8")
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [p.strip() for p in stripped.split("|")]
        # Skip header row and separator row
        if len(parts) < 4:
            continue
        name, slug, status = parts[1], parts[2], parts[3]
        if name.lower() in ("name", "---", ":---", "---:"):
            continue
        if slug.startswith("---"):
            continue
        projects.append({"name": name, "slug": slug, "status": status})
    return projects


def check_project(workspace_root: Path, project: dict) -> list[str]:
    """Return a list of error strings for a given project entry."""
    errors = []
    slug = project["slug"]

    # Silo root entry is special — "." means the repo root itself
    if slug == ".":
        return errors

    project_dir = workspace_root / slug
    if not project_dir.exists():
        errors.append(f"Directory missing: workspace/{slug}/")
    return errors


def main() -> None:
    registry = paths.PROJECTS_REGISTRY
    workspace_root = paths.WORKSPACE_ROOT

    if not registry.exists():
        print(f"ERROR: {registry} not found. Run from the repo root.", file=sys.stderr)
        sys.exit(1)

    projects = parse_projects_md(registry)
    if not projects:
        print(f"ERROR: No projects found in {registry}.", file=sys.stderr)
        sys.exit(1)

    all_errors: dict[str, list[str]] = {}
    healthy_count = 0

    for project in projects:
        errs = check_project(workspace_root, project)
        if errs:
            all_errors[project["name"]] = errs
        else:
            healthy_count += 1

    print(f"--- Silo Health Report ({healthy_count}/{len(projects)} healthy) ---")
    if all_errors:
        for name, errs in all_errors.items():
            print(f"\n[!] Project: {name}")
            for err in errs:
                print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nAll systems green.")
        sys.exit(0)


if __name__ == "__main__":
    main()
