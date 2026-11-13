#!/usr/bin/env bash
# .claude/hooks/harness-gate-on-stop.sh
# Stops Claude from finishing the turn while the gate of the kit (harness-gate) is red.
# The second stop in a row goes through, warning that the gate is still red (R6).
input=$(cat)
cd "$CLAUDE_PROJECT_DIR" || exit 0
tool=$(command -v prek || command -v pre-commit) || {
  echo "harness-gate no se ha ejecutado: ni prek ni pre-commit están instalados." >&2
  exit 0
}
log=$(mktemp)
trap 'rm -f "$log"' EXIT
if "$tool" run harness-gate --hook-stage manual >"$log" 2>&1; then
  exit 0
fi
cat "$log" >&2
if [ "$(echo "$input" | jq -r '.stop_hook_active')" = "true" ]; then
  echo "El harness-gate sigue en rojo: puedes terminar, pero la PR no lo pasará." >&2
  exit 0
fi
exit 2   # exit 2 = block and return the message to Claude
