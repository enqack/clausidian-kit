import unittest
import tempfile
import shutil
import json
import datetime
from pathlib import Path
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

# We need to import close_run, but it depends on file system structure.
# We'll test the extraction and update logic primarily.

# Mocking the imports or using subprocess might be better for full E2E, 
# but let's try to import functions first.
sys.path.append(os.path.abspath("tools"))
from close_run import extract_lessons, update_global_lessons, main

class TestCloseRun(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)
        
    def test_extract_lessons(self):
        run_dir = Path("knowledge-vault/Runs/test_run")
        run_dir.mkdir(parents=True)
        wt = run_dir / "walkthrough.md"
        wt.write_text("# Walkthrough\n\n## Lessons Learned\n- Lesson 1\n- Lesson 2\n\n## Other\n", encoding="utf-8")
        
        lessons = extract_lessons(run_dir)
        self.assertEqual(lessons, ["Lesson 1", "Lesson 2"])
        
    def test_extract_lessons_empty(self):
        run_dir = Path("knowledge-vault/Runs/test_run")
        run_dir.mkdir(parents=True)
        wt = run_dir / "walkthrough.md"
        wt.write_text("# Walkthrough\n\nNo lessons section\n", encoding="utf-8")
        
        lessons = extract_lessons(run_dir)
        self.assertEqual(lessons, [])

    def test_update_global_lessons(self):
        global_dir = Path("knowledge-vault/Lessons")
        global_dir.mkdir(parents=True)

        lessons = ["New Lesson"]
        added = update_global_lessons(lessons, "test_run")

        f = global_dir / "lessons-learned.md"
        self.assertTrue(f.exists())
        content = f.read_text()
        self.assertEqual(added, 4)
        self.assertIn("**Lesson**: New Lesson.", content)

    def test_update_global_lessons_dedup(self):
        global_dir = Path("knowledge-vault/Lessons")
        global_dir.mkdir(parents=True)

        existing = global_dir / "lessons-learned.md"
        existing.write_text(
            "# Lessons Learned\n\n- Old Lesson (from [old_run](runs/old_run/walkthrough.md))\n",
            encoding="utf-8",
        )

        added = update_global_lessons(["Old Lesson", "New Lesson"], "new_run")

        content = existing.read_text()
        self.assertEqual(added, 7)
        self.assertEqual(content.count("Old Lesson"), 3)
        self.assertIn("**Lesson**: New Lesson.", content)

    def test_main_no_runs(self):
        with patch.object(sys, "argv", ["close_run"]):
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = main()
        self.assertEqual(rc, 1)
        self.assertIn("close_run: ERROR: no runs found", stderr.getvalue())

    def test_main_missing_plan(self):
        run_dir = Path("knowledge-vault/Runs/run-123")
        run_dir.mkdir(parents=True)

        with patch.object(sys, "argv", ["close_run", "run-123"]):
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = main()

        self.assertEqual(rc, 1)
        self.assertIn("close_run: Closing run: run-123", stdout.getvalue())
        self.assertIn("close_run: ERROR: missing implementation_plan.md", stderr.getvalue())

    def test_main_success_writes_closure(self):
        run_dir = Path("knowledge-vault/Runs/run-456")
        run_dir.mkdir(parents=True)
        (run_dir / "implementation_plan.md").write_text("# plan", encoding="utf-8")

        with patch.object(sys, "argv", ["close_run"]):
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = main()

        self.assertEqual(rc, 0)
        closure_path = run_dir / "closure.json"
        self.assertTrue(closure_path.exists())
        closure = json.loads(closure_path.read_text())

        for key in ("closed_at", "final_status", "lessons_extracted", "lessons_added"):
            self.assertIn(key, closure)

        self.assertEqual(closure["final_status"], "closed")
        self.assertIsNotNone(datetime.datetime.fromisoformat(closure["closed_at"]).tzinfo)
        output = stdout.getvalue()
        self.assertIn("Generating journal artifact for the run", output)
        self.assertIn("Journal written to knowledge-vault/Journal/run-456.md", output)
        self.assertIn("Run run-456 closed successfully.", output)

    def test_main_generates_journal(self):
        run_dir = Path("knowledge-vault/Runs/run-789")
        run_dir.mkdir(parents=True)
        (run_dir / "implementation_plan.md").write_text("# plan", encoding="utf-8")
        (run_dir / "implementation_plan.json").write_text(
            json.dumps({
                "items": [
                    {"id": "B", "hypothesis": "Hyp B", "status": "done", "evidence": {"required_artifacts": ["b.md", "a.md"]}},
                    {"id": "A", "hypothesis": "Hyp A"},
                ]
            }),
            encoding="utf-8",
        )
        (run_dir / "walkthrough.md").write_text("# Walkthrough\n\n## Lessons Learned\n- Learned A\n- Learned B\n", encoding="utf-8")

        with patch.object(sys, "argv", ["close_run", "run-789"]):
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = main()

        self.assertEqual(rc, 0)
        # knowledge-vault/Journal is at repo root. test_dir/knowledge-vault/Journal
        journal_path = Path("knowledge-vault/Journal/run-789.md")
        self.assertTrue(journal_path.exists())
        content = journal_path.read_text(encoding="utf-8")
        self.assertIn("**Run run-789**", content)
        self.assertIn("Learned A", content)
        self.assertIn("Journal written to", stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
