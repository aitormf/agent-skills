# Actualizar un repositorio a la v2

Para proyectos que ya usan el kit (la v1, centrada en el SDD). Qué cambia y por qué está en el [plan de la v2](plan-v2.md). Aquí solo los pasos.

Nada de esto rompe un proyecto que no se actualice: el SDD sigue funcionando igual, y `task-done` solo exige el commit en rojo a las tareas que declaran `tests:`.

## 1. Las skills y los agentes

Lo que se instala como plugin se actualiza solo cuando cambia la versión. Lo que se copió a mano hay que volver a copiarlo.

- [ ] **Claude Code (plugin):** `/plugin marketplace update aitormf` y después actualiza `harness@aitormf` desde `/plugin`. Comprueba que aparece `/harness:idea-to-issue`.
- [ ] **Codex (plugin):** actualiza el marketplace y el plugin `harness@aitormf`. Los agentes no vienen con el plugin: vuelve a copiar `adapters/codex/agents/*.toml` a `.codex/agents/` (o a `~/.codex/agents/`).
- [ ] **OpenCode:** `npx skills update` y vuelve a copiar `adapters/opencode/agents/*.md` a `.opencode/agents/`.
- [ ] **`npx skills` (cualquier agente):** `npx skills update`, y haz commit de `.agents/skills/`, `.claude/skills/` y `skills-lock.json`. Si instalaste skills sueltas, añade las nuevas: `idea-to-issue` y `record-decision`.

Instrucciones de instalación completas: [README](../README.md#instalar).

## 2. Lo que se copió dentro del repositorio

Estos ficheros son copias; el plugin no los toca.

- [ ] **Hook `pre-push`** (si lo usas): vuelve a copiarlo.

  ```bash
  cp <skill review-prepush>/assets/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
  ```

  La versión nueva deja leer issues y PRs con `gh` (la review lee el issue de la rama) y sigue bloqueando todo lo que escribe.
- [ ] **Workflow `claude-review.yml`** (si lo usas): vuelve a copiar `skills/review-pr/assets/claude-review.yml` a `.github/workflows/` y repite tus cambios locales (el paso «Prepare project», sobre todo). El job de review necesita ahora `issues: read` para leer las tareas del issue.

## 3. El contexto del proyecto

Lo más cómodo es volver a ejecutar `generate-project-context`: en un proyecto existente solo pregunta por los huecos y propone diffs. Lo que debería proponer:

- [ ] **Niveles en `AGENTS.md`:** la tabla de niveles de proceso, las señales para subir o bajar, la regla de evidencia («no digas que los tests pasan sin haber ejecutado el comando en esta sesión») y el glosario. Es el fragmento [`AGENTS-levels.md`](../skills/generate-project-context/assets/es/AGENTS-levels.md).
- [ ] **Glosario:** pasa de `ARCHITECTURE.md` a `AGENTS.md` (D-0016). En `ARCHITECTURE.md` queda el modelo de dominio.
- [ ] **Registro de decisiones:** `docs/decisions/` con su índice `README.md`. Si tienes `docs/adr/`, `record-decision` ofrece moverlos con `git mv` como `type: architecture`. Si prefieres no moverlos, conviven y el índice los enlaza.
- [ ] Comprueba el resultado: `python3 <skill record-decision>/scripts/check_decisions.py docs/decisions`.

## 4. Cambios en la forma de trabajar

Para contárselo a quien trabaje en el repositorio.

- **La entrada por defecto es `idea-to-issue`, no `idea-to-spec`.** La nota, el mapa de ejemplos y las tareas viven en un issue de GitHub. El SDD queda para cuando hay diseño de verdad que decidir.
- **Una rama por issue, con el número delante:** `gh issue develop 42` (o `42-cancelar-viaje`, `feat/42-cancelar-viaje`). `task-done` y la review encuentran el issue por ese número.
- **Tareas con sus ejemplos:** `- [ ] T2. <tarea> — tests: E1, E2 — verificación: <comando>`. Las tareas delicadas añaden `— level: A` y el agente se para con los tests en rojo.
- **Commit de tests en rojo antes del código:** `test(T2): E1 E2 red` y después `feat(T2): …`. Los tests se nombran por ejemplo (`test_E1_…`) y citan la decisión que protegen (`# D-0021`).
- **`task-done` comprueba los tests en rojo:** si falta el commit en rojo o se ha cambiado un test suyo, no marca la tarea (exit 3).
- **La review comprueba más cosas:** ejemplos con test, tests en rojo intactos, choques con decisiones aceptadas y llamadores fuera del diff.
- **Las decisiones se registran:** las redacta el agente en `proposed` y una persona las pasa a `accepted`. Una decisión aceptada no se edita: se sustituye por otra.

Las tareas en curso de la v1 (`tasks.md` sin `tests:`) se terminan como siempre.
