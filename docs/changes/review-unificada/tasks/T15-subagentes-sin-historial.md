---
id: T15
title: Los subagentes de la review arrancan sin el historial de la sesión principal
status: todo
depends_on: [T17]
examples: [E30, E31]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `review-prepush` y `review-pr` lanzan las personas sin historial heredado (en Codex, `fork_turns: "none"`), con un encargo que basta por sí solo (R7, D-0046).

**Dentro:** el paso de lanzar subagentes de las dos skills; `check.sh` con checks nombrados E30–E31 que comprueban que las dos lo dicen.

**Fuera:** las lecturas de la sesión principal (T16); cambiar el contenido de las personas.

**Flag:** ninguno.
