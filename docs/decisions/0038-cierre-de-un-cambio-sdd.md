---
id: D-0038
title: En el nivel SDD, task_done.py marca spec.md y plan.md como obsolete al cerrar el cambio; las decisiones se registran al planificar
type: architecture
status: accepted
date: 2026-10-28
affects: [skills/task-done/, skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, agents/implement.md]
supersedes: null
superseded_by: null
issue: null
---

# D-0038: En el nivel SDD, task_done.py marca spec.md y plan.md como obsolete al cerrar el cambio; las decisiones se registran al planificar

## Contexto

D-0006 dice que, al terminar, las decisiones de la spec y del plan pasan a `docs/decisions/` y la spec se marca `obsolete`. Con una PR por tarea (D-0031) y sin tareas de cierre (D-0036), hay que decidir quién da ese paso y cuándo.

## Decisión

- Las decisiones se registran al planificar: `idea-to-spec` y `spec-to-plan` las redactan como `proposed` y la persona las acepta en la misma parada que la spec o el plan (D-0003). `plan-to-tasks` comprueba que todas están aceptadas antes de la PR del plan.
- Cuando `task_done.py` pone el README del cambio en `status: done`, pone también `spec.md` y `plan.md` en `status: obsolete`. Va en la PR de la última tarea.

## Alternativas descartadas

- Pasar las decisiones a `docs/decisions/` al terminar la última tarea: va contra D-0003 y mete registros `proposed` en una PR que abre `implement` sin nadie delante.
- Una tarea final de cierre: D-0036 quitó las tareas de cierre.
- Una instrucción en `implement`: se olvida.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py`, probado en `scripts/check.sh` («did not set spec.md and plan.md obsolete when the change was done (D-0006)» y «set the spec obsolete with tasks left»).
