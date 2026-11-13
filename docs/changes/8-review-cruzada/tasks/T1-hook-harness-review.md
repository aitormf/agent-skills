---
id: T1
title: La review llega como hook harness-review del kit y no lanza el revisor con el gate en rojo
status: todo
depends_on: []
examples: [E1, E2, E3]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: publicar la review como hook `harness-review` (pre-push) que ejecuta el gate antes de lanzar el revisor (R1, D-0055).

**Dentro:** el script del hook en el kit, a partir del `pre-push` actual (`git mv` a `skills/review-prepush/scripts/`, para que el diff cuente el movimiento y no una copia), que primero ejecuta `gate.py` y con el gate en rojo sale 1 sin lanzar el revisor; la entrada `harness-review` en `.pre-commit-hooks.yaml` (`language: script`, `stages: [pre-push]`); el hook en la plantilla `.pre-commit-config.yaml` de `setup-guardrails-python`. Los tests, con un `claude` falso en el `PATH` que registra si lo llamaron. El revisor sigue siendo `claude` para cualquier push.

**Fuera:** detectar el agente (T2); elegir el revisor (T3); la documentación de migración (T8).

**Flag:** ninguno.
