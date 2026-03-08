import json
import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch
from pathlib import Path

# Add linters to path
sys.path.append(os.path.abspath("tools/cvr/linters"))
import plan_lint

class TestPlanLint(unittest.TestCase):
    def setUp(self):
        # Capture stdout/stderr
        self.held_stdout = StringIO()
        self.held_stderr = StringIO()
        self.sys_stdout = sys.stdout
        self.sys_stderr = sys.stderr
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr
        
        # Save CWD
        self.old_cwd = os.getcwd()

    def tearDown(self):
        sys.stdout = self.sys_stdout
        sys.stderr = self.sys_stderr
        os.chdir(self.old_cwd)

    def test_missing_plan_file(self):
        # Create a temp dir using a context manager would be better, but for now 
        # let's just use a subdir or assume we are in a clean env? 
        # unittest doesn't have tmp_path fixture same as pytest.
        # We'll use TemporaryDirectory.
        from tempfile import TemporaryDirectory
        
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            rc = plan_lint.main(["plan_lint"])
            
            self.assertEqual(rc, 1)
            self.assertIn("implementation_plan.json not found", self.held_stderr.getvalue())

    def test_run_mode_missing_artifact(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)

            rc = plan_lint.main(["plan_lint", "--run"])

            self.assertEqual(rc, 1)
            self.assertIn("no knowledge-vault/Runs/**/implementation_plan.json found", self.held_stderr.getvalue())

    def test_malformed_json(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            p = Path("implementation_plan.json")
            p.write_text("{ invalid", encoding="utf-8")
            
            rc = plan_lint.main(["plan_lint"])
            
            self.assertEqual(rc, 1)
            # JSON error message varies slightly by python version, but typically contains "Expecting"
            self.assertRegex(self.held_stderr.getvalue(), r"implementation_plan\.json: .*")

    def test_lint_obj_validation(self):
        with self.assertRaises(ValueError):
            plan_lint.lint_obj({})
        with self.assertRaises(ValueError):
            plan_lint.lint_obj({"meta": {}, "items": []})

    def test_valid_plan_root(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            p = Path("implementation_plan.json")
            p.write_text(json.dumps({"meta": {"version": "1.0", "generated_at": "now", "operating_mode": "full-execution"}, "relevant_lessons": ["none"], "items": [
                {
                    "id": "HYP-0001",
                    "status": "proposed",
                    "hypothesis": "Valid hypothesis string > 10 chars",
                    "scope": {"components": ["core"], "files": []},
                    "invariants": ["none"],
                    "tasks": [{"step": 1, "description": "d", "done_definition": "d"}],
                    "tests": {"unit": [], "integration": [], "build": []},
                    "evidence": {"required_artifacts": ["dummy"]}
                }
            ]}), encoding="utf-8")
            
            rc = plan_lint.main(["plan_lint"])
            
            self.assertEqual(rc, 0)
            self.assertIn("plan_lint: OK", self.held_stdout.getvalue())

    def test_valid_plan_run_mode(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            run = Path("knowledge-vault/Runs/run-1")
            run.mkdir(parents=True)
            (run / "implementation_plan.json").write_text(
                json.dumps({"meta": {"version": "1.0", "generated_at": "now", "operating_mode": "full-execution"}, "relevant_lessons": ["none"], "items": [
                    {
                        "id": "HYP-0002",
                        "status": "proposed",
                        "hypothesis": "Valid hypothesis string > 10 chars",
                        "scope": {"components": ["core"], "files": []},
                        "invariants": ["none"],
                        "tasks": [{"step": 1, "description": "d", "done_definition": "d"}],
                        "tests": {"unit": [], "integration": [], "build": []},
                        "evidence": {"required_artifacts": ["dummy"]}
                    }
                ]}), encoding="utf-8"
            )
            
            rc = plan_lint.main(["plan_lint", "--run"])
            
            self.assertEqual(rc, 0)
            self.assertIn("knowledge-vault/Runs/run-1/implementation_plan.json", self.held_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
