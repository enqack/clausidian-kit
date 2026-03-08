---
name: adk-post-execution-review
description: Capture institutional memory from an executed plan. Use when /post-execution-review is invoked or after post-verify to record lessons learned.
---

# adk-post-execution-review

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Inputs

- `knowledge-vault/Runs/<run-id>/walkthrough.md`
- `knowledge-vault/Logs/post_verify_report.md` (preferred)
- Evidence under `knowledge-vault/`

## Rules

- Entries MUST include evidence pointers (repo-relative paths).
- Do NOT add an entry if there is no evidence.
