#!/usr/bin/env bash
set -euo pipefail

if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

# Add linters and CVR directories to Python path
if [ -d tools/cvr ]; then
  export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/tools/cvr:$(pwd)/tools/cvr/linters"
elif [ -d tools/linters ]; then
  export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/tools/linters"
fi

mkdir -p knowledge-vault/Logs/test_results knowledge-vault/Runs knowledge-vault/Intent

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# CVR directory (Canonical Verification Runtime)
# If forbidden in normal mode, this script will degrade gracefully.
CVR_DIR="tools/cvr"
[ -d "$CVR_DIR" ] || CVR_DIR="tools"

run_log() {
  local name="$1"
  shift
  local out="knowledge-vault/Logs/${name}.log"
  echo "==> ${name} @ ${ts}" | tee "${out}"
  echo "+ $*" | tee -a "${out}"
  ( "$@" ) >>"${out}" 2>&1
  echo "==> OK: ${name}" | tee -a "${out}"
}

# Check external tools
if [ -x tools/check_tools.sh ]; then
  if tools/check_tools.sh >/dev/null 2>&1; then
    # Tools present, enforce strictness
    run_log "format_md_check" python3 "$CVR_DIR/format_md.py" --check
  else
    echo "WARNING: Missing markdown tools (see tools/check_tools.sh). Skipping formatting checks."
  fi
fi

# Baseline template presence
if [ -f "$CVR_DIR/linters/template_baseline_lint.py" ]; then
  run_log "template_baseline_lint" python3 "$CVR_DIR/linters/template_baseline_lint.py"
fi

# Mechanical enforcement: workflows must require intent (except establish-intent)
if [ -f "$CVR_DIR/linters/workflow_intent_lint.py" ]; then
  run_log "workflow_intent_lint" python3 "$CVR_DIR/linters/workflow_intent_lint.py"
fi

# Panic messaging style enforcement (no override prompts)
if [ -f "$CVR_DIR/linters/panic_style_lint.py" ]; then
  run_log "panic_style_lint" python3 "$CVR_DIR/linters/panic_style_lint.py"
fi

# Intent must exist for any real work. (Fail closed.)
if [ -f "$CVR_DIR/linters/intent_lint.py" ]; then
  run_log "intent_lint" python3 "$CVR_DIR/linters/intent_lint.py"
fi

# Lints
if [ -f "$CVR_DIR/linters/agenda_lint.py" ]; then run_log "agenda_lint" python3 "$CVR_DIR/linters/agenda_lint.py"; fi
if [ -f "$CVR_DIR/linters/context_manifest_lint.py" ] && [ -f knowledge-vault/Logs/context_manifest.md ]; then
  run_log "context_manifest_lint" python3 "$CVR_DIR/linters/context_manifest_lint.py"
fi
if [ -f "$CVR_DIR/linters/post_verify_lint.py" ] && [ -f knowledge-vault/Logs/post_verify_report.md ]; then
  run_log "post_verify_lint" python3 "$CVR_DIR/linters/post_verify_lint.py"
fi
if [ -f "$CVR_DIR/linters/lessons_lint.py" ] && [ -f knowledge-vault/Lessons/lessons-learned.md ]; then
  run_log "lessons_lint" python3 "$CVR_DIR/linters/lessons_lint.py"
fi
if [ -f "$CVR_DIR/linters/walkthrough_lint.py" ]; then
  # Only run if a walkthrough exists (root or in runs/)
  if [ -f walkthrough.md ] || find knowledge-vault/Runs -name "walkthrough.md" -type f 2>/dev/null | grep -q .; then
    run_log "walkthrough_lint" python3 "$CVR_DIR/linters/walkthrough_lint.py"
  fi
fi
if [ -f "$CVR_DIR/linters/run_artifacts_lint.py" ] && [ -d knowledge-vault/Runs ]; then
  run_log "run_artifacts_lint" python3 "$CVR_DIR/linters/run_artifacts_lint.py"
fi
if [ -f "$CVR_DIR/linters/evidence_location_lint.py" ]; then
  run_log "evidence_location_lint" python3 "$CVR_DIR/linters/evidence_location_lint.py"
fi
if [ -f "$CVR_DIR/linters/journal_lint.py" ]; then
  run_log "journal_lint" python3 "$CVR_DIR/linters/journal_lint.py"
fi
if [ -f "$CVR_DIR/linters/content_lint.py" ]; then
  run_log "content_lint" python3 "$CVR_DIR/linters/content_lint.py"
fi
if [ -f "$CVR_DIR/history_lint.py" ]; then
  run_log "history_lint" python3 "$CVR_DIR/history_lint.py"
else
  # Fallback to tools/cvr/linters/history_lint.py if moved (it was in plan to update, kept in linters/)
  if [ -f "$CVR_DIR/linters/history_lint.py" ]; then
    run_log "history_lint" python3 "$CVR_DIR/linters/history_lint.py"
  fi
fi

# Journal lint
if [ -f "$CVR_DIR/linters/journal_lint.py" ] && [ -d knowledge-vault/Journal ]; then
  # Only run if journals exist
  if ls knowledge-vault/Journal/*.md >/dev/null 2>&1; then
    run_log "journal_lint" python3 "$CVR_DIR/linters/journal_lint.py"
  fi
fi

# Plan lint: validate run-dir plan if present, else root
if [ -f "$CVR_DIR/linters/plan_lint.py" ]; then
  if find knowledge-vault/Runs -name "implementation_plan.json" -type f 2>/dev/null | grep -q .; then
    run_log "plan_lint_run" python3 "$CVR_DIR/linters/plan_lint.py" --run
  elif [ -f implementation_plan.json ]; then
    run_log "plan_lint_root" python3 "$CVR_DIR/linters/plan_lint.py"
  fi
fi

# Project tests (language-agnostic hook)
if [ -x tools/test.sh ]; then
  run_log "project_tests" tools/test.sh
else
  echo "verify_all: tools/test.sh not present/executable; skipping project tests"
fi

echo "verify_all: OK"
