---
id: D-0044
title: Cada tarea es atómica (un solo propósito y un solo cambio) y su diff tiene como mucho 200 líneas con los tests; deja la rama base desplegable y lo que está a medias va detrás de un flag que retira la última tarea
type: rule
status: accepted
date: 2026-11-03
affects: [skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, agents/code-reviewer.md]
supersedes: D-0033
superseded_by: null
issue: null
---

# D-0044: Cada tarea es atómica y su diff tiene como mucho 200 líneas con los tests

## Contexto

D-0033 pedía un solo propósito por tarea (comportamiento nuevo, refactor o preparación) y unas 150 líneas sin contar los tests. Dos huecos: "comportamiento nuevo" admite varios comportamientos en una tarea, y sin contar los tests una tarea podía llegar a 300–400 líneas de PR. La review se abarata con diffs pequeños (D-0045): un solo reviewer basta si el diff cabe entero en su atención.

## Decisión

- **Atómica:** un solo propósito (comportamiento nuevo, refactor o preparación, sin mezclar) **y** un solo cambio: un comportamiento, una regla del mapa de ejemplos. El propósito se explica en una frase sin "y"; si necesita "y", son dos tareas.
- **Tamaño:** como mucho 200 líneas de diff (añadidas + borradas) **con los tests incluidos**, contadas como en D-0047 (sin lockfiles, generados ni snapshots). Si una tarea promete más, se parte al planificar.
- **Cada tarea deja la rama base en verde y desplegable.** Si el comportamiento queda a medias, va detrás de un feature flag apagado por defecto, con el mecanismo que diga `AGENTS.md`.
- **Un cambio con flag termina con una tarea que lo retira**, con el código muerto y los tests del camino viejo. Esa tarea depende de todas las demás.

## Alternativas descartadas

- 150 líneas sin tests (D-0033): una PR de 150 líneas de código más sus tests ya no se lee de una vez, y la cifra no coincide con la que usa la review.
- Contar solo el código: incentiva tests escasos para caber en el límite.
- Bloquear mecánicamente una tarea grande: el tamaño sigue siendo una señal para la persona (D-0037), no una regla que pare una PR correcta.

## Cómo se hace cumplir

`idea-to-change` y `plan-to-tasks` lo aplican al partir; `implement` para y lo informa si el diff pasa de 200; `code-reviewer` lo señala como Optional (D-0037) con el recuento de `diff_size.py`. `check.sh` comprueba que esos textos dicen 200 líneas con los tests.
