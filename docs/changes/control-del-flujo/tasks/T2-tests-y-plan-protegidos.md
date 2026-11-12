---
id: T2
title: El gate exige el audit de task-done y protege el plan en la rama de la tarea
status: done
depends_on: [T1]
examples: [E8, E9, E10, E11, E25, E26]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: en la rama de una tarea, el gate falla si el audit de `task_done.py` falla o si la rama cambia el plan aprobado (R2).

**Dentro:** llamar a `task_done.py --audit` y propagar sus líneas `PROBLEM`; comparar `examples`, `verification` y `depends_on` del fichero de la tarea con la rama base; fallar si se toca el fichero de otra tarea.

**Fuera:** repetir la lógica del audit; el tamaño (T3).

**Flag:** ninguno.
