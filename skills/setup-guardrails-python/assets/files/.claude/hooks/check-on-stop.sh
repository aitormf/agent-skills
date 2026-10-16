#!/usr/bin/env bash
# .claude/hooks/check-on-stop.sh
# Impide que Claude dé el trabajo por terminado si check.sh no pasa.
# Por qué: docs/arnes/herramientas-arnes.md §4.4.
input=$(cat)
# Evita bucles infinitos: si ya se bloqueó una vez en este turno, deja terminar.
if [ "$(echo "$input" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || exit 0
log=$(mktemp)
trap 'rm -f "$log"' EXIT
if ! ./scripts/check.sh >"$log" 2>&1; then
  echo "check.sh ha fallado. Corrige estos errores antes de terminar:" >&2
  tail -n 40 "$log" >&2
  exit 2   # exit 2 = bloquear y devolver el mensaje a Claude
fi
