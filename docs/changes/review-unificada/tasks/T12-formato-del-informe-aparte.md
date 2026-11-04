---
id: T12
title: El formato del informe final, fuera de lo que cargan las personas
status: todo
depends_on: [T17]
examples: [E29]
verification: scripts/check.sh
---
**Propósito:** refactor: los layouts del informe (§4.1, §4.2) y el bloque JSON (§4.3) pasan a `skills/review-report/references/report-format.md`, que solo leen `review-prepush` y `review-pr` en la sesión principal (R6, D-0045).

**Dentro:** mover §4 a la referencia y dejar en `review-report` una línea que la señale; las referencias a "§4" en skills, agentes y docs apuntan a la referencia; el check del workflow de publish sigue en verde; check en `check.sh` nombrado E29 (las personas no citan §4; las dos skills de review leen la referencia).

**Fuera:** cambiar el contenido del formato.

**Flag:** ninguno.
