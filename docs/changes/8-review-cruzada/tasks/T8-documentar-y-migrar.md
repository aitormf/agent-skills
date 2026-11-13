---
id: T8
title: Documentar harness-review, [review] y cómo pasar del pre-push copiado al hook
status: done
depends_on: [T1, T2, T3, T4, T5, T6]
examples: []
verification: scripts/check.sh
---

**Propósito:** preparación: que un proyecto sepa instalar `harness-review`, configurar `[review]` y retirar el `.git/hooks/pre-push` copiado (S3).

**Dentro:** `docs/actualizar.md` (sección de la versión siguiente), README (la fila de la review en «Qué se garantiza»), `review-prepush` (el hook ya no se copia), `setup-guardrails-python` (`[review]` en `.harness-config.toml`), `docs/review/README.md` (la combinación recomendada); la comprobación de los textos en `scripts/check.sh`.

**Fuera:** subir la versión y el tag (se hace al publicar).

**Flag:** ninguno.
