---
id: T3
title: setup-guardrails-python escribe [review] verify
status: done
depends_on: []
examples: [E16]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: el `.harness-config.toml` que genera `setup-guardrails-python` trae `[review] verify = ["./scripts/check.sh"]` (R5, D-0061).

**Dentro:** la plantilla y el texto de `setup-guardrails-python` (que explica la clave junto a `reviewers`) y su test en `scripts/check.sh`.

**Fuera:** el `.harness-config.toml` de este repo, que es un fichero de control y lo cambia la persona en `main`. Tampoco entra `docs/actualizar.md`, salvo una línea para proyectos existentes si la sección de la versión ya existe.

**Flag:** ninguno.
