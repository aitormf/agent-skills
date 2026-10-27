---
id: D-0031
title: Una rama y una PR por tarea, <cambio>/T<n>, con la rama base como base; el plan va en su propia PR
type: architecture
status: accepted
date: 2026-10-27
affects: [skills/task-done/, skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/review-prepush/, skills/review-pr/, skills/review-context/]
supersedes: D-0022
superseded_by: null
issue: null
---

# D-0031: Una rama y una PR por tarea, <cambio>/T<n>, con la rama base como base; el plan va en su propia PR

## Contexto

Una PR con todas las tareas de un cambio es larga de leer. Se quiere una PR por tarea, pequeña y de un solo propósito (D-0033). D-0022 sacaba de la rama solo la carpeta del cambio.

## Decisión

- **PR del plan:** rama `<cambio>/plan`, con el README, las tareas y las decisiones. Se abre después del ok de la persona al mapa de ejemplos (D-0026). Mergearla deja el plan en la rama base.
- **PR de tarea:** rama `<cambio>/T<n>`, que sale de la rama base cuando la tarea está lista (D-0030). De ese nombre, `task-done` y la review sacan la carpeta y la tarea.
- `task-done` comprueba la protección de los tests en rojo (D-0024, sin cambios: la base de cada rama es la rama base) y, si la verificación pasa, pone `status: done` en el fichero de la tarea dentro de la propia PR. En la rama base, `done` significa mergeada, sin ningún paso posterior al merge.
- Al terminar una tarea, el agente hace push y abre la PR (`gh pr create`) y pasa a la siguiente tarea lista.
- Una vez mergeada una tarea, `task-done` ya no protege sus tests frente a PRs posteriores. Eso lo ve la review en el diff, que en una PR pequeña salta a la vista.

## Alternativas descartadas

- Una PR por cambio (D-0021, D-0022): PRs largas de leer.
- Que la persona abra las PRs: el agente se para en cada tarea, para algo que es mecánico.
- Marcar `done` después del merge: un paso más que se olvida, y otro commit en la rama base.
- Ramas `<cambio>-T<n>`: no se distingue con seguridad del nombre del cambio; con `/`, el cambio es el penúltimo tramo y la tarea el último.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py`, probado en `scripts/check.sh`: carpeta y tarea sacadas de la rama, `status: done` al pasar la verificación.
