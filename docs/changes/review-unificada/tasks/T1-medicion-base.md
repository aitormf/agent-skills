---
id: T1
title: Medición base de la review en el sandbox con Codex
status: done
depends_on: [T14]
examples: []
verification: scripts/check.sh
---
**Propósito:** medir cuántos tokens gastan y qué encuentran `review-pr` y `review-prepush` tal como están hoy, para tener con qué comparar (S1).

**Dentro:** una opción de `tests/review-sandbox/build.sh` que instala también la disposición de Codex (skills y `adapters/codex/agents/*.toml` donde Codex los lee); un script `tests/review-sandbox/measure.sh <comando> <n>` que ejecuta la review `n` veces con `codex exec --json`, guarda cada informe y suma los tokens por agente; `docs/review/medicion-review.md` con 3 ejecuciones de cada comando: tokens (entrada, salida, razonamiento) por agente y total, y qué bugs (B1–B9) y señuelos (D1–D3) de `EXPECTED.md` aparecen.

**Fuera:** cambiar la review; puntuar automáticamente los informes (se puntúan a mano contra `EXPECTED.md`); meter la medición en `check.sh` (necesita red).

**Flag:** ninguno.
