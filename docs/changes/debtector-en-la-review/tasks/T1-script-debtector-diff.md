---
id: T1
title: debtector_diff.py lista lo que la rama añade según debtector
status: todo
depends_on: []
examples: [E1, E2, E3, E4, E5, E6, E7]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo. `skills/review-context/scripts/debtector_diff.py <base>` ejecuta `debtector --json diff --base <base>` y escribe un hallazgo por línea de lo que la rama añade o empeora, y después un recuento (R1, D-0063).

**Dentro:**

- El script, en inglés (docstring, mensajes y salida), con la misma forma que `semgrep_added.py`: sale con 0 con o sin hallazgos, y con 2 si debtector no está en el `PATH` o sale con 2.
- Una línea por ítem de `new_cycles`, `new_god_modules`, `new_sdp_violations`, `instability_regressions`, `worsened_functions`, `new_hotspots` y `worsened_hotspots`, más las de `skipped`. Después, el recuento `debtector: <n> new or worse; <m> resolved`, con `; would block its CI job` si debtector salió con 1.
- Los tests en `scripts/check.sh`, con un `debtector` falso en el `PATH` que devuelve un JSON fijo y el código de salida que se le pida.

**Fuera:** que el hook lo ejecute (T2) y el texto de los skills de review (T3).

**Flag:** ninguno. Nadie llama al script hasta T2 y T3.
