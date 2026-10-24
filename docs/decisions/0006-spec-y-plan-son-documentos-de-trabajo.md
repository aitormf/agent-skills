---
id: D-0006
title: spec.md y plan.md son documentos de trabajo; perduran las decisiones y los tests
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, docs/sdd/]
supersedes: null
superseded_by: null
issue: null
---

# D-0006: spec.md y plan.md son documentos de trabajo; perduran las decisiones y los tests

## Contexto

La guía dice que el código manda; el SDD trataba la spec como referencia viva, y nadie la mantiene al día.

## Decisión

Qué hace el sistema lo dicen los tests; por qué, `docs/decisions/`. Al cerrar un trabajo SDD, sus decisiones pasan a `docs/decisions/` y la spec se marca `obsolete` o se archiva.

## Alternativas descartadas

- Spec viva mantenida al día: se desfasa sin que nada avise.

## Cómo se hace cumplir

No se automatiza todavía; el cierre lo harán las skills de SDD (fase 5).
