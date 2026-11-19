---
id: T4
title: Medición de la review por tramos con el cambio 95
status: done
depends_on: [T1, T2]
examples: []
verification: scripts/check.sh
---

**Propósito:** preparación: medir la review por tramos y recomendar `max_lines_per_reviewer` con el dato.

**Dentro:** una rama con los commits de T2 a T6 de `95-hechos-de-la-review` revisada por tramos con `tests/review-sandbox` (Codex, `gpt-6.1-terra`, `medium`, 3 ejecuciones). Se compara con lo medido en T6: coste, hallazgos confirmados frente a refutados, hallazgos «falta X, que está en otro tramo» y lo que encuentra solo la pasada de costuras. El resultado va en `docs/review/medicion-review.md`, y la recomendación sobre `[review] max_lines_per_reviewer` (si se activa y con qué valor), con su justificación.

**Fuera:** tocar `.harness-config.toml` (fichero de control, D-0054: la persona pone el valor en `main`); cambiar el corte o la review según el resultado; si hace falta, es otro cambio.

**Flag:** ninguno.
