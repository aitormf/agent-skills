---
id: T5
title: review-pr elige los revisores por el tamaño del diff
status: todo
depends_on: [T2, T3, T16, T18]
examples: [E10, E11, E12]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: en los tiers 1–2, `review-pr` lanza el `code-reviewer` unificado y el verifier si el diff tiene como mucho 200 líneas (en tier 2, con la pasada de seguridad obligatoria), y el fan-out completo si tiene más o con `--deep`; el tier 0 no cambia (R2, D-0045).

**Dentro:** Step 2 y Step 4 de `skills/review-pr/SKILL.md`, `--deep` en `argument-hint`, la línea de tamaño en el resumen; checks en `check.sh` nombrados E10–E12.

**Fuera:** `review-prepush` (T4); el workflow de CI y `--inline`; la salida compacta (T6).

**Flag:** ninguno.
