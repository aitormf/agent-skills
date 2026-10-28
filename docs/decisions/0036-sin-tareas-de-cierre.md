---
id: D-0036
title: Desaparecen las tareas de cierre W<n>; implement ejecuta la verificación completa antes de cada PR
type: architecture
status: accepted
date: 2026-10-28
affects: [skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/task-done/]
supersedes: null
superseded_by: null
issue: null
---

# D-0036: Desaparecen las tareas de cierre W<n>; implement ejecuta la verificación completa antes de cada PR

## Contexto

La tarea `W1` ejecutaba la verificación completa al final de un cambio que iba en una sola PR. Con una PR por tarea (D-0031) y la rama base desplegable tras cada una (D-0033), esperar al final deja pasar PRs que rompen la verificación completa.

## Decisión

- `implement` ejecuta la verificación completa de `AGENTS.md` antes de abrir cada PR, además de la verificación de la tarea.
- Las tareas se llaman solo `T<n>`. No hay tareas de cierre.

## Alternativas descartadas

- Mantener `W1` como última tarea: llegaría tarde, con las PRs anteriores ya mergeadas.

## Cómo se hace cumplir

No se automatiza: lo dice `agents/implement.md`. `task_done.py` y `board.py` solo aceptan ids `T<n>`.
