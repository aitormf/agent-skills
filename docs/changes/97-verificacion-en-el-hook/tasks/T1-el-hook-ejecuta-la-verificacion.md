---
id: T1
title: El hook ejecuta la verificación y Semgrep antes del revisor
status: done
depends_on: []
examples: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E15]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo. En el push de un agente, `harness-review.sh` ejecuta los comandos de `[review] verify` y Semgrep, ambos leídos de la rama base, antes de lanzar al revisor. Bloquea si la verificación sale en rojo y pasa los resultados al revisor en `REVIEW_KIT_VERIFICATION` (R1, R2, R3, D-0061, D-0062).

**Dentro:**
- La lectura de `[review] verify` y `[review] semgrep` desde la rama base (D-0054), con un script de Python junto al hook si hace falta parsear TOML.
- La ejecución con 600 s por comando.
- El bloqueo con el comando, el código de salida y las últimas 40 líneas.
- `semgrep_added.py`.
- El fichero `.git/review-kit/verification.md`.
- La variable de entorno que se pasa al revisor (claude y codex).
- Que la caché de veredictos se compruebe antes de verificar.
- Los tests del hook en `scripts/check.sh`, con un revisor falso.

**Fuera:** que `review-prepush` use el fichero (T2) y la plantilla de `setup-guardrails-python` (T3).

**Flag:** ninguno. Sin la clave, el hook no ejecuta nada nuevo.
