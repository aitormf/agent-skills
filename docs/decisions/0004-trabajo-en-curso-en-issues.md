---
id: D-0004
title: El trabajo en curso (nota, mapa, tareas) vive en un issue de GitHub
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/task-done/, skills/idea-to-issue/]
supersedes: null
superseded_by: null
issue: null
---

# D-0004: El trabajo en curso (nota, mapa, tareas) vive en un issue de GitHub

## Contexto

La nota de la idea, el mapa de ejemplos y las tareas solo sirven mientras se trabaja; al terminar, lo que perdura son las decisiones y los tests.

## Decisión

Viven en el cuerpo de un issue de GitHub, con el checklist de tareas. El issue da el tablero Kanban sin hacer nada más. `tasks.md` sigue siendo válido para quien trabaje sin red o sin `gh`.

## Alternativas descartadas

- Fichero en `docs/work/` dentro del repo: hay que mantenerlo y borrarlo, y no da tablero.

## Cómo se hace cumplir

No se automatiza.
