---
name: verify-agenda
description: Verify agenda items and classify their completion status. Use when /verify-agenda is invoked or before planning to ensure AGENDA.md is valid.
---

# verify-agenda

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `establish-intent` skill.
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
