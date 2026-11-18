---
status: open
issue: 95
---
# Hechos de la review en una sola llamada

**Problema:** en la medición de la review cruzada (T9 en `docs/review/medicion-review.md`), la sesión principal de `review-prepush` sigue siendo más de la mitad de la entrada, unos 300.000 de 500.000 tokens. Hace de 9 a 14 llamadas para reunir hechos que no necesitan modelo: la base, la rama, el log, el diff, el estado, la tarea y la auditoría de `task_done.py`. Además, la review ya no detecta los TODO añadidos sin ticket (B5 de `tests/review-sandbox`, #90), y eso se puede detectar sin modelo. Le importa a quien paga la review en cada push de un agente.

**Plazo máximo:** unos 2 días de trabajo de agente, en tareas de como mucho 200 líneas con los tests (D-0044).

**Fuera de alcance:** `review-pr` (puede usar el script después, en otro change); que el hook `harness-review` calcule los hechos y los pase en el prompt; detectar otros restos sin modelo (salidas de depuración, código comentado), porque ahí un script da falsos positivos; cambiar los revisores o su número (D-0047); arreglar la regresión de B5 en el modelo (el script la cubre sin depender de él).

## Mapa de ejemplos

```
Rule R1: un script lista los TODO, FIXME, XXX y HACK que añade la rama sin ticket
  E1: la rama añade `// TODO: cache invoices in memory` en src/invoices.js:12 → lo lista como `src/invoices.js:12`
  E2: la rama añade `# TODO(#123): …`, `// FIXME ABC-45: …` o un TODO con una URL → no lista ninguno
  E3: un TODO que ya estaba en la base, en una línea que la rama no toca → no lo lista
  E4: `todos = []`, `fixmeCount` o «New TODO/FIXME without a ticket» en un .md (sin dos puntos) → no lista nada
  E5: un TODO añadido en un lockfile o en un fichero borrado → no lo lista
Rule R2: el informe recoge los TODO del script en un solo Nit, fuera del límite de Nits y sin pasar por el verifier (D-0057)
  E6: el script lista dos TODO y el revisor ya llenó Max Nits → el informe tiene además un Nit «2 TODO/FIXME sin ticket» con las dos ubicaciones
  E7: el script no lista ninguno → no hay Nit de TODO
Rule R3: el script de hechos devuelve en una llamada lo que necesita la review de la rama
  E8: en la rama 42-cancelar/T2 con base main → imprime la base resuelta, la rama, el log, el diff --stat, la tarea (fichero y estado), la salida y el código de salida de la auditoría y los TODO de R1
  E9: la rama no tiene commits por delante de la base → imprime «sin cambios frente a <base>» y sale 0
  E10: hay cambios sin commit → lo dice («los cambios sin commit no se revisan ni se suben»)
  E11: rama fix/errata, sin carpeta de change → «tarea: ninguna» y no ejecuta la auditoría
  E12: sin argumento → la base sale de la sección Code review de AGENTS.md; si no hay, de origin/HEAD, main o master; usa origin/<base> si existe
  E13: la auditoría no se puede ejecutar (sin python3 para ella, sale 2) → «auditoría: no comprobada (<motivo>)», sin fallar el resto
Rule R4: review-prepush usa el script de hechos en lugar de reunirlos a mano
  E14: los pasos 1 y 2 de review-prepush piden una llamada al script y pasan su salida tal cual en el brief del code-reviewer; ya no listan los comandos git ni la auditoría
```

La medición final (sin ejemplos) repite la de T9 con `tests/review-sandbox` (Codex, `gpt-6.1-terra`, `medium`, 3 ejecuciones). El objetivo es encontrar 6 de 6 B, con B5 incluido, y que la sesión principal haga menos llamadas y consuma menos entrada que en T9.

## Supuestos

- Ticket es `#<n>`, `<PROYECTO>-<n>` (mayúsculas, guion y número) o una URL en la misma línea. `TODO(nombre):` no es un ticket. Si un proyecto necesita otro patrón, irá después a `.harness-config.toml`.
- Un TODO solo cuenta con forma de comentario: la palabra en mayúsculas y luego `:`, con o sin `(…)` entre medias. Una línea reindentada con un TODO antiguo cuenta como añadida; se acepta.
- El script vive en `skills/review-context/scripts/review_facts.py`, el lado de entrada de las reviews, y llama a `../task-done/scripts/task_done.py --audit` como hoy la skill.
- Los lockfiles son los mismos que ignora `diff_size.py`.

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tareas son la única fuente.
