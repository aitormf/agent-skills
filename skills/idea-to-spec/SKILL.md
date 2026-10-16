---
name: idea-to-spec
description: Convierte una idea vaga o a medio definir en una spec (problema, usuarios, historias de usuario, requisitos, casos límite y criterios de aceptación) mediante una entrevista por rondas. Úsala cuando pidan escribir una spec, definir una funcionalidad, aclarar requisitos o pasar de una idea a algo implementable.
---

# De idea a spec

Ayuda a la persona a transformar una idea en una spec lista para planificar. Conduces la conversación; **las respuestas las da la persona**.

## Artefactos y estado

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/`. El tipo sigue Conventional Commits (`feat`, `fix`, `refactor`, `docs`…) y el nombre va en kebab-case. Si ya existe ese directorio, añade `-2`.
- `spec.md` y `plan.md` llevan en el frontmatter `status: borrador | aprobada | obsoleta`. Solo una persona pone `aprobada`.
- Si modificas un artefacto aprobado, devuélvelo a `borrador` y avisa.
- La gestión del trabajo (prioridad, responsable, hecho) no es cosa de esta skill: vive en el tracker. Si hay issue, su ID va en `issue:`.

## Comportamiento

- Empieza resumiendo la idea en un párrafo corto.
- Identifica qué falta para escribir una buena spec y haz el **mínimo de preguntas útiles**, primero las que bloquean.
- Céntrate en el qué y el porqué, no en el cómo: nada de frameworks ni arquitectura salvo que la persona lo pida. Eso es de `spec-to-plan`.
- Si `docs/ARCHITECTURE.md` existe, léelo para usar el vocabulario del glosario y detectar choques con los principios.

## Preguntas por rondas

1. Problema y resultado esperado.
2. Usuarios y actores.
3. Historias de usuario (qué necesita cada uno y para qué).
4. Alcance y fuera de alcance.
5. Comportamiento y casos límite: datos vacíos, inválidos o masivos; fallos de dependencias externas; acciones simultáneas.
6. Restricciones no funcionales.
7. Seguridad, si toca datos, autenticación o entradas externas: sensibilidad de los datos, quién puede hacer qué, qué entradas no son fiables y qué tests negativos hacen falta.
8. Criterios de aceptación ("Dado…, cuando…, entonces…").

Si tras una ronda algo sigue ambiguo, pregunta solo por esa parte.

## Preguntas abiertas

**Nunca asumas una respuesta en silencio.** Para cada pregunta sin resolver:

> **[Pregunta]**
> - A) [Tu propuesta por defecto, si la hay]
> - B) [Alternativa evidente]
> - C) Dejarla como pregunta abierta en la spec
> - D) Otra respuesta

Solo es resuelta cuando la persona responde o elige dejarla abierta.

Formato de cada respuesta: `Lo que entiendo` · `Preguntas abiertas` · `Siguiente paso`.

## Tamaño

Ajusta la profundidad al cambio. Propón el recorrido y que la persona decida:

| Cambio | Artefactos |
|---|---|
| Bug de una línea | Ninguno, o solo `tasks.md` |
| Bug complejo | `spec.md` + `tasks.md` |
| Funcionalidad pequeña | `spec.md` + `plan.md` + `tasks.md` |
| Funcionalidad de producción o refactor arquitectural | Todo, con revisión de spec y de plan |

## Cuándo parar

Para cuando haya suficiente para: objetivo, problema, usuarios, historias de usuario, alcance y fuera de alcance, requisitos funcionales y no funcionales, casos límite y criterios de aceptación.

Entonces:

1. Propón el nombre del directorio y redacta `spec.md` a partir de `assets/spec-template.md`, con `status: borrador`. Borra las secciones opcionales que no aplican.
2. Enseña el borrador y escribe solo cuando la persona lo apruebe.
3. Siguiente paso sugerido: revisarla con `review-spec`. Si es pequeña y la persona la da por buena, puede marcarla como `aprobada` y pasar a `spec-to-plan`.
