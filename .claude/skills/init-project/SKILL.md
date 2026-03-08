---
name: init-project
description: >
  Add a new project to the clausidian-kit Silo. Use this skill whenever the
  operator says "add a project", "new project", "init project", "initialize
  project", "create project", or otherwise requests a new entry in the Silo.
  Trigger even if the operator only provides a name or slug without full
  details — gather missing inputs before proceeding. This skill runs a
  multi-step initialization sequence with verification gates; do not shortcut
  the verify steps.
---

# init-project

**Pattern**: Guarded Initialization + Post-Condition Verification

**Problem solved**: Ensures new projects are added to the Silo in a consistent,
verified state with an updated registry before any work begins.

**Tradeoff**: Requires a healthy Silo before it can run — unhealthy existing
projects will block new additions until resolved.

---

## Preconditions — Fail Closed on Any Failure

Before gathering inputs, verify all conditions:

**0. Silo intent is established:**

`knowledge-vault/Intent/project_intent.md` must exist. If it is missing,
invoke `establish-intent` before proceeding.

**1. Silo Root is healthy:**

```bash
python3 tools/cvr/verify_silo.py
```

If this fails: report the error verbatim. Do not proceed. Instruct the
operator to resolve the failing project(s) before adding a new one.

**2. Target directory does not already exist.**

Check after the slug is known (Step 1). If `workspace/<slug>/` is present:
fail closed and report the conflict to the operator.

---

## Step 1 — Information Gathering

Collect the following. Ask the operator for any that are missing:

| Input | Description |
|-------|-------------|
| **Project Name** | Human-readable label (e.g. `My New Service`) |
| **Slug** | Filesystem-safe directory name, lowercase with hyphens (e.g. `my-new-service`) |

Do not proceed to Step 2 until both values are confirmed. Once the slug is
known, verify `workspace/<slug>/` does not already exist (see Preconditions).

---

## Step 2 — Initialize

Run the initialization tool with confirmed inputs:

```bash
python3 tools/cvr/init_project.py --name "NAME" --slug "SLUG"
```

If the command fails: report the error verbatim and **fail closed**. Do not
proceed to Step 3.

---

## Step 3 — Verify

**3a. Verify the Silo is still healthy** after initialization:

```bash
python3 tools/cvr/verify_silo.py
```

If this fails: report the error verbatim. The project may be partially
initialized — flag this explicitly and instruct the operator to inspect
before continuing.

**3b. Re-run context manifest generation** to include the new workspace entry:

```bash
python3 tools/cvr/generate_context_manifest.py
```

---

## Step 4 — Log and Notify

Log the action to the activity ledger:

```bash
python3 tools/cvr/log_action.py \
  --intent init-project \
  --action project_initialized \
  --scope workspace/SLUG \
  --result ok \
  --evidence PROJECTS.md
```

Then confirm completion to the operator with:

- Project name and slug
- `PROJECTS.md` updated: yes
- Silo verification: passed
- Final line: "Project `SLUG` is ready. Add your source code to `workspace/SLUG/`."

---

## Prohibitions

- No initialization without a passing pre-flight `verify_silo.py`
- No proceeding past a failed `init_project.py`
- No skipping post-initialization verification
- Do not stage, commit, or push — operator-only
- Do not create ADK files (AGENDA.md, CLAUDE.md, artifacts/) inside `workspace/<slug>/` — projects are source code only
