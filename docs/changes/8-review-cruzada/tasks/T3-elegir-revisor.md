---
id: T3
title: harness-review elige un revisor de otra familia de la lista de la base, o bloquea si no hay ninguno
status: todo
depends_on: [T2]
examples: [E9, E10, E11, E12, E13, E14, E15, E16]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el revisor es el primero de `[review] reviewers` de la base que no es de una familia autora y está instalado; si no queda ninguno, el push se bloquea (R3 y su borde R4, D-0056).

**Dentro:** leer `[review]` del `.harness-config.toml` de la rama base (como `gate.py`, nunca de la rama; por defecto `["claude", "codex"]`); elegir; bloquear con mensaje explícito sin mirar la política fail-open; lanzar el elegido con su línea de comando (`claude -p …` como hoy, `codex exec … -s read-only` con la review y los agentes del proyecto). Los tests, con `claude` y `codex` falsos en el `PATH`.

**Fuera:** el modelo y el esfuerzo de `[review.codex]` y los fallos del revisor (T4); la caché (T5).

**Flag:** ninguno.
