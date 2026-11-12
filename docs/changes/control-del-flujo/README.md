---
status: done
issue: null
---
# Control del flujo fuera del agente

**Problema:** las reglas del flujo (una tarea por rama, el commit en rojo con los tests de sus ejemplos, que esos tests no se toquen, el tamaño de la tarea) hoy son instrucciones a `implement` y comprobaciones de `task-done`, que el agente puede no ejecutar. Solo Claude Code tiene barreras en la sesión, y ninguna mira estas reglas. Con Codex u OpenCode, o con un `--no-verify`, nada lo para. Le importa a cualquiera que use el kit con más de un agente o en equipo. Karajan Code lo resuelve con Sentinel (hooks de Claude Code que analizan cada comando), que solo vale para Claude Code y que ellos mismos están retirando hacia git hooks y CI (D-0051).

**Plazo máximo:** unos 2–3 días de trabajo de agente, en tareas de como mucho 200 líneas con los tests (D-0044).

**Fuera de alcance:** analizar comandos de shell al estilo Sentinel; bloqueos entre sesiones o worktrees; un motor de políticas; RAG; la review (el revisor de otra familia y el resumen de hechos son otro change, sobre #8, que usará este gate como corte previo); exigir tests por heurística de rutas a cambios sin tarea (D-0011 lo deja al criterio de la persona y de la review); poner CI en este repositorio.

## Mapa de ejemplos

```
Rule R1: el gate solo aplica las reglas de una tarea en su rama (<…>/<cambio>/T<n>, D-0031); en otra rama no exige nada salvo que el proyecto pida --require-task
  E1: rama 42-cancelar/T3 con docs/changes/42-cancelar/tasks/T3-reembolso.md → aplica R2 y R3, sale 0 si pasan
  E2: rama fix/errata, sin --require-task → sale 0 con el aviso "la rama no nombra una tarea: no se comprueba nada"
  E3: rama fix/errata con --require-task y un cambio en src/ → sale 1: "la rama no nombra una tarea"
  E4: rama fix/errata con --require-task y solo cambios en docs/ → sale 0
  E5: rama 42-cancelar/T9 sin fichero T9-*.md en el cambio → sale 1: "la tarea T9 no existe en docs/changes/42-cancelar/"
  E6: rama 42-cancelar/plan con solo ficheros de docs/ → sale 0
  E7: rama 42-cancelar/plan que toca src/ → sale 1: "la PR del plan no lleva código"
Rule R2: en una tarea con ejemplos, los tests en rojo los protege el audit de task-done (D-0012, D-0024); el gate no repite su lógica
  E8: T3 con examples [E1, E2], commit test(T3): E1 E2 red y los tests sin tocar → pasa
  E9: T3 con examples [E1] sin commit test(T3) → sale 1 con las líneas PROBLEM del audit
  E10: una línea añadida en el commit en rojo, cambiada en un commit posterior → sale 1 con la línea PROBLEM del audit
  E11: T3 con examples [] en la rama base → no exige commit en rojo
  E25: la rama de T3 cambia examples, verification o depends_on de su fichero respecto a la rama base (examples [E1] → []) → sale 1: "el plan aprobado no se cambia en la rama de la tarea"
  E26: la rama de T3 toca el fichero de otra tarea (T4-*.md) → sale 1
Rule R3: el tamaño se cuenta como en D-0047 y se avisa, sin bloquear (D-0053)
  E12: 180 líneas → sin aviso
  E13: 260 líneas, tests incluidos → sale 0 con el aviso "260 líneas > 200 (D-0044): parte la tarea en el plan"
  E14: 260 líneas, 120 de ellas en uv.lock → cuenta 140, sin aviso
Rule R4: el mismo gate corre en local y en CI, con el mismo resultado; llega al proyecto como hook de pre-commit del kit (D-0052)
  E15: git push de 42-cancelar/T3 con un test en rojo cambiado → el hook pre-push sale 1 y el push no sale
  E16: el mismo commit subido con --no-verify → el job de CI falla con el mismo mensaje
  E17: CI en la PR de 42-cancelar/T3, con checkout en HEAD separado → toma la rama de GITHUB_HEAD_REF
  E18: sin rama base que comparar (ni origin/HEAD, ni origin/main, ni main) → sale 2: "no puedo comprobar: no encuentro la rama base"
Rule R5: Claude Code, al empezar, reanudar o compactar una sesión, recibe la rama, la tarea y las reglas del flujo
  E19: sesión compactada en 42-cancelar/T3 → el contexto lleva la rama, el título y el propósito de T3, sus ejemplos, su verification y las reglas del flujo
  E20: sesión en main o en una rama sin tarea → solo las reglas del flujo
  E21: rama de una tarea cuyo fichero no existe → las reglas y el aviso de E5, sin fallar
Rule R6: Claude Code no termina el turno con el gate en rojo en la rama de una tarea; a la segunda parada seguida, deja terminar
  E22: 42-cancelar/T3 con examples [E1], código cambiado y sin commit test(T3) → el Stop bloquea con el mensaje del gate
  E23: la misma situación con stop_hook_active true → deja terminar y avisa de que el gate sigue en rojo
  E24: rama sin tarea → el Stop no bloquea
Rule R7: la rama de una tarea no toca los ficheros de control; la lista sale de la rama base, nunca de la rama que se comprueba
  E27: la rama de T3 cambia .pre-commit-config.yaml, .github/workflows/ci.yml, .claude/settings.json o scripts/check.sh → sale 1: "una tarea no cambia el arnés: va en su propia PR, revisada por CODEOWNERS"
  E28: la rama de T3 añade un patrón a la lista de control o lo quita → se usa la lista de la rama base; si la rama toca la lista, sale 1 (E27)
  E29: CI en la PR de T3 con .pre-commit-config.yaml cambiado a otra rev del kit → CI ejecuta el gate en la rev de la rama base
Requisito del proyecto (documentación, sin ejemplos): lo que el kit no puede poner y sin lo que R4 y R7 se quedan en avisos
  S1: setup-guardrails-python y la tabla «Qué se garantiza» del README dicen, como requisito: branch protection en la rama base con el check del gate obligatorio, "Require review from Code Owners", CODEOWNERS sobre la lista de control, la protección aplicada también a admins, y el agente con una identidad propia (cuenta bot o fine-grained token) sin permiso para saltarse la protección ni aprobar → se comprueba con scripts/check.sh (los textos existen)
Question: ¿cómo llega el gate a un proyecto? → D-0052 (recomendado: hook remoto de pre-commit del kit con rev fijada)
Question: ¿el tamaño bloquea? → D-0053 (recomendado: solo avisa; D-0037 sigue en pie)
Question: ¿--require-task por defecto? | a) apagado; el proyecto lo enciende en los args del hook (recomendada: D-0001 deja trabajo directo sin tarea) b) encendido
```

## Supuestos

- `gate.py` vive en `skills/task-done/scripts/`, junto a `board.py` y `task_done.py`, y llama al `--audit` de este último y a `skills/review-context/scripts/diff_size.py`, sin copiar su lógica. Solo usa la biblioteca estándar y git.
- Códigos de salida como `task_done.py`: 0 pasa (con avisos), 1 una regla falla, 2 no se puede comprobar. En CI, 2 hace fallar el job.
- "Cambio de código" para E3, E4, E6 y E7: cualquier fichero fuera de `docs/` y de los `*.md` de la raíz.
- Los hooks de Claude Code (R5, R6) van en la plantilla `.claude/settings.json` de `setup-guardrails-python`, junto a los que ya hay, y llaman al gate con `pre-commit run kit-gate` (el Stop) o `pre-commit run kit-context` (el SessionStart, un segundo hook del kit con `--context`), así que no necesitan otra instalación. El Stop actual (`check-on-stop.sh`) se mantiene.
- La branch protection (el check del gate obligatorio para mergear) se documenta en `setup-guardrails-python` y en la tabla «Qué se garantiza en cada herramienta» del README. Es la única barrera que no se salta con `--no-verify`.
- Lista de control por defecto (R7): `.github/**`, `.pre-commit-config.yaml`, `.claude/settings*.json`, `.claude/hooks/**`, `.codex/**`, `opencode.json`, `scripts/check.sh`, `.gitattributes`, `CODEOWNERS` y la propia lista. El proyecto la amplía en un fichero propio, que también es de control.
- La verificación de cada tarea es `scripts/check.sh` (no hay `AGENTS.md`).

## Tareas

Hay un fichero por tarea en `tasks/`, y cada tarea tiene su rama y su PR. Para ver cuáles están listas, usa el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tarea son la única fuente.
