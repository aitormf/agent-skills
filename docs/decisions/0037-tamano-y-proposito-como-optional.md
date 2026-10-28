---
id: D-0037
title: code-reviewer señala una tarea demasiado grande o con propósitos mezclados como Optional, nunca Required
type: rule
status: accepted
date: 2026-10-28
affects: [agents/code-reviewer.md]
supersedes: null
superseded_by: null
issue: null
---

# D-0037: code-reviewer señala una tarea demasiado grande o con propósitos mezclados como Optional, nunca Required

## Contexto

D-0033 da un tamaño orientativo (unas 150 líneas sin tests) y pide un solo propósito por tarea, pero dice que el tamaño es una señal, no una regla mecánica. Hay que decidir con qué gravedad lo señala la review.

## Decisión

`code-reviewer` informa un hallazgo **Optional**, en el fichero de la tarea, si el diff se pasa claramente del tamaño (con el recuento) o mezcla propósitos (con los ficheros de cada uno). El arreglo es partir la tarea en el plan. Nunca es Critical ni Required.

## Alternativas descartadas

- Required: bloquearía PRs correctas por un número orientativo.
- No señalarlo: las tareas crecerían sin que nadie lo vea.

## Cómo se hace cumplir

No se automatiza: lo dice `agents/code-reviewer.md`.
