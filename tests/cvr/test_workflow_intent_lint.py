from pathlib import Path

import workflow_intent_lint


def test_missing_workflows(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = workflow_intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing .claude/skills directory" in captured.err


def test_workflow_missing_intent(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  skill_dir = Path(".claude/skills/adk-build")
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text("Steps only", encoding="utf-8")

  rc = workflow_intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "workflows missing intent requirement" in captured.err


def test_compliant_workflows(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  ei_dir = Path(".claude/skills/adk-establish-intent")
  ei_dir.mkdir(parents=True)
  (ei_dir / "SKILL.md").write_text("bootstrap", encoding="utf-8")
  work_dir = Path(".claude/skills/adk-work")
  work_dir.mkdir(parents=True)
  (work_dir / "SKILL.md").write_text(
    "Precondition: knowledge-vault/Intent/project_intent.md must exist", encoding="utf-8"
  )

  rc = workflow_intent_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "workflow_intent_lint: OK" in captured.out
