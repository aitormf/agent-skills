---
id: T10
title: Medición del reviewer unificado frente a la base
status: todo
depends_on: [T17, T4, T5, T11, T12, T13, T15, T16]
examples: []
verification: scripts/check.sh
---
**Propósito:** comprobar con datos que el reviewer unificado gasta menos sin perder hallazgos (S3).

**Dentro:** 3 ejecuciones de `review-prepush` y `review-pr` con el cambio, con `tests/review-sandbox/measure.sh`; la comparación con la base de T17 en `docs/review/medicion-review.md` (tokens por agente, total y sin caché; bugs y señuelos por ejecución). Si el unificado detecta menos B1–B6 que la base de forma consistente, se dice en la página y en la PR, y no se da el cambio por bueno hasta reforzar los disparadores (otra tarea).

**Fuera:** reforzar los disparadores en esta misma tarea.

**Flag:** ninguno.
