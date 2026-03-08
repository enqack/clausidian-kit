# Design: Migrate Artifact Store to Obsidian Vault

**Date**: 2026-03-08
**Status**: Approved

## Overview

Replace the `artifacts/` directory with a fully Obsidian-native `knowledge-vault/` at the project root. The vault becomes both the machine-written artifact store (via updated CVR tools) and the human authoring/browsing surface (via Obsidian's graph view, Dataview queries, Calendar plugin, and wikilinks).

## Motivation

- Browse and search run history, journals, and activity logs in Obsidian's UI
- Use Obsidian as the authoring surface for plans, intent, lessons, and reflections
- Enable graph-view navigation between runs, journals, cursed knowledge, and deep thoughts
- Add two new institutional memory types: Cursed Knowledge and Deep Thoughts

## Approach

Approach B (Full Obsidian-native rewrite) was selected over:

- **Approach A** (thin repath): too shallow — no real Obsidian features
- **Approach C** (post-processor pipeline): two representations in flight; adds maintenance burden

## Vault Layout

```
knowledge-vault/
├── .obsidian/                  ← committed; standardizes Obsidian setup
│   ├── community-plugins.json
│   └── plugins/
│       ├── dataview/
│       └── calendar/
├── Intent/
│   └── project_intent.md
├── Runs/
│   └── <run-id>/
│       ├── implementation_plan.md
│       └── walkthrough.md
├── Journal/
│   └── <run-id>.md
├── Activity/
│   └── YYYY-MM-DD.md           ← daily note; ledger entries as markdown table
├── History/
│   └── history.md              ← Dataview query over all Runs
├── Lessons/
│   └── lessons-learned.md
├── Cursed Knowledge/
│   └── <slug>.md               ← per-note footguns and anti-patterns
├── Deep Thoughts/
│   └── <slug>.md               ← per-note agent reflections
└── Logs/
    ├── context_manifest.md
    ├── post_verify_report.md
    ├── agent_mode.json
    └── test_results/
```

### Path Mapping from `artifacts/`

| Old path | New path |
|---|---|
| `artifacts/intent/project_intent.md` | `knowledge-vault/Intent/project_intent.md` |
| `artifacts/history/runs/<run-id>/` | `knowledge-vault/Runs/<run-id>/` |
| `artifacts/journal/<run-id>.md` | `knowledge-vault/Journal/<run-id>.md` |
| `artifacts/history/history.md` | `knowledge-vault/History/history.md` |
| `artifacts/history/deep-thoughts.md` | `knowledge-vault/Deep Thoughts/` (split to per-run notes) |
| `artifacts/history/lessons-learned.md` | `knowledge-vault/Lessons/lessons-learned.md` |
| `artifacts/logs/` | `knowledge-vault/Logs/` |
| `artifacts/logs/agent_mode.json` | `knowledge-vault/Logs/agent_mode.json` |
| `artifacts/test_results/` | `knowledge-vault/Logs/test_results/` |
| `artifacts/diffs/` | `knowledge-vault/Logs/diffs/` |
| `artifacts/agent_activity.jsonl` | replaced by `knowledge-vault/Activity/YYYY-MM-DD.md` |

## Note Schemas

All notes carry YAML frontmatter for Dataview queries and wikilink navigation.

### Run (`Runs/<run-id>/implementation_plan.md`)

```yaml
---
type: run
run_id: 2026-03-08-10-00-00
status: complete
intent: "[[Intent/project_intent]]"
journal: "[[Journal/2026-03-08-10-00-00]]"
tags: [run]
---
```

### Journal (`Journal/<run-id>.md`)

```yaml
---
type: journal
run_id: 2026-03-08-10-00-00
run: "[[Runs/2026-03-08-10-00-00/implementation_plan]]"
date: 2026-03-08
tags: [journal]
---
```

### Activity (`Activity/YYYY-MM-DD.md`)

```yaml
---
type: activity
date: 2026-03-08
tags: [activity, daily]
---
```

Ledger entries rendered as a markdown table:

```markdown
| Time  | Actor | Intent | Scope | Action | Result |
|-------|-------|--------|-------|--------|--------|
| 07:07 | sysop | toggle_maintenance_mode | agent_mode | toggle | ok |
```

### Cursed Knowledge (`Cursed Knowledge/<slug>.md`)

```yaml
---
type: cursed-knowledge
discovered: 2026-03-08
run: "[[Runs/2026-03-08-10-00-00/implementation_plan]]"
tags: [cursed-knowledge]
---
```

### Deep Thoughts (`Deep Thoughts/<slug>.md`)

```yaml
---
type: deep-thought
date: 2026-03-08
run: "[[Runs/2026-03-08-10-00-00/implementation_plan]]"
tags: [deep-thought]
---
```

### History (`History/history.md`)

Contains a live Dataview query instead of static content:

````markdown
```dataview
TABLE run_id, status, date FROM "Runs" SORT date DESC
```
````

## CVR Tool Changes

### `paths.py`

All path constants repointed to `knowledge-vault/`. New constants added:

- `VAULT_DIR`
- `ACTIVITY_DIR` (`knowledge-vault/Activity/`)
- `CURSED_KNOWLEDGE_DIR` (`knowledge-vault/Cursed Knowledge/`)
- `DEEP_THOUGHTS_DIR` (`knowledge-vault/Deep Thoughts/`)
- `LESSONS_FILE` → `knowledge-vault/Lessons/lessons-learned.md`

`AGENT_ACTIVITY_JSONL` removed.

### `log_action.py`

Replaces JSONL append with daily note writer:

1. Resolve `knowledge-vault/Activity/YYYY-MM-DD.md`
2. Create with frontmatter + table header if missing
3. Append one table row per invocation

### `log_action.py` → daily note writer

Replaces JSONL append:

1. Resolve `knowledge-vault/Activity/YYYY-MM-DD.md`
2. Create with frontmatter + table header if missing
3. Append one table row per invocation

### `compile_timeline.py`

Emits individual per-run notes into `knowledge-vault/Deep Thoughts/<run-id>.md` instead of one aggregated file.

### `aggregate_history.py`

Outputs `knowledge-vault/History/history.md` with a Dataview query block.

### `close_run.py` / `journal.py`

Output to `knowledge-vault/Journal/<run-id>.md` with full frontmatter and wikilinks to run and intent.

### `generate_context_manifest.py`

Output path updated to `knowledge-vault/Logs/context_manifest.md`.

### All linters

Path references updated to `knowledge-vault/` equivalents. No logic changes.

### New: `add_note.py`

Agent-callable script for creating Cursed Knowledge and Deep Thought notes:

```bash
python3 tools/cvr/add_note.py --type cursed-knowledge --title "Never use X" --run-id 2026-03-08-10-00-00
python3 tools/cvr/add_note.py --type deep-thought --title "On the nature of linting" --run-id 2026-03-08-10-00-00
```

Creates the note with correct frontmatter, a kebab-case slug, and wikilink back to the run.

## Migration Path

### Phase 1 — Scaffold the vault

- Create `knowledge-vault/` with all subdirectories
- Commit `.obsidian/` config with Dataview and Calendar plugins enabled
- Create stub notes: `History/history.md` (Dataview block), `Lessons/lessons-learned.md`

### Phase 2 — Migrate existing artifacts

In order:

1. `artifacts/intent/project_intent.md` → `knowledge-vault/Intent/project_intent.md` + frontmatter
2. `artifacts/agent_activity.jsonl` → convert each JSONL entry to the correct daily note in `knowledge-vault/Activity/YYYY-MM-DD.md`
3. `artifacts/history/runs/` → `knowledge-vault/Runs/` + frontmatter on each `implementation_plan.md`
4. `artifacts/journal/` → `knowledge-vault/Journal/` + frontmatter + wikilinks
5. `artifacts/history/lessons-learned.md` → `knowledge-vault/Lessons/lessons-learned.md`
6. `artifacts/history/deep-thoughts.md` → split into individual `knowledge-vault/Deep Thoughts/` notes
7. `artifacts/logs/` → `knowledge-vault/Logs/`
8. `artifacts/test_results/` → `knowledge-vault/Logs/test_results/`

### Phase 3 — Update CVR tools (maintenance mode required)

Order:

1. `paths.py`
2. `log_action.py`
3. `close_run.py` + `journal.py`
4. `compile_timeline.py`
5. `aggregate_history.py`
6. `generate_context_manifest.py`
7. All linters
8. New: `add_note.py`

### Phase 4 — Update references and remove `artifacts/`

1. Update `CLAUDE.md` artifact directory structure section
2. Update all skill `SKILL.md` files referencing `artifacts/` paths
3. Run `tools/verify_all.sh` — confirm clean pass
4. Delete `artifacts/`
