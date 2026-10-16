---
name: review-spec
description: Revisa una spec o un plan antes de implementar, buscando ambigüedades, huecos, contradicciones, sobreingeniería y choques con los principios de ARCHITECTURE.md y los ADRs. Escribe una recomendación, nunca aprueba. Úsala cuando pidan revisar o auditar una spec, un plan o unas tareas.
---

# Revisar spec o plan

Revisa los artefactos de un trabajo y deja una recomendación. **No apruebas ni modificas nada**: la aprobación es de una persona, y los cambios los aplica `apply-review`.

Para revisar con contexto limpio, delega en el subagente `spec-reviewer`, que aplica esta misma skill.

## Artefactos y estado

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/`.
- `spec.md` y `plan.md` llevan en el frontmatter `status: borrador | aprobada | obsoleta`. **Solo una persona pone `aprobada`. Tú nunca cambias `status`.**

## Qué revisar

Identifica el trabajo (pregunta si no está claro) y qué toca revisar:

- **Spec** (`spec.md`).
- **Plan** (`spec.md` + `plan.md`, y `tasks.md` si existe).

Lee también, si existen:

- `docs/ARCHITECTURE.md`, sobre todo "Principios innegociables" y el glosario;
- los ADRs de `docs/adr/` relacionados.

Busca:

- **Ambigüedad:** requisitos que admiten dos lecturas; términos que no están en el glosario o se usan con otro sentido.
- **Huecos:**
  - casos límite sin cubrir;
  - criterios de aceptación que no se pueden verificar;
  - requisitos sin criterio de aceptación;
  - la sección Seguridad, si falta y la funcionalidad toca datos, auth o entradas externas;
  - en un plan, criterios de aceptación sin test que los pruebe.
- **Contradicciones:** entre secciones, entre spec y plan, o con otras specs vigentes de `docs/specs/`.
- **Principios y ADRs:** cada choque con un principio innegociable o con un ADR aceptado es **bloqueante**, salvo que el plan lo justifique y proponga un ADR.
- **Sobreingeniería y alcance:** complejidad que la spec no pide, o un plan que hace más de lo que dice la spec.
- **Supuestos** no declarados.

## Resultado

1. Escribe `review-spec.md` o `review-plan.md` en el directorio del trabajo, a partir de `assets/review-template.md`.
   - Hallazgos numerados y por prioridad: bloqueantes, importantes y menores. Cada uno con la sección afectada, qué falla y el arreglo sugerido.
   - Si ya existía una revisión anterior, sustitúyela; el historial queda en git.
2. Recomendación:
   - **"Listo para aprobar"** si no hay bloqueantes;
   - **"Devolver"** si los hay, con el motivo.
3. Dile a la persona el siguiente paso:
   - aplicar los cambios con `apply-review`;
   - o, si está lista, cambiar ella misma `status: aprobada`.

Sé concreto y cita la sección. No reescribas el artefacto ni propongas mejoras que no vengan de un hallazgo.
