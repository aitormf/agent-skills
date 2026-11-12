---
status: open
issue: null
---
# Las tareas de docs/changes como HUs de Karajan Code

> **En pausa desde el 2026-11-12 ([D-0051](../../decisions/0051-aplazar-la-integracion-con-karajan.md)).** T1 está hecha y se queda. No implementes T2 a T8: se retoma cuando alguien que use `kj` lo pida.

**Problema:** Karajan Code (`kj`) gobierna el trabajo del agente con tarjetas (HUs): sus gates `card-first` y `board-sync` piden que cada rama nombre una tarjeta y que una tarjeta mergeada se mueva en el tablero. Nuestras skills ya llevan el trabajo en curso en `docs/changes/<cambio>/tasks/T<n>-<slug>.md` (D-0029), con la rama como señal de "en curso" (D-0034). Si un proyecto usa las dos cosas, hoy hay que escribir cada tarea dos veces, una como fichero y otra como HU, y los dos estados se separan. Le importa a quien usa nuestras skills dentro de un proyecto con Karajan.

**Plazo máximo:** unos 2–3 días de trabajo de agente, repartidos en tareas de como mucho 200 líneas con los tests (D-0044).

**Fuera de alcance:** sincronizar con GitHub Issues, Linear o Trello (Karajan ya tiene sus managers, y se puede apuntar a ellos con `--ref`); el rol `hu-reviewer` y su certificación de historias; cambiar el agente `implement` para que delegue en `kj code` (gate `delegate`); publicar el paquete en npm, si Karajan puede cargarlo desde el repo (Q2); los estados `failed` y `skipped`, que no tienen equivalente en nuestro tablero.

## Mapa de ejemplos

```
Rule R1: cada tarea de un cambio abierto es una HU; su id es <cambio>/T<n>, el mismo nombre que su rama (D-0031), y su ref es la ruta del fichero (D-0048)
  E1: docs/changes/42-cancelar-viaje/tasks/T3-reembolso.md → HU short_id "42-cancelar-viaje/T3", title el del frontmatter, ref "docs/changes/42-cancelar-viaje/tasks/T3-reembolso.md"
  E2: un cambio cuyo README dice status: done → list() no devuelve sus tareas
  E3: un repo sin docs/changes/ → list() devuelve []
  E4: un fichero de tarea mal formado (board.py sale con 2) → list() lanza BoardRejectedError con el mensaje del tablero; no devuelve una lista a medias
Rule R2: el estado de la HU sale de git como en el tablero de task-done (D-0034); el manager no guarda nada
  E5: T3 con status: todo, sin rama, dependencias mergeadas (ready) → pending
  E6: T3 con status: todo y una dependencia sin mergear (blocked) → pending
  E7: existe la rama 42-cancelar-viaje/T3 (local o en origin) → running
  E8: status: done mergeado en la rama base → done
  E9: status: done solo en la rama de la tarea, con la PR sin mergear → running
  E10: ninguna tarea sale nunca como failed ni skipped
Rule R3: el manager nunca escribe; move, claim y create solo comprueban y releen (D-0048)
  E11: move("42-cancelar-viaje/T3", "running") con la rama creada → devuelve la HU en running
  E12: move(…, "running") sin la rama → BoardRejectedError que dice "git switch -c 42-cancelar-viaje/T3 origin/main"
  E13: move(…, "done") con la PR mergeada → devuelve la HU en done (así pasa el gate board-sync)
  E14: move(…, "done") sin mergear → BoardRejectedError: "pasa task-done y mergea la PR"
  E15: move(…, "pending" | "failed" | "skipped") → BoardRejectedError
  E16: create({ title: "Paginar el listado" }) → BoardRejectedError: las tareas nacen en idea-to-change o plan-to-tasks
  E17: claim("42-cancelar-viaje/T3", "aitor") → devuelve la HU con claimed_by null (la reserva es la rama; capability assignee: false)
  E18: move o claim de un id que no existe ("42-cancelar-viaje/T9") → BoardRejectedError
Rule R4: un id es <cambio>/T<n>; se reconoce también con el prefijo de rama que el proyecto use (D-0031)
  E19: isId("42-cancelar-viaje/T3") → true
  E20: isId("HU-12") → false; isId("T3") → false; isId("42-cancelar-viaje/T3-reembolso") → false
  E21: canonicalId("feat/42-cancelar-viaje/T3") → "42-cancelar-viaje/T3"
Rule R5: una tarea puede llevar tier (trivial | standard | deep) con su motivo; una tarea level: A es siempre deep
  E22: tier: trivial y tier_reason: "solo docs" → la HU lleva tier { level: "trivial", reason: "solo docs" }
  E23: sin tier → la HU no lleva tier (kj usa su propia señal)
  E24: level: A con tier: standard → la HU sale deep
  E25: tier: huge → board.py lo cuenta como problema y sale con 2
Rule R6: el manager cumple el story-contract de Karajan
  E26: assertManager(createManager({ config, env, run })) no lanza; capabilities { acceptanceCriteria: "body", dependencies: "graph", assignee: false, verdicts: "pr", offline: true, tier: true }; credentials []
  E27: runStoryContract("kj-board-changes", makeManager) pasa contra un repo de prueba con un cambio de tres tareas
Question: ¿el manager escribe (crea la rama, pone status) o solo comprueba? → D-0048 (recomendado: solo comprueba)
Question: ¿dónde vive el código JS y cómo se prueba? → D-0049 (recomendado: integrations/karajan-board/, Node ≥ 22, en check.sh)
Question: ¿Karajan carga un manager de la allowlist desde una ruta del repo o solo desde node_modules? | a) T1 lo comprueba y, si solo es node_modules, la doc dice `npm install --no-save ./integrations/karajan-board` (recomendada) b) publicar en npm ya
Question: ¿runStoryContract exige que create funcione? | a) si lo exige, la tarea de R6 lo dice y paramos a decidir antes de forzar escrituras (recomendada) b) que create escriba un fichero de tarea suelto
```

## Supuestos

- La lista de HUs sale de `board.py`, con un modo `--json` nuevo, por cada `docs/changes/*/` con README `status: open`. No se duplica la lógica del tablero en JS.
- `acceptanceCriteria` va en el `body`: las líneas `E<n>` del mapa que la tarea lista en `examples`.
- Las dependencias (`depends_on`) se exponen como grafo con el nombre de campo que use `src/hu/graph.js` de Karajan; T1 lo comprueba.
- `offline: true`: el manager solo lee refs locales y la rama base local o en `origin`, sin hacer `git fetch`.
- La rama de la tarea la sigue creando `implement` como hoy (`<cambio>/T<n>`). `kj hu start` la reutiliza porque nombra el id. Una rama `feat/<id>-<slug>` creada por `kj` no se reconoce (E20).
- `idea-to-change` y `plan-to-tasks` proponen el `tier` de cada tarea. Si no se proponen, la tarea va sin tier (E23).
- La verificación de cada tarea es `scripts/check.sh` (no hay `AGENTS.md`).

## Tareas

Hay un fichero por tarea en `tasks/`, y cada tarea tiene su rama y su PR. Para ver cuáles están listas, usa el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tarea son la única fuente.
