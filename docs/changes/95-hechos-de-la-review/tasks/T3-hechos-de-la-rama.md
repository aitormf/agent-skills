---
id: T3
title: review_facts.py imprime la base, la rama, el log, el diff y el estado
status: todo
depends_on: [T1]
examples: [E9, E10, E12]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el script reúne en una llamada los hechos de la rama que hoy busca la sesión principal (R3).

**Dentro:** la resolución de la base (el argumento; si no hay, la sección Code review de `AGENTS.md`, `origin/HEAD`, `main` o `master`; y `origin/<base>` si existe), la rama, `git log <base>..HEAD`, `git diff --stat <base>...HEAD`, el aviso de cambios sin commit y «sin cambios frente a <base>» con salida 0. Los tests van en `scripts/check.sh`.

**Fuera:** la tarea y la auditoría (T4); que la skill use el script (T5).

**Flag:** ninguno.
