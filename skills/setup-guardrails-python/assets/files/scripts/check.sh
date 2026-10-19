#!/usr/bin/env bash
# scripts/check.sh: full verification. Must pass before considering anything done.
# Run by people, the agent (Stop hook) and CI: a single definition of "it is fine".
# Remove the lines for what you do not use yet; brownfield: start with what exists today.
set -euo pipefail

echo "▶ format";       uv run ruff format --check .
echo "▶ lint";          uv run ruff check .
echo "▶ types";         uv run mypy
# echo "▶ architecture";  uv run lint-imports
echo "▶ tests";         uv run pytest --cov
echo "✔ all green"
