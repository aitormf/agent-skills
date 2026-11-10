---
id: T5
title: tier opcional en las tareas, expuesto en la HU
status: todo
depends_on: [T2]
examples: [E22, E23, E24, E25]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: una tarea puede llevar su tier y Karajan lo usa para elegir el modelo de `kj code --card`.

**Dentro:**
- `board.py` acepta en el frontmatter `tier` (`trivial | standard | deep`) y `tier_reason`, que son opcionales. Cualquier otro valor de `tier` es un problema, y el tablero sale con 2.
- `--json` saca `tier` y `tier_reason`; una tarea `level: A` sale `deep`.
- El manager pone `tier { level, reason }` en la HU, sin tier si la tarea no lo tiene, y declara `tier: true`.
- Tests en `check.sh` y en el paquete.

**Fuera:** que las skills propongan el tier (T6).

**Flag:** ninguno; sin `tier` todo sigue igual.
