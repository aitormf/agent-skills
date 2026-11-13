---
id: T5
title: El veredicto guardado recuerda la familia del revisor
status: todo
depends_on: [T3]
examples: [E21, E22]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: un veredicto guardado (D-0042) solo se reutiliza si su revisor no es de una familia autora del push actual (R6).

**Dentro:** guardar la familia del revisor en `.git/review-kit/verdicts`; ignorar al leer los veredictos de una familia autora; los veredictos antiguos sin familia no se reutilizan con un agente.

**Fuera:** cambiar la clave del diff.

**Flag:** ninguno.
