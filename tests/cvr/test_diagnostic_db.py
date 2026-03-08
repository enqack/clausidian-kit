import unittest
import sys
import os
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Add linters to path
sys.path.append(os.path.abspath("tools/linters"))
import diagnostic_db

class TestDiagnosticDB(unittest.TestCase):
    def test_lookup_missing_db(self):
        # Should handle missing DB gracefully
        with TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir) / "rules.json"
            # It shouldn't exist
            db = diagnostic_db.DiagnosticDB(p)
            result = db.lookup("tool_name", "some message")
            self.assertIsNone(result)

    def test_lookup_exact_tool_mismatch(self):
        with TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir) / "rules.json"
            p.write_text(json.dumps({
                "rules": [
                    {
                        "tool": "other_tool",
                        "rule_id": "TEST_RULE",
                        "message_regex": "foo"
                    }
                ]
            }), encoding="utf-8")
            
            db = diagnostic_db.DiagnosticDB(p)
            result = db.lookup("my_tool", "foo")
            self.assertIsNone(result)

    def test_lookup_match(self):
        with TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir) / "rules.json"
            p.write_text(json.dumps({
                "rules": [
                    {
                        "tool": "my_tool",
                        "rule_id": "TEST_RULE",
                        "message_regex": "error: .* failed"
                    }
                ]
            }), encoding="utf-8")
            
            db = diagnostic_db.DiagnosticDB(p)
            result = db.lookup("my_tool", "error: something failed")
            self.assertIsNotNone(result)
            self.assertEqual(result["rule_id"], "TEST_RULE")

    def test_lookup_regex_no_match(self):
        with TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir) / "rules.json"
            p.write_text(json.dumps({
                "rules": [
                    {
                        "tool": "my_tool",
                        "rule_id": "TEST_RULE",
                        "message_regex": "error: .* failed"
                    }
                ]
            }), encoding="utf-8")
            
            db = diagnostic_db.DiagnosticDB(p)
            result = db.lookup("my_tool", "success: everything passed")
            self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
