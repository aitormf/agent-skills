---
id: D-0025
title: La review de CI no usa gh ni lee la descripción de la PR; los mensajes de los commits ocupan su lugar
type: architecture
status: accepted
date: 2026-10-25
affects: [skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0025: La review de CI no usa gh ni lee la descripción de la PR; los mensajes de los commits ocupan su lugar

## Contexto

Con D-0021 el job de review de CI deja de leer issues. Para leer la descripción de la PR seguiría necesitando `gh` y un token, y la descripción es texto que no ha pasado por un commit (D-0023). El diff no necesita `gh`: el checkout trae la historia completa.

## Decisión

- El job de review de CI solo tiene `contents: read`, sin `GH_TOKEN`, con `Bash(gh:*)` bloqueado y sin credenciales guardadas tras el checkout.
- Crea una rama local con el nombre de la rama de la PR y apunta `origin/HEAD` a su base. Después ejecuta `/review-pr <rama> origin/<base>`; `review-pr` acepta la rama base como argumento opcional.
- La descripción de la PR no se comprueba en CI; los mensajes de los commits ocupan su lugar. En local, `review-pr` sigue igual.

## Alternativas descartadas

- Permitir solo `gh pr view --json title,body`: vuelve a meter `gh` y un token en un job con la clave de la API, por un texto que D-0023 trata como no fiable.
- Pasar la descripción al job desde el evento de GitHub: es el mismo texto no fiable, solo que por otra vía.

## Cómo se hace cumplir

`scripts/check.sh` («review: gh fully denied in the pre-push hook and in the review job»): comprueba que el workflow bloquea `gh` y no pide `issues: read` ni `pull-requests: read`.
