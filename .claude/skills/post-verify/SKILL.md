---
name: post-verify
description: Re-run agenda verification after execution and record reconciliation results. Use when /post-verify is invoked or after executing a plan to reconcile AGENDA.md.
---

# post-verify

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

After executing a plan, re-verify that `AGENDA.md` reflects reality.

## Output requirements

Emit `knowledge-vault/Logs/post_verify_report.md` with the following **exact** section headings:

- `## Completed items`
- `## Items still open`
- `## Evidence`

## Rules

- Evidence pointers MUST be repo-relative paths (e.g. `knowledge-vault/Logs/test_results/...`).
- Evidence pointers MUST NOT be absolute paths and MUST NOT use `file://` URLs.
- Avoid truncation (`...`) in evidence pointers; they must be auditable.
