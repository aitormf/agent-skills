---
id: T6
title: Los agentes no se saltan los hooks del push por las vías normales
status: done
depends_on: []
examples: [E23, E24, E25]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: las plantillas de las tres herramientas impiden `--no-verify` y sus variantes en `git push` y `git commit` (R7; defensa en profundidad, la garantía es #77).

**Dentro:** un hook PreToolUse en la plantilla `.claude/` de `setup-guardrails-python` que analiza el comando como `ask_on_force_push.py` y deniega `--no-verify`, `commit -n`, `SKIP=`, `core.hooksPath` y `SKIP_CLAUDE_REVIEW`; `prefix_rule` con `decision = "forbidden"` en `.codex/rules/guardrails.rules`; `permission.bash` con `deny` en `opencode.json`. Los tests: el hook con JSON en la entrada, `codex execpolicy check` si está, y el JSON de OpenCode.

**Fuera:** el sandbox sin red y `harness push` (#77).

**Flag:** ninguno.
