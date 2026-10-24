---
id: D-0005
title: La puerta por defecto antes del código es el mapa de ejemplos
type: rule
status: proposed
date: 2026-10-24
affects: [skills/idea-to-issue/, agents/implement.md, skills/task-done/]
supersedes: null
superseded_by: null
issue: null
---

# D-0005: La puerta por defecto antes del código es el mapa de ejemplos

## Contexto

Parar en cada tarea multiplica el tiempo de la persona; no parar nunca deja pasar reglas mal entendidas.

## Decisión

Nivel B por defecto: la persona revisa reglas, ejemplos y decisiones una vez por idea, y el agente hace todas las tareas con la protección mecánica de los tests (commit en rojo y comprobación en git). Nivel A (parada en los tests en rojo de cada tarea delicada) para dinero y datos personales; nivel C (solo revisión del diff) para lo trivial.

## Alternativas descartadas

- Parada en cada tarea siempre (A): demasiado lento para el caso normal.
- Ninguna parada (C): no detecta reglas mal entendidas antes del código.

## Cómo se hace cumplir

La protección de los tests la comprobarán `task-done` y la review (fases 2 y 4).
