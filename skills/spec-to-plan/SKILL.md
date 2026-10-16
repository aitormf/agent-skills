---
name: spec-to-plan
description: Convierte una spec aprobada en un plan técnico mínimo (arquitectura, componentes, modelo de datos, contratos, pruebas y riesgos) y lo contrasta con los principios innegociables de ARCHITECTURE.md. Úsala cuando haya una spec y pidan planificar, diseñar la solución o decidir cómo implementarla.
---

# De spec a plan

Convierte una spec en un plan técnico que se pueda partir en tareas. Lo mínimo que la spec exige, nada más.

## Artefactos y estado

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/`.
- `spec.md` y `plan.md` llevan en el frontmatter `status: borrador | aprobada | obsoleta`. Solo una persona pone `aprobada`.

## Antes de empezar

1. Identifica el trabajo y lee `spec.md`.
2. **Puerta:** si la spec no tiene `status: aprobada`, para y pregunta:
   > La spec está en `<status>`. Planificar sobre una spec sin aprobar puede obligar a rehacer el plan. ¿Continúo de todas formas, la revisamos antes con `review-spec`, o la apruebas ahora?

   Sigue solo con una respuesta explícita. Si la persona dice que continúe, anótalo en "Decisiones abiertas" del plan.
3. Lee, si existen:
   - `docs/ARCHITECTURE.md`: capas, reglas de dependencia, principios innegociables y mapa del código;
   - los ADRs relacionados de `docs/adr/`;
   - el código de las zonas que se van a tocar.

## Comportamiento

- Primero, lista las preguntas abiertas y los supuestos. Si hay alguna que bloquee, pregúntala antes de redactar, con opciones concretas.
- Separa la intención de producto (es de la spec) de las decisiones técnicas (son del plan). Si el plan obliga a cambiar la spec, dilo; no la cambies.
- Encaja la solución en las capas y el mapa del código que ya existen. Si propones algo nuevo (capa, dependencia, patrón), justifícalo.
- Para cada criterio de aceptación y cada test negativo de la sección Seguridad, indica qué prueba lo cubrirá.
- **Comprobación de principios:** recorre uno a uno los "Principios innegociables" de `ARCHITECTURE.md` y rellena su tabla en el plan. Si el plan incumple uno, no lo escondas: justifícalo y propón un ADR. Si `ARCHITECTURE.md` no existe, dilo en el plan y sugiere `generate-project-context`.

Formato de cada respuesta: `Lo que entiendo` · `Preguntas abiertas` · `Borrador del plan` · `Siguiente paso`.

## Resultado

1. Redacta `plan.md` a partir de `assets/plan-template.md`, con `status: borrador`.
2. Enseña el borrador y escribe solo cuando la persona lo apruebe.
3. Siguiente paso sugerido:
   - si es un cambio grande, revisarlo con `review-spec`;
   - si no, que la persona lo marque como `aprobada` y pasar a `plan-to-tasks`.
