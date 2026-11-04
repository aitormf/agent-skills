---
id: T13
title: Quitar de las personas las plantillas de salida que contradicen review-report
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** refactor: borrar el "Output Format" y el "Review Output Template" de `code-reviewer`, el "Test Coverage Analysis" de `test-engineer` y el "Security Audit Report" de `security-auditor`; cada uno remite a `review-report` §3 en una línea.

**Dentro:** los tres agentes, sus adaptadores regenerados y la nota de cambios en `docs/review/UPSTREAM.md`. La escala de severidad de `security-auditor` se queda (la usa el mapeo de §2).

**Fuera:** la salida compacta (T6).

**Flag:** ninguno.
