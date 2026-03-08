import os
import sys
from pathlib import Path

# Add linters to path
sys.path.append(os.path.abspath("tools/linters"))
import journal_lint


def _write_journal(root: Path, content: str, name: str = "entry-1.md") -> Path:
    journal_dir = root / "knowledge-vault/Journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    p = journal_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_journal_files(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    # No knowledge-vault/Journal created

    rc = journal_lint.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "no knowledge-vault/Journal directory" in captured.out


def test_missing_header(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    _write_journal(
        tmp_path, 
        f"Just the disclaimer.\n\n---\n{journal_lint.DISCLAIMER_REQ}\n"
    )

    rc = journal_lint.main()
    captured = capsys.readouterr()

    assert rc == 1
    assert "missing required header" in captured.err


def test_missing_disclaimer(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    _write_journal(
        tmp_path, 
        f"{journal_lint.HEADER_REQ}\n\nNotes."
    )

    rc = journal_lint.main()
    captured = capsys.readouterr()

    assert rc == 1
    assert "missing required editor disclaimer" in captured.err


def test_unsafe_paths(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    _write_journal(
        tmp_path,
        f"{journal_lint.HEADER_REQ}\n"
        f"I looked at /etc/passwd\n"
        f"\n---\n{journal_lint.DISCLAIMER_REQ}\n"
    )

    rc = journal_lint.main()
    captured = capsys.readouterr()

    assert rc == 1
    assert "absolute path" in captured.err


def test_valid_journal(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    _write_journal(
        tmp_path,
        f"{journal_lint.HEADER_REQ}\n"
        f"I thought about artifacts/history/plan.md\n"
        f"\n---\n{journal_lint.DISCLAIMER_REQ}\n"
    )

    rc = journal_lint.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "journal_lint: OK" in captured.out
