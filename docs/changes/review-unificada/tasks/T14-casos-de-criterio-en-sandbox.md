---
id: T14
title: Casos plantados en el sandbox para el criterio de code-review-and-quality
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** preparación: que la medición detecte si el reviewer pierde el criterio que hoy le da `code-review-and-quality` (S0).

**Dentro:** en `tests/review-sandbox/layers/`, tres casos más en la rama feature: B7, un helper nuevo casi igual a uno que ya existe en main; B8, un refactor que mueve ramas a otro fichero sin quitar ninguna; B9, una función que el cambio deja sin llamadores. Sus filas en `EXPECTED.md` con la severidad esperada; `build.sh` sigue funcionando. Cada caso, pequeño: el diff del sandbox no debe pasar de 200 líneas, para medir el reviewer unificado.

**Fuera:** la medición (T1, T10).

**Flag:** ninguno.
