# Antigravity → Claude Code Conversion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace all Antigravity IDE integration points with Claude Code equivalents while leaving the Verification Runtime (`tools/`) untouched.

**Architecture:** Create `.claude/skills/` with 14 skill files converted from `.agent/workflows/`; rename `AGENTS.md` → `CLAUDE.md` with content updates; delete `.aiexclude`; replace the Antigravity safety doc with a Claude Code equivalent; update human-facing docs.

**Tech Stack:** Markdown files only. No code changes. Verification via `tools/verify_all.sh` and grep checks.

---

## What NOT to touch

- `tools/` — entire Verification Runtime is off-limits
- `tests/` — no test changes needed
- `artifacts/` — no artifact changes
- `.agentsignore` — stays as-is (valid for Claude Code)
- `.agent/workflows/` — keep as reference; skills are the authoritative copy going forward

---

### Task 1: Create `.claude/` directory structure

**Files:**

- Create: `.claude/rules/contract-precedence.md`
- Create: `.claude/skills/` (directory, populated in subsequent tasks)

**Step 1: Create the rules file**

Content for `.claude/rules/contract-precedence.md`:

```markdown
# Contract Precedence

If any skill, rule, or instruction conflicts with `CLAUDE.md`,
then `CLAUDE.md` takes precedence.
```

**Step 2: Verify it exists**

Run: `ls .claude/rules/`
Expected: `contract-precedence.md`

**Step 3: Commit**

```bash
git add .claude/rules/contract-precedence.md
git commit -m "chore: add .claude/rules directory with contract-precedence"
```

---

### Task 2: Create `CLAUDE.md` from `AGENTS.md`

**Files:**

- Create: `CLAUDE.md` (based on `AGENTS.md` with edits below)
- Do NOT delete `AGENTS.md` yet (delete in Task 17)

**Step 1: Copy `AGENTS.md` to `CLAUDE.md`**

```bash
cp AGENTS.md CLAUDE.md
```

**Step 2: Apply all textual substitutions**

Make these replacements throughout `CLAUDE.md`:

| Find | Replace |
|---|---|
| `AGENTS.md` | `CLAUDE.md` |
| `workflow` | `skill` (where it refers to the ADK concept; keep "skill" as noun) |
| `.agent/workflows/**` | `.claude/skills/**` |
| `Antigravity` | `Claude Code` |
| `.aiexclude` | *(remove the sentence/bullet containing it)* |

**Step 3: Update the Verification Runtime Boundary section**

Find the block:

```
- `tools/cvr/**` (Canonical Verification Runtime substrate)
- `tools/verify_all.sh` (Verification orchestrator bridge)
- `.agent/workflows/**` (Workflow definitions)
```

Replace with:

```
- `tools/cvr/**` (Canonical Verification Runtime substrate)
- `tools/verify_all.sh` (Verification orchestrator bridge)
- `.claude/skills/**` (Skill definitions)
```

**Step 4: Add Skills Index section before the Privilege Warning section**

Append this section:

```markdown
## Skills Index

The following skills are available. Invoke them via their slash command alias.

| Slash command | Skill file | Purpose |
|---|---|---|
| `/start` | `adk-start` | Entry point for a new session or work cycle |
| `/plan-cycle` | `adk-plan-cycle` | Orchestrate the full plan → execute → review loop |
| `/establish-intent` | `adk-establish-intent` | Define project intent before planning |
| `/prep-context` | `adk-prep-context` | Load and verify workspace context |
| `/verify-agenda` | `adk-verify-agenda` | Validate AGENDA.md state |
| `/plan-execution` | `adk-plan-execution` | Produce an implementation plan |
| `/execute-plan` | `adk-execute-plan` | Execute an approved plan |
| `/post-verify` | `adk-post-verify` | Reconcile AGENDA.md after execution |
| `/post-execution-review` | `adk-post-execution-review` | Capture lessons learned |
| `/finish` | `adk-finish` | Unified verify → review → commit sequence |
| `/commit-message` | `adk-commit-message` | Generate Conventional Commit message |
| `/markdown-checklist` | `adk-markdown-checklist` | Verify Markdown quality |
| `/toggle-maintenance-mode` | `adk-toggle-maintenance-mode` | Enable/disable maintenance mode |
```

**Step 5: Verify no `AGENTS.md` self-references remain**

Run: `grep -n "AGENTS\.md" CLAUDE.md`
Expected: no output

**Step 6: Verify no Antigravity references remain**

Run: `grep -ni "antigravity\|\.aiexclude" CLAUDE.md`
Expected: no output

**Step 7: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add CLAUDE.md converted from AGENTS.md for Claude Code"
```

---

### Task 3: Create skill `adk-start`

**Files:**

- Create: `.claude/skills/adk-start.md`
- Reference: `.agent/workflows/start.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-start.md`:

```markdown
---
name: adk-start
description: Begin a new ADK session or work cycle. Use when the user runs /start, begins a new session, or wants to start a planning cycle. Ensures intent and context exist, then chains to plan-cycle.
---

# adk-start

## Purpose

User-friendly entry point for the agentic development cycle.

Ensures foundational artifacts exist (`project_intent.md`, context manifest) then hands off to `adk-plan-cycle`.

## Inputs

- `auto_approve` (boolean, optional): If true, skips the plan approval gate. default: `false`.

> **Warning:** Setting `auto_approve: true` removes the human-in-the-loop safety check. Use only for routine tasks or trusted automated loops.

## Workflow

1. **Check Intent**

   - Check if `artifacts/intent/project_intent.md` exists.
   - If MISSING, run `adk-establish-intent` skill.

2. **Ensure Context Prepared**

   - Check if `artifacts/logs/context_manifest.md` exists.
   - If MISSING, run `adk-prep-context` skill.
   - If PRESENT, do not re-run (treat as already prepared for this session).

3. **Hand off to Cycle**

   - Run `adk-plan-cycle` skill with the `auto_approve` argument.
```

**Step 2: Verify**

Run: `grep -n "AGENTS\|Antigravity\|\.aiexclude" .claude/skills/adk-start.md`
Expected: no output

**Step 3: Commit**

```bash
git add .claude/skills/adk-start.md
git commit -m "feat(skills): add adk-start skill"
```

---

### Task 4: Create skill `adk-plan-cycle`

**Files:**

- Create: `.claude/skills/adk-plan-cycle.md`
- Reference: `.agent/workflows/plan-cycle.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-plan-cycle.md`:

```markdown
---
name: adk-plan-cycle
description: Orchestrate the full ADK development lifecycle (prepare → verify agenda → plan → execute → review). Use when the user runs /plan-cycle or needs to run the full loop.
---

# adk-plan-cycle

## Purpose

Meta-skill that orchestrates the standard development lifecycle. Does not perform work directly; chains other skills to ensure safety, context, and institutional memory.

## Inputs

- `auto_approve` (boolean, optional): Bypass manual plan approval. default: `false`.

## Workflow Sequence

### 1. Preparation

1. **`adk-prep-context`**

   - Loads `CLAUDE.md`, `AGENDA.md`, and respects `.agentsignore`.
   - Produces `artifacts/logs/context_manifest.md`.

2. **`adk-verify-agenda`**

   - Ensures `AGENDA.md` is classified and valid.
   - Prevents planning against completed or unknown items.

### 2. Planning

3. **`adk-plan-execution`**

   - Reads context and agenda.
   - Produces `artifacts/history/runs/<run-id>/implementation_plan.md`.

   **Approval Decision:**

   - IF `auto_approve` is `true`: **PROCEED** automatically to execution.
   - IF `auto_approve` is `false` (default): **STOP** and wait for operator approval of the plan.

### 3. Execution

4. **`adk-execute-plan`**

   - Executes the approved plan.
   - Runs verification (`tools/verify_all.sh`).

### 4. Review

5. **`adk-post-verify`**

   - Reconciles `AGENDA.md` against reality.
   - Produces `artifacts/logs/post_verify_report.md`.

6. **`adk-post-execution-review`**

   - Captures lessons learned in `artifacts/history/lessons-learned.md`.
   - Closes the run.
```

**Step 2: Verify**

Run: `grep -n "AGENTS\|Antigravity\|workflow" .claude/skills/adk-plan-cycle.md`
Expected: no output (skill/skills only, no workflow references)

**Step 3: Commit**

```bash
git add .claude/skills/adk-plan-cycle.md
git commit -m "feat(skills): add adk-plan-cycle skill"
```

---

### Task 5: Create skill `adk-establish-intent`

**Files:**

- Create: `.claude/skills/adk-establish-intent.md`
- Reference: `.agent/workflows/establish-intent.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-establish-intent.md`:

```markdown
---
name: adk-establish-intent
description: Establish project intent before any planning or execution. Use when /establish-intent is invoked, or when artifacts/intent/project_intent.md is missing.
---

# adk-establish-intent

## Purpose

Prevent premature domain assumptions. Before any planning or execution, establish what this repository is for.

## Instructions

1. Ask the user a single neutral question:

   "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"

2. Write `artifacts/intent/project_intent.md` with the result using the schema below.

3. If the user refuses or is unsure, set `primary_domain: unknown` and proceed with minimal, non-domain-specific planning only.

## Schema (required)

`artifacts/intent/project_intent.md` MUST contain YAML frontmatter with:

- `primary_domain`: one of `software`, `writing`, `research`, `art`, `mixed`, `unknown`
- `deliverable`: short description of the end product
- `first_milestone_done`: definition of done for the first milestone
- `constraints`: list of constraints
- `non_goals`: list of non-goals
- `preferred_tools`: list of tools/skills the user prefers (optional)

## Notes

- Do not introduce language-specific scaffolding unless `primary_domain: software` AND the user wants it.
- For non-software domains, prefer doc-first workflows (outlines, drafts, experiments, citations, etc.).
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-establish-intent.md
git commit -m "feat(skills): add adk-establish-intent skill"
```

---

### Task 6: Create skill `adk-prep-context`

**Files:**

- Create: `.claude/skills/adk-prep-context.md`
- Reference: `.agent/workflows/prep-context.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-prep-context.md`:

```markdown
---
name: adk-prep-context
description: Load and verify workspace context at the start of a session. Use when /prep-context is invoked or artifacts/logs/context_manifest.md is missing.
---

# adk-prep-context

## Precondition

- `artifacts/intent/project_intent.md` exists.

If the precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Operating Rules

- No code or configuration modifications are permitted.
- Artifact writes permitted **only** under `artifacts/**` as specified.
- Runs in audit-only mode.

## Purpose

Load and verify required workspace context before any planning or execution:

- `CLAUDE.md` (mandatory)
- `AGENDA.md` (mandatory)
- Relevant files under `docs/` if present and not ignored

If any mandatory context file is missing, **fail closed**.

## Agent Ignore

- MUST respect `.agentsignore` when selecting additional files to read.
- `.agentsignore` MUST be parseable by `tools/cvr/generate_context_manifest.py`.
- If `.agentsignore` is missing, unreadable, or malformed, **fail closed**.

## Required Actions

1. Read all mandatory context files.
2. Read additional context files subject to `.agentsignore` and any read-scope budget.
3. Extract and internalize all enforceable constraints defined in `CLAUDE.md`.

## Output: context_manifest.md

Emit `artifacts/logs/context_manifest.md`.

The file MUST be generated by running:

```bash
python3 tools/cvr/generate_context_manifest.py
```

Manual creation or editing of this file is prohibited.

### Required Fields

- Timestamp (ISO-8601, UTC)
- Operating mode
- Agent ignore file used
- Files read as context (repo-relative paths)
- Files skipped due to `.agentsignore` (if detectable)
- Any read-scope budget applied (count/bytes) and whether truncation occurred
- **Constraints acknowledged**: concise list of enforceable rules extracted from `CLAUDE.md`

## Prohibitions

- No code changes
- No configuration changes
- No partial artifacts
- No speculative continuation beyond context loading
```

**Step 2: Verify**

Run: `grep -n "AGENTS\|Antigravity\|\.aiexclude" .claude/skills/adk-prep-context.md`
Expected: no output

**Step 3: Commit**

```bash
git add .claude/skills/adk-prep-context.md
git commit -m "feat(skills): add adk-prep-context skill"
```

---

### Task 7: Create skill `adk-verify-agenda`

**Files:**

- Create: `.claude/skills/adk-verify-agenda.md`
- Reference: `.agent/workflows/verify-agenda.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-verify-agenda.md`:

```markdown
---
name: adk-verify-agenda
description: Verify agenda items and classify their completion status. Use when /verify-agenda is invoked or before planning to ensure AGENDA.md is valid.
---

# adk-verify-agenda

## Precondition

- `artifacts/intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Classification

Agenda items MUST be classified as one of:

- `finished`
- `in-progress`
- `blocked`
- `not-started`
- `unknown`

## Rules

- `finished` items MUST include evidence pointers (repo-relative paths only).
- `unknown` items are defects and MUST specify what evidence would resolve them.

## Planning rule

Items marked `finished` MUST NOT appear in `implementation_plan.*` unless explicitly reopened under a new hypothesis ID (or marked regression-only).
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-verify-agenda.md
git commit -m "feat(skills): add adk-verify-agenda skill"
```

---

### Task 8: Create skill `adk-plan-execution`

**Files:**

- Create: `.claude/skills/adk-plan-execution.md`
- Reference: `.agent/workflows/plan-execution.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-plan-execution.md`:

```markdown
---
name: adk-plan-execution
description: Produce an implementation plan from the verified agenda. Use when /plan-execution is invoked or when a plan artifact is needed before execution.
---

# adk-plan-execution

## Precondition

- `artifacts/intent/project_intent.md` exists and reflects the repo's purpose.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Prerequisites (conditional)

Before drafting any plan, ensure context is loaded and agenda is verified:

1. **Context Manifest**:
   - Check if `artifacts/logs/context_manifest.md` exists.
   - If MISSING, run `adk-prep-context` skill.

2. **Agenda Verification**:
   - Check if `artifacts/logs/post_verify_report.md` exists and is fresher than the latest `AGENDA.md` edit (heuristic).
   - If in doubt, or if never run for this session, run `adk-verify-agenda` skill.

## Ignore semantics (normative)

`.gitignore` and `.agentsignore` are NOT permission systems. They MUST NOT be treated as a precondition failure or a panic.

- You MUST write planning artifacts under `artifacts/history/runs/<run-id>/` even if git ignores that directory.
- Do NOT ask the user to bypass ignore rules.
- Ignore rules only affect what gets committed or included in agent context, not what can be created on disk.

## Context load (normative)

Before drafting any plan, read:

- `artifacts/intent/project_intent.md`
- `CLAUDE.md`
- `AGENDA.md`

Use the intent to choose domain-appropriate planning:

- software: design + tests + build verification
- writing: outlines + milestones + editorial workflow
- research: hypotheses + methods + citations + reproducibility steps
- art: briefs + iterations + asset workflow
- mixed/unknown: minimal, conservative plan with explicit unknowns

## Run directory

All plan artifacts MUST be written under:

`artifacts/history/runs/<run-id>/`

## Outputs (normative paths)

- `artifacts/history/runs/<run-id>/implementation_plan.md`
- `artifacts/history/runs/<run-id>/implementation_plan.json`

Workspace root MUST NOT be used for plan artifacts.
```

**Step 2: Verify**

Run: `grep -n "AGENTS\|Antigravity" .claude/skills/adk-plan-execution.md`
Expected: no output

**Step 3: Commit**

```bash
git add .claude/skills/adk-plan-execution.md
git commit -m "feat(skills): add adk-plan-execution skill"
```

---

### Task 9: Create skill `adk-execute-plan`

**Files:**

- Create: `.claude/skills/adk-execute-plan.md`
- Reference: `.agent/workflows/execute-plan.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-execute-plan.md`:

```markdown
---
name: adk-execute-plan
description: Execute an approved implementation plan, collect evidence, and summarize results. Use when /execute-plan is invoked or when the user approves a plan and wants to proceed with execution.
---

# adk-execute-plan

## Precondition

- `artifacts/intent/project_intent.md` exists and reflects the repo's purpose.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Ignore semantics (normative)

`.gitignore` and `.agentsignore` are NOT permission systems. They MUST NOT be treated as a precondition failure or a panic.

- Do NOT ask the user to bypass ignore rules.
- Ignore rules only affect what gets committed or included in agent context, not what can be created on disk.

## Verification (recommended default)

Run `tools/verify_all.sh` to:

- validate template baseline + intent
- execute lints
- run project tests via `tools/test.sh` (language-agnostic hook)
- capture outputs under `artifacts/logs/*.log` and `artifacts/test_results/*`

## After completion (normative)

The agent MUST NOT consider `adk-execute-plan` finished until the feedback loop is closed.

1. **Agenda Reconciliation**:
   - Run `adk-post-verify` skill.
   - This generates `artifacts/logs/post_verify_report.md`.

2. **Institutional Memory**:
   - Run `adk-post-execution-review` skill.
   - This ensures lessons are captured in `artifacts/history/lessons-learned.md`.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-execute-plan.md
git commit -m "feat(skills): add adk-execute-plan skill"
```

---

### Task 10: Create skill `adk-post-verify`

**Files:**

- Create: `.claude/skills/adk-post-verify.md`
- Reference: `.agent/workflows/post-verify.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-post-verify.md`:

```markdown
---
name: adk-post-verify
description: Re-run agenda verification after execution and record reconciliation results. Use when /post-verify is invoked or after executing a plan to reconcile AGENDA.md.
---

# adk-post-verify

## Precondition

- `artifacts/intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

After executing a plan, re-verify that `AGENDA.md` reflects reality.

## Output requirements

Emit `artifacts/logs/post_verify_report.md` with the following **exact** section headings:

- `## Completed items`
- `## Items still open`
- `## Evidence`

## Rules

- Evidence pointers MUST be repo-relative paths (e.g. `artifacts/test_results/...`).
- Evidence pointers MUST NOT be absolute paths and MUST NOT use `file://` URLs.
- Avoid truncation (`...`) in evidence pointers; they must be auditable.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-post-verify.md
git commit -m "feat(skills): add adk-post-verify skill"
```

---

### Task 11: Create skill `adk-post-execution-review`

**Files:**

- Create: `.claude/skills/adk-post-execution-review.md`
- Reference: `.agent/workflows/post-execution-review.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-post-execution-review.md`:

```markdown
---
name: adk-post-execution-review
description: Capture institutional memory from an executed plan. Use when /post-execution-review is invoked or after post-verify to record lessons learned.
---

# adk-post-execution-review

## Precondition

- `artifacts/intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Inputs

- `artifacts/history/runs/<run-id>/walkthrough.md`
- `artifacts/logs/post_verify_report.md` (preferred)
- Evidence under `artifacts/`

## Rules

- Entries MUST include evidence pointers (repo-relative paths).
- Do NOT add an entry if there is no evidence.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-post-execution-review.md
git commit -m "feat(skills): add adk-post-execution-review skill"
```

---

### Task 12: Create skill `adk-finish`

**Files:**

- Create: `.claude/skills/adk-finish.md`
- Reference: `.agent/workflows/finish.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-finish.md`:

```markdown
---
name: adk-finish
description: Unified finishing sequence for closing a development cycle (verify → review → commit). Use when /finish is invoked or when implementation is done and the user wants to wrap up.
---

# adk-finish

## Purpose

Unified entry point for closing a development cycle. Ensures the repository is verified, history is aggregated, and a commit message is prepared.

## Precondition

- `artifacts/intent/project_intent.md` exists.

## Workflow

1. **Verify Results**

   - Run `adk-post-verify` to reconcile `AGENDA.md` and generate the final report.

2. **Seal History**

   - Run `adk-post-execution-review` to aggregate the run into permanent history and extract lessons learned.

3. **Prepare Handoff**

   - Run `adk-commit-message` to generate candidate Conventional Commit messages.

4. **Format Documentation**

   - Run `python3 tools/cvr/format_md.py` to ensure all artifacts and history files are perfectly formatted.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-finish.md
git commit -m "feat(skills): add adk-finish skill"
```

---

### Task 13: Create skill `adk-commit-message`

**Files:**

- Create: `.claude/skills/adk-commit-message.md`
- Reference: `.agent/workflows/commit-message.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-commit-message.md`:

```markdown
---
name: adk-commit-message
description: Generate a Conventional Commit message from changes since the last commit. Use when /commit-message is invoked or the user asks for a commit message.
---

# adk-commit-message

## Precondition

- `artifacts/intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Commit message format (normative)

Use **Conventional Commits**:

```
<type>(<scope>): <short summary>

<body>   # optional: why + what changed
<footer> # optional: Fixes #123, BREAKING CHANGE: ...
```

Allowed `type` values (preferred): `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`.

Rules:

- Summary line is imperative mood, <= ~72 chars, no trailing period.
- `scope` is optional; use a short subsystem name if it clarifies impact.
- If change is breaking, include `!` after type/scope (e.g., `feat(api)!:`) and add `BREAKING CHANGE:` in footer.

## Link hygiene (normative)

Commit messages must be portable across machines, editors, and hosting platforms.

### Allowed references

- **Repo-relative file paths**: prefer inline code (e.g. `tools/linters/rules.json`)
- **Public web links**: `https://…` only

### Forbidden references

- `file://…`
- `cci:`, `vscode:`, `idea:` deep-links
- Absolute local paths like `/home/...`, `/Users/...`, `C:\...`

### Sanitization rule

If a generated commit message includes forbidden links: replace with repo-relative paths in backticks, or remove the link entirely.

## Authority and safety (normative)

- The agent MUST NOT stage, commit, amend commits, push, rebase, or otherwise mutate Git history.
- The agent's output is limited to commit message candidates and formatting fixes.

## Steps

1. **Review diff since last commit** — read and summarize the workspace diff vs `HEAD`.
2. **Draft message content** — write the header first, add body only when needed.
3. **Propose 2–3 candidate commit messages** matching the format above.
4. **Sanitize references** — hard-check for forbidden patterns; fix any violations.
5. **Approval gate** — present the top candidate as the default; ask the user to approve or edit.
6. **Stop** — do not run any Git commands. The operator performs staging and committing.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-commit-message.md
git commit -m "feat(skills): add adk-commit-message skill"
```

---

### Task 14: Create skill `adk-markdown-checklist`

**Files:**

- Create: `.claude/skills/adk-markdown-checklist.md`
- Reference: `.agent/workflows/markdown-checklist.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-markdown-checklist.md`:

```markdown
---
name: adk-markdown-checklist
description: Verify Markdown structure and quality. Use when /markdown-checklist is invoked or when creating or modifying significant Markdown documentation.
---

# adk-markdown-checklist

## Precondition

- `artifacts/intent/project_intent.md` exists.

## Steps

1. **Format**

   - Run `python3 tools/cvr/format_md.py`
   - If it fails, check `tools/check_tools.sh` and resolve dependencies.

2. **Verify Structure**

   - [ ] Fenced code blocks have language identifiers?
   - [ ] Blank lines surround code blocks?
   - [ ] Lists use consistent indentation (2 spaces)?
   - [ ] No mixed bullets (`-` vs `*`)?
   - [ ] No hard-coded file links (`file://`)? (Run `linters/lint_common.py` checks)

3. **Verify Links**

   - [ ] All internal links are repo-relative?
   - [ ] External links are valid (`https://`)?

4. **Commit**

   - Only commit after formatting passes cleanly.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-markdown-checklist.md
git commit -m "feat(skills): add adk-markdown-checklist skill"
```

---

### Task 15: Create skill `adk-toggle-maintenance-mode`

**Files:**

- Create: `.claude/skills/adk-toggle-maintenance-mode.md`
- Reference: `.agent/workflows/toggle-maintenance-mode.md`

**Step 1: Create the skill file**

Content for `.claude/skills/adk-toggle-maintenance-mode.md`:

```markdown
---
name: adk-toggle-maintenance-mode
description: Toggle MAINTENANCE mode for the agent (operator-controlled). Use when /toggle-maintenance-mode is invoked or the operator needs to enable Runtime modification access.
---

# adk-toggle-maintenance-mode

## Purpose

Operator-controlled switch that marks the agent as being in **MAINTENANCE mode** (or not).

This is a **state toggle only**. It does not stage/commit/push anything, and it does not modify Runtime code by itself.

## Inputs

- `state` (string, optional): one of `on`, `off`, `toggle`. default: `toggle`.
- `reason` (string, optional): short human note explaining why maintenance is being enabled.

## Normative behavior

### State file

Maintain exactly one state file:

- `artifacts/logs/agent_mode.json`
- `artifacts/agent_activity.jsonl` (append-only ledger)

Schema:

```json
{
  "mode": "maintenance | normal",
  "timestamp": "ISO-8601",
  "reason": "string (optional)"
}
```

### Transition rules

- If `state: on`: write the state file with `"mode": "maintenance"`, then log action via `python3 tools/cvr/log_action.py --intent toggle_maintenance_mode --action toggle --scope agent_mode --result ok --evidence artifacts/logs/agent_mode.json`
- If `state: off`: write the state file with `"mode": "normal"`, then log action.
- If `state: toggle`: if current mode is `maintenance`, switch to `normal`; otherwise switch to `maintenance`. Log action in both cases.

### Continuous notification requirement

While `"mode": "maintenance"` is active, the agent MUST prepend the following banner to **every** response until the mode is set back to `normal`:

> **MAINTENANCE MODE ENABLED** — Runtime modifications may be in progress. Operator intent required for any risky actions.

### Safety note (normative)

- MAINTENANCE mode only expands what changes are *permitted* under `CLAUDE.md`; it does not remove any other constraints.
- The agent MUST still: fail closed when preconditions are unmet, produce evidence for non-trivial changes, and avoid staging/committing/pushing (operator-only).

## Steps

1. Read `artifacts/intent/project_intent.md` (precondition consistency check).
2. Read current `artifacts/logs/agent_mode.json` if it exists; otherwise assume `"normal"`.
3. Apply Transition rules, writing the updated state file.
4. Echo the new mode + timestamp + reason (if provided) to the operator.
5. Stop.
```

**Step 2: Commit**

```bash
git add .claude/skills/adk-toggle-maintenance-mode.md
git commit -m "feat(skills): add adk-toggle-maintenance-mode skill"
```

---

### Task 16: Delete `.aiexclude`

**Files:**

- Delete: `.aiexclude`

**Step 1: Delete the file**

```bash
git rm .aiexclude
```

**Step 2: Commit**

```bash
git commit -m "chore: remove .aiexclude (Antigravity-specific, no Claude Code equivalent)"
```

---

### Task 17: Replace `docs/antigravity_safety.md` with `docs/claude_code_safety.md`

**Files:**

- Delete: `docs/antigravity_safety.md`
- Create: `docs/claude_code_safety.md`

**Step 1: Delete the old file**

```bash
git rm docs/antigravity_safety.md
```

**Step 2: Create the new file**

Content for `docs/claude_code_safety.md`:

```markdown
# Safe Claude Code Configuration

This document describes a safe configuration for using Claude Code with the
Agentic Development Kit (ADK). It focuses on minimizing unintended access,
destructive operations, and agent behaviors that conflict with workspace policies.

> Note: Claude Code permission controls are behavioral, not OS-level security
> boundaries. Always pair them with human review and environment isolation.

---

## 1) Use an Appropriate Permission Mode

Claude Code has three permission modes:

- **Default mode**: Claude proposes actions and waits for approval on risky operations.
- **Auto-approve mode** (`--dangerously-skip-permissions`): Skips confirmation prompts. Use only for trusted, automated loops.
- **Plan mode** (`/plan`): Claude describes what it would do without doing it. Useful for reviewing intent before execution.

**Recommendation**: Use default mode for all interactive sessions. Reserve auto-approve for well-understood, scripted pipelines.

---

## 2) Guard Off-Limits Paths via `CLAUDE.md`

`CLAUDE.md` is the authoritative contract between you and the agent. Use it to declare off-limits paths explicitly:

```
Agents MUST NOT modify the following paths:
- tools/cvr/**
- tools/verify_all.sh
- .claude/skills/**
```

Claude Code reads and respects `CLAUDE.md` instructions during every session.

---

## 3) Use `.agentsignore` as a Context Filter

The `.agentsignore` file (gitignore-like syntax) controls what files the agent reads as context. It is **not** a security boundary — it is a context filter.

- Use it to exclude secrets, large binaries, and build artifacts from agent context.
- The ADK ships a pre-configured `.agentsignore` that fences off the Verification Runtime and run artifacts.

Do NOT treat `.agentsignore` as a substitute for proper secrets management.

---

## 4) Audit Agent Activity

The ADK records all agent actions in an append-only ledger:

- **Path**: `artifacts/agent_activity.jsonl`
- **Format**: NDJSON, one entry per action

Review this file regularly to audit what the agent has done.

---

## 5) Enforce Human Review at Key Gates

The ADK's workflow skills have built-in human approval gates:

- `adk-plan-cycle` stops after `adk-plan-execution` by default and waits for you to approve the plan before execution begins.
- `adk-commit-message` generates candidates but never commits — the operator runs `git commit`.
- `adk-toggle-maintenance-mode` requires explicit operator invocation to expand agent permissions.

Do not bypass these gates without understanding the consequences.

---

## 6) Use Isolated Environments

For maximum safety:

- Run Claude Code inside a container or virtual machine.
- Mount only the project workspace into the environment.
- Avoid running agents on hosts with sensitive data outside the workspace.

---

## 7) Safe Mode Checklist

- [ ] `CLAUDE.md` defines off-limits paths
- [ ] `.agentsignore` configured and reviewed
- [ ] Default permission mode in use (not auto-approve)
- [ ] Plan approval gate enabled (not bypassed via `auto_approve: true`)
- [ ] `artifacts/agent_activity.jsonl` reviewed after sessions
- [ ] Prefer container or VM execution for sensitive workloads
```

**Step 3: Commit both changes**

```bash
git add docs/claude_code_safety.md
git commit -m "docs: replace antigravity_safety.md with claude_code_safety.md"
```

---

### Task 18: Update `HUMANS.md`

**Files:**

- Modify: `HUMANS.md`

**Step 1: Apply substitutions**

Make these replacements throughout `HUMANS.md`:

| Find | Replace |
|---|---|
| `AGENTS.md` | `CLAUDE.md` |
| `Antigravity` | `Claude Code` |
| `workflow` | `skill` (where it refers to ADK concepts) |
| Any reference to `.aiexclude` | Remove the sentence/bullet |

**Step 2: Verify no Antigravity or AGENTS references remain**

Run: `grep -ni "antigravity\|AGENTS\.md\|\.aiexclude" HUMANS.md`
Expected: no output

**Step 3: Commit**

```bash
git add HUMANS.md
git commit -m "docs: update HUMANS.md for Claude Code (remove Antigravity references)"
```

---

### Task 19: Update `README.md`

**Files:**

- Modify: `README.md`

**Step 1: Apply substitutions**

Make these replacements throughout `README.md`:

| Find | Replace |
|---|---|
| `AGENTS.md` | `CLAUDE.md` |
| `Antigravity` | `Claude Code` |
| `workflow` | `skill` (where referring to ADK slash commands) |

**Step 2: Verify**

Run: `grep -ni "antigravity\|AGENTS\.md" README.md`
Expected: no output

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for Claude Code (remove Antigravity references)"
```

---

### Task 20: Delete `AGENTS.md` and final sweep

**Files:**

- Delete: `AGENTS.md`

**Step 1: Confirm `CLAUDE.md` is complete**

Run: `wc -l CLAUDE.md AGENTS.md`
Expected: `CLAUDE.md` has roughly the same line count as `AGENTS.md`.

**Step 2: Delete `AGENTS.md`**

```bash
git rm AGENTS.md
```

**Step 3: Full sweep — no remaining Antigravity references**

Run:

```bash
grep -rni "antigravity\|\.aiexclude\|AGENTS\.md" \
  --include="*.md" --include="*.txt" --include="*.json" --include="*.sh" \
  --exclude-dir=".git" --exclude-dir=".agent" \
  .
```

Expected: no output (`.agent/workflows/` is excluded from this check as it is legacy reference material).

**Step 4: Run verification suite**

```bash
source .venv/bin/activate && tools/verify_all.sh
```

Expected: all checks pass.

**Step 5: Commit**

```bash
git commit -m "chore: remove AGENTS.md now superseded by CLAUDE.md"
```

---

### Task 21: Final integration commit

**Step 1: Confirm skill count**

Run: `ls .claude/skills/ | wc -l`
Expected: `13`

**Step 2: Confirm no broken cross-references in skills**

Run: `grep -rn "AGENTS\.md\|Antigravity\|\.aiexclude\|establish-intent workflow\|plan-execution workflow" .claude/skills/`
Expected: no output

**Step 3: Confirm `.aiexclude` is gone**

Run: `ls .aiexclude 2>&1`
Expected: `ls: cannot access '.aiexclude': No such file or directory`

**Step 4: Tag or note completion**

This task is complete when:

- `CLAUDE.md` exists and passes the grep sweep
- `.claude/skills/` contains 13 skill files
- `.aiexclude` does not exist
- `docs/claude_code_safety.md` exists
- `docs/antigravity_safety.md` does not exist
- `tools/verify_all.sh` passes
