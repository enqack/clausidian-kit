from pathlib import Path

import lessons_lint


def test_missing_title(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("knowledge-vault/Lessons").mkdir(parents=True)
  Path("knowledge-vault/Lessons/lessons-learned.md").write_text("- Evidence: docs/log\n", encoding="utf-8")

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing title" in captured.err


def test_missing_evidence(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text("# Lessons Learned\n\n- Learned something\n", encoding="utf-8")

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing Evidence field" in captured.err


def test_rejects_file_urls(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text(
    "# Lessons Learned\n\n- Lesson\n- Evidence: file://tmp/log\n",
    encoding="utf-8",
  )

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "contains file://" in captured.err


def test_rejects_absolute_paths_and_truncation(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text(
    "# Lessons Learned\n\n- Lesson\n- Evidence: docs/log\n/abs/path/to/file\n...\n",
    encoding="utf-8",
  )

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "absolute path" in captured.err


def test_rejects_truncation(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text(
    "# Lessons Learned\n\n- Lesson\n- Evidence: docs/log\n...\n",
    encoding="utf-8",
  )

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "contains '...'" in captured.err


def test_code_blocks_ignored(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text(
    "# Lessons Learned\n\n"
    "- Lesson\n"
    "- Evidence: docs/log\n"
    "```\n/absolute/path\n```\n",
    encoding="utf-8",
  )

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "OK" in captured.out


def test_valid_lessons(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  p = Path("knowledge-vault/Lessons/lessons-learned.md")
  p.parent.mkdir(parents=True)
  p.write_text(
    "# Lessons Learned\n\n- Lesson A\n- Evidence: knowledge-vault/Runs/run-1/walkthrough.md\n",
    encoding="utf-8",
  )

  rc = lessons_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "lessons_lint: OK" in captured.out
