---
id: D-0029
title: Cada cambio es docs/changes/<cambio>/ con un README.md y un fichero por tarea en tasks/
type: architecture
status: accepted
date: 2026-10-27
affects: [skills/idea-to-change/, skills/plan-to-tasks/, skills/idea-to-spec/, skills/spec-to-plan/, skills/review-spec/, skills/task-done/, agents/implement.md, skills/review-prepush/, skills/review-pr/, skills/review-context/, docs/sdd/]
supersedes: D-0021
superseded_by: null
issue: null
---

# D-0029: Cada cambio es docs/changes/<cambio>/ con un README.md y un fichero por tarea en tasks/

## Contexto

Tras probar el flujo B se quiere una PR por tarea, para que cada PR sea fácil de leer (D-0031), y tareas que dependen unas de otras (D-0030). Un único `tasks.md` con un checklist no tiene sitio para el estado, las dependencias ni el propósito de cada tarea, y varias ramas a la vez tocarían el mismo fichero.

## Decisión

Se mantiene de D-0021 que el cambio en curso vive en el repo y que los issues de GitHub son solo la entrada de ideas (con D-0023 y D-0026). Cambia la forma de la carpeta:

```
docs/changes/<cambio>/
  README.md        # nota, mapa de ejemplos; frontmatter status (open | done) e issue
  tasks/
    T1-<slug>.md   # una tarea por fichero
  spec.md, plan.md # solo nivel C
```

- Frontmatter de cada tarea: `id`, `title`, `status` (`todo | doing | done`), `depends_on` (D-0030), `examples` (los `E<n>` del mapa) y `verification` (de `AGENTS.md`, nunca del issue). El cuerpo dice el propósito en una frase, qué entra y qué no, y el flag si lo hay (D-0033).
- `<cambio>` es el nombre corto del cambio (`42-cancelar-viaje`), con el número del issue delante si viene de uno.
- Todos los niveles usan `tasks/`, aunque el cambio tenga una sola tarea: un solo formato y un solo script.
- `tasks.md` desaparece. El README pasa a `status: done` cuando todas las tareas están `done` en la rama base.

## Alternativas descartadas

- Seguir con un `tasks.md` con checklist: no caben el estado ni las dependencias, y varias PRs a la vez chocan en el mismo fichero.
- Un fichero por tarea solo en los cambios grandes: dos formatos y dos caminos en cada script y skill.
- Las tareas en el frontmatter del README: un fichero que tocan todas las PRs del cambio.

## Cómo se hace cumplir

El script de tablero de `task-done` (D-0030) valida el frontmatter de cada tarea, probado en `scripts/check.sh`.
