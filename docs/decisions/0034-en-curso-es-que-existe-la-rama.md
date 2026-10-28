---
id: D-0034
title: El tablero cuenta una tarea como en curso si existe su rama; implement no hace commit de status: doing
type: architecture
status: accepted
date: 2026-10-28
affects: [skills/task-done/, agents/implement.md]
supersedes: null
superseded_by: null
issue: null
---

# D-0034: El tablero cuenta una tarea como en curso si existe su rama; implement no hace commit de status: doing

## Contexto

Con una PR por tarea (D-0031), la tarea sigue en `todo` en la rama base hasta que se mergea. Sin otra señal, el tablero (D-0030) la ofrecería como lista mientras su PR espera revisión, y el agente la empezaría otra vez.

## Decisión

- Una tarea no mergeada está **en curso** si su fichero en el árbol de trabajo dice `doing` o `done`, o si existe una rama `<…>/<cambio>/T<n>` en local o en el remoto.
- `implement` no edita ni hace commit de `status: doing`: crear la rama es lo que marca la tarea como tomada.

## Alternativas descartadas

- Hacer commit de `status: doing` en la rama base: un commit en la rama base por cada tarea que empieza, y quedaría `doing` si la rama se abandona.
- `status: doing` solo en la rama de la tarea: el tablero lee la rama base y no lo vería.

## Cómo se hace cumplir

`skills/task-done/scripts/board.py`, probado en `scripts/check.sh` («the board did not take a task with a branch as doing»).
