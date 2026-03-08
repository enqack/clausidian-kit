import unittest
import tempfile
import os
from pathlib import Path
import sys
sys.path.append(os.path.abspath("tools/linters"))
from content_lint import count_words, check_structure, check_word_count

class TestContentLint(unittest.TestCase):
    def test_count_words_ignores_code(self):
        text = "Hello world `code` ```block```"
        self.assertEqual(count_words(text), 2)
        
    def test_check_structure(self):
        # implemention_plan.md needs Proposed Changes and Verification Plan
        p = Path("implementation_plan.md")
        valid = "# Plan\n## Proposed Changes\n## Verification Plan\n"
        self.assertEqual(check_structure(p, valid), [])
        
        invalid = "# Plan\n## Proposed Changes\n"
        self.assertEqual(check_structure(p, invalid), ["missing required section: '## Verification Plan'"])

    def test_check_word_count(self):
        # walkthrough.md needs 100 words
        p = Path("walkthrough.md")
        short = "word " * 90
        long = "word " * 110
        self.assertTrue(check_word_count(p, short))
        self.assertFalse(check_word_count(p, long))

if __name__ == "__main__":
    unittest.main()
