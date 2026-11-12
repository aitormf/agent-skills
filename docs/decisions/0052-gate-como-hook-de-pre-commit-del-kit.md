---
id: D-0052
title: El gate del flujo llega a cada proyecto como hook remoto de pre-commit del kit, con rev fijada; el mismo hook corre en pre-push y en CI
type: architecture
status: accepted
date: 2026-11-12
affects: [skills/task-done/scripts/, .pre-commit-hooks.yaml, skills/setup-guardrails-python/]
supersedes: null
superseded_by: null
issue: null
---

# D-0052: El gate llega como hook remoto de pre-commit del kit

## Contexto

`gate.py` tiene que correr en el repositorio del proyecto, en local y en CI, con cualquier agente. El kit se instala como plugin o con `npx skills`, fuera del repositorio: CI no lo ve. Hoy la review de CI instala el plugin con `claude`, lo que ata el check a Claude Code. El proyecto ya usa pre-commit (`setup-guardrails-python`).

## Decisión

- El kit publica un `.pre-commit-hooks.yaml` en su raíz con el hook `kit-gate` (`language: script`, `entry: skills/task-done/scripts/gate.py`, `stages: [pre-push, manual]`), sin dependencias de Python.
- El proyecto lo declara en su `.pre-commit-config.yaml` con una `rev` fijada (una etiqueta del kit). Actualizarla es una PR del proyecto.
- En local corre en `pre-push`. CI ejecuta el mismo hook con `pre-commit run kit-gate --hook-stage manual`, y la branch protection lo exige para mergear.
- Los hooks de Claude Code llaman también a `pre-commit run kit-gate`.

## Alternativas descartadas

- **Copiar `gate.py` al repositorio del proyecto**: la copia se separa del kit y nadie la actualiza; además depende de `task_done.py` y `diff_size.py`, que habría que copiar también.
- **Instalar el plugin en CI y llamar al script desde allí**: necesita el CLI `claude` y credenciales para un check que no usa ningún modelo.
- **Sin rev fijada (siempre la última del kit)**: un cambio del kit cambiaría el resultado de CI sin una PR del proyecto.

## Cómo se hace cumplir

`scripts/check.sh` valida `.pre-commit-hooks.yaml` (el `entry` existe y es ejecutable) y ejecuta el hook con `pre-commit try-repo` en un repositorio de prueba.
