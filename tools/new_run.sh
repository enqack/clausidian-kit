#!/usr/bin/env bash
# Generate a new run directory with canonical run ID format
# Usage: tools/new_run.sh [hypothesis-id]

set -euo pipefail

# Generate run ID in new format: YYYY-MM-DD-HH-MM-SS
RUN_ID=$(date -u +"%Y-%m-%d-%H-%M-%S")

# Optional hypothesis ID suffix
if [ $# -gt 0 ]; then
    HYP_ID="$1"
    RUN_ID="${RUN_ID}-${HYP_ID}"
fi

RUN_DIR="knowledge-vault/Runs/${RUN_ID}"

# Create run directory
mkdir -p "${RUN_DIR}"

# Create placeholder files
touch "${RUN_DIR}/implementation_plan.md"
touch "${RUN_DIR}/walkthrough.md"

echo "Created run directory: ${RUN_DIR}"
echo "Run ID: ${RUN_ID}"
