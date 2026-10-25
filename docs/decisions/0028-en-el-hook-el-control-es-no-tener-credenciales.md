---
id: D-0028
title: En el hook pre-push, lo que protege es que la review no tiene credenciales de GitHub; bloquear gh es defensa en profundidad
type: architecture
status: proposed
date: 2026-10-25
affects: [skills/review-prepush/]
supersedes: null
superseded_by: null
issue: null
---

# D-0028: En el hook pre-push, lo que protege es que la review no tiene credenciales de GitHub; bloquear gh es defensa en profundidad

## Contexto

D-0021 dice que el hook `pre-push` «bloquea `gh` entero». La tercera review de la PR #20 (O1) mostró que `Bash(gh:*)` se salta con `/usr/bin/gh`, `bash -c 'gh …'` o `curl` con `$(gh auth token)`, y en local el `gh` de la persona tiene sesión iniciada. D-0027 resolvió lo mismo para CI.

## Decisión

- El hook ejecuta `claude` sin credenciales de GitHub: sin `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN` ni `GITHUB_ENTERPRISE_TOKEN`, y con un `GH_CONFIG_DIR` temporal y vacío que se borra al salir.
- `Bash(gh:*)` sigue bloqueado como defensa en profundidad.
- No cubre los helpers de credenciales de git ni `~/.netrc`; `git push` está bloqueado aparte.

## Alternativas descartadas

- Ampliar la lista de bloqueos: no puede cubrir todas las formas de llamar a la API.

## Cómo se hace cumplir

`scripts/check.sh` («review: no GitHub credentials in the pre-push hook nor in the review job…»): un `claude` falso registra su entorno y comprueba que no hay tokens, que `GH_CONFIG_DIR` está vacío y que el directorio desaparece tras el hook.
