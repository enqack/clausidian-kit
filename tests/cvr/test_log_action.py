#!/usr/bin/env python3
"""Tests for log_action.py daily-note writer."""
import sys
from pathlib import Path
from datetime import date


def test_creates_daily_note_on_first_call(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Activity").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Logs").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    # Force reimport with new cwd
    import importlib
    if "tools.cvr.log_action" in sys.modules:
        del sys.modules["tools.cvr.log_action"]
    if "tools.cvr.paths" in sys.modules:
        del sys.modules["tools.cvr.paths"]
    from tools.cvr import log_action

    today = date.today().isoformat()
    log_action.append_entry("test-intent", "test-action", scope="test", result="ok")

    daily = tmp_path / "knowledge-vault" / "Activity" / f"{today}.md"
    assert daily.exists(), "Daily note should be created"
    content = daily.read_text()
    assert "type: activity" in content
    assert "| Time |" in content
    assert "test-intent" in content


def test_appends_row_to_existing_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Activity").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Logs").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    import importlib
    if "tools.cvr.log_action" in sys.modules:
        del sys.modules["tools.cvr.log_action"]
    if "tools.cvr.paths" in sys.modules:
        del sys.modules["tools.cvr.paths"]
    from tools.cvr import log_action

    log_action.append_entry("intent-1", "action-1")
    log_action.append_entry("intent-2", "action-2")

    today = date.today().isoformat()
    daily = tmp_path / "knowledge-vault" / "Activity" / f"{today}.md"
    content = daily.read_text()
    assert "intent-1" in content
    assert "intent-2" in content
    # Header should appear only once
    assert content.count("| Time |") == 1
