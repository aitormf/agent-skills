#!/usr/bin/env bash
# Builds the sandbox git repo at examples/sandbox/repo from the layers/ directory:
#   main                                 ← layers/main + review skills and agents in .claude/ + pre-push hook
#   feature/orders-pagination-invoices   ← layers/feature on top (contains the planted bugs)
# Re-running deletes and recreates repo/.
#
# Option --codex: installs also the Codex layout (skills in .agents/skills/, agents in .codex/agents/*.toml),
# so `codex exec` run inside repo/ sees the review skills and personas. See measure.sh.
set -euo pipefail
CODEX=0
case "${1:-}" in
  "") ;;
  --codex) CODEX=1 ;;
  *) echo "uso: build.sh [--codex]" >&2; exit 2 ;;
esac
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="${KIT:-$(cd "$HERE/../.." && pwd)}"   # root of agent-skills; KIT=<dir> copies skills, agents and adapters from another checkout (a worktree at the commit to measure)
REPO="$HERE/repo"

rm -rf "$REPO"; mkdir -p "$REPO"; cd "$REPO"
git init -q -b main
git config user.name "Sandbox Dev"; git config user.email "sandbox@example.invalid"
git config commit.gpgsign false

cp -R "$HERE/layers/main/." .
git add -A && git commit -q -m "Initial orders service"

# Same layout npx skills / a manual copy leaves: un-namespaced skills, so the hook runs /review-prepush.
mkdir -p .claude/skills .claude/agents
for skill in code-review-and-quality review-context review-report review-prepush review-pr; do
  cp -R "$KIT/skills/$skill" .claude/skills/
done
for agent in code-reviewer security-auditor test-engineer finding-verifier; do
  cp "$KIT/agents/$agent.md" .claude/agents/
done
if [ "$CODEX" = 1 ]; then
  mkdir -p .agents/skills .codex/agents
  for skill in code-review-and-quality review-context review-report review-prepush review-pr task-done; do
    cp -R "$KIT/skills/$skill" .agents/skills/
  done
  cp "$KIT"/adapters/codex/agents/{code-reviewer,security-auditor,test-engineer,finding-verifier}.toml .codex/agents/
fi
printf '#!/usr/bin/env bash\nexec bash "%s/skills/review-prepush/scripts/harness-review.sh"\n' "$KIT" > .git/hooks/pre-push && chmod +x .git/hooks/pre-push
git add -A && git commit -q -m "Install review skills"

git switch -q -c feature/orders-pagination-invoices
cp -R "$HERE/layers/feature/." .
git add -A && git commit -q -m "Añadir paginación a /orders y endpoint /invoices para descargar facturas

- GET /orders?page=N&size=M (páginas 1-indexadas, tamaño máx. 50)
- listOrders devuelve los pedidos más recientes primero
- GET /invoices?file=<nombre> devuelve el PDF de la factura"

echo "Sandbox listo en $REPO (rama $(git branch --show-current))"
git log --oneline --all
