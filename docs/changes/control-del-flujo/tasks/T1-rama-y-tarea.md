---
id: T1
title: gate.py reconoce la rama de una tarea y la rama del plan
status: done
depends_on: []
examples: [E1, E2, E3, E4, E5, E6, E7, E17, E18]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `skills/task-done/scripts/gate.py` decide qué comprobar según la rama (R1), de punta a punta, con sus códigos de salida.

**Dentro:** el script (rama actual o `GITHUB_HEAD_REF`, rama base como en `task_done.py`, `--require-task`, "cambio de código" = fuera de `docs/` y de los `*.md` de la raíz, salidas 0/1/2); sus tests en `scripts/check.sh` con repos de prueba.

**Fuera:** el audit (T2), el tamaño (T3), la lista de control (T4), cómo llega al proyecto (T5).

**Flag:** ninguno (nadie lo ejecuta hasta T5).
