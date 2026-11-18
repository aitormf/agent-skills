---
id: D-0058
title: Cada tarea es una parte con sentido de una funcionalidad, con un solo objetivo y sin límite de líneas; la rama base sigue desplegable y lo que está a medias va detrás de un flag que retira la última tarea
type: rule
status: accepted
date: 2026-11-18
affects: [skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, agents/code-reviewer.md]
supersedes: D-0044
superseded_by: null
issue: null
---

# D-0058: Tareas por objetivo, sin límite de líneas

## Contexto

D-0044 limita cada tarea a 200 líneas con los tests y a una sola regla del mapa de ejemplos. El límite se pensó para el revisor: un solo code-reviewer es preciso si el diff cabe en su atención. Pero obliga a trocear las funcionalidades en pasos que no tienen sentido por sí solos, multiplica las ramas, las PRs y las reviews, y hace que ninguna review vea el conjunto. La precisión del revisor se puede conservar de otra forma: revisando una rama grande por tramos de commits (D-0060).

## Decisión

- **Por objetivo:** cada tarea es una parte con sentido de una funcionalidad, con un solo objetivo explicado en una frase sin "y". Por ejemplo, «exponer las facturas en `GET /invoices`» y, en otra tarea, «mostrar las facturas en una tabla». Si necesita "y", son dos tareas.
- **Varias reglas, un objetivo:** una tarea puede cubrir varias reglas del mapa si todas sirven a su objetivo.
- **Sin límite de líneas:** el tamaño es una consecuencia de partir bien, no un criterio. Ni el plan ni `implement` cuentan líneas.
- Se mantiene de D-0044: un solo propósito por tarea (comportamiento nuevo, refactor o preparación, sin mezclar). La rama base queda en verde y desplegable tras cada tarea. Lo que queda a medias va detrás de un feature flag apagado, y la última tarea lo retira.

## Alternativas descartadas

- Mantener 200 líneas (D-0044): parte por el revisor, no por utilidad. Ese coste ya no hace falta con la review por tramos.
- Un número más alto (700 líneas): sigue siendo partir por líneas. Una funcionalidad bien partida no crece tanto, y el número acabaría siendo el criterio.
- Separar la tarea de la PR (varias tareas por PR, o una tarea en varias PRs): rompe una tarea, una rama, una PR (D-0031) y la auditoría por rama (D-0032), sin ganar nada que no den los tramos.
- Puntos de control de review dentro de la tarea: es otra forma de trocear para el revisor, con un orden de commits que habría que vigilar.

## Cómo se hace cumplir

`idea-to-change` y `plan-to-tasks` lo aplican al partir, y `code-reviewer` señala los objetivos mezclados como Optional (D-0037). `check.sh` comprueba que esos textos explican el criterio por objetivo y ya no dicen 200 líneas (E1–E5 del cambio `tareas-por-objetivo`).
