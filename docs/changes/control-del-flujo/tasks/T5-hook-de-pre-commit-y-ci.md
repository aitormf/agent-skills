---
id: T5
title: El gate llega al proyecto como hook de pre-commit del kit y corre en CI con la configuración de la base
status: todo
depends_on: [T1]
examples: [E15, E16, E29]
verification: scripts/check.sh
---
**Propósito:** preparación: publicar el gate como hook `kit-gate` y llamarlo en pre-push y en CI (R4, D-0052).

**Dentro:** `.pre-commit-hooks.yaml` en la raíz del kit (`language: script`, `stages: [pre-push, manual]`); el hook en la plantilla `.pre-commit-config.yaml` de `setup-guardrails-python` con `rev` fijada; un job en la plantilla `ci.yml` que ejecuta `pre-commit run kit-gate --hook-stage manual` con el `.pre-commit-config.yaml` de la rama base (`git show origin/<base>:…`); la comprobación en `check.sh` con `pre-commit try-repo` sobre un repo de prueba.

**Fuera:** los hooks de Claude Code (T6, T7); la documentación de la branch protection (T8).

**Flag:** ninguno.
