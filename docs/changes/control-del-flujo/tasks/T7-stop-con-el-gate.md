---
id: T7
title: Claude Code no termina el turno con el gate en rojo, salvo a la segunda parada seguida
status: todo
depends_on: [T5]
examples: [E22, E23, E24]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: un hook Stop ejecuta `pre-commit run kit-gate --hook-stage manual` y bloquea si falla, salvo con `stop_hook_active` (R6).

**Dentro:** `.claude/hooks/kit-gate-on-stop.sh` en la plantilla de `setup-guardrails-python` (lee el JSON de la entrada, sale 2 con la salida del gate), y su entrada en el `Stop` de la plantilla `.claude/settings.json`, junto a `check-on-stop.sh`.

**Fuera:** cambiar `check-on-stop.sh`.

**Flag:** ninguno.
