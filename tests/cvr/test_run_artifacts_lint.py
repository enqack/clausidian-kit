from pathlib import Path

import run_artifacts_lint


def test_forbidden_root_artifacts(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("implementation_plan.md").write_text("plan", encoding="utf-8")
  Path("walkthrough.md").write_text("walkthrough", encoding="utf-8")

  rc = run_artifacts_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "root contains forbidden execution artifacts" in captured.err


def test_no_runs_ok(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = run_artifacts_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "OK (no runs)" in captured.out


def test_runs_missing_required_files(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  run_dir = Path("knowledge-vault/Runs/run-1")
  run_dir.mkdir(parents=True)

  rc = run_artifacts_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "implementation_plan.json" in captured.err


def test_runs_with_required_files(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  run_dir = Path("knowledge-vault/Runs/run-2")
  run_dir.mkdir(parents=True)
  (run_dir / "implementation_plan.json").write_text("{}", encoding="utf-8")
  (run_dir / "walkthrough.md").write_text("# Walkthrough", encoding="utf-8")

  rc = run_artifacts_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "run_artifacts_lint: OK" in captured.out
