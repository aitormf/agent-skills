---
id: D-0010
title: Los ADRs existentes se ofrecen mover a docs/decisions/
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/generate-project-context/, skills/record-decision/]
supersedes: null
superseded_by: null
issue: null
---

# D-0010: Los ADRs existentes se ofrecen mover a docs/decisions/

## Contexto

Hay proyectos que ya usan `docs/adr/`.

## Decisión

En un proyecto existente, `generate-project-context` ofrece moverlos con `git mv`, conservando los números, como tipo `architecture` (los `rejected`, como `discarded`). Si la persona no quiere, conviven y el índice enlaza los ADRs.

## Alternativas descartadas

- Mover siempre sin preguntar: cambia rutas que pueden estar enlazadas fuera del repo.
- Que convivan siempre: dos sitios donde buscar el porqué.

## Cómo se hace cumplir

No se automatiza; el procedimiento está en `record-decision`.
