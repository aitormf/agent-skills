---
id: D-0016
title: El glosario ligero vive en AGENTS.md; ARCHITECTURE.md se queda con el modelo de dominio
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/generate-project-context/, skills/idea-to-spec/, skills/review-spec/]
supersedes: null
superseded_by: null
issue: null
---

# D-0016: El glosario ligero vive en AGENTS.md; ARCHITECTURE.md se queda con el modelo de dominio

## Contexto

La guía y el plan-v2 (sección 6.2) piden un glosario del dominio en `AGENTS.md` (DDD ligero): que el agente nombre código, tests y ejemplos con las palabras del negocio. La plantilla de `ARCHITECTURE.md` ya tenía una tabla de glosario en su sección 8, que el agente solo lee al planificar.

## Decisión

El glosario va en la sección «Glosario» del fragmento de niveles de `AGENTS.md`: un término por línea, menos de unos 15. La sección 8 de `ARCHITECTURE.md` pasa a «Modelo de dominio» (entidades, invariantes y relaciones que no caben en una línea) y remite al glosario. `idea-to-spec`, `review-spec` y `CONTRIBUTING.md` lo buscan en `AGENTS.md`, y en proyectos antiguos en `ARCHITECTURE.md`.

## Alternativas descartadas

- Seguir en `ARCHITECTURE.md`: no se carga en cada sesión, que es lo que hace útil al glosario.
- En los dos ficheros: se desincronizan; la regla de `generate-project-context` es no duplicar.

## Cómo se hace cumplir

No se automatiza.
