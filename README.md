# clausidian-kit

A multi-project **Agentic Development Kit (ADK)** Silo for planning, executing,
and verifying work with AI agents under a strict, evidence-based operating
contract.

## Architecture

- **Silo Root** (`/`) — Supervision kernel: runtime tools, skills, shared vault.
- **Verification Runtime** (`tools/cvr/`, `.claude/skills/`) — Language-agnostic
  lifecycle engine. Off-limits for agent modification.
- **User Projects** (`workspace/<slug>/`) — Source code only. Registered in
  `PROJECTS.md`.

## Prerequisites

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-verify.txt
```

## Getting Started

**1. Establish intent** — define what you are building and what "done" looks like:

```text
/establish-intent
```

This creates `knowledge-vault/Intent/project_intent.md`.

**2. Start a work cycle:**

```text
/start
```

**3. Check Silo health at any time:**

```sh
bin/silo-status
```

## Silo Management

| Command                            | Purpose                                            |
| ---------------------------------- | -------------------------------------------------- |
| `bin/silo-status`                  | Dashboard: mode, projects, health, recent activity |
| `bin/new-project`                  | Register and bootstrap a new project               |
| `/init-project`                    | Guided new-project workflow (via agent skill)      |
| `python3 tools/cvr/verify_silo.py` | Run Silo health check directly                     |

## Verification

Run the full verification suite at any time:

```sh
tools/verify_all.sh
```

This executes all linters, schema validators, and `tools/test.sh` (your
project's language-agnostic test hook).

## Further Reading

See [HUMANS.md](HUMANS.md) for the full operator reference: architecture,
workflows, all slash commands, artifact paths, and escalation protocol.
