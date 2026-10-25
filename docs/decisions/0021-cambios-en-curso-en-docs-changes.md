---
id: D-0021
title: Cada cambio en curso es una carpeta docs/changes/<rama>/ en el repo, para todos los niveles; los issues de GitHub son solo la entrada de ideas
type: architecture
status: accepted
date: 2026-10-25
affects: [skills/idea-to-issue/, skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, skills/review-spec/, skills/task-done/, agents/implement.md, skills/review-prepush/, skills/review-pr/, docs/sdd/]
supersedes: D-0004
superseded_by: null
issue: null
---

# D-0021: Cada cambio en curso es una carpeta docs/changes/<rama>/ en el repo, para todos los niveles; los issues de GitHub son solo la entrada de ideas

## Contexto

La review de la PR #20 (R1, R2, R3) mostró que con D-0004 los agentes leen y ejecutan texto que puede haber escrito cualquiera: en un repo público, cualquiera abre un issue. El job de review de CI lo lee con Bash y la clave de la API en el entorno; `implement` ejecuta su `verificación:`; el hook pre-push necesitaba `gh` y su lista de bloqueos se podía saltar. La inyección de prompts no se filtra de forma fiable: la defensa es controlar quién escribe el texto que lee el agente. Además, el nivel B (issue) y el SDD (`docs/specs/`) guardaban las tareas en dos sitios con dos lógicas.

## Decisión

- Cada cambio es una carpeta `docs/changes/<rama>/`, con el último tramo del nombre de la rama (`feat/42-cancelar-viaje` → `42-cancelar-viaje/`).
- Nivel B: solo `tasks.md`, con la nota, el mapa de ejemplos y el checklist de tareas. Nivel C: el mismo `tasks.md` más `spec.md` y `plan.md`. Subir de nivel es añadir ficheros, no mover nada. `docs/specs/` desaparece.
- El texto de las tareas entra por la misma puerta que el código: commit y PR. Quien puede cambiarlo ya puede cambiar el código.
- Frontmatter de `tasks.md`: `status: open | done` e `issue:` (el número o null). El tablero es la carpeta (`grep -l "status: open" docs/changes/*/tasks.md`). Al terminar, `status: done`; la carpeta se puede borrar cuando se quiera, git la guarda.
- Los issues de GitHub son la bandeja de entrada: se puede partir de uno, pero una persona aprueba `tasks.md` antes del commit (D-0023). Desde entonces ningún agente vuelve a leer el issue; la PR lo cierra con `Closes #N`.
- Ni `task-done`, ni `implement`, ni la review usan `gh` ni la red para las tareas.

## Alternativas descartadas

- Seguir con los issues y filtrar por `author_association`: tapa el cuerpo del issue, pero no las ediciones ni los comentarios, deja la red y `gh` en el hook y en CI, y cada lector tiene que repetir el filtro.
- Marcar el texto del issue como no fiable en el prompt: reduce el riesgo, no lo quita.
- Un fichero por cambio en `docs/work/` y el SDD aparte en `docs/specs/`: dos sitios y dos formatos de tareas que mantener.
- Un único fichero de tablero para todos los cambios: conflictos de merge entre ramas.
- Numeración propia de los cambios: dos ramas en paralelo cogen el mismo número; el nombre de la rama ya es único.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py` lee solo ficheros del repo, probado en `scripts/check.sh`. El hook `pre-push` y `claude-review.yml` bloquean `gh` entero y el job de review no tiene `issues: read`.
