---
id: T1
title: Modo --json en el tablero de task-done
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** preparación. `board.py --json <cambio>` saca el tablero como JSON para que el manager de Karajan lo lea sin volver a calcular nada (D-0049).

**Dentro:**
- `skills/task-done/scripts/board.py --json [CHANGE_DIR]` saca una lista con, por tarea: `id`, `title`, `kind` (`ready | blocked | doing | done`), `branch` (o `null`), `depends_on`, `examples` y `path`. Además, la rama base.
- Con problemas en los ficheros de tarea sale con 2 y los mensajes van a stderr, igual que la salida de texto.
- Tests en `scripts/check.sh` sobre un repo temporal con una tarea en cada estado.

**Fuera:** `tier` (T5); el manager JS (T2); la salida de texto, que no cambia.

**Flag:** ninguno; sin `--json` todo sigue igual.
