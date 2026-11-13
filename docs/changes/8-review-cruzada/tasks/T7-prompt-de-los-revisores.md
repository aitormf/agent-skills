---
id: T7
title: Los revisores no bloquean solo porque crean que algo no está soportado
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---

**Propósito:** preparación: añadir a `code-reviewer` y `finding-verifier` que creer que algo no está soportado no basta para bloquear, porque sus datos de entrenamiento pueden ser anteriores (S1).

**Dentro:** la línea en `agents/`, `adapters/codex/agents/` y `adapters/opencode/agents/` (o en su fuente, si se generan con `scripts/build-agents.py`); la comprobación del texto en `scripts/check.sh`.

**Fuera:** otros cambios en los prompts de los revisores.

**Flag:** ninguno.
