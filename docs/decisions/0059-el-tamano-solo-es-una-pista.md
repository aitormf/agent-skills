---
id: D-0059
title: El gate deja de avisar por el tamaño de la tarea; el recuento de líneas solo aparece como pista en los hechos de la review
type: rule
status: accepted
date: 2026-11-18
affects: [skills/task-done/scripts/, skills/review-context/scripts/review_facts.py, agents/code-reviewer.md]
supersedes: D-0053
superseded_by: null
issue: null
---

# D-0059: El tamaño solo es una pista

## Contexto

D-0053 hace que el gate avise si una tarea pasa de 200 líneas, el límite de D-0044. D-0058 quita ese límite: las tareas se parten por objetivo. Un aviso con un número que ya no es una regla acaba siendo ruido, o vuelve a convertir el número en criterio.

## Decisión

El gate deja de contar líneas y no avisa por el tamaño. `review_facts.py` incluye el recuento de `diff_size.py` y el número de tramos (D-0060) como dato. Si una rama sale mucho más grande de lo normal, el revisor se pregunta si mezcla objetivos y lo señala como Optional (D-0037), con los ficheros de cada objetivo. No informa nada por el tamaño solo.

## Alternativas descartadas

- Mantener el aviso con un número más alto: es un número que nadie decidió como regla, y empuja a partir por líneas.
- Bloquear por tamaño: ya descartado en D-0053 por las mismas razones.

## Cómo se hace cumplir

Tests E6–E9 del cambio `tareas-por-objetivo` en `scripts/check.sh`.
