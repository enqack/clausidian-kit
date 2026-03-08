# CVR Tests

Tests for the Canonical Verification Runtime (CVR) - the Python-based verification tooling in `tools/cvr/`.

## Running Tests

```bash
source .venv/bin/activate
pytest tests/cvr/
```

Or via the test script:

```bash
source .venv/bin/activate
tools/test.sh
```

## Structure

- **Linter tests**: `test_*_lint.py` - Tests for individual linters in `tools/cvr/linters/`
- **Tool tests**: `test_aggregate_history.py`, `test_journal.py`, `test_close_run.py` - Tests for core CVR tools
- **Common utilities**: `test_lint_common.py` - Tests for shared linter utilities

## Path Setup

The `conftest.py` file configures pytest to find CVR modules by adding `tools/cvr/` and `tools/cvr/linters/` to the Python path. This allows tests to import modules directly:

```python
import intent_lint
from aggregate_history import main
```

## Adding New Tests

1. Create test file in `tests/cvr/` following pytest naming convention: `test_*.py`
2. Import CVR modules directly (path is configured by conftest.py)
3. Write tests using pytest conventions
4. Run with `pytest tests/cvr/test_yourfile.py`
