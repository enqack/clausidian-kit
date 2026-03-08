# Design: Convert ADK from Antigravity IDE to Claude Code

**Date**: 2026-03-08
**Status**: Approved

## Summary

Convert the Agentic Development Kit (ADK) from Antigravity IDE conventions to Claude Code conventions. The core workflow logic, verification runtime, and artifact schema are preserved unchanged. Only the agent-facing integration layer changes.

## Scope

### What changes

| Antigravity | Claude Code | Action |
|---|---|---|
| `AGENTS.md` | `CLAUDE.md` | Rename; update all internal self-references |
| `.agent/workflows/*.md` (14 files) | `.claude/skills/*.md` (14 files) | Convert each workflow to a Claude Code skill |
| `.aiexclude` | *(deleted)* | Delete entirely |
| `docs/antigravity_safety.md` | `docs/claude_code_safety.md` | Replace with Claude Code equivalent |
| `HUMANS.md` | `HUMANS.md` | Update slash command format and remove Antigravity references |
| `README.md` | `README.md` | Update Antigravity references |
| `.agent/rules/contract-precedence.md` | `.claude/rules/contract-precedence.md` | Move to `.claude/` |

### What does NOT change

- `tools/` (entire Verification Runtime)
- `tools/cvr/` (supervision kernel — off-limits per AGENTS.md contract)
- `artifacts/` schema and paths
- `.agentsignore` (remains valid for Claude Code context filtering)
- `tests/`
- `requirements-verify.txt`
- `.agent/workflows/` source files (kept for reference; skills are the authoritative copy going forward)

## Design Decisions

### D1: Skills in `.claude/skills/` with `adk-` prefix

All 14 workflows become skills under `.claude/skills/`. The `adk-` prefix namespaces them to avoid collisions with other skills in the user's Claude Code environment.

Skill files:

- `adk-start.md`
- `adk-plan-cycle.md`
- `adk-establish-intent.md`
- `adk-prep-context.md`
- `adk-verify-agenda.md`
- `adk-plan-execution.md`
- `adk-execute-plan.md`
- `adk-post-verify.md`
- `adk-post-execution-review.md`
- `adk-finish.md`
- `adk-commit-message.md`
- `adk-markdown-checklist.md`
- `adk-toggle-maintenance-mode.md`

### D2: Skill frontmatter format

Claude Code skills use `name` and `description` YAML fields. The Antigravity `operating_mode` and `artifacts_required` fields are folded into the skill body as normative constraints (not frontmatter).

Example:

```yaml
---
name: adk-start
description: Begin a new ADK session or work cycle. Use when starting work, running /start, or beginning a new planning cycle.
---
```

The `description` field is written to be informative enough for Claude Code's trigger system to match it correctly against user intent.

### D3: Cross-references updated throughout

Inside each skill, all references to:

- `AGENTS.md` → `CLAUDE.md`
- `<workflow-name> workflow` → `adk-<workflow-name> skill`
- `.aiexclude` → removed (no equivalent)
- `.agentsignore` → unchanged

### D4: `CLAUDE.md` structure

`CLAUDE.md` retains all content from `AGENTS.md` with these additions/changes:

- Self-references: `AGENTS.md` → `CLAUDE.md`
- Terminology: `workflow` → `skill` throughout
- Verification Runtime Boundary updated: `.agent/workflows/**` → `.claude/skills/**`
- New **Skills Index** section listing all 13 user-invocable skills and their slash command aliases
- Antigravity-specific language removed (no `.aiexclude`, no "Antigravity IDE")

### D5: `.aiexclude` deleted

Claude Code has no `.aiexclude` equivalent at the project level. The same restrictions are enforced via:

1. Explicit `CLAUDE.md` instructions ("Do not modify `tools/cvr/**` or `.claude/skills/**`")
2. `.agentsignore` (already present and valid)

### D6: `docs/claude_code_safety.md`

Replaces `docs/antigravity_safety.md`. Covers:

- Claude Code permission modes (default, auto-approve, plan mode)
- `CLAUDE.md` as the primary guard for off-limits paths
- `.agentsignore` as context filter
- Agent activity audit via `artifacts/agent_activity.jsonl`
- Recommended settings for safe operation

## Success Criteria

- `CLAUDE.md` exists and is complete
- `.claude/skills/` contains all 14 skill files
- `.aiexclude` is deleted
- `docs/claude_code_safety.md` exists
- `HUMANS.md` and `README.md` contain no Antigravity references
- `tools/verify_all.sh` passes (runtime unchanged)
- All cross-references within skills resolve correctly (no broken `AGENTS.md` mentions)
