#!/usr/bin/env python3
"""Tests for add_note.py."""
import sys
from pathlib import Path


def test_creates_cursed_knowledge_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Cursed Knowledge").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Deep Thoughts").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Runs").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    if "tools.cvr.add_note" in sys.modules:
        del sys.modules["tools.cvr.add_note"]
    if "tools.cvr.paths" in sys.modules:
        del sys.modules["tools.cvr.paths"]
    from tools.cvr import add_note

    path = add_note.create_note(
        note_type="cursed-knowledge",
        title="Never use rm -rf /",
        run_id="2026-03-08-10-00-00",
    )
    assert path.exists()
    content = path.read_text()
    assert "type: cursed-knowledge" in content
    assert "Never use rm -rf /" in content
    assert "[[Runs/2026-03-08-10-00-00/implementation_plan]]" in content


def test_creates_deep_thought_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Cursed Knowledge").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Deep Thoughts").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    if "tools.cvr.add_note" in sys.modules:
        del sys.modules["tools.cvr.add_note"]
    if "tools.cvr.paths" in sys.modules:
        del sys.modules["tools.cvr.paths"]
    from tools.cvr import add_note

    path = add_note.create_note(
        note_type="deep-thought",
        title="On the nature of linting",
        run_id=None,
    )
    assert path.exists()
    content = path.read_text()
    assert "type: deep-thought" in content
    assert "On the nature of linting" in content


def test_slug_is_kebab_case(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge-vault" / "Cursed Knowledge").mkdir(parents=True)
    (tmp_path / "knowledge-vault" / "Deep Thoughts").mkdir(parents=True)

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    if "tools.cvr.add_note" in sys.modules:
        del sys.modules["tools.cvr.add_note"]
    if "tools.cvr.paths" in sys.modules:
        del sys.modules["tools.cvr.paths"]
    from tools.cvr import add_note

    path = add_note.create_note(
        note_type="deep-thought",
        title="Hello World This Is A Test",
    )
    assert "-" in path.name
    assert " " not in path.name
    assert path.name == path.name.lower() or path.name[0].isdigit()
