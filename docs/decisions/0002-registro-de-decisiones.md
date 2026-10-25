---
id: D-0002
title: Las decisiones viven en docs/decisions/, un fichero por decisión con índice
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/record-decision/, skills/generate-project-context/, docs/decisions/]
supersedes: null
superseded_by: null
issue: null
---

# D-0002: Las decisiones viven en docs/decisions/, un fichero por decisión con índice

## Contexto

Dentro de dos meses no recordaremos por qué se decidió algo, y un desarrollo nuevo puede contradecirlo sin darse cuenta. Los ADRs solo cubrían arquitectura.

## Decisión

Un fichero por decisión en `docs/decisions/NNNN-*.md`, de tipo `architecture`, `rule` o `discarded`, con un índice en `README.md`. El agente lee el índice y abre solo las decisiones cuyo `affects` cubre lo que va a tocar.

## Alternativas descartadas

- Fichero único: llena el contexto a medida que crece.
- Seguir en `docs/adr/`: no cubre reglas de negocio ni descartes.

## Cómo se hace cumplir

`check_decisions.py` (en `scripts/check.sh`) valida numeración, frontmatter, sustituciones e índice.
