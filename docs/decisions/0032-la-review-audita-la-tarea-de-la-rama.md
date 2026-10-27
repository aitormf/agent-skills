---
id: D-0032
title: La review audita con task_done.py --audit la tarea de la rama, o el plan entero en la PR del plan
type: architecture
status: accepted
date: 2026-10-27
affects: [skills/task-done/, skills/review-prepush/, skills/review-pr/, skills/review-report/]
supersedes: D-0019
superseded_by: null
issue: null
---

# D-0032: La review audita con task_done.py --audit la tarea de la rama, o el plan entero en la PR del plan

## Contexto

D-0019 hacía que la review recorriera todo el checklist de un cambio con `task_done.py --audit`. Con una PR por tarea (D-0031), las tareas ya mergeadas tienen su commit en rojo en la rama base, y recorrerlas daría problemas falsos.

## Decisión

Se mantiene de D-0019 que la review reutiliza `task_done.py --audit`, de solo lectura, que lo ejecuta la sesión principal y que cada `PROBLEM` es Required, nunca Critical. Cambia el alcance:

- **En una rama `<cambio>/T<n>`:** audita solo esa tarea. Comprueba su commit en rojo y sus tests, que sus `examples` existen en el mapa, y que sus `depends_on` están `done` en la rama base.
- **En una rama `<cambio>/plan`:** comprueba el tablero (D-0030: sin ciclos ni dependencias inexistentes) y que cada ejemplo del mapa está en los `examples` de alguna tarea. No hay commits en rojo que mirar.

## Alternativas descartadas

- Auditar todas las tareas del cambio en cada PR: las mergeadas no tienen su commit en rojo en la rama, así que todas darían problema.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py` (`--audit`), probado en `scripts/check.sh` para una rama de tarea y una rama de plan.
