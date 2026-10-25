---
id: D-0008
title: Un issue de trabajo se reconoce por el que se pasa, sin etiqueta
type: architecture
status: obsolete
date: 2026-10-24
affects: [skills/task-done/, skills/review-prepush/, skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0008: Un issue de trabajo se reconoce por el que se pasa, sin etiqueta

## Contexto

Obsoleta desde el 2026-10-25: con D-0021 el trabajo ya no vive en un issue, no hay issue de trabajo que reconocer.

`task-done` y la review necesitan saber qué issue tiene las tareas de un trabajo.

## Decisión

Usan el issue que se les pasa o el enlazado en la rama, y buscan el checklist `- [ ] T1.`. Si algo necesita listar trabajos en curso, se añadirá una etiqueta entonces.

## Alternativas descartadas

- Etiqueta fija `work`: otra convención que cumplir sin un uso que la pida todavía.
- Cualquier issue abierto con checklist: búsqueda frágil y lenta.

## Cómo se hace cumplir

No se automatiza.
