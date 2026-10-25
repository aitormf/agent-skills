---
id: D-0022
title: task-done y la review encuentran el cambio en curso por el nombre de la rama
type: architecture
status: accepted
date: 2026-10-25
affects: [skills/task-done/, skills/review-prepush/, skills/review-pr/, agents/implement.md]
supersedes: D-0013
superseded_by: null
issue: null
---

# D-0022: task-done y la review encuentran el cambio en curso por el nombre de la rama

## Contexto

Con los cambios en `docs/changes/<rama>/` (D-0021), el número del issue deja de ser la clave. D-0013 sacaba el número de la rama para ir a GitHub.

## Decisión

Sin argumentos, `task-done` y `task_done.py --audit` usan `docs/changes/<último tramo de la rama>/tasks.md`. Si no existe, salen con 2 y dicen qué ruta buscaron; se puede pasar la ruta del fichero.

## Alternativas descartadas

- Un número en el nombre de la rama que apunte a la carpeta: otra convención que cumplir, y el nombre de la rama ya identifica el cambio.
- Buscar el `tasks.md` con `status: open` más reciente: con dos cambios abiertos elige mal.

## Cómo se hace cumplir

`skills/task-done/scripts/task_done.py`, probado en `scripts/check.sh` (cambio encontrado por la rama; rama sin carpeta sale con 2).
