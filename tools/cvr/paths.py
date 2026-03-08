#!/usr/bin/env python3
"""Canonical artifact paths for the ADK Verification Runtime.

This module defines the single source of truth for all artifact paths.
All Python scripts SHOULD import from this module rather than hardcoding paths.
"""

from pathlib import Path

# Root directories
VAULT_ROOT = Path("knowledge-vault")

# Intent
INTENT_DIR = VAULT_ROOT / "Intent"
PROJECT_INTENT = INTENT_DIR / "project_intent.md"

# Runs
RUNS_DIR = VAULT_ROOT / "Runs"

# Journal
JOURNAL_DIR = VAULT_ROOT / "Journal"

# Activity (daily notes - replaces agent_activity.jsonl)
ACTIVITY_DIR = VAULT_ROOT / "Activity"

# History
HISTORY_DIR = VAULT_ROOT / "History"
HISTORY_NDJSON = HISTORY_DIR / "history.ndjson"
HISTORY_MD = HISTORY_DIR / "history.md"

# Lessons
LESSONS_DIR = VAULT_ROOT / "Lessons"
LESSONS_LEARNED = LESSONS_DIR / "lessons-learned.md"

# Cursed Knowledge
CURSED_KNOWLEDGE_DIR = VAULT_ROOT / "Cursed Knowledge"

# Deep Thoughts
DEEP_THOUGHTS_DIR = VAULT_ROOT / "Deep Thoughts"

# Logs
LOGS_DIR = VAULT_ROOT / "Logs"
AGENT_MODE_FILE = LOGS_DIR / "agent_mode.json"
CONTEXT_MANIFEST = LOGS_DIR / "context_manifest.md"
POST_VERIFY_REPORT = LOGS_DIR / "post_verify_report.md"
AGENDA_STATE = HISTORY_DIR / "agenda_state.json"

# Evidence directories
DIFFS_DIR = LOGS_DIR / "diffs"
TEST_RESULTS_DIR = LOGS_DIR / "test_results"
