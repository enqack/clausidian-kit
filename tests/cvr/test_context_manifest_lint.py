from pathlib import Path

import context_manifest_lint


def test_missing_manifest(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)

  rc = context_manifest_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "missing knowledge-vault/Logs/context_manifest.md" in captured.err


def test_missing_required_fields(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  manifest = Path("knowledge-vault/Logs")
  manifest.mkdir(parents=True)
  (manifest / "context_manifest.md").write_text(
    "timestamp: now\noperating mode: auto\nfiles read: []\n", encoding="utf-8"
  )

  rc = context_manifest_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "context_manifest.md missing required fields: .agentsignore" in captured.err


def test_rejects_file_urls(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  manifest = Path("knowledge-vault/Logs")
  manifest.mkdir(parents=True)
  (manifest / "context_manifest.md").write_text(
    "timestamp: now\noperating mode: auto\nx.agentsignore: present\nfiles read: file://tmp/foo\n",
    encoding="utf-8",
  )

  rc = context_manifest_lint.main()
  captured = capsys.readouterr()

  assert rc == 1
  assert "contains file://" in captured.err


def test_valid_manifest(monkeypatch, tmp_path, capsys):
  monkeypatch.chdir(tmp_path)
  manifest = Path("knowledge-vault/Logs")
  manifest.mkdir(parents=True)
  (manifest / "context_manifest.md").write_text(
    "timestamp: now\nOperating Mode: auto\nx.agentsignore: present\nfiles read: docs/README.md\n",
    encoding="utf-8",
  )

  rc = context_manifest_lint.main()
  captured = capsys.readouterr()

  assert rc == 0
  assert "context_manifest_lint: OK" in captured.out
