from pathlib import Path

import evidence_location_lint


def test_no_test_results_dir_ok(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = evidence_location_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "evidence_location_lint: OK" in captured.out


def test_lint_logs_in_test_results_fail(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  bad_dir = Path("knowledge-vault/Logs/test_results")
  bad_dir.mkdir(parents=True)
  (bad_dir / "sample-lint.log").write_text("lint output", encoding="utf-8")
  (bad_dir / "other.log").write_text("ok", encoding="utf-8")

  rc = evidence_location_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "knowledge-vault/Logs/test_results/sample-lint.log" in captured.err
