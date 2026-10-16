# agent-skills

Skills y guías para trabajar con agentes de IA en repositorios de código.

```
skills/     Skills autocontenidas (SKILL.md + assets/ + references/)
agents/     Subagentes (contexto limpio)
docs/arnes/ Guías del arnés: el porqué de cada pieza. El código y las plantillas viven en los assets de las skills
scripts/    Tests de las skills
```

## Skills

### Preparar el proyecto

| Skill | Qué hace |
|---|---|
| [`generate-project-context`](skills/generate-project-context/SKILL.md) | Entrevista para crear AGENTS.md, ARCHITECTURE.md (con principios innegociables), CONTRIBUTING.md, ADRs y SECURITY.md. Sustituye a la constitución de Spec Kit |
| [`setup-guardrails-python`](skills/setup-guardrails-python/SKILL.md) | Instala los guardrails deterministas de un repo Python: check.sh, pre-commit, CI, seguridad, y permisos y hooks de Claude Code |

### Spec-Driven Development

| Skill / agente | Qué hace |
|---|---|
| [`idea-to-spec`](skills/idea-to-spec/SKILL.md) | De idea a `spec.md` mediante entrevista por rondas |
| [`review-spec`](skills/review-spec/SKILL.md) · agente [`spec-reviewer`](agents/spec-reviewer.md) | Revisa la spec o el plan. Recomienda, nunca aprueba |
| [`apply-review`](skills/apply-review/SKILL.md) | Aplica los hallazgos que la persona aprueba, uno a uno |
| [`spec-to-plan`](skills/spec-to-plan/SKILL.md) | De spec aprobada a `plan.md`, con comprobación de principios |
| [`plan-to-tasks`](skills/plan-to-tasks/SKILL.md) | De plan aprobado a `tasks.md`, con la verificación de cada tarea |
| agente [`implement`](agents/implement.md) | Implementa las tareas, marca `[x]` y termina con el comando de verificación en verde |
| [`sdd-next`](skills/sdd-next/SKILL.md) | ¿En qué punto está cada trabajo y qué toca ahora? Solo lectura |

```
idea-to-spec → [review-spec → apply-review] → persona: status: aprobada
  → spec-to-plan → [review-spec → apply-review] → persona: status: aprobada
  → plan-to-tasks → implement → revisión del código y PR
```

Convenciones de SDD:

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/` (`spec.md`, `plan.md`, `tasks.md` y las revisiones).
- `spec.md` y `plan.md` llevan `status: borrador | aprobada | obsoleta` en el frontmatter. **Solo una persona pone `aprobada`.** Las skills avisan y preguntan si se intenta avanzar sin aprobación.
- No hay backlog central. La gestión del trabajo (prioridad, responsable, hecho) vive en el tracker; la spec puede enlazarlo con `issue:`.
- El contrato con los guardrails es el comando de verificación de la sección `Comandos` de `AGENTS.md`.

## Tests

```bash
scripts/test-guardrails-python.sh   # requiere uv, jq y red
```
