---
id: D-0033
title: Cada tarea tiene un solo propósito y deja la rama base desplegable; lo que está a medias va detrás de un flag que retira la última tarea
type: rule
status: accepted
date: 2026-10-27
affects: [skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, agents/code-reviewer.md]
supersedes: null
superseded_by: null
issue: null
---

# D-0033: Cada tarea tiene un solo propósito y deja la rama base desplegable; lo que está a medias va detrás de un flag que retira la última tarea

## Contexto

Con una PR por tarea (D-0031), cada tarea se mergea sola en la rama base. Para que la PR sea fácil de leer, la tarea tiene que ser pequeña. Para que mergearla no rompa nada, tiene que dejar la rama base en verde aunque el cambio no esté terminado.

## Decisión

- **Un solo propósito por tarea:** o comportamiento nuevo, o refactor, o preparación (fontanería, migración). No se mezclan. El propósito cabe en una frase.
- **Tamaño orientativo:** unas 150 líneas de diff sin contar los tests. Si una tarea promete más, se parte.
- **Cada tarea deja la rama base en verde y desplegable.** Si el comportamiento queda a medias, va detrás de un feature flag apagado por defecto, con el mecanismo que diga `AGENTS.md`.
- **Un cambio con flag termina con una tarea que lo retira**, con el código muerto y los tests del camino viejo. Esa tarea depende de todas las demás.

## Alternativas descartadas

- Que el cambio solo funcione cuando entra la última PR: la rama base queda rota o a medias entre PRs.
- Retirar el flag fuera del cambio: se olvida y se acumulan flags muertos.
- Un límite de tamaño estricto que bloquee: el tamaño es una señal para partir, no una regla mecánica.

## Cómo se hace cumplir

No se automatiza: lo aplican `idea-to-change` y `plan-to-tasks` al partir, y `code-reviewer` lo señala en la review.
