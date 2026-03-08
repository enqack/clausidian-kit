#!/usr/bin/env bash
set -euo pipefail

# Language-agnostic project test hook.
# This is the canonical place to define "project tests" for this workspace.
#
# Conventions:
# - Prefer deterministic, local tests.
# - Write any extra outputs to artifacts/test_results/ as needed.
#
# Default behavior:
# - If the project is recognized (Go/Rust/Node/Python), run standard tests.
# - Otherwise, print a message and exit 0.

mkdir -p artifacts/test_results

# Check for and source local virtual environment
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi


if [ -f go.mod ]; then
  echo "tools/test.sh: detected Go (go.mod) -> go test ./..."
  go test ./... | tee artifacts/test_results/go_test_output.txt
  exit 0
fi

if [ -f Cargo.toml ]; then
  echo "tools/test.sh: detected Rust (Cargo.toml) -> cargo test"
  cargo test | tee artifacts/test_results/cargo_test_output.txt
  exit 0
fi

if [ -f package.json ]; then
  echo "tools/test.sh: detected Node (package.json) -> npm test"
  # npm can be noisy; keep output captured
  npm test | tee artifacts/test_results/npm_test_output.txt
  exit 0
fi

# Python: only run if there is a python tests dir (avoid guessing other languages).
if [ -d tests ] && command -v python3 >/dev/null 2>&1; then
  # Prefer python -m pytest to ensure we use the same interpreter environment
  if python3 -c "import pytest" >/dev/null 2>&1; then
    echo "tools/test.sh: detected Python tests -> pytest (module)"
    python3 -m pytest -q | tee artifacts/test_results/pytest_output.txt
    exit 0
  fi
  
  if command -v pytest >/dev/null 2>&1; then
     echo "tools/test.sh: detected Python tests -> pytest (binary)"
     pytest -q | tee artifacts/test_results/pytest_output.txt
     exit 0
  fi
  
  echo "tools/test.sh: detected Python tests -> unittest"
  PYTHONPATH=tools/cvr:tools/cvr/linters python3 -m unittest discover -s tests -p "test*.py" | tee artifacts/test_results/unittest_output.txt
  exit 0
fi

echo "tools/test.sh: no recognized test runner. Define tests here if applicable."
exit 0
