---
id: D-0050
title: El manager de Karajan sigue en solo lectura aunque la suite runStoryContract no lo admita; su conformidad la prueba un test propio con los casos que caben en solo lectura
type: architecture
status: accepted
date: 2026-11-12
affects: [integrations/karajan-board/, scripts/check.sh]
supersedes: null
superseded_by: null
issue: null
---

# D-0050: Conformidad propia del manager de solo lectura

## Contexto

D-0048 hace del manager `kj-board-changes` un tablero que solo lee y comprueba. En T2 se vio que `@karajan-family/story-contract` 1.0.0, la única versión en npm, trae una suite (`runStoryContract`) que da por hecho un tablero escribible:

- `create` crea HUs y las lista;
- `move` escribe y relee;
- `claim` guarda quién tiene la carta y la disputa entre dos.

La suite también exige exactamente las cinco capabilities de 1.0.0, sin el `tier` opcional de 1.1.0. Al cargar un manager, Karajan solo le pasa `assertManager` (`src/hu/managers/index.js`), no la suite.

## Decisión

- El manager sigue en solo lectura (D-0048 no cambia).
- No se corre `runStoryContract` tal cual. Un test propio pasa `assertManager` y reproduce los casos de la suite que caben en solo lectura:
  - capabilities y credentials;
  - la forma de `list`;
  - `move` que relee;
  - `BoardRejectedError` cuando git no coincide.
- El README del paquete lista los casos que no aplican y por qué.

## Alternativas descartadas

- **Una capa de estado local** (`create`, `move` y `claim` en un fichero sin commitear de `.karajan/`, por encima de git): pasa la suite, pero vuelve a haber dos fuentes de estado, que es lo que D-0048 evita.
- **Que el manager escriba en git** (crear ficheros de tarea, poner `status`): choca con D-0034 y con D-0026.

## Cómo se hace cumplir

`scripts/check.sh` corre el test de conformidad propio de `integrations/karajan-board/` (T7, E27).
