---
id: T8
title: Cómo usar las skills con Karajan
status: todo
depends_on: [T6, T7]
examples: []
verification: scripts/check.sh
---
**Propósito:** documentación: cómo se enchufa `kj-board-changes` en un proyecto con Karajan y cómo se trabaja con las dos cosas.

**Dentro:**
- Una sección en `README.md` y el `integrations/karajan-board/README.md`. Cubren el `.karajan/board.yml` con el backend y la allowlist a versión exacta, la instalación (según lo que T2 averiguó), el ciclo `idea-to-change` → PR del plan → `implement` crea `<cambio>/T<n>` → `kj hu move` → `task-done` → merge → `kj hu move … done`, y qué rechaza el manager y por qué (D-0048).
- Si el repo tiene un check de enlaces o de referencias a decisiones en `check.sh`, que siga en verde.

**Fuera:** cambiar el playbook que instala `kj env install`.

**Flag:** ninguno.
