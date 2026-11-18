---
id: D-0057
title: Los TODO añadidos sin ticket los detecta un script y van al informe en un solo Nit, fuera del límite de Nits y sin pasar por el verifier
type: rule
status: accepted
date: 2026-11-14
affects: [skills/review-context/, skills/review-prepush/, skills/review-report/]
supersedes: null
superseded_by: null
issue: 90
---

# D-0057: TODO sin ticket en un Nit determinista

## Contexto

`review-report` §1 trata un TODO/FIXME nuevo sin ticket como Nit u Optional. Desde la evolución del kit entre T20 y T10, el `code-reviewer` deja de verlo (B5, #90): no lo descarta el verifier ni el límite de Nits, ni siquiera aparece. Un TODO sin ticket se reconoce sin modelo en las líneas que añade el diff.

## Decisión

`review_facts.py` lista los TODO, FIXME, XXX y HACK que añade la rama sin ticket. La sesión principal los pone en el informe como **un solo Nit** con todas las ubicaciones. Ese Nit no pasa por el `finding-verifier` ni cuenta para `Max Nits`. El revisor no los vuelve a informar.

## Alternativas descartadas

- **Pasarlos al `code-reviewer` como hechos y que él los informe**: vuelve a depender del modelo, que es lo que falla en #90, y el límite de Nits o el verifier pueden recortarlos.
- **Un Nit por TODO, dentro del límite**: una rama con muchos TODO llenaría los Nits y echaría hallazgos del modelo, o los TODO caerían en el recorte.
- **Subirlos a Required**: son restos baratos de arreglar y `review-report` los clasifica como Nit u Optional; bloquear por ellos no compensa.

## Cómo se hace cumplir

Tests E1–E7 del change `95-hechos-de-la-review` en `scripts/check.sh`.
