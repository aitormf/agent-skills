---
id: D-0027
title: En CI, lo que protege el job de review es que no tiene token; bloquear gh es defensa en profundidad
type: architecture
status: accepted
date: 2026-10-25
affects: [skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0027: En CI, lo que protege el job de review es que no tiene token; bloquear gh es defensa en profundidad

## Contexto

D-0021 dice que el hook y `claude-review.yml` «bloquean `gh` entero». La segunda review de la PR #20 (O1) señaló que `Bash(gh:*)` es una regla por prefijo: `/usr/bin/gh`, `bash -c` o `curl` se la saltan, y el agente tiene Bash en ese job. Si alguien añade un token al job, el bloqueo no lo para.

## Decisión

- El control real del job de review es que no tiene credenciales: permisos exactamente `contents: read`, sin `GH_TOKEN` ni `github.token`, y checkout con `persist-credentials: false`. Sin token no hay lecturas autenticadas de texto no fiable ni escrituras.
- `Bash(gh:*)` sigue bloqueado como defensa en profundidad, no como la protección.
- El token vive solo en el job `publish`, que no ejecuta ningún modelo.

## Alternativas descartadas

- Confiar en la lista de bloqueos de herramientas: se salta con cualquier otra forma de llamar a `gh` o a la API.

## Cómo se hace cumplir

`scripts/check.sh` («review: gh fully denied in the pre-push hook and in the review job»): comprueba los permisos del job `review`, `persist-credentials: false` y la ausencia de tokens.
