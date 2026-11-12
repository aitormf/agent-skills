---
id: T2
title: Paquete kj-board-changes con list() y la tabla de estados
status: done
depends_on: [T1]
examples: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E26]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: Karajan puede listar las tareas de los cambios abiertos como HUs (D-0048, D-0049).

**Dentro:**
- El paquete Node `integrations/karajan-board/` (`kj-board-changes`): `package.json` (Node ≥ 22 y devDependencies con `@karajan-family/story-contract` a versión fija), `createManager({ config, env, run })`, `credentials = []` y las capabilities de E26.
- `list()` recorre `docs/changes/*/` con README `status: open`, llama a `board.py --json` con `run` y traduce: `short_id` `<cambio>/T<n>`, `ref` la ruta del fichero y estado `ready|blocked → pending`, `doing → running`, `done → done`.
- Un `board.py` que sale con 2 lanza `BoardRejectedError`.
- `move`, `claim` y `create` lanzan `BoardRejectedError("not yet")` hasta T4.
- `npm ci && npm test` en `scripts/check.sh`, que falla diciendo por qué si no hay Node ≥ 22.
- Se comprueba en el código de Karajan cómo carga un manager de la allowlist (¿ruta del repo o solo `node_modules`?) y el nombre del campo de dependencias en `src/hu/graph.js`. Las dos respuestas se apuntan en `integrations/karajan-board/README.md`. Si contradicen un supuesto del README del cambio, se para y se avisa.

**Fuera:** los ids con prefijo (T3), `move`, `claim` y `create` de verdad (T4), `tier` (T5) y `runStoryContract` (T7).

**Flag:** ninguno; el manager solo se usa si un proyecto lo pone en `.karajan/board.yml`.
