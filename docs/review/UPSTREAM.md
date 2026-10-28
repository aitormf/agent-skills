# Upstream: addyosmani/agent-skills

- Repo: <https://github.com/addyosmani/agent-skills>
- Commit tomado como base: `aeac41d4d005999432bb7312f7ff06383a91d59d` (2026-10-13)
- Licencia: MIT, © 2025 Addy Osmani → `LICENSE-agent-skills`

Este material viene de **review-kit** (aitormf), integrado en `aitormf/agent-skills` el 2026-10-16. Cambios de la integración, además de los listados abajo:

- Los comandos `/review-prepush` y `/review-pr` son ahora skills (`skills/review-prepush/`, `skills/review-pr/`), para que funcionen en Claude Code, Codex, OpenCode y pi. Si la herramienta no puede lanzar subagentes, la skill ejecuta los roles en la sesión principal.
- Se elimina el `/review` de upstream: es la skill `code-review-and-quality`, invocable directamente.
- La configuración del repo se lee de `AGENTS.md` (antes `CLAUDE.md`).
- `review-context` §4: si la rama (`<cambio>/T<n>` o `<cambio>/plan`) tiene su carpeta en `docs/changes/<cambio>/` (README, tareas y, en SDD, spec y plan), la review comprueba el código contra su tarea, o el plan en la rama del plan.
- Namespace del plugin: `harness:` (antes `review-kit:`). Los agentes se generan para Codex y OpenCode con `scripts/build-agents.py`.
- `install.sh` desaparece: se instala como el resto del repositorio (plugin o `npx skills`). El hook y la Action son assets de sus skills.

Todo fichero derivado lleva una cabecera `Origin:` con la ruta upstream. Esta tabla es la lista completa.

## Ficheros de Addy

| Aquí | Upstream | Estado | Cambios |
|---|---|---|---|
| `skills/code-review-and-quality/SKILL.md` | `skills/code-review-and-quality/SKILL.md` | Modificado | Cabecera de origen; nota de precedencia de `review-report`; referencias a `security-and-hardening`, `performance-optimization` y `constraint-driven-development` (no incluidas) cambiadas por las checklists incluidas o eliminadas; `npm audit`/`package.json` generalizados a cualquier ecosistema; "See Also" re-apuntado. El resto, idéntico. |
| `skills/code-review-and-quality/references/security-checklist.md` | `references/security-checklist.md` | Sin cambios | Solo cabecera. Movido dentro de la skill para que la ruta relativa funcione en modo plugin y en `.claude/`. |
| `skills/code-review-and-quality/references/performance-checklist.md` | `references/performance-checklist.md` | Sin cambios | Ídem. |
| `agents/code-reviewer.md` | `agents/code-reviewer.md` | Modificado | Frontmatter `tools` (solo lectura + Bash) y `skills`; formato de salida delegado en `review-report`; reglas 7–8 (precisión, solo lectura); bloque Composition con los comandos de review-kit; sección «Beyond the diff» (llamadores fuera del diff, decisiones, tamaño y propósito de la tarea; comprobaciones de tests de `review-report` §5 solo si va sin `test-engineer`). Cinco ejes intactos. |
| `agents/security-auditor.md` | `agents/security-auditor.md` | Modificado | Frontmatter `tools`/`skills`; nota de formato y mapeo de severidades para review-kit; reglas 9–10 (checklist, rutas de alto riesgo, solo lectura); Composition. |
| `agents/test-engineer.md` | `agents/test-engineer.md` | Modificado | Frontmatter `tools` **sin Write** (el kit solo revisa: esta persona audita tests, no los escribe) y `skills`; sección nueva "Auditing the tests of a diff", con las comprobaciones de tests de `review-report` §5 en `review-pr`; Composition. |
| `docs/review/agents.md` | `docs/agents.md` | Modificado | Tabla de personas (sin `web-performance-auditor`, con `finding-verifier`); ejemplos con `/review-prepush` y `/review-pr`; ejemplo de fan-out con paso de verificación; nombres con namespace en modo plugin. |
| `docs/review/orchestration-patterns.md` | `references/orchestration-patterns.md` | Sin cambios | Solo cabecera. Movido a `docs/` (documentación, no se usa en ejecución). |

## Derivados (nuestros, inspirados en un comando de Addy)

| Aquí | Basado en | Diferencias principales |
|---|---|---|
| `skills/review-prepush/SKILL.md` | `/review` | Lanza `code-reviewer` en contexto limpio sobre `git diff <base>...HEAD`; verificación desde CLAUDE.md; foco reducido (tarea, bugs, tests vacíos, restos); `finding-verifier`; línea `REVIEW_RESULT` para el hook. |
| `skills/review-pr/SKILL.md` | `/ship` | Mismo fan-out paralelo + merge; añade tier de riesgo, `finding-verifier` tras el merge y revisión de la descripción de la PR; sin go/no-go ni plan de rollback; nunca aprueba. |

## Originales de review-kit

`agents/finding-verifier.md`, `skills/review-context/` (con `assets/`), `skills/review-report/SKILL.md`, `skills/review-prepush/assets/pre-push`, `skills/review-pr/assets/claude-review.yml`, `docs/review/orchestration-addendum.md`, `docs/review/README.md`, `tests/review-sandbox/`, `NOTICE.md`, este fichero.

## No incluido de upstream (y por qué)

- Resto de skills (spec, plan, build, TDD, shipping…): fuera del alcance de un kit de review.
- `agents/web-performance-auditor.md` y `/webperf`: específico de web.
- `/ship` y la skill `shipping-and-launch`: sustituidos por `/review-pr` (review consultiva, no gate de lanzamiento).
- `references/testing-patterns.md`: solo JS/TS; rompería la independencia del stack.
- Variantes `.toml` de comandos (Gemini CLI), hooks de sesión y evals de upstream.

## Cómo sincronizar con upstream

```bash
git clone https://github.com/addyosmani/agent-skills /tmp/agent-skills
cd /tmp/agent-skills && git diff aeac41d..HEAD -- \
  skills/code-review-and-quality agents/code-reviewer.md agents/security-auditor.md \
  agents/test-engineer.md .claude/commands/review.md .claude/commands/ship.md \
  references/security-checklist.md references/performance-checklist.md \
  references/orchestration-patterns.md docs/agents.md
```

Aplica los cambios relevantes a mano conservando las modificaciones listadas arriba, y actualiza el commit en este fichero y en las cabeceras `Origin:`.
