---
id: T10
title: Medición del reviewer unificado frente a la base
status: done
depends_on: [T20, T21, T4, T5, T11, T12, T13, T15, T16]
examples: []
verification: scripts/check.sh
---
**Propósito:** comprobar con datos que el reviewer unificado gasta menos sin perder hallazgos (S3).

**Dentro:** 3 ejecuciones de `review-prepush` y `review-pr` con el cambio, con `tests/review-sandbox/measure.sh`, `gpt-6.1-terra` y esfuerzo `medium`; la comparación con la base en `docs/review/medicion-review.md` (tokens por agente, total y sin caché; bugs y señuelos por ejecución): `review-prepush` contra la base `medium` de T20 y `review-pr` contra la base `low` de T17, porque T20 no tiene ninguna ejecución válida de `review-pr`; esa comparación dice en la página que mezcla dos esfuerzos. El efecto de T15 se mide aparte, porque la base mezcla los dos modos: con el mismo commit, 3 ejecuciones de `review-prepush` pidiendo en el prompt `fork_turns: "none"` y 3 pidiendo `"all"`, comparando entrada total, sin caché y la de la sesión principal. Si el unificado detecta menos B1–B6 que la base de forma consistente, se dice en la página y en la PR, y no se da el cambio por bueno hasta reforzar los disparadores (otra tarea).

**Fuera:** reforzar los disparadores en esta misma tarea.

**Flag:** ninguno.
