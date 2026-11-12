---
id: D-0053
title: El gate del flujo avisa cuando una tarea pasa de 200 líneas, pero no bloquea; el tamaño sigue siendo una señal para partir el plan (D-0037)
type: rule
status: accepted
date: 2026-11-12
affects: [skills/task-done/scripts/]
supersedes: null
superseded_by: null
issue: null
---

# D-0053: El gate avisa del tamaño sin bloquear

## Contexto

D-0044 pone el límite de una tarea en 200 líneas con los tests, contadas como en D-0047. D-0037 hace que la review lo informe como Optional, nunca como bloqueo, porque el arreglo es partir la tarea en el plan y no tocar el código. El gate del flujo (control-del-flujo) puede contar las líneas en cada push y en CI.

## Decisión

El gate cuenta el diff de la rama de la tarea con `diff_size.py` y, si pasa de 200 líneas, avisa con el recuento y sale con 0. No bloquea ni el push ni el merge. D-0037 sigue en pie.

## Alternativas descartadas

- **Bloquear por encima de 200 líneas**: obligaría a sustituir D-0037. Un diff grande ya está escrito cuando llega el push, y bloquearlo empuja a trocear commits en lugar de replanificar. Además, el recuento depende de que los generados estén marcados en `.gitattributes`.
- **Bloquear con un margen (300 líneas)**: un segundo número que nadie decidió; si hace falta, es una decisión nueva que sustituya a esta.

## Cómo se hace cumplir

Tests E12–E14 del change `control-del-flujo` en `scripts/check.sh`.
