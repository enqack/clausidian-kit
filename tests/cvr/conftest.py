"""pytest configuration for CVR (Canonical Verification Runtime) tests.

The CVR is the Python-based verification runtime for the ADK.
These tests verify the Python linters and tools in tools/cvr/.
"""

import sys
from pathlib import Path

# Add tools/cvr directories to path for CVR module imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "tools" / "cvr"))
sys.path.insert(0, str(repo_root / "tools" / "cvr" / "linters"))
