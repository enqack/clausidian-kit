from pathlib import Path

import lint_common


def test_path_validators():
  assert lint_common.validate_no_file_urls("see file://tmp") is not None
  assert lint_common.validate_no_file_urls("relative/path") is None

  assert lint_common.validate_no_absolute_paths("/abs/path") is not None
  assert lint_common.validate_no_absolute_paths("docs/path") is None

  assert lint_common.validate_no_truncation("...") is not None
  assert lint_common.validate_no_truncation("complete") is None

  assert "file://" in lint_common.validate_paths("file://tmp/path")
  assert "absolute path" in lint_common.validate_paths("/abs/path only")
  assert "..." in lint_common.validate_paths("truncated ... evidence")


def test_find_run_artifact(monkeypatch, tmp_path):
  monkeypatch.chdir(tmp_path)
  assert lint_common.find_run_artifact("implementation_plan.json") is None

  runs_root = tmp_path / "knowledge-vault/Runs"
  run_a = runs_root / "run-a"
  run_a.mkdir(parents=True)
  run_b = runs_root / "run-b"
  run_b.mkdir()

  target = run_b / "implementation_plan.json"
  target.write_text("{}", encoding="utf-8")

  found = lint_common.find_run_artifact("implementation_plan.json")
  assert found is not None
  assert found.name == "implementation_plan.json"
  assert target.samefile(found)
