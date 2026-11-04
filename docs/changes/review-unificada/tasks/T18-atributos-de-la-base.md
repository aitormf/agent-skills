---
id: T18
title: diff_size.py lee los atributos de la base del diff
status: done
depends_on: [T2]
examples: [E34, E35]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: una rama no puede rebajar su propio tamaño marcando ficheros como generados, porque los atributos se leen de la merge base del rango y no del árbol de trabajo (R1).

**Dentro:** `skills/review-context/scripts/diff_size.py`, con `git check-attr --source=<merge base>` si la versión de git lo permite, y qué hace si no; sus casos en `check.sh` nombrados E34–E35.

**Fuera:** los permisos (T19); usar el script desde las skills (T4, T5, T7).

**Flag:** ninguno.
