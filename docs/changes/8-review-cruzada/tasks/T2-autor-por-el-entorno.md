---
id: T2
title: harness-review distingue el push de un agente del de una persona por el entorno
status: done
depends_on: [T1]
examples: [E4, E5, E6, E7, E8]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el hook saca las familias autoras del entorno del push y no revisa el de una persona (R2, D-0056).

**Dentro:** la detección por marcadores concretos (`CLAUDECODE=1`, `CODEX_THREAD_ID` y el de OpenCode, que se comprueba aquí y se anota en D-0056 si hace falta), en un solo sitio del script; sin marcadores, sale 0 con «push de una persona: sin review automática»; con un agente, se ignoran `SKIP_CLAUDE_REVIEW`, `REVIEW_KIT_COMMAND`, `REVIEW_KIT_ALLOWED_TOOLS` y `REVIEW_KIT_MODEL`.

**Fuera:** elegir el revisor según las familias (T3).

**Flag:** ninguno.
