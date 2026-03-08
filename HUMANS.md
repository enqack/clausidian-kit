# Human Guide to the Agentic Development Kit

Welcome! This repository uses the Agentic Development Kit (ADK) to structure collaboration between humans and AI agents. The ADK defines a strict, evidence-based operating contract to ensure correctness and maintainability.

## 🚀 Getting Started

1.  **Install Dependencies**:

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-verify.txt
    ```

1.  **Establish Intent**:
    Run `/establish-intent` to define the project's "North Star". This creates `artifacts/intent/project_intent.md`.

## 🔄 Core Workflows

The ADK revolves around a disciplined **Perceive -> Plan -> Act -> Prove -> Summarize** loop.

### 1. Planning

Triggers: `/plan-execution` or `/start`

- The agent analyzes requirements, context, and lessons learned.
- It produces an **Implementation Plan** (`artifacts/history/runs/<run-id>/implementation_plan.md`).
- **Your Job**: Review the plan. Verify the hypotheses and safety checks.

### 2. Execution (Act)

- The agent applies code or configuration changes.
- **Your Job**: Monitor the session and review artifact generation.

### 3. Verification & Closure (Prove & Summarize)

- Run `tools/verify_all.sh` to ensure all tests and linters pass.
- Once verified, the run is summarized into a **Journal** entry (`artifacts/journal/<run-id>.md`).
- A narrative reconstruction of the session is added to **Deep Thoughts** (`artifacts/history/deep-thoughts.md`).

## 🔬 Scientific Method (Epistemic Contract)

The agent operates as a **scientific investigator of systems**. This means:

- **Hypotheses**: Every non-trivial action must be grounded in an explicit hypothesis.
- **Experiments**: All code changes are treated as experiments to prove or falsify a theory.
- **Evidence**: Assertions are invalid without evidence (logs, test results, terminal output).
- **Falsification**: Discovering an assumption is wrong is considered a successful outcome.

## 🤖 Agent Workflows

Interact with the agent using slash commands.

### Lifecycle Orchestration

- **`/start`**: Entry point for a new session or work cycle.
- **`/plan-cycle`**: Orchestrates the full loop from planning to review.
- **`/finish`**: The unified sequence to verify, review, and draft commits.

### Setup & Intent

- **`/establish-intent`**: Define what we are building and what "done" looks like.
- **`/prep-context`**: Load `CLAUDE.md` and verify workspace context.
- **`/verify-agenda`**: Validate the `AGENDA.md` state.

### Planning & Execution

- **`/plan-execution`**: Produce a technical implementation plan.
- **`/execute-plan`**: Apply changes and run verification.
- **`/markdown-checklist`**: Verify documentation quality.

### Review & History

- **`/post-verify`**: Reconcile `AGENDA.md` against completed work.
- **`/post-execution-review`**: Capture "lessons learned" for institutional memory.
- **`/commit-message`**: Generate standard Conventional Commit messages.

### Maintenance

- **`/toggle-maintenance-mode`**: Enable `maintenance` mode to allow agent modifications to the Runtime itself.

## 🚨 Escalation Protocol

If you or the agent encounter bugs or limitations in the **Verification Runtime** (e.g., `tools/cvr/**`, `tools/verify_all.sh`):

1.  **STOP**: Do not attempt to work around the issue.
2.  **NOTIFY**: Alert the operator (user) with the exact error and affected component.
3.  **DEFER**: The human operator must decide whether to fix the Runtime, grant `maintenance` mode, or escalate.

## 🛑 Fail‑Closed Semantics

If a strict requirement is not met (e.g., missing Intent or failing verification), the agent will **Fail Closed**. It stops immediately to prevent damage or non-deterministic state.

## 📂 Key Artifacts

- **`artifacts/intent/project_intent.md`**: The top-level definition of success.
- **`artifacts/history/runs/<run-id>/`**: Where the current work is documented (plans, logs, results).
- **`artifacts/journal/<run-id>.md`**: The deterministic summary of a completed Run.
- **`artifacts/history/history.md`**: The immutable lineage of all work.
- **`AGENDA.md`**: Current workspace hypotheses, blockers, and risks.
