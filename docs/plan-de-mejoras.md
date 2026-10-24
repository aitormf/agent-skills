# Plan de mejoras

Fecha: 2026-10-20, revisado el 2026-10-22. Documento de trabajo para decidir qué hacer. No describe nada implementado.

Reúne la comparación de este repo con [karajan-code](https://github.com/manufosela/karajan-code) y [Ponytail](https://github.com/DietrichGebert/ponytail), las issues abiertas (#1–#5, inspiradas en [superpowers](https://github.com/obra/superpowers)), las issues creadas a raíz de la comparación (#7–#12), las que salieron de medir el coste del flujo de SDD (#13–#15, #18) y la PR #6.

El 2026-10-22 se revisó todo con un criterio: el proceso ya pesa demasiado, así que vale más lo que quita fricción o atrapa bugs reales que lo que añade pasos o texto. Se cerraron #1 (fusionada en #11), #4, #5 y #12. El orden nuevo está en la sección 5.

## 1. Los tres proyectos

| | agent-skills (este repo) | Karajan | Ponytail |
|---|---|---|---|
| Qué es | Proceso: SDD, review y guardrails, en skills y agentes Markdown | Un CLI (`kj`) en Node que gobierna al agente con gates | Un prompt de 52 líneas ("el cambio completo más pequeño") y adaptadores |
| Cómo hace cumplir las reglas | Hooks de Claude Code, pre-commit, CI y el comando de verificación de `AGENTS.md` | Gates en git, hooks del agente (Sentinel), políticas y CI | Solo el prompt; los hooks únicamente inyectan las reglas |
| Agentes | Claude Code, Codex, OpenCode, pi | 9 CLIs | Unos 30 hosts |
| Cómo demuestra que funciona | Sandbox de review con hallazgos esperados, puntuado a mano | Tareas de referencia deterministas con línea base | Benchmark A/B con y sin la skill, varias ejecuciones por tarea, resultados publicados con fecha |
| Licencia | — | AGPL-3.0 | MIT |

Por la licencia, de Karajan se toman **ideas, no código**. De Ponytail se puede copiar texto citando la fuente.

### Lo que ya hacemos bien
Karajan y Ponytail confirman estas decisiones:

- Quien escribe no es quien revisa: personas de review con contexto limpio.
- Un verificador adversarial de hallazgos (`finding-verifier`).
- Revisión de la spec y el plan antes de implementar.
- El Stop hook con `check.sh` y la confirmación al forzar el push.
- Una sola fuente de los agentes y adaptadores generados con comprobación de que están al día (`build-agents.py --check`).

## 2. Las ideas

Cada idea indica su origen, dónde está registrada y una estimación de esfuerzo (S/M/L).

### Review

| # | Idea | Origen | Registro | Esfuerzo |
|---|---|---|---|---|
| 1 | **Veredicto ligado al hash del diff.** `review-prepush` guarda el veredicto con el sha256 de `git diff <base>...HEAD`. El hook `pre-push` lo reutiliza si el diff no ha cambiado. | Karajan (`verdict-store.js`) | #7 | S |
| 2 | **Revisa un modelo distinto del autor.** `REVIEW_KIT_REVIEWER=codex` en el hook `pre-push`. Si no está disponible, avisar de forma visible, nunca caer en silencio al mismo modelo. | Karajan | #8 | S |
| 8 | **Registro de falsos positivos conocidos.** Una sección "Known non-issues" en el `Code review` de AGENTS.md, con motivo, que `review-context` pasa al `finding-verifier`. | Karajan (`audit.false_positives`) | — | S |
| 12 | **Buscar llamadores fuera del diff.** Si cambia una firma, un valor de retorno o un comportamiento, buscar con grep todos los usos. Decir qué carga del sistema se ha supuesto. | Ponytail (`ponytail-review`) | #10 | S |
| 13 | **Formato de hallazgo.** Campo "If we skip it" (qué pasa si no se arregla). | Ponytail | #10 (opcional) | S |
| 18 | **Análisis determinista como filtro previo, solo en líneas añadidas.** Los hallazgos de Semgrep se filtran a las líneas que añade el diff (`git diff --unified=0`), no a ficheros enteros: la deuda previa no es del autor. Un hallazgo de severidad alta en esas líneas para `review-prepush` antes de lanzar las personas, sin gastar tokens. Si el analizador no está, se avisa y se sigue. | Karajan (`sonar-pregate.js`) | — | S |
| 19 | **Usar SonarQube solo si el repo ya lo tiene.** `Sonar: yes` en el `Code review` de AGENTS.md. `review-context` lee el quality gate y las incidencias de la PR (API o MCP de SonarSource) como fuente `sonar` en `review-report`, igual que `semgrep`. No instalamos ni arrancamos nada. | Karajan | — | S–M |

### Implementación y SDD

| # | Idea | Origen | Registro | Esfuerzo |
|---|---|---|---|---|
| 4 | **Medir si la implementación se ciñó al plan.** Cruzar los ficheros declarados en `tasks.md` con `git diff` y los `[x]`. Señalar ficheros que no pertenecen a ninguna tarea y tareas marcadas sin cambios. Si los commits citan `T<n>`, atribuirlos a tareas. | Karajan (`plan-adherence.md`) | Comentario en #2 | M |
| 14 | **Orden de preferencia en `implement`:** ¿hace falta? → ¿ya existe en el repo? → ¿librería estándar? → ¿dependencia instalada? → ¿una línea? → el mínimo. Más una lista de lo que nunca se recorta, el cierre "qué no hice o no comprobé" y el criterio único de test. | Ponytail | #11 | S |
| 15 | ~~**Atajos deliberados con `shortcut: <límite>, <cuándo revisarlo>`** en lugar de TODOs sin ticket.~~ Descartada: otra convención para un problema que no hemos tenido. | Ponytail (`ponytail-debt`) | #12 (cerrada) | S |
| 21 | **Ciclo TDD de un test cada vez** en `implement`, con informe de los tests vistos en rojo; `plan-to-tasks` ordena los tests de cada tarea. Caso real: el agente implementó una función entera tras ver en rojo solo los primeros tests. | Uso real | #18 | S |

### Coste del flujo de SDD

Medido en un trabajo real (un runner con su comando `run`): spec, plan y tareas llevaron unas 2h20. Las respuestas de la persona eran de una línea y casi siempre elegían la opción A. De unas 40 preguntas, solo 6–8 eran decisiones suyas. El tiempo se fue sobre todo en leer unos 50k caracteres de borradores y reviews en el chat.

| # | Idea | Origen | Registro | Esfuerzo |
|---|---|---|---|---|
| 22 | **Preguntar solo las decisiones de la persona.** Las reviews separan "decisión" (con alternativas reales) de "arreglo" (respuesta obvia, se aplica en bloque). Los detalles reversibles se proponen y se anotan en `Supuestos`; "ok" acepta todas las recomendaciones. | Uso real | #14 | M |
| 23 | **Escribir los artefactos en `draft` sin aprobación previa en el chat**, y enseñar solo un resumen de decisiones, supuestos y preguntas abiertas. | Uso real | #13 | S |
| 24 | **Plan a nivel de diseño, no de implementación**, y proponer partir los trabajos grandes (más de unos 12 RF o varias user stories independientes). | Uso real | #15 | S–M |

### Guardrails y seguridad

| # | Idea | Origen | Registro | Esfuerzo |
|---|---|---|---|---|
| 5 | **Detectar prompt injection en los ficheros que lee el agente** (AGENTS.md, CLAUDE.md, skills, specs): directivas ocultas, Unicode invisible, comentarios HTML con órdenes. | Karajan (`injection-findings.js`) | #9 | M |
| 6 | **Stop hook con reglas sobre la forma de trabajar:** código editado en la rama base, código sin ningún test tocado (según el criterio de #11), implementar sin spec o plan aprobados. Las vías de escape quedan registradas y, si el hook falla, deja terminar al agente y lo avisa. | Karajan (Sentinel) | — | M |
| 7 | **Tabla de qué se garantiza en cada nivel:** al usar una herramienta (solo hosts con hooks), al hacer commit (cualquier host) y en CI. Deja claro qué se pierde con Codex, OpenCode o pi. | Karajan | — | S |
| 10 | **Guía para aislar al agente:** usuario Linux separado con ACL, copias de seguridad, protección de ramas en el servidor. Una lista de comandos prohibidos no basta. | Karajan (`HARDENING-AGAINST-AI.md`) | — | S |
| 16 | **Pasar las reglas a los subagentes** con el hook `SubagentStart`, si las reglas de la idea 6 deben aplicarse a `implement`. | Ponytail | — | S |
| 20 | **Complejidad sin servidor.** Reglas de ruff `C901`, `PLR0912` y `PLR0915` en `setup-guardrails-python`; cobertura del código nuevo con `diff-cover` o `--cov-fail-under`. Cubre lo que aporta SonarQube más allá de la seguridad. | Karajan (SonarQube) | — | S |

### Calidad del propio repo

| # | Idea | Origen | Registro | Esfuerzo |
|---|---|---|---|---|
| 3 + 11 | **Harness de evaluación en `tests/evals/`:** suite de activación (#3); sandbox de review con `must_find` / `must_not_survive` / `verdict` y `baseline.json`; comparación A/B (sin skill, versión anterior, versión nueva) con varias ejecuciones y resultados con fecha; evaluador con tests sin API key dentro de `check.sh`. | Karajan (golden tasks), Ponytail (benchmark) | Comentario en #3 | L |
| 9 | **Comprobar si un repo está preparado para agentes:** AGENTS.md con `Commands` y comando de verificación, ARCHITECTURE.md con principios, ficheros que no excedan un tamaño. Como modo de auditoría de `generate-project-context`. Y un tope de tamaño para nuestros SKILL.md en `check.sh`. | Karajan (`agent-readiness.js`) | — | M |
| 17 | **Portabilidad:** en la tabla de instalación, la versión de cada herramienta con la que se probó. | Ponytail | — | S |

### Issues previas (superpowers)

| Issue | Qué propone | Relación con las ideas |
|---|---|---|
| #1 | Ninguna afirmación de éxito sin evidencia fresca | **Fusionada en #11** (punto 3b): mismo texto que el cierre "qué no hice o no comprobé". La idea 6 la haría cumplir. |
| #2 | Implementación por tarea, con revisión entre tareas y `## Decisiones` | Con un diff por tarea, la idea 4 es trivial. El revisor entre tareas puede ser otro modelo (idea 2). No sustituye a `review-prepush` final (idea 1). |
| #3 | Tests de activación de skills | Base del harness 3 + 11. Se hace primero solo la suite de activación. |
| #4 | Tablas de excusas y probar antes de escribir | **Cerrada.** Alarga los prompts (3.4). La excusa del test va en el criterio de #11. |
| #5 | Skill para cerrar una rama | **Cerrada.** `gh pr create` ya lo cubre y el merge local choca con 3.2. |

## 3. Choques: decisiones pendientes

Hay que decidirlas antes de implementar las piezas afectadas.

### 3.1 ¿Todo cambio lleva test?
- #4 responde a "es un cambio pequeño, no hace falta test" con "los cambios pequeños también rompen".
- Ponytail solo exige test para lógica no trivial.
- Si se hace la idea 6, el criterio pasa a bloquear de verdad.

**Propuesta (en #11):** un criterio único, escrito en un sitio y enlazado desde #4, `implement`, el Stop hook y `code-reviewer`.
- **Exigen test:** una rama, un bucle, un parser, dinero, seguridad, escritura de datos o un bug fix.
- **No lo exigen:** los cambios de solo docs o config.
- Es coherente con `debug-root-cause` (#6), que exige test de regresión en todo bug fix.

### 3.2 ¿La base solo avanza por PR?
- #5 ofrece "mergear en local" como opción.
- Hacer push a la base después se salta `review-pr` y debilita el hook `pre-push`.
- La idea 6 marcaría "código editado en la rama base".

**Propuesta:** el merge local solo si la sección `Code review` de AGENTS.md lo permite de forma explícita. Por defecto: push + PR, o dejar la rama.

### 3.3 ¿Dónde se registran las decisiones?
- #2 propone `## Decisiones` en `tasks.md`.
- #12 propone `shortcut:` en el código.

**Propuesta:** las decisiones sobre la spec o el plan van en `tasks.md`. Un límite concreto en una línea de código va en `shortcut:`. `sdd-next` muestra ambos por trabajo.

### 3.4 ¿Cuánto pueden crecer las instrucciones de `implement`?
Las tablas de excusas (#4), el orden de preferencia (#11) y el cierre obligatorio alargan el agente. Ponytail cabe en 52 líneas.

**Propuesta:** tope de tamaño en `check.sh` (idea 9) y medir cada añadido con el harness.

## 4. PR #6 (`debug-root-cause`, `apply-code-review`, `task-done`)

### Qué aporta
- `task-done`: un script marca `[x]` solo si la verificación sale con 0, con IDs `T<n>.` / `W<n>.`. Es el patrón de Karajan, "el programa manda, el agente piensa", y adelanta parte de #1 dentro de `implement`.
- `debug-root-cause`: causa raíz, una hipótesis cada vez, test de regresión que falla sin el arreglo. Para tras tres intentos y pregunta, que es mejor que el árbitro automático de Karajan.
- `apply-code-review`: clasificar, rebatir con evidencia y corregir uno a uno. Comparte la actitud de Ponytail: si nadie usa el código, propone borrarlo; no amplía el alcance.

### Problemas encontrados
1. **W1 no tiene una verificación ejecutable.** La plantilla pone `verification: the tests that cover them`, pero `plan-to-tasks` exige que la verificación se pueda ejecutar con `task-done`. *Arreglar antes de mergear.*
2. **`task-done` no comprueba que el comando sea el declarado en la tarea.** El agente pasa lo que quiera tras `--`; el propio test de `check.sh` usa `-- true`. El log va a un temporal que no se borra y la evidencia se pierde. Karajan liga la verificación al comando declarado (`card-verify.js`). *Arreglo mínimo:* avisar si el comando no aparece en la línea de la tarea y dejar comando y código de salida en el informe.
3. **`apply-code-review` permite rebatir hallazgos de seguridad** cuando la persona pide "atiende la review directamente". El criterio de "revisor de confianza" es ambiguo. *Propuesta:* rebatir un Critical o un hallazgo de seguridad siempre se para a preguntar. *Arreglar antes de mergear.*
4. **Más skills con nombres cercanos:** `apply-review`, `apply-code-review` y `code-review-and-quality`; y `debug-root-cause` se activa con algo tan amplio como "whenever something is broken". Incluir estos pares en los tests de activación (#3).

### Decisión (2026-10-22)
- Mergear `task-done` y `debug-root-cause` tras arreglar los puntos 1 y 2, y acotar la descripción de `debug-root-cause` (punto 4).
- **Sacar `apply-code-review` de la PR.** Repite la ceremonia que #14 quita de `apply-review` (uno a uno, esperar confirmación) y se solapa con ella. Se rehace después de #14, con el mismo criterio de "decisión frente a arreglo" y la regla del punto 3.

### Relación con las issues
- **#2:** depende de `task-done` y de los IDs. Falta la convención de citar `T<n>` en los commits para la idea 4.
- **#7:** hace automática la comprobación "el código no ha cambiado" de `apply-code-review`.
- **#11:** choca porque ambas tocan `agents/implement.md`. Hacer #11 después de mergear #6.

## 5. Orden propuesto

Revisado el 2026-10-22. Antes el harness (#3) iba primero y bloqueaba lo demás. Ahora va lo que ya hemos medido que cuesta horas, y el harness se reduce a la suite de activación.

| Fase | Qué | Por qué en este orden |
|---|---|---|
| 1 | #14 → #13 → #15 | El coste medido del flujo de SDD: horas de lectura y preguntas que ya tenían respuesta |
| 2 | PR #6 sin `apply-code-review`, con los puntos 1 y 2 arreglados | Pequeño; desbloquea #2, #11 y #18 y evita conflictos en `implement.md` |
| 3 | #10, #11 (con #1 dentro) y #18 | Cambios de texto baratos con efecto directo en la calidad. #11 y #18 tocan `implement.md`: juntas o seguidas |
| 4 | #7 y la suite de activación de #3 | Ahorro de reviews repetidas; detectar que una skill deja de activarse |
| 5 | `apply-code-review` rehecha con el criterio de #14 | Depende de #14 |
| Backlog | #8, #2, #9 e ideas 4, 5, 6, 7, 8, 9, 10, 16–20 | Sin evidencia de que hagan falta todavía. #2 multiplica tokens y pasos; #9 cobra sentido al evaluar repos ajenos |

## 6. Lo que no copiaríamos

- **De Karajan:** RAG, panel de tareas, 9 CLIs de agente, el árbitro Solomon (nuestro `finding-verifier` y la escalada a la persona cubren su papel) y el clasificador de intención por palabras clave. Son mucho que mantener y se salen del enfoque de skills portables.
- **SonarQube como dependencia del kit.** Karajan dedica unas 2.400 líneas a arrancarlo en Docker, gestionar tokens y el scanner. Es un servidor Java con Elasticsearch (unos 2 GB de RAM); la Community Edition no analiza ramas ni PRs y SonarCloud solo es gratis para repos públicos. En seguridad ya lo cubren ruff `S`, Semgrep, pip-audit y gitleaks. Nos quedamos con el patrón (ideas 18 y 19) y la complejidad con ruff (idea 20).
- **De Ponytail:** el band de coste y tokens y su panel, y los niveles lite/full/ultra (`review-pr` ya ajusta la profundidad al riesgo). De sus cifras, solo el rigor: si publicamos números, con método, varias ejecuciones y limitaciones, como su nota "Read this number honestly".

## 7. Preguntas para pensar

1. ¿Queremos que las reglas bloqueen (Stop hook, idea 6) o que solo avisen? Bloquear es más fiable pero solo funciona bien en Claude Code.
2. ¿Qué criterio de test adoptamos (3.1)? Afecta a cuatro piezas a la vez.
3. ¿Aceptamos el merge local a la base en algún caso (3.2)?
4. ¿Cuánto presupuesto en tokens estamos dispuestos a gastar en evaluaciones (harness 3/11) y con qué frecuencia: cada cambio de skill, cada release, a mano?
5. ¿Hace falta un segundo modelo para la review (#8) en todos los repos, o solo en los de mayor riesgo?
6. ~~¿Merece la pena seguir añadiendo skills, o conviene consolidar las que se parecen?~~ Consolidar primero: `apply-code-review` se rehace tras #14 con el criterio de `apply-review`.

## Referencias

- Issues: #1–#5 (superpowers), #7–#12 (esta comparación), #13–#15 y #18 (uso real). Cerradas el 2026-10-22: #1, #4, #5, #12 y, por fusión, #16 y #17. PR #6.
- Karajan: `src/review/sonar-pregate.js`, `docs/golden-tasks.md`, `docs/plan-adherence.md`, `docs/HARDENING-AGAINST-AI.md`, `docs/audit-false-positives.md`, `src/review/verdict-store.js`, `src/audit/injection-findings.js`, `src/audit/agent-readiness.js`, `src/harden/sentinel/`.
- Ponytail: `skills/ponytail/SKILL.md`, `skills/ponytail-review/SKILL.md`, `skills/ponytail-debt/SKILL.md`, `benchmarks/README.md`, `tests/behavior.test.js`, `docs/agent-portability.md`.
