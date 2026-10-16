#!/usr/bin/env bash
# scripts/check.sh: verificación completa. Debe pasar antes de dar algo por terminado.
# Lo ejecutan las personas, el agente (hook Stop) y CI: una sola definición de "está bien".
# Quita las líneas de lo que aún no uses; brownfield: empieza con lo que haya hoy.
set -euo pipefail

echo "▶ formato";       uv run ruff format --check .
echo "▶ lint";          uv run ruff check .
echo "▶ tipos";         uv run mypy
# echo "▶ arquitectura";  uv run lint-imports
echo "▶ tests";         uv run pytest --cov
echo "✔ todo en verde"
