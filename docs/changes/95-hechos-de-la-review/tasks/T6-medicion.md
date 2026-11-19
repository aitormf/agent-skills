---
id: T6
title: Medir la review con el script de hechos frente a T9
status: done
depends_on: [T5]
examples: []
verification: scripts/check.sh
---

**Propósito:** preparación: medir el change con `tests/review-sandbox` y dejarlo escrito en `docs/review/medicion-review.md`.

**Dentro:** 3 ejecuciones de `review-prepush` con `build.sh --codex` y `measure.sh`, con `gpt-6.1-terra` y esfuerzo `medium`, comparadas con T9: B encontradas (con B5), llamadas y entrada de la sesión principal, entrada total y tiempo. Los artefactos van en `docs/review/medicion-review/`. Si B5 no aparece o la entrada no baja, se dice tal cual.

**Fuera:** cambiar las skills a partir de lo que salga (otro change).

**Flag:** ninguno.
