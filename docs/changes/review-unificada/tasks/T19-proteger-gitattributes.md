---
id: T19
title: Denegar al modelo la edición de .gitattributes
status: done
depends_on: []
examples: [E36]
verification: scripts/check.sh
---
**Propósito:** preparación: que el modelo no pueda editar `.gitattributes` con sus herramientas de edición, porque decide qué cuenta como generado en la review (R9).

**Dentro:** `Edit(./.gitattributes)` en `deny` de `skills/setup-guardrails-python/assets/files/.claude/settings.json`; un `.claude/settings.json` en este repo con esa regla y `Edit(./.claude/settings.json)`, y `.claude/worktrees/` en `.gitignore`; la fila de la tabla de garantías de `README.md`, diciendo con claridad lo que no cubre: una regla `Edit` no frena un comando de shell, y hay que comprobar si Codex tiene un equivalente para ficheros; si no lo tiene, se dice; un check en `check.sh` nombrado E36.

**Fuera:** `diff_size.py` (T18).

**Flag:** ninguno.
