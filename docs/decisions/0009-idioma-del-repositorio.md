---
id: D-0009
title: Skills, commits, scripts y frontmatter en inglés; la documentación, en español
type: rule
status: accepted
date: 2026-10-24
affects: [.]
supersedes: null
superseded_by: null
issue: null
---

# D-0009: Skills, commits, scripts y frontmatter en inglés; la documentación, en español

## Contexto

El repo se usa desde varias herramientas y modelos, y las skills se tradujeron al inglés (e459978). Traducir toda la documentación tiene un coste que no compensa ahora.

## Decisión

En inglés: nombres, `description` y cuerpo de skills y agentes; mensajes de commit y PRs; scripts, tests y manifiestos; claves y valores del frontmatter de lo que generan las skills. En el idioma del proyecto (aquí, español): `docs/` y el texto de los artefactos generados. Lo existente no se traduce de forma proactiva. Las frases de `tests/evals/triggering/cases.tsv` siguen en español a propósito: prueban peticiones en español.

## Alternativas descartadas

- Traducir todo ahora: coste alto y parte se reescribirá en la fase 5.
- Descripciones de skills con frases en español: mezcla idiomas; la suite de activación ya cubre las peticiones en español.

## Cómo se hace cumplir

La suite de activación (`tests/evals/triggering/run.py`) comprueba que las peticiones en español activan las skills en inglés.
