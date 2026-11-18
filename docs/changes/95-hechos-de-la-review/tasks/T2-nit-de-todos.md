---
id: T2
title: El informe de review-prepush recoge los TODO del script en un solo Nit
status: done
depends_on: [T1]
examples: [E6, E7]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: `review-prepush` ejecuta `review_facts.py` y pone sus TODO en el informe como un solo Nit, fuera de `Max Nits` y sin pasar por el verifier (R2, D-0057).

**Dentro:** el texto de `review-prepush` (cuándo ejecutar el script y cómo escribir el Nit) y de `review-report` (la excepción al límite de Nits y al verifier, y que el revisor no repite esos TODO). Los tests de texto en `scripts/check.sh`.

**Fuera:** sustituir los pasos 1 y 2 de la skill por el script (T5).

**Flag:** ninguno.
