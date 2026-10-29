---
id: D-0042
title: El hook pre-push guarda el veredicto con el sha256 del diff y lo reutiliza, también un bloqueo, mientras el diff no cambie
type: architecture
status: accepted
date: 2026-10-29
affects: [skills/review-prepush/]
supersedes: null
superseded_by: null
issue: 7
---

# D-0042: El hook pre-push guarda el veredicto con el sha256 del diff y lo reutiliza, también un bloqueo, mientras el diff no cambie

## Contexto

Si un push falla por otro motivo (red, rechazo del remoto) o se repite hacia otro remoto, el hook volvía a lanzar la review completa sobre el mismo diff, y se pagaba dos veces (#7).

## Decisión

- La clave es el sha256 de `git diff --binary <base>...HEAD`, el diff que ve `review-prepush`. La base es `REVIEW_KIT_BASE` o, si no, `origin/HEAD`, `origin/main`, `origin/master`, `main` o `master`. Sin base, o sin historia común con ella, no se guarda nada.
- Se guarda en `.git/review-kit/verdicts`, fuera de git, una línea por veredicto: hash, `PASS` o `BLOCK`, base y fecha. El informe de un bloqueo se copia a `.git/review-kit/<hash>.md`.
- Un bloqueo también se reutiliza: repetir la review del mismo diff suele dar lo mismo y cuesta lo mismo. `REVIEW_KIT_RERUN=1` la repite.
- Si la review falla (error, timeout, sin línea `REVIEW_RESULT`), no se guarda nada.

## Alternativas descartadas

- La clave por commit (`HEAD`): un rebase sin cambios en el diff obligaría a revisar otra vez.
- Que lo guarde la skill: la skill no sabe si el push salió, y fuera del hook nadie lo reutiliza.
- Reutilizar solo los `PASS`: un bloqueo repetido costaría una review entera para, casi siempre, el mismo resultado.

## Cómo se hace cumplir

`scripts/check.sh`, «review: the pre-push hook reuses the verdict of a diff it already reviewed (#7)».
