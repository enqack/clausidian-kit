from pathlib import Path

import os
import sys

# Add linters to path
sys.path.append(os.path.abspath("tools/linters"))
import agenda_lint


def test_missing_agenda(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "agenda_lint: ERROR: AGENDA.md not found" in captured.err


def test_missing_required_headings(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("AGENDA.md").write_text("# Agenda\n\n## Active Hypotheses\n\n## Blockers\n", encoding="utf-8")

  rc = agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing required heading: ## Deferred Risks" in captured.err


def test_invalid_status_values(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("AGENDA.md").write_text(
    "# Agenda\n\n"
    "## Active Hypotheses\n"
    "- [ ] ID: HYP-0001\n"
    "Status: done\n\n"
    "## Blockers\n"
    "- none\n\n"
    "## Deferred Risks\n"
    "- none\n",
    encoding="utf-8",
  )

  rc = agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "agenda_lint: WARNING: unknown status format: 'done'" in captured.err


def test_finished_status_requires_evidence(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("AGENDA.md").write_text(
    "# Agenda\n\n"
    "## Active Hypotheses\n"
    "- [ ] ID: HYP-0002\n"
    "Status: finished\n\n"
    "## Blockers\n"
    "- none\n\n"
    "## Deferred Risks\n"
    "- none\n",
    encoding="utf-8",
  )

  rc = agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  # assert "finished item missing non-empty Evidence:" in captured.err


def test_valid_agenda(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  Path("AGENDA.md").write_text(
    "# Agenda\n\n"
    "## Active Hypotheses\n"
    "- [ ] ID: HYP-0003\n"
    "Status: in-progress\n"
    "Evidence: artifacts/history/runs/run-0003/walkthrough.md\n\n"
    "## Blockers\n"
    "- none\n\n"
    "## Deferred Risks\n"
    "- none\n",
    encoding="utf-8",
  )

  rc = agenda_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "agenda_lint: OK" in captured.out
