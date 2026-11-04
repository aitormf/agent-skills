---
id: T16
title: La sesión principal de la review solo lee lo que usa
status: done
depends_on: [T15]
examples: [E32, E33]
verification: scripts/check.sh
---
**Propósito:** refactor del contexto: la sesión principal deja de leer las definiciones de las personas y las skills que no necesita en esa ejecución (R8).

**Dentro:** una instrucción en `review-prepush` y `review-pr`: no leer `.codex/agents/` ni `agents/`, y leer `task-done` y `review-prepush` solo si hay carpeta de cambio; el comando exacto de la auditoría va en la propia skill si hace falta para eso; checks en `check.sh` nombrados E32–E33.

**Fuera:** el formato del informe (T12); las instrucciones base de Codex, sus herramientas y la lista de skills instaladas, que dependen de la configuración de cada persona.

**Flag:** ninguno.
