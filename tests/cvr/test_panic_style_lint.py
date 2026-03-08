from pathlib import Path

import panic_style_lint


def test_missing_workflows_dir(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = panic_style_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing .claude/skills directory" in captured.err


def test_banned_phrases(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  skill_dir = Path(".claude/skills/adk-override")
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text("Please override this check", encoding="utf-8")

  rc = panic_style_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "banned phrase" in captured.err


def test_missing_canonical_intent_question(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  skill_dir = Path(".claude/skills/adk-plan")
  skill_dir.mkdir(parents=True)
  (skill_dir / "SKILL.md").write_text(
    "Precondition: establish-intent\nSteps:\n- Do work\n", encoding="utf-8"
  )

  rc = panic_style_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing canonical intent question text" in captured.err


def test_compliant_workflows(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  ei_dir = Path(".claude/skills/adk-establish-intent")
  ei_dir.mkdir(parents=True)
  (ei_dir / "SKILL.md").write_text("Bootstrap", encoding="utf-8")
  main_dir = Path(".claude/skills/adk-main")
  main_dir.mkdir(parents=True)
  (main_dir / "SKILL.md").write_text(
    "Precondition: establish-intent\n\n"
    f"{panic_style_lint.CANON_Q}\n",
    encoding="utf-8",
  )

  rc = panic_style_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "panic_style_lint: OK" in captured.out
