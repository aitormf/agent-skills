---
id: T10
title: El revisor usa la skill y las personas del kit fijado, no las de la rama revisada
status: done
depends_on: []
examples: [E26, E27]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: lo que guía al revisor sale de la copia del kit que fija la base, para que un agente no rebaje la review desde su propia rama (R8, D-0056).

**Dentro:** en `harness-review.sh`, el prompt de `codex` apunta al `SKILL.md` de la copia del kit (junto al script) y deja de nombrar `.agents/skills/` y `.codex/agents/` del proyecto; `claude` carga la review del kit (comprobar si `claude -p` admite cargar un plugin desde un directorio, como `--plugin-dir`; si no, usa siempre el plugin instalado, nunca `.claude/skills/` ni `.claude/agents/` del repositorio). Los tests, con CLIs falsos que registran sus argumentos.

**Fuera:** proteger otras skills del proyecto; el sandbox de #77.

**Flag:** ninguno.
