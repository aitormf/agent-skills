---
id: D-0048
title: Con Karajan Code, cada tarea de docs/changes es una HU con id <cambio>/T<n>; el repo es la fuente de verdad y el board manager solo lee y comprueba, nunca escribe
type: architecture
status: accepted
date: 2026-11-10
affects: [integrations/karajan-board/, skills/task-done/, skills/idea-to-change/, skills/plan-to-tasks/]
supersedes: null
superseded_by: null
issue: null
---

# D-0048: Las tareas de docs/changes son las HUs de Karajan; el manager solo lee y comprueba

## Contexto

Karajan Code lleva el trabajo en HUs y lo gobierna con gates de git. `card-first` exige que la rama nombre una tarjeta y `board-sync` exige mover una tarjeta mergeada. Admite backends de tablero con un contrato, el story-contract: `create`, `list`, `move` y `claim`, con relectura después de cada escritura. Nuestras skills ya guardan el trabajo en curso en ficheros de tarea (D-0029), con una rama y una PR por tarea (D-0031). Una tarea está en curso si existe su rama (D-0034) y está hecha si su `status: done` está mergeado.

## Decisión

- **HU = tarea.** Cada `docs/changes/<cambio>/tasks/T<n>-<slug>.md` de un cambio abierto es una HU. El cambio no tiene equivalente en Karajan.
- **Id = rama.** El `short_id` es `<cambio>/T<n>`, el nombre de la rama de la tarea, así que `card-first` y `kj hu start` la reconocen sin reglas nuevas. El `ref` es la ruta del fichero.
- **El repo manda.** Un board manager propio (`kj-board-changes`) calcula el estado con el tablero de `task-done`:
  - `ready` y `blocked` pasan a `pending`;
  - `doing` (existe la rama) pasa a `running`;
  - `done` mergeado pasa a `done`.

  Nunca devuelve `failed` ni `skipped`.
- **El manager no escribe.** `move` y `claim` comprueban que git ya dice lo que se pide y releen. Si git no lo dice, lanzan `BoardRejectedError` con el paso que falta (crear la rama, pasar `task-done` o mergear). `create` se rechaza siempre: las tareas nacen en `idea-to-change` o `plan-to-tasks` y entran por la PR del plan. La reserva es la rama (`assignee: false`).

## Alternativas descartadas

- **Las skills empujan a Karajan.** `kj hu add` por tarea, `hu:` en el frontmatter y `kj hu move` desde `task-done`. Habría dos fuentes de estado que se separan, y una tarea editada en la PR del plan no llegaría a la HU.
- **HU = cambio.** Una HU de Karajan es una rama y una PR, y un cambio tiene varias.
- **Que `move` cree la rama o haga commit de `status`.** `move(running)` haría commit de `status: doing`, que D-0034 quitó porque varias ramas chocan en el mismo fichero. Además, un backend que escribe en git a espaldas del agente rompe el "una rama, una tarea" del `implement`.
- **Que `create` escriba un fichero de tarea.** La tarea entraría sin mapa de ejemplos ni el ok de la persona (D-0026).

## Cómo se hace cumplir

`scripts/check.sh` pasa los tests de `integrations/karajan-board/`: la tabla de estados (E5–E10), los rechazos (E12, E14–E16, E18) y la suite `runStoryContract` contra un repo de prueba (E27).
