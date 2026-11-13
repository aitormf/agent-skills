---
id: T9
title: Medir la review cruzada con el sandbox
status: todo
depends_on: [T7, T8, T10]
examples: []
verification: scripts/check.sh
---

**Propósito:** preparación: comprobar con `tests/review-sandbox` que la review cruzada encuentra lo mismo que la de hoy (S2). Cierra el issue: `Closes #8`.

**Dentro:** `build.sh --codex` y un push de un agente Claude por `harness-review`, que revisa `codex` (`gpt-6.1-terra`, `medium`); el resultado en `docs/review/medicion-review.md`: B1–B6 detectados (6 de 6), ningún señuelo D1–D3 superviviente, tokens y duración. Si no llega a 6 de 6, la tarea lo dice y no se marca como hecha. Resultado: 5 de 6 en todas las ejecuciones; B5 se escapa también sin la review cruzada (diagnóstico en `medicion-review.md`), así que se acepta con la regresión de B5 aparte, en #90.

**Fuera:** recortar la orquestación (otro change).

**Flag:** ninguno.
