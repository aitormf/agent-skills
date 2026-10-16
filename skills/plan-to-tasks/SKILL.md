---
name: plan-to-tasks
description: Parte un plan técnico aprobado en tareas pequeñas, ordenadas por dependencias, con ficheros afectados, verificación por tarea y grupos en paralelo. Úsala cuando haya un plan y pidan desglosarlo en tareas o prepararlo para implementar.
---

# De plan a tareas

Convierte un plan en una lista de tareas ejecutable que el agente `implement` pueda seguir y marcar.

## Artefactos y estado

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/`.
- `spec.md` y `plan.md` llevan en el frontmatter `status: borrador | aprobada | obsoleta`. Solo una persona pone `aprobada`.
- `tasks.md` no tiene status: su progreso son las casillas `[x]`.

## Antes de empezar

1. Identifica el trabajo y lee `plan.md` y `spec.md`.
2. **Puerta:** si el plan no tiene `status: aprobada`, para y pregunta:
   > El plan está en `<status>`. ¿Continúo de todas formas, lo revisamos antes con `review-spec`, o lo apruebas ahora?

   Sigue solo con una respuesta explícita. En un cambio pequeño sin plan, la puerta se aplica a la spec.
3. Lee el **comando de verificación** en la sección `Comandos` de `AGENTS.md`. Si no lo hay, pregunta cuál es o deja la tarea de cierre con un aviso.

## Cómo partir

- Tareas pequeñas: cada una es un cambio revisable que deja el proyecto en verde.
- Ordenadas por dependencias. Marca con `[P]` las que se pueden hacer en paralelo con la anterior.
- Cada tarea indica los **ficheros** que toca, si se saben, y **cómo se verifica**: qué test, o qué comando.
- Si el proyecto trabaja con TDD (lo dirá `CONTRIBUTING.md` o `AGENTS.md`), el test va antes que el código o en la misma tarea, nunca al final.
- Cada criterio de aceptación de la spec y cada test negativo de Seguridad debe estar cubierto por al menos una tarea. Si alguno no lo está, dilo.
- La fase de **Cierre** es obligatoria: criterios de aceptación con test y el comando de verificación en verde.
- No añadas trabajo que no esté en el plan. Si falta algo en el plan, señálalo como pregunta.

## Resultado

1. Redacta `tasks.md` a partir de `assets/tasks-template.md`.
2. Enseña el borrador con:
   - las tareas;
   - los grupos en paralelo;
   - los puntos de verificación;
   - las preguntas que queden.
3. Escribe solo cuando la persona lo apruebe.
4. Siguiente paso sugerido: implementar con el agente `implement`.
