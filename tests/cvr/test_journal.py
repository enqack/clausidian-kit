import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath("tools"))
import journal  # noqa: E402


def test_emit_journal_with_artifacts(tmp_path, capsys):
    run_dir = tmp_path / "knowledge-vault/Runs/run-1"
    run_dir.mkdir(parents=True)
    (run_dir / "implementation_plan.json").write_text(
        json.dumps({
            "items": [
                {"id": "B", "status": "Done", "hypothesis": "B hyp", "evidence": {"required_artifacts": ["2.md", "1.md"]}},
                {"id": "A", "status": "Active", "hypothesis": "A hyp"},
            ]
        }),
        encoding="utf-8",
    )
    (run_dir / "walkthrough.md").write_text(
        "# Walkthrough\n\n## Lessons Learned\n- Lesson 2\n- Lesson 1\n",
        encoding="utf-8",
    )
    (run_dir / "post_verify_report.md").write_text(
        "Run ID: ...\nStatus: finished\n",
        encoding="utf-8",
    )

    # Need to mock the journal output directory to be inside tmp_path,
    # journal.py writes to paths.JOURNAL_DIR = knowledge-vault/Journal.
    # We chdir to tmp_path so paths are relative to it.

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        path = journal.emit_journal(run_dir)
    finally:
        os.chdir(cwd)

    journal_path = tmp_path / "knowledge-vault/Journal/run-1.md"
    assert path == Path("knowledge-vault/Journal/run-1.md")
    
    content = journal_path.read_text(encoding="utf-8")
    assert "### Deep Thoughts, by an Agent" in content
    assert "**Run run-1**" in content
    assert "**Goal**: I set out to test 2 hypotheses, starting with 'B hyp'." in content
    assert "**Outcome**: The run finished with status 'finished'." in content
    assert "**Reflections**:" in content
    assert "- Lesson 2" in content
    assert "- Lesson 1" in content
    assert "Editor’s note" in content


def test_emit_journal_missing_plan(tmp_path, capsys):
    run_dir = tmp_path / "knowledge-vault/Runs/run-2"
    run_dir.mkdir(parents=True)
    # No artifacts

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        path = journal.emit_journal(run_dir)
    finally:
        os.chdir(cwd)

    journal_path = tmp_path / "knowledge-vault/Journal/run-2.md"
    assert path == Path("knowledge-vault/Journal/run-2.md")
    
    content = journal_path.read_text(encoding="utf-8")
    assert "**Goal**: I had no plan, behaving purely reactively." in content
    assert "**Reflections**:\n- I learned nothing specific this time." in content


def test_main_runs(tmp_path, capsys):
    # Setup standard layout
    runs_dir = tmp_path / "knowledge-vault/Runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "run-3").mkdir()

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        rc = journal.main([])
    finally:
        os.chdir(cwd)

    assert rc == 0
    assert (tmp_path / "knowledge-vault/Journal/run-3.md").exists()
