---
id: D-0043
title: En las reviews, Semgrep solo cuenta los hallazgos en líneas que añade el diff
type: rule
status: accepted
date: 2026-10-29
affects: [skills/review-context/]
supersedes: null
superseded_by: null
issue: null
---

# D-0043: En las reviews, Semgrep solo cuenta los hallazgos en líneas que añade el diff

## Contexto

Semgrep se ejecutaba sobre los ficheros cambiados enteros. En un repo con deuda, cada review arrastraba hallazgos que el autor no había escrito, que luego el verifier tenía que descartar.

## Decisión

`review-context/scripts/semgrep_added.py` ejecuta Semgrep sobre los ficheros cambiados y solo devuelve los hallazgos que tocan una línea añadida o cambiada (`git diff --unified=0 <base>...HEAD`). Los demás se cuentan en Verification, sin listarlos. Con las herramientas MCP de Semgrep se aplica el mismo filtro a mano.

## Alternativas descartadas

- `--baseline-commit` de Semgrep: analiza también la base, que es más lento, y deja pasar hallazgos nuevos en líneas sin tocar de un fichero cambiado, que no son del autor.
- Filtrar en el prompt: un filtro determinista se puede probar y no gasta tokens.

## Cómo se hace cumplir

`scripts/check.sh`, «review: Semgrep only reports findings on the lines the diff adds».
