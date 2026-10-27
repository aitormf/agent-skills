---
id: D-0030
title: Las tareas declaran solo depends_on; qué bloquean y si están listas se calcula
type: architecture
status: accepted
date: 2026-10-27
affects: [skills/task-done/, skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/review-prepush/, skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0030: Las tareas declaran solo depends_on; qué bloquean y si están listas se calcula

## Contexto

Con una PR por tarea (D-0031), unas tareas no pueden empezar hasta que otras estén mergeadas. Si el agente no sabe qué está desbloqueado, se queda parado mientras la persona revisa una PR, o empieza algo que choca con lo que está pendiente.

## Decisión

- Cada tarea declara `depends_on: [T1, T3]`, o `[]`. Lo que bloquea una tarea no se escribe: se deduce de las demás.
- Una tarea está **lista** si está en `todo` y todas sus dependencias están `done` en la rama base, es decir, mergeadas.
- Un script de la skill `task-done` hace de tablero: lista las tareas listas, bloqueadas (y por cuál), en curso y hechas. Falla con 2 si hay un ciclo, una dependencia que no existe o un frontmatter mal formado.
- El agente elige la siguiente tarea entre las listas. Mientras una PR espera revisión, sigue con otra tarea lista. No hay PRs apiladas.

## Alternativas descartadas

- Escribir `depends_on` y `blocks`: dos sitios que dicen lo mismo y acaban desincronizados.
- PRs apiladas (T2 sale de la rama de T1): rebases cada vez que cambia la PR de abajo, y la base de cada PR deja de ser `main`.
- Orden implícito por número de tarea: obliga a serializar tareas que podrían ir en paralelo.

## Cómo se hace cumplir

El script de tablero de `skills/task-done/scripts/`, probado en `scripts/check.sh`: ciclo, dependencia inexistente, tarea lista y tarea bloqueada.
