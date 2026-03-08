from pathlib import Path

import post_verify_lint


REPORT_BASE = (
  "# Report\n\n"
  "## Completed items\nDone\n\n"
  "## Items still open\nNone\n\n"
  "## Evidence\n- docs/proof\n"
)


def test_missing_report(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = post_verify_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing knowledge-vault/Logs/post_verify_report.md" in captured.err


def test_missing_required_headings(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  report = Path("knowledge-vault/Logs/post_verify_report.md")
  report.parent.mkdir(parents=True)
  report.write_text("# Report\n\n## Completed items\nDone\n", encoding="utf-8")

  rc = post_verify_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing required headings" in captured.err


def test_path_bans(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  report = Path("knowledge-vault/Logs/post_verify_report.md")
  report.parent.mkdir(parents=True)
  report.write_text(
    REPORT_BASE + "file://tmp/log\n/abs/path\n...\n", encoding="utf-8"
  )

  rc = post_verify_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "file://" in captured.err or "absolute path" in captured.err or "contains '...'" in captured.err


def test_helper_failure_bubbles_up(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  report = Path("knowledge-vault/Logs/post_verify_report.md")
  report.parent.mkdir(parents=True)
  report.write_text(REPORT_BASE, encoding="utf-8")

  helper = tmp_path / "tools/post_verify_agenda_lint.py"
  helper.parent.mkdir(parents=True)
  helper.write_text("import sys; sys.stderr.write('agenda failed'); sys.exit(1)", encoding="utf-8")

  rc = post_verify_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "agenda failed" in captured.err


def test_success_with_helper(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  report = Path("knowledge-vault/Logs/post_verify_report.md")
  report.parent.mkdir(parents=True)
  report.write_text(REPORT_BASE, encoding="utf-8")

  helper = tmp_path / "tools/post_verify_agenda_lint.py"
  helper.parent.mkdir(parents=True)
  helper.write_text("import sys; sys.exit(0)", encoding="utf-8")

  rc = post_verify_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "post_verify_lint: OK" in captured.out
