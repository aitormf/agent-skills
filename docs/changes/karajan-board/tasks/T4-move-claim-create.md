---
id: T4
title: move, claim y create solo comprueban y releen
status: todo
depends_on: [T2]
examples: [E11, E12, E13, E14, E15, E16, E17, E18]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: los movimientos de Karajan se aceptan si git ya los refleja y se rechazan con el paso que falta (D-0048).

**Dentro:**
- `move(id, status)`: relee con `board.py --json` y devuelve la HU si su estado es el pedido. Si no, lanza `BoardRejectedError` con el siguiente paso: el `git switch -c <cambio>/T<n> <base>` (`base` de `board.py --json` ya es la ref, p. ej. `origin/main`) para `running`; pasar `task-done` y mergear la PR para `done`. `pending`, `failed` y `skipped` siempre se rechazan.
- `claim(id, who, { release })` devuelve la HU con `claimed_by: null`.
- `create` siempre lanza `BoardRejectedError`.
- Un id que no existe lanza `BoardRejectedError`.
- Tests sobre un repo temporal.

**Fuera:** escribir en git o en los ficheros de tarea (D-0048); `manager.write.*` y `assertNotHeld`.

**Flag:** ninguno.
