---
id: D-0007
title: Se retira sdd-next
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/sdd-next/]
supersedes: null
superseded_by: null
issue: null
---

# D-0007: Se retira sdd-next

## Contexto

Con el trabajo en issues, el estado lo da el tablero de GitHub. `sdd-next` solo lee `docs/specs/`.

## Decisión

Se retira en la fase 5, con sus referencias en el README y en `docs/sdd/`. En el nivel SDD basta con mirar el `status` de los artefactos.

## Alternativas descartadas

- Adaptarla para leer issues: duplica el tablero y depende de `gh`.
- Mantenerla solo para SDD: una skill más que mantener para el nivel menos usado.

## Cómo se hace cumplir

No se automatiza.
