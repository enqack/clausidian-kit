from pathlib import Path

import template_baseline_lint


def test_missing_requirements_file(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = template_baseline_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing verification requirements file" in captured.err


def test_missing_required_paths(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("requirements-verify.txt").write_text("deps", encoding="utf-8")

  rc = template_baseline_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing required template files/dirs" in captured.err


def test_valid_template(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("requirements-verify.txt").write_text("deps", encoding="utf-8")
  Path(".gitignore").write_text("", encoding="utf-8")
  Path(".agentsignore").write_text("", encoding="utf-8")
  Path("CLAUDE.md").write_text("", encoding="utf-8")
  Path("AGENDA.md").write_text("", encoding="utf-8")
  Path(".claude").mkdir()
  Path("knowledge-vault/Intent").mkdir(parents=True)

  rc = template_baseline_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "template_baseline_lint: OK" in captured.out
