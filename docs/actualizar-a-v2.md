# Actualizar un repositorio a la v2

Para proyectos que ya usan el kit (la v1, centrada en el SDD). Qué cambia y por qué está en el [plan de la v2](plan-v2.md). Aquí solo los pasos.

Lo único que hay que mover son los trabajos en curso: de `docs/specs/` a `docs/changes/` y, si tienen un `tasks.md`, a un `README.md` y un fichero por tarea (sección 4). `task-done` ya no lee `tasks.md`.

## 1. Las skills y los agentes

Lo que se instala como plugin se actualiza solo cuando cambia la versión. Lo que se copió a mano hay que volver a copiarlo.

- [ ] **Claude Code (plugin):** `/plugin marketplace update aitormf` y después actualiza `harness@aitormf` desde `/plugin`. Comprueba que aparece `/harness:idea-to-change`.
- [ ] **Codex (plugin):** actualiza el marketplace y el plugin `harness@aitormf`. Los agentes no vienen con el plugin: vuelve a copiar `adapters/codex/agents/*.toml` a `.codex/agents/` (o a `~/.codex/agents/`).
- [ ] **OpenCode:** `npx skills update` y vuelve a copiar `adapters/opencode/agents/*.md` a `.opencode/agents/`.
- [ ] **`npx skills` (cualquier agente):** `npx skills update`, y haz commit de `.agents/skills/`, `.claude/skills/` y `skills-lock.json`. Si instalaste skills sueltas, añade las nuevas, `idea-to-change` y `record-decision`, y borra de `.agents/skills/`, `.claude/skills/` y `skills-lock.json` la skill del siguiente paso del SDD, que ya no existe (D-0007).
- [ ] **Desaparece la skill del siguiente paso del SDD** ([D-0007](decisions/README.md), versión 0.5.0), la que decía en qué punto estaba cada trabajo. Con el plugin se va sola; si la copiaste a mano en otro sitio, bórrala. Su trabajo lo hacen el `status` de `spec.md` y `plan.md`, el tablero de `task-done` (`scripts/board.py docs/changes/<cambio>`) y, para ver los cambios abiertos, `grep -l "status: open" docs/changes/*/README.md`.

Instrucciones de instalación completas: [README](../README.md#instalar).

## 2. Lo que se copió dentro del repositorio

Estos ficheros son copias; el plugin no los toca.

- [ ] **Hook `pre-push`** (si lo usas): vuelve a copiarlo.

  ```bash
  cp <skill review-prepush>/assets/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
  ```

  La review no usa `gh`: lee la tarea de `docs/changes/<cambio>/`, con commit, y el hook ejecuta la review sin credenciales de GitHub (sin `GH_TOKEN`, `GITHUB_TOKEN` ni `GH_ENTERPRISE_TOKEN`, y con un `GH_CONFIG_DIR` vacío). Sigue bloqueando `Bash(gh:*)`, como en la v1, pero eso es defensa en profundidad: `/usr/bin/gh` o `bash -c 'gh …'` se lo saltan.
- [ ] **Workflow `claude-review.yml`** (si lo usas): vuelve a copiar `skills/review-pr/assets/claude-review.yml` a `.github/workflows/` y repite tus cambios locales (el paso «Prepare project», sobre todo). El job de review ya no necesita token de GitHub: solo `contents: read`, sin `pull-requests: read` ni `issues: read`, y con `gh` bloqueado. Revisa la rama de la PR contra su base con git y lee la tarea de `docs/changes/<cambio>/` (de la rama `<cambio>/T<n>`); la descripción de la PR ya no se revisa en CI.

## 3. El contexto del proyecto

Lo más cómodo es volver a ejecutar `generate-project-context`: en un proyecto existente solo pregunta por los huecos y propone diffs. Lo que debería proponer:

- [ ] **Niveles en `AGENTS.md`:** la tabla de niveles de proceso, las señales para subir o bajar, la regla de evidencia («no digas que los tests pasan sin haber ejecutado el comando en esta sesión»), la línea de feature flags (cómo se esconde lo que está a medias, o «ninguno») y el glosario. Es el fragmento [`AGENTS-levels.md`](../skills/generate-project-context/assets/es/AGENTS-levels.md).
- [ ] **Glosario:** pasa de `ARCHITECTURE.md` a `AGENTS.md` (D-0016). En `ARCHITECTURE.md` queda el modelo de dominio.
- [ ] **Registro de decisiones:** `docs/decisions/` con su índice `README.md`. Si tienes `docs/adr/`, `record-decision` ofrece moverlos con `git mv` como `type: architecture`. Si prefieres no moverlos, conviven y el índice los enlaza.
- [ ] Comprueba el resultado: `python3 <skill record-decision>/scripts/check_decisions.py docs/decisions`.

## 4. Los trabajos en curso: a `docs/changes/<cambio>/` con un fichero por tarea

Cada cambio vive ahora en `docs/changes/<cambio>/`, para todos los niveles, con un `README.md` (nota y mapa de ejemplos) y un fichero por tarea en `tasks/`. `docs/specs/` y `tasks.md` desaparecen. `<cambio>` es un nombre corto en kebab-case, con el número del issue delante si parte de uno (`42-cancelar-viaje`).

- [ ] **Por cada trabajo de `docs/specs/` que siga abierto:**

  ```bash
  git mv docs/specs/<trabajo> docs/changes/<cambio>
  ```

- [ ] **Por cada cambio con `tasks.md`** (de `docs/specs/` o de una versión anterior de la v2), pásalo al formato nuevo:

  ```bash
  cd docs/changes/<cambio>
  git mv tasks.md README.md
  mkdir tasks
  ```

  1. En el frontmatter del `README.md` deja `status: open` e `issue:` (el número del issue, o `null`). Si no tenía frontmatter, añádelo.
  2. Por cada línea `- [ ] T<n>. <tarea> — tests: E1, E2 — verificación: <comando>` del checklist, crea `tasks/T<n>-<slug>.md` con este frontmatter y el propósito de la tarea en el cuerpo:

     ```yaml
     ---
     id: T2
     title: <tarea>
     status: todo            # done si estaba marcada [x]
     depends_on: [T1]        # las tareas que tienen que estar mergeadas antes; [] si ninguna
     examples: [E1, E2]      # lo que decía tests:; [] si nada
     verification: <comando>
     ---
     ```

     Las tareas `W<n>` de cierre (verificación completa) no se pasan: `implement` ejecuta la verificación completa antes de cada PR. Una tarea con `— level: A` lleva `level: A` en el frontmatter.
  3. Borra el checklist del `README.md`; el mapa de ejemplos y los supuestos se quedan.
  4. Comprueba el resultado con el tablero y la auditoría del plan de `task-done`:

     ```bash
     python3 <skill task-done>/scripts/board.py docs/changes/<cambio>
     python3 <skill task-done>/scripts/task_done.py --audit docs/changes/<cambio>
     ```

- [ ] **Las ramas:** el plan va en `<cambio>/plan` y cada tarea en su rama, `<cambio>/T<n>`, que sale de la rama base, con una PR cada una. `task-done` y la review sacan la carpeta y la tarea del nombre de la rama: el cambio es el penúltimo tramo y la tarea el último. Se admite un prefijo delante (`feat/42-cancelar-viaje/T2`). Un cambio a medias en una rama de las de antes (`feat/42-cancelar-viaje`): haz commit del formato nuevo en esa rama como PR del plan y, una vez mergeada, sigue con una rama por tarea. A `task-done` también se le puede pasar la carpeta y la tarea: `task_done.py docs/changes/<cambio> T2 -- <comando>`.
- [ ] **Los trabajos terminados** se pueden borrar o dejar donde están: git los guarda. Si quieres conservar algo de ellos, que sean sus decisiones, en `docs/decisions/`.

## 5. Cambios en la forma de trabajar

Para contárselo a quien trabaje en el repositorio.

- **La entrada por defecto es `idea-to-change`, no `idea-to-spec`.** Escribe la nota y el mapa de ejemplos en `docs/changes/<cambio>/README.md` y un fichero por tarea en `tasks/`, y abre la PR del plan (rama `<cambio>/plan`), que se revisa como el código. El SDD queda para cuando hay diseño de verdad que decidir: añade `spec.md` y `plan.md` a la misma carpeta.
- **Un issue puede ser el punto de partida, no el sitio de las tareas.** Su texto lo puede escribir cualquiera: el agente lo lee una vez como datos, avisa si el autor no es del proyecto y la persona aprueba el mapa de ejemplos antes del commit. Después ningún agente vuelve a leerlo; la PR de la última tarea lo cierra con `Closes #<n>`.
- **Una rama y una PR por tarea:** `<cambio>/T<n>`, desde la rama base. `task-done` y la review encuentran el cambio y la tarea por el nombre de la rama, y solo cuentan los commits de la rama desde la rama base. El agente abre la PR y sigue con la siguiente tarea lista; las que dependen de una PR sin mergear esperan.
- **Tareas pequeñas, de un solo propósito:** comportamiento nuevo, refactor o preparación, sin mezclar, y unas 150 líneas sin contar los tests. Cada una deja la rama base desplegable: lo que está a medias va detrás de un feature flag, y la última tarea lo retira.
- **Tareas con sus ejemplos y dependencias:** `examples: [E1, E2]` y `depends_on: [T1]` en el frontmatter de la tarea. Las tareas delicadas añaden `level: A` y el agente se para con los tests en rojo.
- **Commit de tests en rojo antes del código:** `test(T2): E1 E2 red` y después `feat(T2): …`. Los tests se nombran por ejemplo (`test_E1_…`) y citan la decisión que protegen (`# D-0021`).
- **`task-done` comprueba los tests en rojo:** si falta el commit en rojo en la rama o se ha cambiado un test suyo, aunque sea en el commit en rojo de otra tarea, no marca la tarea (exit 3).
- **La review comprueba más cosas:** ejemplos con test, tests en rojo intactos, dependencias mergeadas, tamaño y propósito de la tarea, choques con decisiones aceptadas y llamadores fuera del diff.
- **Las decisiones se registran:** las redacta el agente en `proposed` y una persona las pasa a `accepted`. Una decisión aceptada no se edita: se sustituye por otra.
- **El SDD es el último nivel y es más corto:** `idea-to-spec`, `spec-to-plan` y `plan-to-tasks` escriben el artefacto en `draft` directamente y en el chat solo preguntan las decisiones y resumen lo supuesto. El plan se queda en el diseño. Con la última tarea, `task-done` marca `spec.md` y `plan.md` `obsolete`: lo que perdura son las decisiones y los tests.

Las tareas en curso de la v1 (sin `tests:`) pasan al formato nuevo con `examples: []` (sección 4) y se terminan como siempre.
