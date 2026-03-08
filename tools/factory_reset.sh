#!/usr/bin/env bash
set -euo pipefail

# factory_reset.sh - Destructively resets the Obsidian knowledge vault to a clean state.
# USE WITH CAUTION.

FORCE=false
INCLUDE_INTENT=false
DRY_RUN=false
VERBOSE=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --force)
      FORCE=true
      shift
      ;;
    --include-intent)
      INCLUDE_INTENT=true
      shift
      ;;
    --dry-run|-n)
      DRY_RUN=true
      shift
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    *)
      ;;
  esac
done

if [ "$FORCE" != "true" ] && [ "$DRY_RUN" != "true" ]; then
  echo "ERROR: This tool is destructive. You must pass --force to run it."
  echo "Usage: ./tools/factory_reset.sh --force [--include-intent] [--dry-run] [--verbose]"
  echo "  --include-intent: Also delete knowledge-vault/Intent/project_intent.md"
  echo "  --dry-run, -n   : Show what would be deleted without doing it"
  echo "  --verbose, -v   : Verbose output"
  exit 1
fi

log() {
  if [ "$VERBOSE" = "true" ] || [ "$DRY_RUN" = "true" ]; then
    echo "$@"
  fi
}

# Helper to remove all contents of a vault directory (preserves the dir itself)
clear_vault_dir() {
  local dir="$1"
  local description="$2"

  if [ -d "$dir" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "[DRY-RUN] Would clear $dir ($description)"
    else
      log "Clearing $dir ($description)..."
      find "$dir" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +
    fi
  fi
}

# Helper to remove a single file
clean_file() {
  local path="$1"
  local description="$2"

  if [ -e "$path" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "[DRY-RUN] Would remove $path ($description)"
    else
      log "Removing $path ($description)..."
      rm -f "$path"
    fi
  fi
}

echo "initiating FACTORY RESET..."
if [ "$DRY_RUN" = "true" ]; then
  echo "(Mode: DRY-RUN. No changes will be made.)"
fi

# .obsidian/ is never touched — vault config is always preserved.

# 1. Clear run artifacts
clear_vault_dir "knowledge-vault/Runs" "Run artifacts"

# 2. Clear journals
clear_vault_dir "knowledge-vault/Journal" "Journal entries"

# 3. Clear activity daily notes
clear_vault_dir "knowledge-vault/Activity" "Activity log"

# 4. Clear history (run index and NDJSON ledger)
clear_vault_dir "knowledge-vault/History" "History"

# 5. Clear lessons learned
clear_vault_dir "knowledge-vault/Lessons" "Lessons"

# 6. Clear cursed knowledge
clear_vault_dir "knowledge-vault/Cursed Knowledge" "Cursed Knowledge"

# 7. Clear deep thoughts
clear_vault_dir "knowledge-vault/Deep Thoughts" "Deep Thoughts"

# 8. Clear logs
clear_vault_dir "knowledge-vault/Logs" "Logs"

# 9. Intent (preserved by default)
if [ "$INCLUDE_INTENT" = "true" ]; then
  clean_file "knowledge-vault/Intent/project_intent.md" "Project Intent"
else
  log "Preserving knowledge-vault/Intent/project_intent.md"
fi

# 10. Reset AGENDA.md
if [ "$DRY_RUN" = "true" ]; then
  log "[DRY-RUN] Would reset AGENDA.md to default state"
else
  cat > AGENDA.md <<EOF
# Agenda

**Status**: Active

## Active Hypotheses

- None.

## Blockers

- None.

## Deferred Risks

- None.
EOF
  log "Reset AGENDA.md"
fi

echo "Factory reset complete."
