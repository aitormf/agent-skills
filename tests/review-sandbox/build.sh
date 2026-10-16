#!/usr/bin/env bash
# Builds the sandbox git repo at examples/sandbox/repo from the layers/ directory:
#   main                                 ← layers/main + review skills and agents in .claude/ + pre-push hook
#   feature/orders-pagination-invoices   ← layers/feature on top (contains the planted bugs)
# Re-running deletes and recreates repo/.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$(cd "$HERE/../.." && pwd)"   # root of agent-skills
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
cp "$KIT/skills/review-prepush/assets/pre-push" .git/hooks/pre-push && chmod +x .git/hooks/pre-push
git add -A && git commit -q -m "Install review skills"

git switch -q -c feature/orders-pagination-invoices
cp -R "$HERE/layers/feature/." .
git add -A && git commit -q -m "Añadir paginación a /orders y endpoint /invoices para descargar facturas

- GET /orders?page=N&size=M (páginas 1-indexadas, tamaño máx. 50)
- GET /invoices?file=<nombre> devuelve el PDF de la factura"

echo "Sandbox listo en $REPO (rama $(git branch --show-current))"
git log --oneline --all
