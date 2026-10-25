---
id: D-0019
title: La review comprueba los ejemplos y los tests en rojo con task_done.py --audit, de solo lectura
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/task-done/, skills/review-prepush/, skills/review-pr/, skills/review-report/]
supersedes: null
superseded_by: null
issue: null
---

# D-0019: La review comprueba los ejemplos y los tests en rojo con task_done.py --audit, de solo lectura

## Contexto

El plan (sección 4.4) pide que la review compruebe al final lo mismo que `task-done` al marcar cada tarea: que cada ejemplo tiene su test y que los tests del commit en rojo no cambiaron. `task-done` ya lo hace de forma determinista (D-0012, D-0014), pero tarea a tarea y ejecutando la verificación.

## Decisión

- `task_done.py --audit <tasks.md>` o `--audit --issue [<n>]`: recorre todo el checklist sin ejecutar nada ni marcar nada. Comprueba las tareas marcadas y las que tienen commit en rojo, y que cada ejemplo del mapa (`E1: …`) está en el `tests:` de alguna tarea. Las tareas sin marcar y sin commit en rojo salen como `pending`, no como problema. Solo mira la historia con commit: lo que no está en un commit no se sube.
- Lo ejecuta la sesión principal en el paso de verificación (`review-prepush`, y `review-pr` cuando el árbol de trabajo es la cabeza del cambio), y su salida va a las personas como un resultado más de verificación.
- La lista de tareas es el `tasks.md` de la spec o el issue cuyo número empieza el nombre de la rama (D-0013), leído con `gh issue view`.
- Cada `PROBLEM` es un hallazgo **Required**, nunca Critical: una comprobación de proceso no bloquea el push.

## Alternativas descartadas

- Describir la comprobación en prosa para que la haga el revisor: no es determinista y repite la lógica de `task_done.py`.
- Un script propio de la review: duplica el código de `task-done` y las dos copias se desfasarían.
- Que las personas ejecuten el script: la verificación ya la hace la sesión principal y se pasa igual a todas.
- Critical si se tocó un test en rojo: bloquearía el push por una cuestión de proceso; la review solo bloquea por fallos confirmados.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py` (`audit`), probado en `scripts/check.sh` («task-done --audit» y el escenario del issue). Si la skill `task-done` no está instalada, la review lo dice en Verification y no lo comprueba.
