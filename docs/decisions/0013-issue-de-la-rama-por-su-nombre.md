---
id: D-0013
title: task-done encuentra el issue de la rama por el número con que empieza su nombre
type: architecture
status: superseded
date: 2026-10-24
affects: [skills/task-done/, skills/idea-to-issue/, agents/implement.md]
supersedes: null
superseded_by: D-0022
issue: null
---

# D-0013: task-done encuentra el issue de la rama por el número con que empieza su nombre

## Contexto

`task-done` marca tareas en el issue que se le pasa o en el «enlazado en la rama» (D-0008), pero GitHub no da una forma barata de ir de una rama a su issue.

## Decisión

Si no se le pasa el número, `task-done --issue` lo saca del nombre de la rama: el número con que empieza (`42-cancelar-viaje`, `feat/42-cancelar-viaje`, `issue-42`). Es el nombre que pone `gh issue develop 42`, que además enlaza la rama al issue en GitHub; `idea-to-issue` lo propone como siguiente paso. Si la rama no lleva número, sale con 2 y pide `--issue <n>`.

## Alternativas descartadas

- Los issues que cierra la PR de la rama (`closingIssuesReferences`): exige abrir la PR antes de la primera tarea.
- Las ramas enlazadas del issue por GraphQL: la búsqueda es del issue a la rama, no al revés; habría que recorrer issues, con más red.
- Un fichero local con el número del issue: otra convención que mantener y que se queda vieja.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py` (`branch_issue`), probado en `scripts/check.sh` («task-done: issue checklist»).
