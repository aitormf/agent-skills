---
id: T6
title: idea-to-change y plan-to-tasks proponen el tier de cada tarea
status: todo
depends_on: [T5]
examples: []
verification: scripts/check.sh
---
**Propósito:** cambio de regla en las skills: al escribir las tareas, proponen `tier` y `tier_reason` (por ejemplo: docs o renombres → `trivial`; `level: A`, auth, secretos o migraciones → `deep`; lo demás → `standard`).

**Dentro:**
- `skills/idea-to-change/SKILL.md`, `skills/plan-to-tasks/SKILL.md` y `skills/idea-to-change/assets/task.md`, con los adaptadores regenerados.
- Un check en `check.sh` que comprueba que las dos skills y la plantilla dicen lo mismo, como el check "test criterion".

**Fuera:** `implement` y `task-done`, que no usan el tier.

**Flag:** ninguno.
