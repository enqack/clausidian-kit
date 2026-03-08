---
name: start
description: Begin a new ADK session or work cycle. Use when the user runs /start, begins a new session, or wants to start a planning cycle. Ensures intent and context exist, then chains to plan-cycle.
---

# start

## Purpose

User-friendly entry point for the agentic development cycle.

Ensures foundational artifacts exist (`project_intent.md`, context manifest) then hands off to `plan-cycle`.

## Inputs

- `auto_approve` (boolean, optional): If true, skips the plan approval gate. default: `false`.

> **Warning:** Setting `auto_approve: true` removes the human-in-the-loop safety check. Use only for routine tasks or trusted automated loops.

## Workflow

1. **Check Intent**

   - Check if `knowledge-vault/Intent/project_intent.md` exists.
   - If MISSING, run `establish-intent` skill.

1. **Ensure Context Prepared**

   - Check if `knowledge-vault/Logs/context_manifest.md` exists.
   - If MISSING, run `prep-context` skill.
   - If PRESENT, do not re-run (treat as already prepared for this session).

1. **Hand off to Cycle**

   - Run `plan-cycle` skill with the `auto_approve` argument.
