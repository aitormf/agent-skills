---
id: T4
title: El gate falla si la rama de una tarea toca un fichero de control
status: done
depends_on: [T1]
examples: [E27, E28]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: la rama de una tarea no cambia el arnés; la lista de control se lee de la rama base (R7).

**Dentro:** la lista por defecto del README del cambio, la ampliación del proyecto en su propio fichero (también de control), leída con `git show <base>:<fichero>`.

**Fuera:** la versión del gate que corre en CI (T5).

**Flag:** ninguno.
