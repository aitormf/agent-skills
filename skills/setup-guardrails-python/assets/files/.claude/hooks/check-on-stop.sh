#!/usr/bin/env bash
# .claude/hooks/check-on-stop.sh
# Stops Claude from considering the work done if check.sh does not pass.
# Why: docs/arnes/herramientas-arnes.md §4.4.
input=$(cat)
# Avoids infinite loops: if it already blocked once in this turn, let it finish.
if [ "$(echo "$input" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || exit 0
log=$(mktemp)
trap 'rm -f "$log"' EXIT
if ! ./scripts/check.sh >"$log" 2>&1; then
  echo "check.sh failed. Fix these errors before finishing:" >&2
  tail -n 40 "$log" >&2
  exit 2   # exit 2 = block and return the message to Claude
fi
