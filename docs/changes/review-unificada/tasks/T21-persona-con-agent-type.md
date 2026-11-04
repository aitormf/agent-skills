---
id: T21
title: En Codex, la review lanza cada persona con su agent_type
status: done
depends_on: []
examples: [E37]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: `review-prepush` y `review-pr` piden en Codex pasar a `spawn_agent` el rol de la persona en `agent_type`, para que se cargue su definición (R10). En T20, con esfuerzo `medium`, la sesión principal lanzó los subagentes sin `agent_type` en 8 de 8 ejecuciones de `review-pr` y en 1 de 4 de `review-prepush`, y arrancaron como agentes genéricos sin instrucciones de persona.

**Dentro:** los pasos que lanzan subagentes (`review-prepush` Steps 3–4, `review-pr` Steps 4 y 6) dicen que en Codex se pase `agent_type: "<persona>"` (`code-reviewer`, `security-auditor`, `test-engineer`, `finding-verifier`) junto a `fork_turns: "none"`; un check en `check.sh` nombrado E37 que lo comprueba en esos cuatro pasos.

**Fuera:** el contenido de las personas; repetir la medición (T10); cambiar el prompt de medición del sandbox.

**Flag:** ninguno.
