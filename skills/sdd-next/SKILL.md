---
name: sdd-next
description: Dice en qué punto está un trabajo de docs/specs/ y cuál es el siguiente paso, mirando qué artefactos existen y su status; sin argumentos, resume todos los trabajos. Solo lee, nunca cambia estados. Úsala cuando pregunten "¿y ahora qué?", "¿en qué punto está X?", "¿qué specs hay abiertas?" o pidan el estado de las specs.
---

# Siguiente paso SDD

Deduce el estado de cada trabajo a partir de sus artefactos. No hay un backlog central ni una máquina de estados: la fuente de verdad son los ficheros y su frontmatter. **Solo lees**: nunca cambias `status` ni escribes artefactos, y no lanzas otras skills sin que la persona lo pida.

La gestión del trabajo (prioridad, responsable, si está hecho) vive en el tracker. Si un artefacto tiene `issue:`, muéstralo, pero no lo consultes.

## Cómo deducir el siguiente paso

Para `docs/specs/<trabajo>/`, aplica la primera fila que encaje:

| Situación | Siguiente paso |
|---|---|
| No hay `spec.md` (ni `tasks.md`) | Escribir la spec: `idea-to-spec` |
| `spec.md` en `borrador`, con una revisión con hallazgos sin decidir | Decidirlos: `apply-review` |
| `spec.md` en `borrador` | Revisarla (`review-spec`) o que la persona la apruebe |
| `spec.md` aprobada, sin `plan.md` | Planificar: `spec-to-plan` (o directamente tareas, si es un cambio pequeño) |
| `plan.md` en `borrador`, con una revisión con hallazgos sin decidir | Decidirlos: `apply-review` |
| `plan.md` en `borrador` | Revisarlo (`review-spec`) o que la persona lo apruebe |
| Plan aprobado (o spec aprobada en un cambio pequeño), sin `tasks.md` | Partir en tareas: `plan-to-tasks` |
| `tasks.md` con casillas sin marcar | Implementar: agente `implement` (indica cuántas faltan) |
| Todas las casillas marcadas | Revisar el código contra la spec y abrir la PR |
| `status: obsoleta` | Nada. Indica qué la sustituye, si lo dice |

Una revisión tiene "hallazgos sin decidir" si alguno no tiene anotada debajo una decisión de `apply-review`.

## Avisos

Además del siguiente paso, avisa si:

- **El plan puede estar desfasado:** `spec.md` se modificó después que `plan.md`. Compáralo con `git log -1 --format=%cI -- <fichero>`. Lo mismo entre `plan.md` y `tasks.md`.
- **Se ha saltado una puerta:** hay `plan.md` con la spec en `borrador`, o `tasks.md` con el plan en `borrador`. Puede ser una decisión consciente; solo dilo.
- **Lleva tiempo parado:** más de 30 días sin commits en el directorio y sin terminar. Pregunta si sigue vivo o se marca como `obsoleta`.

## Formato

**Un trabajo:** directorio, artefactos con su status, progreso de tareas (`5/8`), siguiente paso y avisos.

**Todos** (sin argumento): una tabla ordenada por fecha, más reciente primero. Columnas: trabajo, spec, plan, tareas, siguiente paso y aviso. Los terminados y los obsoletos van al final en una línea cada uno. Esta vista se genera cada vez: no la guardes en un fichero.
