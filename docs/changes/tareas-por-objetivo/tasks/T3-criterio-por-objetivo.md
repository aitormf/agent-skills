---
id: T3
title: El plan parte por objetivo y el tamaño solo es una pista
status: done
depends_on: []
examples: [E1, E2, E3, E4, E5, E6, E8, E9]
verification: scripts/check.sh
---

**Propósito:** refactor de reglas: los textos que parten y revisan tareas pasan del límite de 200 líneas al criterio por objetivo, y el gate deja de avisar por el tamaño (R1, R2, D-0058, D-0059).

**Dentro:** `skills/idea-to-change/`, `skills/plan-to-tasks/`, `agents/implement.md` (no para por el tamaño) y `agents/code-reviewer.md` (señala los objetivos mezclados como Optional y nada por el tamaño solo), los adaptadores regenerados, el aviso de tamaño de `skills/task-done/scripts/gate.py`, y los tests de `scripts/check.sh` que hoy exigen «200 líneas» (D-0044, D-0053), que pasan a exigir el criterio nuevo.

**Fuera:** el corte en tramos (T1) y la review por tramos (T2); `diff_size.py`, que se sigue usando para contar.

**Flag:** ninguno.
