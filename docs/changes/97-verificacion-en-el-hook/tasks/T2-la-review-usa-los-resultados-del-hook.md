---
id: T2
title: review-prepush usa los resultados del hook
status: todo
depends_on: [T1]
examples: [E13, E14]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo. Si `REVIEW_KIT_VERIFICATION` apunta a un fichero, el paso 2 de `review-prepush` (y `review-context` §2) no ejecuta comandos ni Semgrep. Cita el fichero en Verification y trata los hallazgos de Semgrep como candidatos (R4, D-0061).

**Dentro:** el texto de `review-prepush` y `review-context` y sus tests de texto en `scripts/check.sh`.

**Fuera:** `review-pr` y el hook (T1).

**Flag:** ninguno. Sin la variable, el paso 2 es el de hoy.
