---
id: T20
title: Repetir la medición base con esfuerzo medium
status: todo
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** preparación: tener una base comparable con el uso real, porque T17 midió con el esfuerzo `low` que `gpt-6.1-terra` trae por defecto (S5).

**Dentro:** una opción de esfuerzo en `measure.sh`, con `medium` por defecto, registrada en `meta.json`; una comprobación en `summarize.py` que invalida una ejecución si algún agente no corre con ese modelo y ese esfuerzo; 3 ejecuciones de cada comando con las skills y personas del commit `20c832c`, anterior a T15, para medir la review de antes del cambio; los resultados en `docs/review/medicion-review.md`, junto a los de T17, que siguen siendo válidos para `low`.

**Fuera:** cambiar la review; sacar conclusiones sobre el reviewer unificado.

**Flag:** ninguno.
