from pathlib import Path

import post_verify_agenda_lint


def _write_report(path: Path, body: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(body, encoding="utf-8")


def _write_agenda(path: Path, body: str) -> None:
  path.write_text(body, encoding="utf-8")


def test_missing_report(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing knowledge-vault/Logs/post_verify_report.md" in captured.err


def test_missing_agenda(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Run ID: 2024-01-01_HYP-0001\n\n## Items still open\nNone\n",
  )

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing AGENDA.md" in captured.err


def test_missing_hypothesis_id(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Summary\n\n## Items still open\nNone\n",
  )
  _write_agenda(tmp_path / "AGENDA.md", "## Active Hypotheses\n")

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "could not find hypothesis id" in captured.err


def test_missing_items_still_open_section(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Run ID: 2024-01-01_HYP-0002\nNo open section here\n",
  )
  _write_agenda(tmp_path / "AGENDA.md", "- [ ] ID: HYP-0002\nStatus: finished\n")

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing '## Items still open'" in captured.err


def test_mismatch_when_report_says_none_open(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Run ID: 2024-01-01_HYP-0003\n\n## Items still open\nNone\n",
  )
  _write_agenda(
    tmp_path / "AGENDA.md",
    "- [ ] ID: HYP-0003\nStatus: in-progress\n",
  )

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "expected 'finished'" in captured.err


def test_mismatch_when_items_open(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Run ID: 2024-01-01_HYP-0004\n\n## Items still open\n- Task remains\n",
  )
  _write_agenda(
    tmp_path / "AGENDA.md",
    "- [ ] ID: HYP-0004\nStatus: finished\n",
  )

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "AGENDA status for HYP-0004 is 'finished'" in captured.err


def test_matching_status(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_report(
    tmp_path / "knowledge-vault/Logs/post_verify_report.md",
    "Run ID: 2024-01-01_HYP-0005\n\n## Items still open\nNone\n",
  )
  _write_agenda(
    tmp_path / "AGENDA.md",
    "- [ ] ID: HYP-0005\nStatus: finished\n",
  )

  rc = post_verify_agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "post_verify_agenda_lint: OK" in captured.out
