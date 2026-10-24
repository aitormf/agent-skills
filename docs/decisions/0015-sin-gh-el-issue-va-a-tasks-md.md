---
id: D-0015
title: Sin gh o sin red, idea-to-issue escribe el cuerpo del issue en docs/specs/<trabajo>/tasks.md
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/idea-to-issue/, skills/task-done/]
supersedes: null
superseded_by: null
issue: null
---

# D-0015: Sin gh o sin red, idea-to-issue escribe el cuerpo del issue en docs/specs/<trabajo>/tasks.md

## Contexto

El flujo por defecto vive en un issue (D-0004), pero `gh` puede no estar instalado, sin sesión o sin red (plan-v2, sección 10).

## Decisión

`idea-to-issue` avisa y escribe el mismo cuerpo (nota, mapa, supuestos y tareas) en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/tasks.md`, la ruta de los trabajos del SDD. `task-done` e `implement` funcionan igual sobre ese fichero, y acotan los commits desde que se añadió. Si después se crea el issue con ese cuerpo, el issue pasa a ser la fuente y el fichero se borra.

## Alternativas descartadas

- No seguir sin `gh`: bloquea el trabajo sin red.
- Un fichero fuera del repo o sin commit: `task-done` no puede acotar los commits del trabajo y se pierde al cambiar de máquina.
- `docs/work/`: descartado en D-0004 como sitio del trabajo en curso; aquí solo es el plan B y reutiliza la ruta que ya entienden las demás piezas.

## Cómo se hace cumplir

No se automatiza.
