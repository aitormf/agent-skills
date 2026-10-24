---
id: D-0014
title: Para una tarea de un issue, el commit en rojo se busca en la rama desde la rama base
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/task-done/]
supersedes: null
superseded_by: null
issue: null
---

# D-0014: Para una tarea de un issue, el commit en rojo se busca en la rama desde la rama base

## Contexto

Los IDs `T<n>` se repiten entre trabajos. Con `tasks.md`, `task-done` mira solo los commits desde que se añadió el fichero (D-0012); un issue no está en git y no marca ese inicio.

## Decisión

Para una tarea de un issue, `task-done` busca el commit `test(T<n>):` y comprueba sus tests solo entre los commits de la rama actual que no están en la rama base (`origin/HEAD`, o si no `origin/main`, `origin/master`, `main` o `master`). Un issue, una rama.

## Alternativas descartadas

- Toda la historia: un `test(T1):` de un trabajo anterior haría pasar la comprobación.
- Solo los commits que citan el issue (`#42`) en el mensaje: otra convención en cada commit, fácil de olvidar.
- Pasar el commit de inicio como argumento: el agente puede pasar otro (el mismo motivo que en D-0012).

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py` (`Issue.commits`), probado en `scripts/check.sh` («task-done: issue checklist»: un `test(T1):` de la rama base no cuenta). Trabajando directamente sobre la rama base no encuentra el commit en rojo y falla con 3.
