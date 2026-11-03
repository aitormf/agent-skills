---
id: T8
title: Documentar la review por tamaño y las tareas atómicas
status: todo
depends_on: [T4, T5, T6, T7]
examples: []
verification: scripts/check.sh
---
**Propósito:** documentación: que las guías para personas digan lo que ya hacen las skills.

**Dentro:** `docs/review/README.md` (tabla "Cuándo usar cada una" con el coste por tamaño, `--deep`, la recomendación de usar `review-prepush` en local), `docs/review/orchestration-addendum.md` (el fan-out pasa a ser para diffs de más de 200 líneas, con referencia a D-0045), `README.md` y `docs/sdd/README.md` (150 → 200 con tests, tarea atómica).

**Fuera:** el modelo de Codex (T9).

**Flag:** ninguno.
