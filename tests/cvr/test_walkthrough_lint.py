from pathlib import Path

import walkthrough_lint


def _write_run_walkthrough(root: Path, content: str) -> Path:
  run = root / "knowledge-vault/Runs/run-1"
  run.mkdir(parents=True)
  wt = run / "walkthrough.md"
  wt.write_text(content, encoding="utf-8")
  return wt


def test_missing_walkthrough(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = walkthrough_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "no walkthrough.md found" in captured.err


def test_root_walkthrough_forbidden(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("walkthrough.md").write_text("# Root walkthrough", encoding="utf-8")

  rc = walkthrough_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "at repo root" in captured.err


def test_walkthrough_path_bans(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_run_walkthrough(tmp_path, "# WT\nfile://tmp\n/abs/path\n...\n")

  rc = walkthrough_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "walkthrough contains file:// URLs" in captured.err


def test_walkthrough_banned_brain(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  _write_run_walkthrough(tmp_path, "# WT\nArtifacts (Brain)\n")

  rc = walkthrough_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "Artifacts (Brain)" in captured.err


def test_valid_walkthrough(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  wt = _write_run_walkthrough(tmp_path, "# WT\nRelative evidence\n")

  rc = walkthrough_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "knowledge-vault/Runs/run-1/walkthrough.md" in captured.out
