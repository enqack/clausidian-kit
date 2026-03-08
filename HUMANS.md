# Human Guide to the Agentic Development Kit

clausidian-kit is a multi-project **Silo** that hosts source projects inside a
shared supervision kernel. The agent operates under a strict, evidence-based
contract: every non-trivial change requires a plan, verification, and a
recorded journal entry.

## Architecture

```text
clausidian-kit/          ← Silo Root (supervision kernel)
├── bin/                 ← Operator CLI tools
├── tools/               ← Verification scripts
│   └── cvr/             ← Canonical Verification Runtime (off-limits)
├── .claude/skills/      ← Agent skills (off-limits)
├── knowledge-vault/     ← All runs, journals, history, and activity logs
│   ├── Intent/          ← project_intent.md lives here
│   ├── Runs/            ← One directory per run
│   ├── Journal/         ← Closed-run journals
│   ├── Activity/        ← Daily activity ledger
│   ├── History/         ← Immutable run lineage (history.ndjson)
│   ├── Lessons/         ← Lessons learned across runs
│   └── Deep Thoughts/   ← Narrative reconstructions
├── workspace/           ← Source projects (workspace/<slug>/)
├── PROJECTS.md          ← Project registry (managed by tools)
└── AGENDA.md            ← Current hypotheses, blockers, risks
```

**Silo invariants:**

- `tools/cvr/verify_silo.py` must pass at all times.
- Every row in `PROJECTS.md` must have a matching `workspace/<slug>/` directory.
- `PROJECTS.md` is managed by `tools/cvr/init_project.py` — never edit it manually.
- The Verification Runtime (`tools/cvr/**`, `.claude/skills/**`) must not be modified by agents.

## Getting Started

**1. Install dependencies:**

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-verify.txt
```

**2. Establish intent** — define what you are building and what "done" looks like:

```text
/establish-intent
```

This creates `knowledge-vault/Intent/project_intent.md`. Most skills will fail
closed if this file does not exist.

**3. Start a work cycle:**

```text
/start
```

This entry point ensures intent and context exist, then chains into the full
plan-cycle workflow.

## Silo Management

### Dashboard

```sh
bin/silo-status
```

Shows agent mode, registered projects, Silo health, and recent activity.

### Adding a Project

To register an empty new project:

```sh
bin/new-project --name "My Project" --slug "my-project"
```

To bootstrap from a remote or local git repository:

```sh
# Remote URL (name inferred from repo)
bin/new-project --slug "my-project" --source https://github.com/user/repo.git

# Remote URL with explicit name and branch
bin/new-project --name "My Project" --slug "my-project" \
  --source https://github.com/user/repo.git --branch develop

# Local path
bin/new-project --slug "my-project" --source ../local/repo
```

Or via the agent skill (guided workflow):

```text
/init-project
```

All of the above create `workspace/<slug>/` and append a row to `PROJECTS.md`.

### Health Check

```sh
python3 tools/cvr/verify_silo.py
```

Verifies all `PROJECTS.md` entries have corresponding `workspace/` directories.

## Core Workflow

The agent follows a strict **Perceive → Plan → Act → Prove → Summarize** loop:

1. **Perceive** — Inspect current state, context, and lessons learned.
1. **Plan** — Produce `knowledge-vault/Runs/<run-id>/implementation_plan.md`.
1. **Act** — Apply changes (only in `full-execution` mode).
1. **Prove** — Execute `tools/verify_all.sh`; assertions require evidence.
1. **Summarize** — Close the run to generate `knowledge-vault/Journal/<run-id>.md`.

Your job at each stage:

- **Plan**: Review the implementation plan. Verify hypotheses and safety checks.
- **Act**: Monitor the session and observe artifact generation.
- **Prove**: Confirm `tools/verify_all.sh` passes cleanly.

## Slash Commands

### Lifecycle Orchestration

| Command       | Purpose                                           |
| ------------- | ------------------------------------------------- |
| `/start`      | Entry point for a new session or work cycle       |
| `/plan-cycle` | Orchestrate the full plan → execute → review loop |
| `/finish`     | Unified verify → review → commit sequence         |

### Setup and Context

| Command             | Purpose                                                 |
| ------------------- | ------------------------------------------------------- |
| `/establish-intent` | Define what you are building and what "done" looks like |
| `/prep-context`     | Load `CLAUDE.md` and verify workspace context           |
| `/verify-agenda`    | Validate `AGENDA.md` state and classify items           |

### Planning and Execution

| Command           | Purpose                                 |
| ----------------- | --------------------------------------- |
| `/plan-execution` | Produce a technical implementation plan |
| `/execute-plan`   | Apply changes and run verification      |

### Review and History

| Command                  | Purpose                                          |
| ------------------------ | ------------------------------------------------ |
| `/post-verify`           | Reconcile `AGENDA.md` against completed work     |
| `/post-execution-review` | Capture lessons learned for institutional memory |
| `/commit-message`        | Generate a Conventional Commit message           |

### Project Management

| Command         | Purpose                                          |
| --------------- | ------------------------------------------------ |
| `/init-project` | Register and bootstrap a new project in the Silo |

### Utilities

| Command                    | Purpose                                     |
| -------------------------- | ------------------------------------------- |
| `/markdown-checklist`      | Verify documentation quality                |
| `/toggle-maintenance-mode` | Enable `maintenance` mode for Runtime fixes |

## Artifact Paths

All artifacts live under `knowledge-vault/`:

| Artifact         | Path                                                   |
| ---------------- | ------------------------------------------------------ |
| Project intent   | `knowledge-vault/Intent/project_intent.md`             |
| Run plans        | `knowledge-vault/Runs/<run-id>/implementation_plan.md` |
| Run walkthroughs | `knowledge-vault/Runs/<run-id>/walkthrough.md`         |
| Journals         | `knowledge-vault/Journal/<run-id>.md`                  |
| History (data)   | `knowledge-vault/History/history.ndjson`               |
| Activity ledger  | `knowledge-vault/Activity/YYYY-MM-DD.md`               |
| Deep Thoughts    | `knowledge-vault/Deep Thoughts/<run-id>.md`            |
| Lessons learned  | `knowledge-vault/Lessons/lessons-learned.md`           |
| Context manifest | `knowledge-vault/Logs/context_manifest.md`             |

**Run ID format:** `YYYY-MM-DD-HH-MM-SS` (UTC). Use `tools/new_run.sh` to
create a new run directory.

## Verification and Testing

```sh
tools/verify_all.sh
```

This runs:

- All linters in `tools/cvr/linters/` (schema, format, agenda, intent, etc.)
- `tools/test.sh` — your project's language-agnostic test hook.

The test hook auto-detects Go, Rust, Node.js, and Python projects. For other
project types, add your own test commands to `tools/test.sh`.

To check required external tools:

```sh
tools/check_tools.sh
```

## Escalation Protocol

If you or the agent encounter bugs or limitations in the Verification Runtime
(`tools/cvr/**`, `tools/verify_all.sh`):

1. **STOP** — Do not attempt to work around the issue.
1. **NOTIFY** — Record the exact error and affected component (file path).
1. **DEFER** — You (the human operator) must decide whether to fix the Runtime,
   grant `maintenance` mode, or escalate to the ADK maintainer.

The agent must not self-promote to `maintenance` mode. You grant it explicitly.

## Fail-Closed Semantics

The agent halts immediately — no partial writes, no ledger entries — when:

- `knowledge-vault/Intent/project_intent.md` is missing (required by most skills).
- `tools/verify_all.sh` fails at the start of a run (clean state check).
- Workspace boundaries are ambiguous.
- Required artifacts cannot be written.

Fail-closed is a feature, not a failure mode. It prevents non-deterministic
state from accumulating.

## Key Artifacts Reference

| File                                         | Description                                           |
| -------------------------------------------- | ----------------------------------------------------- |
| `AGENDA.md`                                  | Current hypotheses, blockers, and deferred risks      |
| `PROJECTS.md`                                | Authoritative project registry (read-only for agents) |
| `CLAUDE.md`                                  | Master operating contract for the agent               |
| `knowledge-vault/Intent/project_intent.md`   | Top-level definition of success                       |
| `knowledge-vault/History/history.ndjson`     | Immutable run lineage                                 |
| `knowledge-vault/Lessons/lessons-learned.md` | Institutional memory across runs                      |
