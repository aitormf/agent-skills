---
id: D-0035
title: Las PRs de un cambio citan su issue con Refs; solo la que deja el cambio en done lo cierra con Closes
type: rule
status: accepted
date: 2026-10-28
affects: [skills/idea-to-change/, agents/implement.md, skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0035: Las PRs de un cambio citan su issue con Refs; solo la que deja el cambio en done lo cierra con Closes

## Contexto

Con una PR del plan y una por tarea (D-0031), un `Closes #n` en la primera PR mergeada cerraría el issue con el cambio a medias.

## Decisión

- La PR del plan y las de las tareas llevan `Refs #<n>` si el README del cambio tiene `issue: <n>`.
- Solo la PR cuyo diff pone el README en `status: done` (la de la última tarea) lleva `Closes #<n>`.
- En `review-pr`, un `Closes` que falta o que llega antes de tiempo es un hallazgo Optional.

## Alternativas descartadas

- `Closes` en la PR del plan: cierra el issue antes de empezar.
- Cerrar el issue a mano al terminar: se olvida.

## Cómo se hace cumplir

No se automatiza: lo dicen `idea-to-change`, `implement` y `review-pr`.
