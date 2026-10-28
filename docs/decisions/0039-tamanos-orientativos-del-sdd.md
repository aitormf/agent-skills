---
id: D-0039
title: En el SDD, un plan de más de unas 150 líneas o una spec con más de unos 12 requisitos o varias historias entregables por separado son señal para partir
type: rule
status: accepted
date: 2026-10-28
affects: [skills/idea-to-spec/, skills/spec-to-plan/, skills/review-spec/]
supersedes: null
superseded_by: null
issue: null
---

# D-0039: En el SDD, un plan de más de unas 150 líneas o una spec con más de unos 12 requisitos o varias historias entregables por separado son señal para partir

## Contexto

#15 midió planes que bajaban al detalle de implementación y trabajos demasiado grandes. Hace falta un umbral para que el agente proponga partir, sin convertirlo en una regla mecánica (igual que D-0033 para las tareas).

## Decisión

- `idea-to-spec` propone partir el cambio, como una pregunta, si tiene varias historias de usuario que se pueden entregar por separado o necesitaría más de unos 12 requisitos funcionales. Cada parte es su propio cambio. Decide la persona.
- `spec-to-plan` escribe un plan de diseño, sin comandos, código, nombres de tests ni pasos línea a línea. Un plan de más de unas 150 líneas está bajando demasiado o el cambio es demasiado grande: lo dice y propone partirlo.
- `review-spec` no trata los detalles de implementación de un plan como hallazgos; uno arriesgado va como una línea en `Risks`.

## Alternativas descartadas

- Límites estrictos: bloquearían specs y planes correctos por un número orientativo.
- Sin umbral: los planes vuelven a bajar al detalle y los cambios crecen.

## Cómo se hace cumplir

No se automatiza: lo dicen `idea-to-spec`, `spec-to-plan` y `review-spec`.
