---
id: T17
title: Repetir la medición base con las personas del sandbox
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** preparación: corregir la base de T1, que usó las copias globales de `~/.codex/agents/` en lugar de las personas del commit medido (S4).

**Dentro:** que `measure.sh` haga que Codex use las personas del sandbox, sin editar `~/.codex` ni copiar credenciales al repo; una comprobación en `summarize.py` que marca como problema una ejecución cuyas personas no coincidan con las del sandbox; una ejecución de prueba y, si pasa, las 3 de cada comando con `gpt-6.1-terra`; Semgrep funcionando si se puede sin ampliar los permisos fuera del sandbox, y si no, dicho; los resultados de T1 quedan marcados como no comparables en `docs/review/medicion-review.md`.

**Fuera:** cambiar la review; actualizar las copias globales de la persona.

**Flag:** ninguno.
