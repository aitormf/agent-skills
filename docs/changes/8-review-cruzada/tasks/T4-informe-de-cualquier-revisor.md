---
id: T4
title: El hook decide con el REVIEW_RESULT de cualquier revisor y nombra al que falla
status: done
depends_on: [T3]
examples: [E17, E18, E19, E20]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el resultado y los fallos de un revisor que no es `claude` se tratan como hoy los de `claude` (R5).

**Dentro:** decidir con la última línea `REVIEW_RESULT` de cualquier revisor; un fallo (salida distinta de 0, timeout) avisa nombrando al revisor y sigue la política actual (`REVIEW_KIT_FAIL_CLOSED`); `codex` con el modelo y el esfuerzo de `[review.codex]` (por defecto `gpt-6.1-terra`, `medium`), en solo lectura y sin credenciales de GitHub (D-0027).

**Fuera:** una cadena de reserva entre revisores.

**Flag:** ninguno.
