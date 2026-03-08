---
name: toggle-maintenance-mode
description: Toggle MAINTENANCE mode for the agent (operator-controlled). Use when /toggle-maintenance-mode is invoked or the operator needs to enable Runtime modification access.
---

# toggle-maintenance-mode

## Purpose

Operator-controlled switch that marks the agent as being in **MAINTENANCE mode** (or not).

This is a **state toggle only**. It does not stage/commit/push anything, and it does not modify Runtime code by itself.

## Inputs

- `state` (string, optional): one of `on`, `off`, `toggle`. default: `toggle`.
- `reason` (string, optional): short human note explaining why maintenance is being enabled.

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Alert the operator that intent must be established before toggling maintenance mode.
- Initiate the `establish-intent` skill.
- Do **not** continue until intent is established.

## Normative behavior

### State file

Maintain exactly one state file:

- `knowledge-vault/Logs/agent_mode.json`
- `knowledge-vault/Activity/YYYY-MM-DD.md` (append-only ledger)

Schema:

```json
{
  "mode": "maintenance | normal",
  "timestamp": "ISO-8601",
  "reason": "string (optional)"
}
```

### Transition rules

- If `state: on`: write the state file with `"mode": "maintenance"`, then log action via `python3 tools/cvr/log_action.py --intent toggle_maintenance_mode --action toggle --scope agent_mode --result ok --evidence knowledge-vault/Logs/agent_mode.json`
- If `state: off`: write the state file with `"mode": "normal"`, then log action.
- If `state: toggle`: if current mode is `maintenance`, switch to `normal`; otherwise switch to `maintenance`. Log action in both cases.

### Continuous notification requirement

While `"mode": "maintenance"` is active, the agent MUST prepend the following banner to **every** response until the mode is set back to `normal`:

> **MAINTENANCE MODE ENABLED** — Runtime modifications may be in progress. Operator intent required for any risky actions.

### Safety note (normative)

- MAINTENANCE mode only expands what changes are *permitted* under `CLAUDE.md`; it does not remove any other constraints.
- The agent MUST still: fail closed when preconditions are unmet, produce evidence for non-trivial changes, and avoid staging/committing/pushing (operator-only).

## Steps

1. Read current `knowledge-vault/Logs/agent_mode.json` if it exists; otherwise assume `"normal"`.
2. Apply Transition rules, writing the updated state file.
3. Echo the new mode + timestamp + reason (if provided) to the operator.
4. Stop.
