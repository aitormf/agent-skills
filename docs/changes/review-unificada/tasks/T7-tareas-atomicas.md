---
id: T7
title: Tareas atómicas de como mucho 200 líneas con los tests
status: todo
depends_on: [T2]
examples: [E20, E21, E22, E23, E24]
verification: scripts/check.sh
---
**Propósito:** cambio de regla: las skills que parten, implementan y revisan tareas aplican D-0044 en lugar de D-0033.

**Dentro:** "Small" y "One purpose" en `skills/idea-to-change/SKILL.md` y `skills/plan-to-tasks/SKILL.md` (200 líneas con tests; un solo cambio, una frase sin "y"); el límite en `agents/implement.md`; el hallazgo Optional de `agents/code-reviewer.md` con el recuento de `diff_size.py` y la referencia a D-0044 (D-0037 no cambia); adaptadores regenerados; checks en `check.sh` nombrados E20–E24 que comprueban que los cuatro textos dicen lo mismo (como el check "test criterion").

**Fuera:** la documentación para personas (T8); `spec-to-plan` y D-0039, que tratan del tamaño del plan, no de la tarea.

**Flag:** ninguno.
