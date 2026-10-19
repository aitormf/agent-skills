#!/usr/bin/env bash
# Smoke test de skills/setup-guardrails-python: instala los assets en un proyecto uv nuevo
# siguiendo el orden de SKILL.md y comprueba que check.sh y los hooks funcionan.
# Requiere uv y jq. Necesita red (PyPI).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$ROOT/skills/setup-guardrails-python/assets"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cd "$TMP"
uv init -q --package demo >/dev/null
cd demo
uv python pin 3.13 >/dev/null

# El cooldown va antes de uv add (ver SKILL.md).
sed -n '/^\[tool.ruff\]/,$p' "$ASSETS/snippets/pyproject.toml" >> pyproject.toml
uv add -q --dev pytest pytest-cov ruff mypy
rsync -a --ignore-existing "$ASSETS/files/" ./
mkdir -p tests
printf 'from demo import main\n\n\ndef test_main() -> None:\n    main()\n' > tests/test_import.py
uv run ruff format -q .

fail() { echo "✘ $1" >&2; exit 1; }

./scripts/check.sh >/dev/null || fail "check.sh no sale en verde"
echo "✔ check.sh"

printf 'hola\xe2\x80\x8bmundo\n' > AGENTS.md
if uv run python scripts/check_hidden_unicode.py AGENTS.md >/dev/null; then fail "no detecta Unicode oculto"; fi
echo "✔ check_hidden_unicode.py"

hook=.claude/hooks/check_new_package.py
echo '{"tool_input":{"command":"uv add requests"}}' | uv run python "$hook" || fail "bloquea un paquete legítimo"
set +e
echo '{"tool_input":{"command":"uv add paquete-que-no-existe-xyz-123"}}' | uv run python "$hook" 2>/dev/null
code=$?
set -e
[ "$code" = 2 ] || fail "no bloquea un paquete inexistente (exit $code)"
echo "✔ check_new_package.py"
hook=.claude/hooks/ask_on_force_push.py
for cmd in "git push --force" "git push -f origin main" "git push origin +main" "git status && git push --force-with-lease"; do
  jq -nc --arg c "$cmd" '{tool_input:{command:$c}}' | uv run python "$hook" | grep -q '"ask"' || fail "no pregunta con: $cmd"
done
for cmd in "git push" "git push -u origin main"; do
  [ -z "$(jq -nc --arg c "$cmd" '{tool_input:{command:$c}}' | uv run python "$hook")" ] || fail "pregunta con un push normal: $cmd"
done
echo "✔ ask_on_force_push.py"
jq -e '.permission.bash' opencode.json >/dev/null || fail "opencode.json sin permission.bash"
if command -v codex >/dev/null; then
  for cmd in "git push --force" "git push origin -f main"; do
    codex execpolicy check --rules .codex/rules/guardrails.rules -- $cmd | grep -q '"prompt"' || fail "Codex no pregunta con: $cmd"
  done
  [ "$(codex execpolicy check --rules .codex/rules/guardrails.rules -- git push origin main)" = '{"matchedRules":[]}' ] \
    || fail "Codex pregunta con un push normal"
  echo "✔ .codex/rules/guardrails.rules"
else
  echo "  (codex no está instalado: se omiten las reglas de Codex)"
fi

echo '{"stop_hook_active":false}' | CLAUDE_PROJECT_DIR="$PWD" .claude/hooks/check-on-stop.sh || fail "el hook Stop bloquea con check.sh en verde"
echo 'x=1' > src/demo/roto.py   # sin formatear: check.sh debe fallar
set +e
echo '{"stop_hook_active":false}' | CLAUDE_PROJECT_DIR="$PWD" .claude/hooks/check-on-stop.sh 2>/dev/null
code=$?
set -e
[ "$code" = 2 ] || fail "el hook Stop no bloquea con check.sh en rojo (exit $code)"
echo "✔ check-on-stop.sh"

echo "✔ todo en verde"
