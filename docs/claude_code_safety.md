# Safe Claude Code Configuration

This document describes a safe configuration for using Claude Code with the
Agentic Development Kit (ADK). It focuses on minimizing unintended access,
destructive operations, and agent behaviors that conflict with workspace policies.

> Note: Claude Code permission controls are behavioral, not OS-level security
> boundaries. Always pair them with human review and environment isolation.

______________________________________________________________________

## 1) Use an Appropriate Permission Mode

Claude Code has three permission modes:

- **Default mode**: Claude proposes actions and waits for approval on risky operations.
- **Auto-approve mode** (`--dangerously-skip-permissions`): Skips confirmation prompts. Use only for trusted, automated loops.
- **Plan mode** (`/plan`): Claude describes what it would do without doing it. Useful for reviewing intent before execution.

**Recommendation**: Use default mode for all interactive sessions. Reserve auto-approve for well-understood, scripted pipelines.

______________________________________________________________________

## 2) Guard Off-Limits Paths via `CLAUDE.md`

`CLAUDE.md` is the authoritative contract between you and the agent. Use it to declare off-limits paths explicitly:

```
Agents MUST NOT modify the following paths:
- tools/cvr/**
- tools/verify_all.sh
- .claude/skills/**
```

Claude Code reads and respects `CLAUDE.md` instructions during every session.

______________________________________________________________________

## 3) Use `.agentsignore` as a Context Filter

The `.agentsignore` file (gitignore-like syntax) controls what files the agent reads as context. It is **not** a security boundary — it is a context filter.

- Use it to exclude secrets, large binaries, and build artifacts from agent context.
- The ADK ships a pre-configured `.agentsignore` that fences off the Verification Runtime and run artifacts.

Do NOT treat `.agentsignore` as a substitute for proper secrets management.

______________________________________________________________________

## 4) Audit Agent Activity

The ADK records all agent actions in an append-only ledger:

- **Path**: `artifacts/agent_activity.jsonl`
- **Format**: NDJSON, one entry per action

Review this file regularly to audit what the agent has done.

______________________________________________________________________

## 5) Enforce Human Review at Key Gates

The ADK's workflow skills have built-in human approval gates:

- `plan-cycle` stops after `plan-execution` by default and waits for you to approve the plan before execution begins.
- `commit-message` generates candidates but never commits — the operator runs `git commit`.
- `toggle-maintenance-mode` requires explicit operator invocation to expand agent permissions.

Do not bypass these gates without understanding the consequences.

______________________________________________________________________

## 6) Use Isolated Environments

For maximum safety:

- Run Claude Code inside a container or virtual machine.
- Mount only the project workspace into the environment.
- Avoid running agents on hosts with sensitive data outside the workspace.

______________________________________________________________________

## 7) Safe Mode Checklist

- [ ] `CLAUDE.md` defines off-limits paths
- [ ] `.agentsignore` configured and reviewed
- [ ] Default permission mode in use (not auto-approve)
- [ ] Plan approval gate enabled (not bypassed via `auto_approve: true`)
- [ ] `artifacts/agent_activity.jsonl` reviewed after sessions
- [ ] Prefer container or VM execution for sensitive workloads
