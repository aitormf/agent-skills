---
id: D-0055
title: La review pre-push llega a cada proyecto como hook harness-review del kit, con rev fijada, y ejecuta el gate antes de lanzar un revisor
type: architecture
status: accepted
date: 2026-11-13
affects: [skills/review-prepush/, .pre-commit-hooks.yaml, skills/setup-guardrails-python/]
supersedes: null
superseded_by: null
issue: 8
---

# D-0055: La review llega como hook harness-review del kit

## Contexto

El hook de la review es una copia de `skills/review-prepush/assets/pre-push` en `.git/hooks/pre-push`. No se actualiza con el kit, y desde D-0052 el gate ya llega como hook remoto de pre-commit con `rev` fijada, con `pre-push` entre los tipos que instala `prek install`, que además sobrescribe ese fichero. La review cruzada (#8) necesita leer `.harness-config.toml` de la rama base y saber si el gate pasa antes de gastar tokens.

## Decisión

La review se publica en `.pre-commit-hooks.yaml` como un tercer hook, `harness-review`, en la fase `pre-push`, y el proyecto lo declara junto a `harness-gate` y `harness-context`, con la misma `rev`. Antes de lanzar ningún revisor ejecuta el gate él mismo, porque pre-commit sigue con el resto de hooks aunque uno falle: con el gate en rojo no se lanza el revisor. Conserva lo que hace hoy el `pre-push`: la caché de veredictos (D-0042), el timeout, la falta de credenciales de GitHub y la línea `REVIEW_RESULT`. No va dentro de `harness-gate`, porque ese hook corre también en el Stop de Claude Code y en CI, y costaría una review por turno.

## Alternativas descartadas

- **Seguir con la copia en `.git/hooks/pre-push`**: no se actualiza con el kit y choca con `prek install`.
- **La review dentro de `harness-gate`**: una review en cada Stop de Claude Code y en cada ejecución de CI.
- **Que pre-commit corte con `fail_fast`**: depende de la configuración del proyecto y corta también sus otros hooks.

## Cómo se hace cumplir

E1–E3 del change `8-review-cruzada` en `scripts/check.sh`.
