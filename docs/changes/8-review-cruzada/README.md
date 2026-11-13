---
status: done
issue: 8
---

# Review cruzada en el push de un agente

**Problema:** el hook pre-push lanza siempre `claude -p`. Si el código lo escribió Claude, el revisor comparte modelo, sesgos y puntos ciegos con el autor («the coder never grades its own homework»). Además, el hook es una copia suelta en `.git/hooks/pre-push`, que no se actualiza con el kit y que un agente se salta con `--no-verify`, `SKIP=` o `SKIP_CLAUDE_REVIEW=1`. Le importa a quien deja que los agentes suban código. Lo que sube una persona es responsabilidad suya: no se revisa de forma automática.

**Plazo máximo:** unos 2–3 días de trabajo de agente, en tareas de como mucho 200 líneas con los tests (D-0044).

**Fuera de alcance:** un revisor en CI; identidades o credenciales por familia; el sandbox sin red con `harness push` (#77), que es la garantía real frente a un agente que esquive las reglas; una cadena de reserva cuando se acaba la cuota (se aplica la política actual, fail-open o fail-closed, con aviso); recortar la orquestación de la review con un script de hechos (otro change); el `finding-verifier` en otra familia; quitar o fusionar revisores (D-0047).

## Mapa de ejemplos

```
Rule R1: la review llega como hook `harness-review` del kit, en pre-push, y antes de lanzar un revisor ejecuta el gate (D-0055)
  E1: un agente hace push de la rama 42-cancelar/T3 sin commit en rojo → el gate sale 1 → harness-review sale 1 con «gate en rojo: no se lanza el revisor» y no llama a ningún revisor
  E2: un agente hace push de fix/errata (el gate sale 0) → se lanza el revisor
  E3: .pre-commit-config.yaml de la plantilla con harness-gate, harness-context y harness-review en el mismo repo y rev → prek install deja el hook pre-push; ya no se copia nada a .git/hooks

Rule R2: el push de una persona no se revisa de forma automática; el de un agente, siempre (D-0056)
  E4: push sin CLAUDECODE ni CODEX_THREAD_ID ni la variable de OpenCode → sale 0 con «push de una persona: sin review automática», sin llamar a ningún revisor
  E5: push con CLAUDECODE=1 → la familia del agente es claude
  E6: push con CODEX_THREAD_ID (y variables CLAUDE_CODE_* heredadas de la sesión que lanzó Codex, pero sin CLAUDECODE) → la familia es codex, solo codex
  E7: push con CLAUDECODE=1 y CODEX_THREAD_ID a la vez (un Codex lanzado desde Claude Code) → las dos familias cuentan como autoras
  E8: push de un agente con SKIP_CLAUDE_REVIEW=1 o REVIEW_KIT_COMMAND=… → se ignoran y se revisa igual; en el push de una persona siguen funcionando

Rule R3: el revisor es el primero de `[review] reviewers`, en el .harness-config.toml de la rama base, que no es de ninguna familia autora y está instalado (D-0056)
  E9: CLAUDECODE=1, reviewers = ["codex", "claude"], codex instalado → revisa codex
  E10: CLAUDECODE=1, reviewers = ["claude", "codex"] → se salta claude y revisa codex
  E11: CODEX_THREAD_ID, reviewers = ["codex", "claude"] → revisa claude
  E12: CLAUDECODE=1 y CODEX_THREAD_ID, reviewers = ["codex", "claude"] → R4 (no queda ninguno)
  E13: la rama cambia reviewers en su .harness-config.toml → se usa la lista de la base
  E14: la base no tiene tabla [review] → se usa la lista por defecto

Rule R4: si no queda ningún revisor de otra familia, el push se bloquea con un mensaje explícito, sea cual sea la política fail-open; nunca se revisa a sí mismo
  E15: CLAUDECODE=1, reviewers = ["claude"] → sale 1: «no hay revisor de otra familia: el agente es claude y reviewers solo tiene claude»
  E16: CLAUDECODE=1, reviewers = ["codex"], codex no está en el PATH → sale 1: «codex no está instalado»

Rule R5: cualquier revisor deja el mismo informe (review-report §4) y la misma línea REVIEW_RESULT, y el hook decide con ella como hoy
  E17: el revisor codex termina con «REVIEW_RESULT: BLOCK critical=1 …» → sale 1 y guarda el informe
  E18: el revisor codex termina con «REVIEW_RESULT: PASS critical=0 …» → sale 0
  E19: el revisor codex sale con error (sin cuota) → aviso que nombra a codex y política actual: sale 0 (fail-open) o 1 con REVIEW_KIT_FAIL_CLOSED=1
  E20: codex se lanza con el modelo y el esfuerzo de [review.codex] (por defecto gpt-6.1-terra, medium), en solo lectura y sin credenciales de GitHub

Rule R6: el veredicto guardado (D-0042) recuerda la familia del revisor y solo se reutiliza si no es de una familia autora
  E21: diff con PASS de codex guardado; hace push un agente claude → se reutiliza
  E22: el mismo diff; hace push un agente codex → no se reutiliza: revisa claude

Rule R7: un agente no se salta los hooks del push por las vías normales (defensa en profundidad; la garantía es #77)
  E23: Claude Code: git push --no-verify, git commit -n, SKIP=harness-review git push, git -c core.hooksPath=/dev/null push → el hook PreToolUse lo deniega; git push origin main y git push -n (dry run) pasan
  E24: Codex: git push --no-verify y git commit --no-verify → codex execpolicy check los marca forbidden
  E25: OpenCode: git push --no-verify y git commit --no-verify → permission.bash los deniega

Rule R8: el revisor usa la skill y las personas de la review del kit fijado (la rev de la base), nunca las de la rama que revisa
  E26: la rama cambia .agents/skills/review-prepush/SKILL.md y un agente claude hace push → codex ejecuta el SKILL.md de la copia del kit, y el prompt no nombra .agents/skills ni .codex/agents del proyecto
  E27: la rama tiene .claude/skills/review-prepush/ y .claude/agents/code-reviewer.md propios y un agente codex hace push → claude no ejecuta /review-prepush del repositorio ni sus agentes: usa los del kit

Question: ¿cómo llega la review al proyecto? → D-0055 (recomendado: hook harness-review del kit, con rev fijada, junto al gate)
Question: ¿quién es el autor y quién revisa? → D-0056 (recomendado: la familia del agente que hace push, por su entorno; la lista de revisores en .harness-config.toml de la base; sin otra familia, se bloquea; el push de una persona no se revisa)
Question: ¿OpenCode como revisor en este change? | a) solo como autor detectado; como revisor, más adelante (recomendada: #8 pide codex, y lanzar la review headless con subagentes en OpenCode está sin probar) b) también como revisor
```

Pasos sin ejemplos:

```
  S1: los prompts de code-reviewer y finding-verifier (agents/, adapters/codex/, adapters/opencode/) dicen que creer que algo no está soportado no basta para bloquear, porque los datos de entrenamiento pueden ser anteriores → scripts/check.sh comprueba el texto
  S2: la medición con tests/review-sandbox (build.sh --codex) con un agente claude haciendo push: revisa codex (terra, medium), detecta B1–B6 (6 de 6) y no sobrevive ningún señuelo D1–D3; queda en docs/review/medicion-review.md
  S3: docs/actualizar.md (sección de la versión siguiente: quitar el .git/hooks/pre-push copiado, añadir harness-review y [review]), README, review-prepush y setup-guardrails-python → scripts/check.sh
```

## Supuestos

- La detección del agente usa marcadores concretos, no prefijos: `CLAUDECODE=1` para Claude Code y `CODEX_THREAD_ID` para Codex (comprobado: un Codex lanzado desde Claude Code hereda las `CLAUDE_CODE_*` pero no `CLAUDECODE`). La variable de OpenCode se comprueba en la primera tarea que lo detecte.
- Lista de revisores por defecto: `["claude", "codex"]` (con OpenCode solo como autor, la pregunta de arriba).
- `harness-review` vive en el kit, junto al gate, y reutiliza la lógica del `pre-push` actual (caché, timeout, sin credenciales de GitHub, `REVIEW_RESULT`). El `pre-push` copiado deja de ser la vía recomendada.
- El gate en rojo con salida 2 (no puede comprobar) sigue la política actual: fail-open avisa y deja pasar sin review, fail-closed bloquea.
- `SKIP_CLAUDE_REVIEW` y el resto de variables del hook solo se respetan en el push de una persona (E8).

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de las tareas son la única fuente.
