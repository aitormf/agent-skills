---
id: T4
title: review_facts.py añade la tarea de la rama y la auditoría de task-done
status: done
depends_on: [T3]
examples: [E8, E11, E13]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el script añade a los hechos la tarea o el plan de la rama y la salida de `task_done.py --audit` (R3, D-0032).

**Dentro:** la carpeta del change y la tarea a partir de la rama (`<change>/T<n>` o `<change>/plan`, como en `gate.py`), con el fichero y su estado; la auditoría con su salida y su código de salida; «tarea: ninguna» sin carpeta; «auditoría: no comprobada (<motivo>)» si no se puede ejecutar. Los tests van en `scripts/check.sh`.

**Fuera:** que la skill use el script (T5).

**Flag:** ninguno.
