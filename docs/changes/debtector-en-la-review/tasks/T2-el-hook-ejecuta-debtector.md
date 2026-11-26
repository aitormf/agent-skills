---
id: T2
title: El hook ejecuta debtector si la base lo activa
status: todo
depends_on: [T1]
examples: [E8, E9, E10, E11, E12, E13]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo. `verify.py` lee `[review] debtector` (por defecto `false`) del `.harness-config.toml` de la rama base y, si vale `true`, añade al fichero de resultados la salida de `debtector_diff.py`, sin bloquear nunca el push (R2, D-0063).

**Dentro:**

- La lectura y la validación de la clave en `verify.py`, junto a `verify` y `semgrep`. El mensaje de error es `[review] debtector must be true or false`, en inglés.
- La sección `## debtector (architecture)` en el fichero de resultados, con la salida del script, o `debtector: not available (<error>)` si sale con 2. Con el mismo tiempo límite que los demás comandos.
- Que ni el exit del script ni un `would block its CI job` cambien el código de salida de `verify.py`.
- Los tests del hook en `scripts/check.sh`, con el `debtector` falso de T1.
- Todo lo nuevo en inglés, aunque `verify.py` ya tenga mensajes en español. Esos mensajes no se tocan.

**Fuera:** el texto de los skills de review (T3) y la plantilla de `setup-guardrails-python`.

**Flag:** ninguno. Sin la clave en la base, el hook no hace nada nuevo.
