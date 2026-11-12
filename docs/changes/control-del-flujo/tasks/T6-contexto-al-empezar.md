---
id: T6
title: Claude Code recibe la rama, la tarea y las reglas al empezar, reanudar o compactar
status: done
depends_on: [T5]
examples: [E19, E20, E21]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `gate.py --context` imprime el contexto de la sesión y un hook SessionStart lo inyecta (R5).

**Dentro:** el modo `--context` (nunca falla: sale 0 y avisa); un segundo hook `kit-context` en `.pre-commit-hooks.yaml` (`stages: [manual]`, `verbose: true`); el hook SessionStart (`startup|resume|compact`) en la plantilla `.claude/settings.json` de `setup-guardrails-python`.

**Fuera:** el Stop (T7).

**Flag:** ninguno.
