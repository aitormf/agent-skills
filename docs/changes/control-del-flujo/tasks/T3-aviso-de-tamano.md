---
id: T3
title: El gate avisa cuando la tarea pasa de 200 líneas
status: todo
depends_on: [T1]
examples: [E12, E13, E14]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: el gate cuenta el diff con `diff_size.py` y avisa por encima de 200 líneas, sin cambiar la salida (R3, D-0053).

**Dentro:** la llamada a `skills/review-context/scripts/diff_size.py` y el aviso.

**Fuera:** bloquear por tamaño (D-0053); cambiar cómo cuenta `diff_size.py` (D-0047).

**Flag:** ninguno.
