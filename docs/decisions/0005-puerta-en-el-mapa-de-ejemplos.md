---
id: D-0005
title: La puerta por defecto antes del código es el mapa de ejemplos
type: rule
status: accepted
date: 2026-10-24
affects: [skills/idea-to-issue/, agents/implement.md, skills/task-done/]
supersedes: null
superseded_by: null
issue: null
---

# D-0005: La puerta por defecto antes del código es el mapa de ejemplos

## Contexto

Parar en cada tarea multiplica el tiempo de la persona; no parar nunca deja pasar reglas mal entendidas.

Los niveles indican dónde se para la persona antes de que haya código (plan-v2, sección 3):

- **C, revisión al final:** no hay parada antes del código. La persona revisa el diff, tests incluidos, con `review-prepush`. Para cambios triviales y bugs, con o sin causa clara.
- **B, mapa de ejemplos:** una parada por idea. La persona revisa las reglas, los ejemplos y las decisiones del issue (10–15 líneas en lenguaje de negocio). Después el agente hace todas las tareas sin parar.
- **A, tests en rojo:** lo mismo que B y, además, en cada tarea delicada el agente escribe los tests, los ve fallar y espera el «ok» antes de implementar (el TDD ping-pong de la guía).

## Decisión

Nivel B por defecto: la persona revisa reglas, ejemplos y decisiones una vez por idea, y el agente hace todas las tareas con la protección mecánica de los tests (commit en rojo y comprobación en git). Nivel A (parada en los tests en rojo de cada tarea delicada) para dinero y datos personales; nivel C (solo revisión del diff) para lo trivial.

## Alternativas descartadas

- Parada en cada tarea siempre (A): demasiado lento para el caso normal.
- Ninguna parada (C): no detecta reglas mal entendidas antes del código.

## Cómo se hace cumplir

La protección de los tests la comprobarán `task-done` y la review (fases 2 y 4).
