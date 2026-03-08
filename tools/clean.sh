#!/usr/bin/env bash
set -euo pipefail

# clean.sh - Removes build artifacts, caches, and temporary files.

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "Cleaning up Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "Cleaning up coverage reports..."
find . -type f -name ".coverage" -delete
find . -type d -name "htmlcov" -exec rm -rf {} +

echo "Cleaning up test artifacts..."
if [ -d "knowledge-vault/Logs/test_results" ]; then
    find knowledge-vault/Logs/test_results -mindepth 1 -delete
fi

echo "Done."
