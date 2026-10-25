# Actualizar un repositorio a la v2

Para proyectos que ya usan el kit (la v1, centrada en el SDD). Qué cambia y por qué está en el [plan de la v2](plan-v2.md). Aquí solo los pasos.

Nada de esto rompe un proyecto que no se actualice: `task-done` solo exige el commit en rojo a las tareas que declaran `tests:`. Lo único que hay que mover son los trabajos en curso de `docs/specs/` (sección 4).

## 1. Las skills y los agentes

Lo que se instala como plugin se actualiza solo cuando cambia la versión. Lo que se copió a mano hay que volver a copiarlo.

- [ ] **Claude Code (plugin):** `/plugin marketplace update aitormf` y después actualiza `harness@aitormf` desde `/plugin`. Comprueba que aparece `/harness:idea-to-change`.
- [ ] **Codex (plugin):** actualiza el marketplace y el plugin `harness@aitormf`. Los agentes no vienen con el plugin: vuelve a copiar `adapters/codex/agents/*.toml` a `.codex/agents/` (o a `~/.codex/agents/`).
- [ ] **OpenCode:** `npx skills update` y vuelve a copiar `adapters/opencode/agents/*.md` a `.opencode/agents/`.
- [ ] **`npx skills` (cualquier agente):** `npx skills update`, y haz commit de `.agents/skills/`, `.claude/skills/` y `skills-lock.json`. Si instalaste skills sueltas, añade las nuevas: `idea-to-change` y `record-decision`.

Instrucciones de instalación completas: [README](../README.md#instalar).

## 2. Lo que se copió dentro del repositorio

Estos ficheros son copias; el plugin no los toca.

- [ ] **Hook `pre-push`** (si lo usas): vuelve a copiarlo.

  ```bash
  cp <skill review-prepush>/assets/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
  ```

  La review no usa `gh`: lee las tareas de `docs/changes/<rama>/`, con commit, y el hook bloquea `gh` entero (`Bash(gh:*)`), como en la v1.
- [ ] **Workflow `claude-review.yml`** (si lo usas): vuelve a copiar `skills/review-pr/assets/claude-review.yml` a `.github/workflows/` y repite tus cambios locales (el paso «Prepare project», sobre todo). El job de review ya no necesita token de GitHub: solo `contents: read`, sin `pull-requests: read` ni `issues: read`, y con `gh` bloqueado. Revisa la rama de la PR contra su base con git y lee las tareas de `docs/changes/<rama>/`; la descripción de la PR ya no se revisa en CI.

## 3. El contexto del proyecto

Lo más cómodo es volver a ejecutar `generate-project-context`: en un proyecto existente solo pregunta por los huecos y propone diffs. Lo que debería proponer:

- [ ] **Niveles en `AGENTS.md`:** la tabla de niveles de proceso, las señales para subir o bajar, la regla de evidencia («no digas que los tests pasan sin haber ejecutado el comando en esta sesión») y el glosario. Es el fragmento [`AGENTS-levels.md`](../skills/generate-project-context/assets/es/AGENTS-levels.md).
- [ ] **Glosario:** pasa de `ARCHITECTURE.md` a `AGENTS.md` (D-0016). En `ARCHITECTURE.md` queda el modelo de dominio.
- [ ] **Registro de decisiones:** `docs/decisions/` con su índice `README.md`. Si tienes `docs/adr/`, `record-decision` ofrece moverlos con `git mv` como `type: architecture`. Si prefieres no moverlos, conviven y el índice los enlaza.
- [ ] Comprueba el resultado: `python3 <skill record-decision>/scripts/check_decisions.py docs/decisions`.

## 4. Los trabajos en curso: de `docs/specs/` a `docs/changes/`

Cada cambio vive ahora en `docs/changes/<rama>/`, con el último tramo del nombre de la rama (`feat/42-cancelar-viaje` → `docs/changes/42-cancelar-viaje/`), para todos los niveles. `docs/specs/` desaparece.

- [ ] **Por cada trabajo que siga abierto,** en la rama donde se implementa:

  ```bash
  git mv docs/specs/<trabajo> docs/changes/<último tramo de la rama>
  ```

- [ ] **Añade el frontmatter a su `tasks.md`:** `status: open` e `issue:` (el número del issue, o `null`). `task-done` pone `status: done` al marcar la última tarea.
- [ ] **Los trabajos terminados** se pueden borrar o dejar donde están: git los guarda. Si quieres conservar algo de ellos, que sean sus decisiones, en `docs/decisions/`.
- [ ] Si `task-done` o la review no encuentran el cambio, comprueba que el nombre de la carpeta es el último tramo de la rama, o pasa la ruta de `tasks.md`.

## 5. Cambios en la forma de trabajar

Para contárselo a quien trabaje en el repositorio.

- **La entrada por defecto es `idea-to-change`, no `idea-to-spec`.** Crea la rama y escribe la nota, el mapa de ejemplos y las tareas en `docs/changes/<rama>/tasks.md`, que pasa por commit y PR como el código. El SDD queda para cuando hay diseño de verdad que decidir: añade `spec.md` y `plan.md` a la misma carpeta.
- **Un issue puede ser el punto de partida, no el sitio de las tareas.** Su texto lo puede escribir cualquiera: el agente lo lee una vez como datos, avisa si el autor no es del proyecto y la persona aprueba `tasks.md` antes del commit. Después ningún agente vuelve a leerlo; la PR lo cierra con `Closes #<n>`.
- **Una rama, un cambio:** `task-done` y la review encuentran el cambio por el nombre de la rama, y solo cuentan los commits de la rama desde la rama base.
- **Tareas con sus ejemplos:** `- [ ] T2. <tarea> — tests: E1, E2 — verificación: <comando>`. Las tareas delicadas añaden `— level: A` y el agente se para con los tests en rojo.
- **Commit de tests en rojo antes del código:** `test(T2): E1 E2 red` y después `feat(T2): …`. Los tests se nombran por ejemplo (`test_E1_…`) y citan la decisión que protegen (`# D-0021`).
- **`task-done` comprueba los tests en rojo:** si falta el commit en rojo en la rama o se ha cambiado un test suyo, aunque sea en el commit en rojo de otra tarea, no marca la tarea (exit 3).
- **La review comprueba más cosas:** ejemplos con test, tests en rojo intactos, choques con decisiones aceptadas y llamadores fuera del diff.
- **Las decisiones se registran:** las redacta el agente en `proposed` y una persona las pasa a `accepted`. Una decisión aceptada no se edita: se sustituye por otra.

Las tareas en curso de la v1 (`tasks.md` sin `tests:`) se terminan como siempre, una vez movidas a `docs/changes/` (sección 4).
