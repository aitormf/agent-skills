---
id: D-0056
title: El push de un agente lo revisa siempre una familia de modelos distinta de la suya, elegida de la lista de .harness-config.toml de la base; si no hay ninguna, se bloquea; el push de una persona no se revisa
type: rule
status: accepted
date: 2026-11-13
affects: [skills/review-prepush/, .harness-config.toml, skills/setup-guardrails-python/]
supersedes: null
superseded_by: null
issue: 8
---

# D-0056: Revisor de otra familia que el agente

## Contexto

El revisor comparte modelo, sesgos y puntos ciegos con el autor si es de la misma familia (#8). En git no hay marca de autoría fiable: los `Co-Authored-By` se bloquean con un hook, y un campo escrito por el propio agente se puede falsear u olvidar. Lo que sube una persona es responsabilidad suya.

## Decisión

- **Autor:** la familia del agente que hace el push, por su entorno, que el hook hereda: `CLAUDECODE=1` es Claude Code y `CODEX_THREAD_ID` es Codex (marcadores concretos, no prefijos: un Codex lanzado desde Claude Code hereda `CLAUDE_CODE_*` pero no `CLAUDECODE`). Si hay marcadores de varias familias, todas cuentan como autoras. Sin ningún marcador, el push es de una persona y no se revisa de forma automática.
- **Revisor:** el primero de `[review] reviewers` en el `.harness-config.toml` de la rama base (D-0054) que no sea de una familia autora y esté instalado. Su modelo y esfuerzo, en `[review.<familia>]`.
- **Sin revisor de otra familia:** el push se bloquea con un mensaje explícito, sea cual sea la política fail-open. Nunca se revisa a sí mismo. Un fallo del revisor elegido (cuota, timeout) sigue la política actual, con un aviso que lo nombra.
- **Variables de salto** (`SKIP_CLAUDE_REVIEW`, `REVIEW_KIT_COMMAND`…): solo se respetan en el push de una persona.
- **Veredicto guardado (D-0042):** recuerda la familia del revisor y solo se reutiliza si no es de una familia autora.

## Alternativas descartadas

- **Trailer `Co-Authored-By` o un campo de la tarea**: bloqueado o falsificable por el propio agente.
- **Identidad por familia comprobada en CI**: robusta, pero exige un revisor en CI y una cuenta por familia; fuera por ahora.
- **Revisar siempre con las dos familias**: cruzado sin saber el autor, a doble coste en cada push.
- **Revisar también el push de una persona**: la persona responde de lo que sube y puede pedir la review a mano.

## Cómo se hace cumplir

E4–E22 del change `8-review-cruzada` en `scripts/check.sh`. Un agente que esquive el hook (un script que haga el push) no queda cubierto: las reglas de E23–E25 son defensa en profundidad, y la garantía es el sandbox de #77.
