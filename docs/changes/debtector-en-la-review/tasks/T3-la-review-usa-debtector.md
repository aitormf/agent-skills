---
id: T3
title: La review usa los hallazgos de debtector como candidatos
status: todo
depends_on: [T1]
examples: [E14, E15, E16]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo. Los skills de review tratan la salida de debtector como hallazgos candidatos con `Source: debtector`, tanto si viene del fichero del hook como si la ejecutan ellos (R3, D-0063).

**Dentro:**

- `review-context` §2: la sección de debtector del fichero del hook se trata como la de Semgrep. Un paso nuevo, §2.7, ejecuta `debtector_diff.py <base>` sin el hook, solo si la rama base tiene `[review] debtector = true`. Con exit 2, escribe `debtector not available — skipped`. Sin la clave, no lo menciona. El paso dice que `debtector diff` solo reescribe su índice ignorado y un worktree temporal: es la excepción explícita a la regla de no cambiar estado.
- `review-report`: `debtector` entra en la lista de `Source`.
- `review-prepush` y `review-pr`: donde citan Semgrep por §2.6, citan también §2.7.
- Lo que `scripts/check.sh` tenga que comprobar de ese texto, si comprueba el de Semgrep.

**Fuera:** el script (T1) y el hook (T2).

**Flag:** ninguno. Sin la clave en la base, la review no cambia.
