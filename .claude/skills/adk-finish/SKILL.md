---
name: adk-finish
description: Unified finishing sequence for closing a development cycle (verify → review → commit). Use when /finish is invoked or when implementation is done and the user wants to wrap up.
---

# adk-finish

## Purpose

Unified entry point for closing a development cycle. Ensures the repository is verified, history is aggregated, and a commit message is prepared.

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `adk-establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Workflow

1. **Verify Results**

   - Run `adk-post-verify` to reconcile `AGENDA.md` and generate the final report.

2. **Seal History**

   - Run `adk-post-execution-review` to aggregate the run into permanent history and extract lessons learned.

3. **Prepare Handoff**

   - Run `adk-commit-message` to generate candidate Conventional Commit messages.

4. **Format Documentation**

   - Run `python3 tools/cvr/format_md.py` to ensure all artifacts and history files are perfectly formatted.
