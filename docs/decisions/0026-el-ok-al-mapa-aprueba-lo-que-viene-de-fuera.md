---
id: D-0026
title: El ok de la persona al mapa de ejemplos aprueba lo que entró desde un issue; los comandos de verificación salen solo de AGENTS.md
type: rule
status: accepted
date: 2026-10-25
affects: [skills/idea-to-change/, skills/plan-to-tasks/]
supersedes: null
superseded_by: null
issue: null
---

# D-0026: El ok de la persona al mapa de ejemplos aprueba lo que entró desde un issue; los comandos de verificación salen solo de AGENTS.md

## Contexto

D-0023 pide que una persona apruebe lo que entra desde fuera del repo antes de que un agente actúe sobre ello, pero no dice cuándo. `idea-to-change` ya tiene una parada en el mapa de ejemplos (D-0005). Una segunda parada solo para el texto del issue duplicaría la revisión.

## Decisión

- La parada del mapa de ejemplos es la aprobación de D-0023. Hasta ese ok no se hace commit de nada.
- Las tareas que se escriben después se guardan sin otra parada, porque su único texto ejecutable, el comando `verification:`, sale siempre de `AGENTS.md`. Nunca sale del issue; si `AGENTS.md` no lo tiene, se pregunta a la persona.

## Alternativas descartadas

- Una parada aparte para aprobar el texto del issue: dos revisiones del mismo contenido, y la persona acaba aprobando sin leer.
- Revisar también las tareas antes del commit: el riesgo estaba en los comandos, y esos ya no vienen del issue.

## Cómo se hace cumplir

No se automatiza: lo dicen `skills/idea-to-change/SKILL.md` y `skills/plan-to-tasks/SKILL.md`.
