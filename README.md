# Agentic Development Template

A language-agnostic repository template for **planning → execution → verification → reconciliation** with explicit evidence.

The project inside the repo may be software, writing, research, art, or mixed. The workflow system uses Python as a **verification runtime only** (to run `tools/*.py`).

## Features

### 🧠 Deep Thoughts Journal

Automated, narrative reconstruction of every run.

*Note: Deep Thoughts is a dramatized reconstruction derived from run artifacts, not a primary source of truth. It illustrates the decision process deterministically.*

- **Narrative**: `artifacts/journal/<run-id>.md` (Theatrical, deterministic summary of Goal, Outcome, and Reflections).
- **Timeline**: `artifacts/history/deep-thoughts.md` (Reverse-chronological compilation of all journals).

### 📜 Unified History

Chronological event log merging hypotheses, agenda items, and journal entries.

- **Data**: `artifacts/history/history.ndjson`
- **Updates**: Automatically aggregated via `tools/aggregate_history.py`.

### 🛡️ Verification Suite

Comprehensive tooling to ensure process integrity.

- **Linters**: Enforce schema compliance for journals, history, and plans (`tools/linters/*.py`).
- **Runner**: `tools/verify_all.sh` runs all linters and project tests.

## Workflow

### 1. Initialize

Run `/establish-intent` to define `docs/intent/project_intent.md`.

### 2. Plan & Execute

Follow the standard loop:

1. **Plan**: `/plan-execution` (Generate `implementation_plan.md`)
1. **Execute**: (Write code)
1. **Verify**: `tools/verify_all.sh`
1. **Close**: `python3 tools/close_run.py <run-id>` (Generates journal)

## Verification runtime

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-verify.txt
```

Run:

```sh
tools/verify_all.sh
```

## Panic / fail-closed behavior

If you invoke a workflow that requires intent (e.g., `/plan-execution`) before intent exists, the agent MUST fail closed and immediately ask the canonical intent question, write the intent file, and then resume the requested workflow. No override prompts.

## Ignore semantics

`.gitignore` and `.agentsignore` are NOT permission systems. They do not block file creation.

- Planning artifacts MUST be written under `artifacts/history/runs/<run-id>/` even though that directory is typically gitignored.
- Agents MUST NOT ask the user to "override gitignore" to create run artifacts.

## Tests are language-agnostic

Project tests are defined in:

- `tools/test.sh`

## Optional history

You can maintain a structured history that captures major runs, decisions, and reconciliations. Regenerate it from the current artifacts with `python tools/aggregate_history.py`, and sanity-check the output with `tools/verify_all.sh`.
