# Obsidian Vault Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace `artifacts/` with a fully Obsidian-native `knowledge-vault/` at the project root, updating all CVR tools to read/write the new paths and note formats.

**Architecture:** Four ordered phases — scaffold vault, migrate existing data, update CVR tools, then clean up references and delete `artifacts/`. All Phase 3 and 4 work requires maintenance mode (`.claude/skills/**` and `tools/cvr/**` are off-limits otherwise).

**Tech Stack:** Python 3, Obsidian (Dataview + Calendar plugins), YAML frontmatter, existing CVR toolchain.

---

> **MAINTENANCE MODE REQUIRED** for Tasks 4–15. Operator must grant maintenance mode before starting Task 4.

---

## Phase 1: Scaffold the Vault

### Task 1: Create vault directory structure

**Files:**
- Create: `knowledge-vault/Intent/.gitkeep`
- Create: `knowledge-vault/Runs/.gitkeep`
- Create: `knowledge-vault/Journal/.gitkeep`
- Create: `knowledge-vault/Activity/.gitkeep`
- Create: `knowledge-vault/History/.gitkeep`
- Create: `knowledge-vault/Lessons/.gitkeep`
- Create: `knowledge-vault/Cursed Knowledge/.gitkeep`
- Create: `knowledge-vault/Deep Thoughts/.gitkeep`
- Create: `knowledge-vault/Logs/.gitkeep`
- Create: `knowledge-vault/Logs/test_results/.gitkeep`
- Create: `knowledge-vault/Logs/diffs/.gitkeep`

**Step 1: Create all vault subdirectories**

```bash
mkdir -p knowledge-vault/{Intent,Runs,Journal,Activity,History,Lessons,Logs} \
  "knowledge-vault/Cursed Knowledge" \
  "knowledge-vault/Deep Thoughts" \
  knowledge-vault/Logs/test_results \
  knowledge-vault/Logs/diffs
```

**Step 2: Add gitkeep files**

```bash
find knowledge-vault -type d -exec touch {}/.gitkeep \;
```

**Step 3: Create stub `History/history.md` with Dataview block**

Create `knowledge-vault/History/history.md`:

````markdown
---
type: history-index
tags: [history]
---

# Run History

```dataview
TABLE run_id, status, date FROM "Runs" SORT date DESC
```
````

**Step 4: Create stub `Lessons/lessons-learned.md`**

```markdown
---
type: lessons
tags: [lessons]
---

# Lessons Learned
```

**Step 5: Verify structure**

```bash
find knowledge-vault -type f | sort
```

Expected: all directories present with `.gitkeep` and two stub markdown files.

**Step 6: Commit**

```bash
git add knowledge-vault/
git commit -m "feat(vault): scaffold knowledge-vault directory structure"
```

---

### Task 2: Commit `.obsidian/` configuration

**Files:**
- Create: `knowledge-vault/.obsidian/app.json`
- Create: `knowledge-vault/.obsidian/community-plugins.json`
- Create: `knowledge-vault/.obsidian/core-plugins.json`
- Create: `knowledge-vault/.obsidian/plugins/obsidian-dataview/manifest.json`
- Create: `knowledge-vault/.obsidian/plugins/calendar/manifest.json`

**Step 1: Create `.obsidian/app.json`**

```json
{
  "userIgnoreFilters": [],
  "newFileLocation": "current",
  "newFileFolderPath": "",
  "attachmentFolderPath": "Logs",
  "showUnsupportedFiles": false
}
```

**Step 2: Create `.obsidian/community-plugins.json`**

```json
["obsidian-dataview", "calendar"]
```

**Step 3: Create `.obsidian/core-plugins.json`**

```json
{
  "file-explorer": true,
  "global-search": true,
  "tags": true,
  "page-preview": true,
  "daily-notes": true,
  "graph": true,
  "backlink": true,
  "outgoing-link": true,
  "outline": true
}
```

**Step 4: Create Dataview plugin manifest**

`knowledge-vault/.obsidian/plugins/obsidian-dataview/manifest.json`:

```json
{
  "id": "obsidian-dataview",
  "name": "Dataview",
  "version": "0.5.67",
  "minAppVersion": "0.15.0",
  "description": "Complex data views for the connected workspace.",
  "author": "Michael Brenan",
  "authorUrl": "https://github.com/blacksmithgu",
  "isDesktopOnly": false
}
```

**Step 5: Create Calendar plugin manifest**

`knowledge-vault/.obsidian/plugins/calendar/manifest.json`:

```json
{
  "id": "calendar",
  "name": "Calendar",
  "version": "1.5.10",
  "minAppVersion": "0.9.11",
  "description": "Simple calendar widget for Obsidian.",
  "author": "Liam Cain",
  "authorUrl": "https://github.com/liamcain",
  "isDesktopOnly": false
}
```

**Step 6: Commit**

```bash
git add knowledge-vault/.obsidian/
git commit -m "feat(vault): add committed .obsidian config with Dataview and Calendar"
```

---

## Phase 2: Migrate Existing Artifacts

### Task 3: Write and run migration script

**Files:**
- Create: `tools/migrate_to_vault.py`

This is a one-shot migration script. It reads from `artifacts/` and writes Obsidian-formatted files to `knowledge-vault/`.

**Step 1: Write `tools/migrate_to_vault.py`**

```python
#!/usr/bin/env python3
"""One-shot migration script: artifacts/ -> knowledge-vault/

Run from repo root:
    python3 tools/migrate_to_vault.py
"""
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OLD = ROOT / "artifacts"
NEW = ROOT / "knowledge-vault"


def add_frontmatter(content: str, frontmatter: dict) -> str:
    """Prepend YAML frontmatter to markdown content."""
    lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, str):
            lines.append(f"{k}: {v!r}")
        elif isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v)}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n" + content


def migrate_intent():
    src = OLD / "intent" / "project_intent.md"
    dst = NEW / "Intent" / "project_intent.md"
    if not src.exists():
        print("  [skip] No intent file found")
        return
    content = src.read_text(encoding="utf-8")
    fm = {"type": "intent", "tags": '["intent"]'}
    dst.write_text(add_frontmatter(content, fm), encoding="utf-8")
    print(f"  [ok] Intent -> {dst.relative_to(ROOT)}")


def migrate_runs():
    runs_src = OLD / "history" / "runs"
    runs_dst = NEW / "Runs"
    if not runs_src.exists():
        print("  [skip] No runs directory")
        return
    for run_dir in sorted(p for p in runs_src.iterdir() if p.is_dir()):
        dst_run = runs_dst / run_dir.name
        dst_run.mkdir(parents=True, exist_ok=True)
        for f in run_dir.iterdir():
            if f.is_dir():
                shutil.copytree(f, dst_run / f.name, dirs_exist_ok=True)
            elif f.suffix == ".md" and f.name == "implementation_plan.md":
                content = f.read_text(encoding="utf-8")
                fm = {
                    "type": "run",
                    "run_id": run_dir.name,
                    "status": "complete",
                    "intent": '"[[Intent/project_intent]]"',
                    "tags": '["run"]',
                }
                (dst_run / f.name).write_text(add_frontmatter(content, fm), encoding="utf-8")
            else:
                shutil.copy2(f, dst_run / f.name)
        print(f"  [ok] Run {run_dir.name} -> {dst_run.relative_to(ROOT)}")


def migrate_journals():
    journal_src = OLD / "journal"
    journal_dst = NEW / "Journal"
    if not journal_src.exists():
        print("  [skip] No journal directory")
        return
    for md in sorted(journal_src.glob("*.md")):
        run_id = md.stem
        content = md.read_text(encoding="utf-8")
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", run_id)
        date = date_match.group(1) if date_match else "unknown"
        fm = {
            "type": "journal",
            "run_id": run_id,
            "run": f'"[[Runs/{run_id}/implementation_plan]]"',
            "date": date,
            "tags": '["journal"]',
        }
        dst = journal_dst / md.name
        dst.write_text(add_frontmatter(content, fm), encoding="utf-8")
        print(f"  [ok] Journal {md.name} -> {dst.relative_to(ROOT)}")


def migrate_lessons():
    src = OLD / "history" / "lessons-learned.md"
    dst = NEW / "Lessons" / "lessons-learned.md"
    if not src.exists():
        print("  [skip] No lessons-learned.md")
        return
    content = src.read_text(encoding="utf-8")
    fm = {"type": "lessons", "tags": '["lessons"]'}
    dst.write_text(add_frontmatter(content, fm), encoding="utf-8")
    print(f"  [ok] Lessons -> {dst.relative_to(ROOT)}")


def migrate_deep_thoughts():
    """Convert existing deep-thoughts.md into individual notes."""
    src = OLD / "history" / "deep-thoughts.md"
    dst_dir = NEW / "Deep Thoughts"
    if not src.exists():
        print("  [skip] No deep-thoughts.md")
        return
    content = src.read_text(encoding="utf-8")
    # Write as a single note (pre-migration archive)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fm = {
        "type": "deep-thought",
        "date": today,
        "tags": '["deep-thought"]',
    }
    dst = dst_dir / "archive-pre-migration.md"
    dst.write_text(add_frontmatter(content, fm), encoding="utf-8")
    print(f"  [ok] Deep Thoughts archive -> {dst.relative_to(ROOT)}")


def migrate_activity_log():
    """Convert agent_activity.jsonl to daily Activity notes."""
    src = OLD / "agent_activity.jsonl"
    if not src.exists():
        print("  [skip] No agent_activity.jsonl")
        return

    # Group entries by date
    by_date: dict = {}
    for line in src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = entry.get("ts", "")
        date = ts[:10] if ts else "unknown"
        by_date.setdefault(date, []).append(entry)

    dst_dir = NEW / "Activity"
    for date, entries in sorted(by_date.items()):
        dst = dst_dir / f"{date}.md"
        fm = {"type": "activity", "date": date, "tags": '["activity", "daily"]'}
        rows = ["| Time | Actor | Intent | Scope | Action | Result |",
                "|------|-------|--------|-------|--------|--------|"]
        for e in entries:
            time = e.get("ts", "")[-9:-4] if e.get("ts") else ""
            rows.append(
                f"| {time} | {e.get('actor','')} | {e.get('intent','')} "
                f"| {e.get('scope','')} | {e.get('action','')} | {e.get('result','')} |"
            )
        table = "\n".join(rows)
        dst.write_text(add_frontmatter(table + "\n", fm), encoding="utf-8")
        print(f"  [ok] Activity {date} -> {dst.relative_to(ROOT)}")


def migrate_logs():
    logs_src = OLD / "logs"
    logs_dst = NEW / "Logs"
    if not logs_src.exists():
        print("  [skip] No logs directory")
        return
    for f in logs_src.iterdir():
        if f.name == ".gitkeep":
            continue
        dst = logs_dst / f.name
        shutil.copy2(f, dst)
        print(f"  [ok] Log {f.name} -> {dst.relative_to(ROOT)}")


def migrate_test_results():
    src = OLD / "test_results"
    dst = NEW / "Logs" / "test_results"
    if not src.exists():
        print("  [skip] No test_results directory")
        return
    for f in src.iterdir():
        if f.name == ".gitkeep":
            continue
        shutil.copy2(f, dst / f.name)
        print(f"  [ok] TestResult {f.name} -> {(dst / f.name).relative_to(ROOT)}")


def migrate_diffs():
    src = OLD / "diffs"
    dst = NEW / "Logs" / "diffs"
    if not src.exists():
        print("  [skip] No diffs directory")
        return
    for f in src.iterdir():
        if f.name == ".gitkeep":
            continue
        shutil.copy2(f, dst / f.name)
        print(f"  [ok] Diff {f.name} -> {(dst / f.name).relative_to(ROOT)}")


def main():
    print("=== Migrating artifacts/ -> knowledge-vault/ ===")
    migrate_intent()
    migrate_activity_log()
    migrate_runs()
    migrate_journals()
    migrate_lessons()
    migrate_deep_thoughts()
    migrate_logs()
    migrate_test_results()
    migrate_diffs()
    print("=== Migration complete ===")
    print("Review knowledge-vault/, then delete artifacts/ in Phase 4.")


if __name__ == "__main__":
    main()
```

**Step 2: Run the migration**

```bash
python3 tools/migrate_to_vault.py
```

Expected: each artifact reported as `[ok]` or `[skip]`.

**Step 3: Verify key files exist**

```bash
ls knowledge-vault/Intent/
ls knowledge-vault/Activity/
ls knowledge-vault/Logs/
```

**Step 4: Commit**

```bash
git add knowledge-vault/
git add tools/migrate_to_vault.py
git commit -m "feat(vault): migrate existing artifacts to knowledge-vault with Obsidian frontmatter"
```

---

## Phase 3: Update CVR Tools

> All tasks in this phase require maintenance mode. Confirm `artifacts/logs/agent_mode.json` shows `"mode": "maintenance"` before proceeding.

### Task 4: Update `tools/cvr/paths.py`

**Files:**
- Modify: `tools/cvr/paths.py`

This is the central change — everything else depends on it.

**Step 1: Replace the full contents of `tools/cvr/paths.py`**

```python
#!/usr/bin/env python3
"""Canonical artifact paths for the ADK Verification Runtime.

This module defines the single source of truth for all artifact paths.
All Python scripts SHOULD import from this module rather than hardcoding paths.
"""

from pathlib import Path

# Root directories
VAULT_ROOT = Path("knowledge-vault")

# Intent
INTENT_DIR = VAULT_ROOT / "Intent"
PROJECT_INTENT = INTENT_DIR / "project_intent.md"

# Runs
RUNS_DIR = VAULT_ROOT / "Runs"

# Journal
JOURNAL_DIR = VAULT_ROOT / "Journal"

# Activity (daily notes - replaces agent_activity.jsonl)
ACTIVITY_DIR = VAULT_ROOT / "Activity"

# History
HISTORY_DIR = VAULT_ROOT / "History"
HISTORY_NDJSON = HISTORY_DIR / "history.ndjson"
HISTORY_MD = HISTORY_DIR / "history.md"

# Lessons
LESSONS_DIR = VAULT_ROOT / "Lessons"
LESSONS_LEARNED = LESSONS_DIR / "lessons-learned.md"

# Cursed Knowledge
CURSED_KNOWLEDGE_DIR = VAULT_ROOT / "Cursed Knowledge"

# Deep Thoughts
DEEP_THOUGHTS_DIR = VAULT_ROOT / "Deep Thoughts"

# Logs
LOGS_DIR = VAULT_ROOT / "Logs"
AGENT_MODE_FILE = LOGS_DIR / "agent_mode.json"
CONTEXT_MANIFEST = LOGS_DIR / "context_manifest.md"
POST_VERIFY_REPORT = LOGS_DIR / "post_verify_report.md"
AGENDA_STATE = HISTORY_DIR / "agenda_state.json"

# Evidence directories
DIFFS_DIR = LOGS_DIR / "diffs"
TEST_RESULTS_DIR = LOGS_DIR / "test_results"
```

**Step 2: Verify Python import works**

```bash
python3 -c "from tools.cvr import paths; print(paths.VAULT_ROOT, paths.RUNS_DIR)"
```

Expected output:
```
knowledge-vault knowledge-vault/Runs
```

**Step 3: Commit**

```bash
git add tools/cvr/paths.py
git commit -m "feat(cvr): repoint all paths to knowledge-vault/ in paths.py"
```

---

### Task 5: Update `tools/cvr/log_action.py`

**Files:**
- Modify: `tools/cvr/log_action.py`

Replace JSONL append with daily-note writer. Each call appends a table row to `knowledge-vault/Activity/YYYY-MM-DD.md`, creating the note with frontmatter + table header if it doesn't exist.

**Step 1: Write the test first**

Create `tests/cvr/test_log_action.py`:

```python
#!/usr/bin/env python3
"""Tests for log_action.py daily-note writer."""
import sys
import json
import tempfile
from pathlib import Path
from datetime import date

# Point paths module at temp vault
import importlib

def make_temp_vault(tmp_path):
    activity_dir = tmp_path / "knowledge-vault" / "Activity"
    activity_dir.mkdir(parents=True)
    logs_dir = tmp_path / "knowledge-vault" / "Logs"
    logs_dir.mkdir(parents=True)
    return activity_dir, logs_dir


def test_creates_daily_note_on_first_call(tmp_path, monkeypatch):
    activity_dir, logs_dir = make_temp_vault(tmp_path)
    monkeypatch.chdir(tmp_path)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.cvr import log_action

    today = date.today().isoformat()
    log_action.append_entry("test-intent", "test-action", scope="test", result="ok")

    daily = activity_dir / f"{today}.md"
    assert daily.exists(), "Daily note should be created"
    content = daily.read_text()
    assert "type: activity" in content
    assert "| Time |" in content
    assert "test-intent" in content


def test_appends_row_to_existing_note(tmp_path, monkeypatch):
    activity_dir, logs_dir = make_temp_vault(tmp_path)
    monkeypatch.chdir(tmp_path)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.cvr import log_action

    log_action.append_entry("intent-1", "action-1")
    log_action.append_entry("intent-2", "action-2")

    today = date.today().isoformat()
    daily = activity_dir / f"{today}.md"
    content = daily.read_text()
    assert content.count("intent-1") == 1
    assert content.count("intent-2") == 1
    # Header should appear only once
    assert content.count("| Time |") == 1
```

**Step 2: Run test to confirm it fails**

```bash
python3 -m pytest tests/cvr/test_log_action.py -v
```

Expected: FAIL (log_action still writes JSONL).

**Step 3: Rewrite `tools/cvr/log_action.py`**

```python
#!/usr/bin/env python3
"""
log_action.py - Append an event to the daily Activity note.

Usage:
  python3 tools/cvr/log_action.py --intent <intent> --action <action> \
    [--scope <scope>] [--result <result>] [--evidence <file>...]

Each call appends one table row to knowledge-vault/Activity/YYYY-MM-DD.md.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.cvr import paths

MODE_FILE = paths.AGENT_MODE_FILE
ACTIVITY_DIR = paths.ACTIVITY_DIR

FRONTMATTER_TEMPLATE = """\
---
type: activity
date: {date}
tags: ["activity", "daily"]
---

| Time | Actor | Intent | Scope | Action | Result |
|------|-------|--------|-------|--------|--------|
"""


def get_current_mode() -> str:
    try:
        if MODE_FILE.exists():
            data = json.loads(MODE_FILE.read_text())
            return data.get("mode", "normal")
    except Exception:
        pass
    return "normal"


def get_actor() -> str:
    return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))


def append_entry(
    intent: str,
    action: str,
    scope: str = "workspace",
    result: str = "ok",
    evidence=None,
    metadata=None,
) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    ACTIVITY_DIR.mkdir(parents=True, exist_ok=True)
    daily_note = ACTIVITY_DIR / f"{today}.md"

    if not daily_note.exists():
        daily_note.write_text(
            FRONTMATTER_TEMPLATE.format(date=today), encoding="utf-8"
        )

    row = (
        f"| {time_str} | {get_actor()} | {intent} "
        f"| {scope} | {action} | {result} |\n"
    )
    with open(daily_note, "a", encoding="utf-8") as f:
        f.write(row)

    print(f"Logged '{action}' for '{intent}' to {daily_note}")


def main():
    parser = argparse.ArgumentParser(description="Log an action to the daily activity note.")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--scope", default="workspace")
    parser.add_argument("--result", default="ok")
    parser.add_argument("--evidence", nargs="*")
    parser.add_argument("--metadata")

    args = parser.parse_args()
    try:
        append_entry(
            intent=args.intent,
            action=args.action,
            scope=args.scope,
            result=args.result,
            evidence=args.evidence,
            metadata=args.metadata,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to confirm pass**

```bash
python3 -m pytest tests/cvr/test_log_action.py -v
```

Expected: PASS.

**Step 5: Smoke test**

```bash
python3 tools/cvr/log_action.py --intent "vault-migration" --action "test" --scope "cvr" --result "ok"
cat "knowledge-vault/Activity/$(date +%Y-%m-%d).md"
```

Expected: Daily note created with a table row.

**Step 6: Commit**

```bash
git add tools/cvr/log_action.py tests/cvr/test_log_action.py
git commit -m "feat(cvr): rewrite log_action.py to write daily Activity notes in knowledge-vault"
```

---

### Task 6: Update `tools/cvr/journal.py`

**Files:**
- Modify: `tools/cvr/journal.py`

Add Obsidian frontmatter and wikilinks to the emitted journal note. Output path remains `JOURNAL_DIR/{run_id}.md` (now `knowledge-vault/Journal/{run_id}.md`).

**Step 1: Update `emit_journal` in `tools/cvr/journal.py`**

In the `emit_journal` function, change the `content` construction to prepend frontmatter:

```python
def emit_journal(run_dir: Path) -> Optional[Path]:
    run_id = run_dir.name

    # 1. Gather context
    plan_summary = load_plan_summary(run_dir)
    outcome = load_outcome(run_dir)
    lessons = extract_lessons(run_dir / "walkthrough.md")

    # 2. Generate narrative body
    body = generate_narrative(run_id, plan_summary, outcome, lessons)

    # 3. Extract date from run_id
    import re as _re
    date_match = _re.search(r"(\d{4}-\d{2}-\d{2})", run_id)
    date_str = date_match.group(1) if date_match else "unknown"

    # 4. Build frontmatter
    frontmatter = f"""\
---
type: journal
run_id: {run_id}
run: "[[Runs/{run_id}/implementation_plan]]"
intent: "[[Intent/project_intent]]"
date: {date_str}
tags: ["journal"]
---

"""

    # 5. Format artifact
    content = f"{frontmatter}{HEADER}\n*(reconstructed)*\n\n{body}\n\n---\n\n{DISCLAIMER}\n"

    # 6. Write
    journal_dir = paths.JOURNAL_DIR
    journal_dir.mkdir(parents=True, exist_ok=True)

    out_path = journal_dir / f"{run_id}.md"
    try:
        out_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        die(f"failed to write {out_path}: {exc}")
        return None

    note(f"wrote journal to {out_path}")
    return out_path
```

**Step 2: Verify output manually**

```bash
# If any run dirs exist in knowledge-vault/Runs/:
python3 tools/cvr/journal.py
cat knowledge-vault/Journal/*.md | head -20
```

Expected: frontmatter block at top with `type: journal`, `run_id`, `run:` wikilink.

**Step 3: Commit**

```bash
git add tools/cvr/journal.py
git commit -m "feat(cvr): add Obsidian frontmatter and wikilinks to journal.py output"
```

---

### Task 7: Update `tools/cvr/close_run.py`

**Files:**
- Modify: `tools/cvr/close_run.py`

The only required change is the evidence pointer in `update_global_lessons` — the relative path calculation must reference `knowledge-vault/Runs/` instead of `artifacts/history/runs/`. The `paths.LESSONS_LEARNED` constant is already updated via `paths.py`.

**Step 1: Fix evidence pointer in `update_global_lessons`**

Find this line in `close_run.py`:

```python
new_entries.append(f"\n**Evidence**: from [{run_name}](runs/{run_name}/walkthrough.md)\n")
```

Replace with:

```python
new_entries.append(f"\n**Evidence**: from [{run_name}](../Runs/{run_name}/walkthrough.md)\n")
```

**Step 2: Smoke test**

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from tools.cvr.close_run import update_global_lessons
update_global_lessons(['test lesson'], 'test-run-id')
cat_cmd = 'cat knowledge-vault/Lessons/lessons-learned.md'
import subprocess; subprocess.run(cat_cmd.split())
"
```

Expected: lessons-learned.md updated with correct relative evidence pointer.

**Step 3: Commit**

```bash
git add tools/cvr/close_run.py
git commit -m "fix(cvr): update evidence pointer in close_run.py for knowledge-vault layout"
```

---

### Task 8: Update `tools/cvr/compile_timeline.py`

**Files:**
- Modify: `tools/cvr/compile_timeline.py`

Currently produces one aggregated `deep-thoughts.md`. Replace with per-run individual notes in `knowledge-vault/Deep Thoughts/`.

**Step 1: Rewrite `tools/cvr/compile_timeline.py`**

```python
#!/usr/bin/env python3
"""Compile per-run Deep Thoughts notes from journals.

For each journal in knowledge-vault/Journal/, emits an individual
note to knowledge-vault/Deep Thoughts/<run-id>.md.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.cvr import paths


def parse_journal_date(journal_path: Path) -> str:
    name = journal_path.stem
    match = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return match.group(1) if match else "unknown"


def make_deep_thought(run_id: str, date_str: str, journal_content: str) -> str:
    # Extract summary (first non-empty line after header)
    lines = journal_content.splitlines()
    summary = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---") and not stripped.startswith("type:"):
            summary = stripped
            break

    frontmatter = f"""\
---
type: deep-thought
run_id: {run_id}
date: {date_str}
run: "[[Runs/{run_id}/implementation_plan]]"
journal: "[[Journal/{run_id}]]"
tags: ["deep-thought"]
---

"""
    body = f"# Deep Thought: {run_id}\n\n{journal_content.strip()}\n"
    return frontmatter + body


def main():
    journal_dir = paths.JOURNAL_DIR
    deep_thoughts_dir = paths.DEEP_THOUGHTS_DIR

    if not journal_dir.exists():
        print(f"No journals found at {journal_dir}")
        return

    deep_thoughts_dir.mkdir(parents=True, exist_ok=True)

    for journal_path in sorted(journal_dir.glob("*.md")):
        run_id = journal_path.stem
        date_str = parse_journal_date(journal_path)
        content = journal_path.read_text(encoding="utf-8")

        out_path = deep_thoughts_dir / f"{run_id}.md"
        out_path.write_text(make_deep_thought(run_id, date_str, content), encoding="utf-8")
        print(f"  [ok] Deep Thought: {out_path.relative_to(Path.cwd())}")

    print("Deep Thoughts compiled.")


if __name__ == "__main__":
    main()
```

**Step 2: Verify**

```bash
python3 tools/cvr/compile_timeline.py
ls "knowledge-vault/Deep Thoughts/"
```

**Step 3: Commit**

```bash
git add tools/cvr/compile_timeline.py
git commit -m "feat(cvr): rewrite compile_timeline.py to emit per-run Deep Thought notes"
```

---

### Task 9: Update `tools/cvr/aggregate_history.py`

**Files:**
- Modify: `tools/cvr/aggregate_history.py`

Two changes:
1. Fix hardcoded `artifacts/journal` path in `collect_journal_entries` (line 347) → use `paths.JOURNAL_DIR`
2. Change `history.md` output from a static table to a Dataview query block

**Step 1: Fix hardcoded journal path**

Find in `collect_journal_entries`:
```python
journal_dir = repo_root / "artifacts/journal"
```

Replace with:
```python
journal_dir = paths.JOURNAL_DIR
```

**Step 2: Replace static `history.md` generation with Dataview block**

Find the block that builds `history_lines` (starting around line 451) and the write at the end. Replace the `history_md_text` construction with:

```python
history_md_text = """\
---
type: history-index
tags: ["history"]
---

# Run History

```dataview
TABLE run_id, status, date FROM "Runs" SORT date DESC
```
"""
```

Remove the loop over `runs_seen` that builds the static table rows — `history.md` is now Dataview-driven.

**Step 3: Update `--narrative` default to write into Deep Thoughts dir**

The `--narrative` arg defaults to `DEEP_THOUGHTS_PATH`. Update:

```python
# At top of file, replace:
DEEP_THOUGHTS_PATH = paths.DEEP_THOUGHTS

# With:
DEEP_THOUGHTS_PATH = paths.DEEP_THOUGHTS_DIR / "aggregate.md"
```

**Step 4: Smoke test**

```bash
python3 tools/cvr/aggregate_history.py
cat knowledge-vault/History/history.md
```

Expected: Dataview block only, no static rows.

**Step 5: Commit**

```bash
git add tools/cvr/aggregate_history.py
git commit -m "fix(cvr): fix hardcoded journal path and emit Dataview history.md in aggregate_history"
```

---

### Task 10: Update `tools/cvr/generate_context_manifest.py`

**Files:**
- Modify: `tools/cvr/generate_context_manifest.py`

The output path is already driven by `paths.CONTEXT_MANIFEST` (which now resolves to `knowledge-vault/Logs/context_manifest.md`). Add Obsidian frontmatter to the generated manifest.

**Step 1: Add frontmatter to manifest output**

In the `main()` function, change the file write to prepend frontmatter:

```python
with open(output_file, "w") as f:
    # Obsidian frontmatter
    f.write("---\n")
    f.write("type: context-manifest\n")
    f.write(f"timestamp: {timestamp}\n")
    f.write('tags: ["logs", "context"]\n')
    f.write("---\n\n")
    # Existing content follows
    f.write("# Context Manifest\n\n")
    f.write(f"- timestamp: {timestamp}\n")
    # ... rest unchanged
```

**Step 2: Smoke test**

```bash
python3 tools/cvr/generate_context_manifest.py
head -10 knowledge-vault/Logs/context_manifest.md
```

Expected: YAML frontmatter block at top.

**Step 3: Commit**

```bash
git add tools/cvr/generate_context_manifest.py
git commit -m "feat(cvr): add Obsidian frontmatter to context_manifest output"
```

---

### Task 11: Update all linters

**Files:**
- Modify: `tools/cvr/linters/evidence_location_lint.py`
- Modify: `tools/cvr/linters/history_lint.py`
- Modify: `tools/cvr/linters/intent_lint.py`
- Modify: `tools/cvr/linters/journal_lint.py`
- Modify: `tools/cvr/linters/agenda_lint.py`
- Modify: `tools/cvr/linters/lessons_lint.py`
- Modify: `tools/cvr/linters/plan_lint.py`
- Modify: `tools/cvr/linters/run_artifacts_lint.py`
- Modify: `tools/cvr/linters/template_baseline_lint.py`
- Modify: `tools/cvr/linters/walkthrough_lint.py`
- Modify: `tools/cvr/linters/workflow_intent_lint.py`
- Modify: `tools/cvr/linters/context_manifest_lint.py`
- Modify: `tools/cvr/linters/post_verify_lint.py`
- Modify: `tools/cvr/linters/post_verify_agenda_lint.py`
- Modify: `tools/cvr/linters/content_lint.py`

**Step 1: For each linter, audit for hardcoded `artifacts/` path strings**

```bash
grep -rn "artifacts" tools/cvr/linters/ --include="*.py"
```

**Step 2: For each match, replace with the equivalent `paths.*` constant**

Common substitutions:

| Hardcoded string | Replace with |
|---|---|
| `"artifacts/intent/project_intent.md"` | `str(paths.PROJECT_INTENT)` |
| `"artifacts/history/runs"` | `str(paths.RUNS_DIR)` |
| `"artifacts/journal"` | `str(paths.JOURNAL_DIR)` |
| `"artifacts/logs/context_manifest.md"` | `str(paths.CONTEXT_MANIFEST)` |
| `"artifacts/history/lessons-learned.md"` | `str(paths.LESSONS_LEARNED)` |
| `Path("artifacts/...")` | `paths.<CONSTANT>` |

Each linter already does `sys.path.insert(0, ...)` and imports — add `from tools.cvr import paths` where missing.

**Step 3: Run linter suite**

```bash
tools/verify_all.sh 2>&1 | head -60
```

Expected: linter errors only about missing files (since runs/journals are empty), not about path resolution failures.

**Step 4: Commit**

```bash
git add tools/cvr/linters/
git commit -m "fix(cvr/linters): replace hardcoded artifacts/ paths with paths module constants"
```

---

### Task 12: Create `tools/cvr/add_note.py`

**Files:**
- Create: `tools/cvr/add_note.py`

Agent-callable script for creating Cursed Knowledge and Deep Thought notes.

**Step 1: Write failing test first**

Create `tests/cvr/test_add_note.py`:

```python
#!/usr/bin/env python3
"""Tests for add_note.py."""
import sys
from pathlib import Path

def test_creates_cursed_knowledge_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Cursed Knowledge").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Deep Thoughts").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Runs").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.cvr import add_note

    path = add_note.create_note(
        note_type="cursed-knowledge",
        title="Never use rm -rf /",
        run_id="2026-03-08-10-00-00",
    )
    assert path.exists()
    content = path.read_text()
    assert "type: cursed-knowledge" in content
    assert "Never use rm -rf /" in content
    assert "[[Runs/2026-03-08-10-00-00/implementation_plan]]" in content


def test_creates_deep_thought_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Cursed Knowledge").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Deep Thoughts").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.cvr import add_note

    path = add_note.create_note(
        note_type="deep-thought",
        title="On the nature of linting",
        run_id=None,
    )
    assert path.exists()
    content = path.read_text()
    assert "type: deep-thought" in content
    assert "On the nature of linting" in content
```

**Step 2: Run to confirm fails**

```bash
python3 -m pytest tests/cvr/test_add_note.py -v
```

Expected: FAIL (module doesn't exist yet).

**Step 3: Write `tools/cvr/add_note.py`**

```python
#!/usr/bin/env python3
"""add_note.py - Create a Cursed Knowledge or Deep Thought note.

Usage:
  python3 tools/cvr/add_note.py --type cursed-knowledge --title "Never do X" [--run-id <run-id>]
  python3 tools/cvr/add_note.py --type deep-thought --title "On linting" [--run-id <run-id>]
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.cvr import paths

NOTE_DIRS = {
    "cursed-knowledge": paths.CURSED_KNOWLEDGE_DIR,
    "deep-thought": paths.DEEP_THOUGHTS_DIR,
}


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug[:60]


def create_note(note_type: str, title: str, run_id: str = None, body: str = "") -> Path:
    if note_type not in NOTE_DIRS:
        raise ValueError(f"Unknown note type: {note_type}. Must be one of {list(NOTE_DIRS)}")

    note_dir = NOTE_DIRS[note_type]
    note_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    slug = slugify(title)
    filename = f"{today}-{slug}.md"
    out_path = note_dir / filename

    run_link = f'"[[Runs/{run_id}/implementation_plan]]"' if run_id else '""'

    frontmatter = f"""\
---
type: {note_type}
title: "{title}"
date: {today}
run: {run_link}
tags: ["{note_type}"]
---

"""
    content = frontmatter + f"# {title}\n\n{body}\n"
    out_path.write_text(content, encoding="utf-8")
    print(f"Created {note_type} note: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Create a Cursed Knowledge or Deep Thought note.")
    parser.add_argument("--type", required=True, choices=["cursed-knowledge", "deep-thought"])
    parser.add_argument("--title", required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--body", default="", help="Optional initial body text")
    args = parser.parse_args()

    try:
        create_note(
            note_type=args.type,
            title=args.title,
            run_id=args.run_id,
            body=args.body,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to confirm pass**

```bash
python3 -m pytest tests/cvr/test_add_note.py -v
```

Expected: PASS.

**Step 5: Smoke test**

```bash
python3 tools/cvr/add_note.py --type cursed-knowledge --title "Never hardcode paths in linters"
python3 tools/cvr/add_note.py --type deep-thought --title "On the nature of linting"
ls "knowledge-vault/Cursed Knowledge/"
ls "knowledge-vault/Deep Thoughts/"
```

**Step 6: Commit**

```bash
git add tools/cvr/add_note.py tests/cvr/test_add_note.py
git commit -m "feat(cvr): add add_note.py for creating Cursed Knowledge and Deep Thought notes"
```

---

## Phase 4: Update References and Clean Up

### Task 13: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

Update the Artifact Directory Structure section to reflect `knowledge-vault/`.

**Step 1: Replace the artifact directory block**

Find the fenced code block under `## Artifact Directory Structure (Canonical)` and replace it:

```
knowledge-vault/
├── .obsidian/               ← committed Obsidian config
├── Intent/
│   └── project_intent.md
├── Runs/
│   └── <run-id>/
│       ├── implementation_plan.md
│       ├── implementation_plan.json
│       └── walkthrough.md
├── Journal/
│   └── <run-id>.md
├── Activity/
│   └── YYYY-MM-DD.md        ← daily note; agent ledger as markdown table
├── History/
│   ├── history.md           ← Dataview query over all Runs
│   └── history.ndjson
├── Lessons/
│   └── lessons-learned.md
├── Cursed Knowledge/
│   └── YYYY-MM-DD-<slug>.md
├── Deep Thoughts/
│   └── YYYY-MM-DD-<slug>.md
└── Logs/
    ├── context_manifest.md
    ├── post_verify_report.md
    ├── agent_mode.json
    ├── test_results/
    └── diffs/
```

**Step 2: Update the Agent Activity Ledger section**

Replace path `artifacts/agent_activity.jsonl` with:

> **Path**: `knowledge-vault/Activity/YYYY-MM-DD.md` (daily note)
> **Format**: Markdown table (one row per entry)
> **Time**: UTC (RFC3339)

**Step 3: Update the off-limits paths section**

The off-limits paths do not change — `tools/cvr/**` and `.claude/skills/**` remain off-limits.

**Step 4: Update AGENDA.md format section** (if it references `artifacts/`)

Search for `artifacts/` in CLAUDE.md and update any remaining references.

**Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md artifact directory structure for knowledge-vault migration"
```

---

### Task 14: Update skill SKILL.md files

**Files:**
- Modify: `.claude/skills/adk-prep-context/SKILL.md`
- Modify: `.claude/skills/adk-verify-agenda/SKILL.md`
- Modify: `.claude/skills/adk-plan-execution/SKILL.md`
- Modify: `.claude/skills/adk-execute-plan/SKILL.md`
- Modify: `.claude/skills/adk-post-verify/SKILL.md`
- Modify: `.claude/skills/adk-post-execution-review/SKILL.md`
- Modify: `.claude/skills/adk-toggle-maintenance-mode/SKILL.md`
- Modify: `.claude/skills/adk-finish/SKILL.md`
- Modify: `.claude/skills/adk-commit-message/SKILL.md`

**Step 1: Audit all skill files for artifacts/ references**

```bash
grep -rn "artifacts/" .claude/skills/ --include="*.md"
```

**Step 2: For each match, update the path**

Common substitutions in skill files:

| Old reference | New reference |
|---|---|
| `artifacts/intent/project_intent.md` | `knowledge-vault/Intent/project_intent.md` |
| `artifacts/logs/context_manifest.md` | `knowledge-vault/Logs/context_manifest.md` |
| `artifacts/logs/post_verify_report.md` | `knowledge-vault/Logs/post_verify_report.md` |
| `artifacts/logs/agent_mode.json` | `knowledge-vault/Logs/agent_mode.json` |
| `artifacts/history/runs/<run-id>/` | `knowledge-vault/Runs/<run-id>/` |
| `artifacts/journal/<run-id>.md` | `knowledge-vault/Journal/<run-id>.md` |
| `artifacts/history/lessons-learned.md` | `knowledge-vault/Lessons/lessons-learned.md` |
| `artifacts/agent_activity.jsonl` | `knowledge-vault/Activity/YYYY-MM-DD.md` |

**Step 3: Verify no remaining references**

```bash
grep -rn "artifacts/" .claude/skills/ --include="*.md"
```

Expected: no output.

**Step 4: Commit**

```bash
git add .claude/skills/
git commit -m "feat(skills): update all artifact path references to knowledge-vault layout"
```

---

### Task 15: Verify clean pass and delete `artifacts/`

**Step 1: Run full verification**

```bash
tools/verify_all.sh 2>&1 | tee knowledge-vault/Logs/vault-migration-verify.log
```

Expected: clean pass (or only expected lint warnings about empty vault).

**Step 2: If errors appear, fix before proceeding**

Check `knowledge-vault/Logs/` for lint logs. Consult `tools/cvr/linters/rules.json` via `tools/cvr/linters/diagnostic_db.py` for fix strategies.

**Step 3: Once clean, delete `artifacts/`**

```bash
rm -rf artifacts/
```

**Step 4: Run verify again to confirm nothing broke**

```bash
tools/verify_all.sh
```

Expected: clean pass.

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat(vault): complete Obsidian vault migration — remove artifacts/, all paths now in knowledge-vault/"
```

---

## Verification Checklist

After all tasks complete:

- [ ] `knowledge-vault/` exists with all subdirectories
- [ ] `.obsidian/` committed with Dataview and Calendar
- [ ] `knowledge-vault/Activity/` contains daily notes with markdown tables
- [ ] `knowledge-vault/History/history.md` contains Dataview query block
- [ ] `python3 tools/cvr/log_action.py --intent test --action test` writes to `knowledge-vault/Activity/`
- [ ] `python3 tools/cvr/add_note.py --type cursed-knowledge --title "Test"` creates note in `knowledge-vault/Cursed Knowledge/`
- [ ] `tools/verify_all.sh` passes cleanly
- [ ] `artifacts/` directory does not exist
- [ ] No remaining `artifacts/` references in skills or CLAUDE.md
