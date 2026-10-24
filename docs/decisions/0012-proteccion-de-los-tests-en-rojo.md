---
id: D-0012
title: Los tests en rojo se protegen con un commit test(Tn) y task-done comprueba líneas, no ficheros
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/task-done/, agents/implement.md]
supersedes: null
superseded_by: null
issue: "#18"
---

# D-0012: Los tests en rojo se protegen con un commit test(Tn) y task-done comprueba líneas, no ficheros

## Contexto

En el nivel B no hay parada por tarea; lo que la sustituye es la protección mecánica de los tests (plan-v2, sección 4.4). #18 pide además un ciclo de un test cada vez, porque el agente implementaba funciones enteras tras ver en rojo solo los primeros tests. Hay que decidir cómo encaja el ciclo con el commit en rojo y qué comprueba `task-done`.

## Decisión

- Por tarea, un commit en rojo con los tests de todos sus ejemplos (`test(T2): E1 E2 red`), cada uno visto fallar por el motivo esperado. Después, la implementación avanza de un test en verde cada vez.
- `task-done` busca el commit en rojo por el asunto `test(T<n>):` entre los commits desde que se añadió `tasks.md` (los IDs `T<n>` se repiten entre trabajos). Solo lo exige si la tarea declara sus ejemplos (`tests: E1, E2`).
- Comprueba que el commit en rojo añade una línea que nombra cada ejemplo, y que ningún commit posterior (salvo los commits en rojo de otras tareas) ni los cambios sin commit quitan o cambian líneas de los ficheros que tocó. Añadir tests nuevos a esos ficheros está permitido. Si falla, no ejecuta la verificación y sale con 3.

## Alternativas descartadas

- Un commit en rojo por test: multiplica los commits; el commit por tarea basta para ver los tests antes del código, y el ciclo de uno en uno lo pide `implement`.
- Congelar los ficheros enteros del commit en rojo: impide añadir el test de un caso que aparece al implementar, que #18 quiere en su propio ciclo.
- Pasar el commit en rojo como argumento (`--red <sha>`): el agente puede pasar otro; el asunto del commit es la convención que ya pide el plan.
- Ejecutar los tests en el commit en rojo para probar que fallaban: lento y depende del entorno; el informe por test de `implement` cubre ese hueco.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py`, probado en `scripts/check.sh` («task-done: red commit protection»). No detecta un test añadido que redefine uno del commit en rojo ni un ejemplo mal traducido a test: eso se ve en la review del diff.
