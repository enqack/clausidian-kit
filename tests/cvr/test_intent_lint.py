from pathlib import Path

import intent_lint


def test_parse_frontmatter_ignores_comments_and_quotes():
  txt = """---
# comment
primary_domain: "software"
deliverable: 'ship'
---
body
"""
  fm = intent_lint.parse_frontmatter(txt)

  assert fm["primary_domain"] == "software"
  assert fm["deliverable"] == "ship"


def test_missing_intent_file(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing knowledge-vault/Intent/project_intent.md" in captured.err


def test_missing_frontmatter(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  intent_path = Path("knowledge-vault/Intent")
  intent_path.mkdir(parents=True)
  (intent_path / "project_intent.md").write_text("no frontmatter", encoding="utf-8")

  rc = intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing YAML frontmatter" in captured.err


def test_missing_required_keys(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  intent_path = Path("knowledge-vault/Intent")
  intent_path.mkdir(parents=True)
  (intent_path / "project_intent.md").write_text(
    """---
primary_domain: software
---
body
""",
    encoding="utf-8",
  )

  rc = intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing required keys" in captured.err
  assert "deliverable" in captured.err


def test_invalid_primary_domain(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  intent_path = Path("knowledge-vault/Intent")
  intent_path.mkdir(parents=True)
  (intent_path / "project_intent.md").write_text(
    """---
primary_domain: unknownish
deliverable: thing
first_milestone_done: done
constraints: none
non_goals: none
---
""",
    encoding="utf-8",
  )

  rc = intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "primary_domain must be one of" in captured.err


def test_valid_intent(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  intent_path = Path("knowledge-vault/Intent")
  intent_path.mkdir(parents=True)
  (intent_path / "project_intent.md").write_text(
    """---
primary_domain: software
deliverable: cli
first_milestone_done: tests green
constraints: none
non_goals: docs
---
""",
    encoding="utf-8",
  )

  rc = intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "intent_lint: OK" in captured.out
