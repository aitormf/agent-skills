---
id: D-0024
title: La protección de los tests en rojo mira los commits de la rama desde la rama base y no exime a ningún commit posterior
type: architecture
status: accepted
date: 2026-10-25
affects: [skills/task-done/, agents/implement.md]
supersedes: D-0012
superseded_by: null
issue: null
---

# D-0024: La protección de los tests en rojo mira los commits de la rama desde la rama base y no exime a ningún commit posterior

## Contexto

D-0012 acotaba los commits desde que se añadió `tasks.md` y dejaba que los commits en rojo de otras tareas tocaran los tests de una anterior. La review de la PR #20 mostró dos fallos: el acotado sigue el orden por fecha, no la historia, y con `tasks.md` sin commit busca en toda la historia (R5); y un `test(T9):` posterior puede debilitar un test de T1 sin que nadie lo vea (R4). D-0014 ya acotaba desde la rama base para los issues.

## Decisión

Igual que D-0012 (un commit `test(T<n>):` por tarea, comprobación por líneas, exit 3), con dos cambios:

- El commit en rojo y los cambios a sus tests se buscan solo entre los commits de la rama que no están en la rama base (`origin/HEAD`, o si no `origin/main`, `origin/master`, `main` o `master`). Una rama, un cambio. Si no encuentra la rama base, sale con 3 y lo dice.
- Ningún commit posterior al commit en rojo puede quitar o cambiar sus líneas, tampoco el commit en rojo de otra tarea. Añadir tests sigue permitido.

## Alternativas descartadas

- Acotar desde el commit que añadió `tasks.md`: el fallo R5.
- Seguir eximiendo los commits en rojo de otras tareas: el fallo R4; si una tarea nueva necesita cambiar un test de otra, es un cambio de comportamiento que se ve en la review.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py`, probado en `scripts/check.sh`: un `test(T1):` de la rama base no cuenta, un `test(T2):` que cambia un test de T1 falla, `tasks.md` sin commit, y rama base no encontrada.
