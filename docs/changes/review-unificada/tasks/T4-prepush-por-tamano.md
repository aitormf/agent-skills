---
id: T4
title: review-prepush elige los revisores por el tamaño del diff
status: done
depends_on: [T2, T3, T16, T18]
examples: [E7, E8, E9]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `review-prepush` mide el diff con `diff_size.py`; hasta 200 líneas lanza el `code-reviewer` unificado y el verifier, y con más de 200 o con `--deep` el fan-out de tres personas y el verifier, con el aviso de tamaño (R2, D-0045).

**Dentro:** `skills/review-prepush/SKILL.md` (el paso del tamaño, `--deep` en `argument-hint`, el fan-out que hoy describe `review-pr` Step 4, el aviso "pasa de 200 líneas (D-0044)" en el resumen); el hook `pre-push` sigue igual (no pasa `--deep`); checks en `check.sh` nombrados E7–E9.

**Fuera:** `review-pr` (T5); la salida compacta (T6); la documentación (T8).

**Flag:** ninguno.
