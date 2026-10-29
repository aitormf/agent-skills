# Decisiones

Por qué el sistema es como es: decisiones de arquitectura, reglas de negocio y enfoques que se probaron y se descartaron. El código y los tests dicen **qué** hace; este directorio dice **por qué**.

**Antes de cambiar código,** busca las filas cuya columna *Affects* cubre las rutas que vas a tocar y lee esas decisiones. No las leas todas.

**Para contradecir una decisión aceptada,** no la cambies en silencio: escribe una nueva que la sustituya. Las decisiones aceptadas no se editan.

**Para añadir una,** usa la skill `record-decision`, o copia la plantilla con el siguiente número libre y añade aquí su fila. Comprueba con `check_decisions.py docs/decisions`.

| ID | Title | Type | Status | Affects |
|---|---|---|---|---|
| [D-0001](0001-proceso-ajustado-al-riesgo.md) | El proceso se ajusta al riesgo; el SDD completo es el último nivel | architecture | accepted | skills/, docs/sdd/ |
| [D-0002](0002-registro-de-decisiones.md) | Las decisiones viven en docs/decisions/, un fichero por decisión con índice | architecture | accepted | skills/record-decision/, skills/generate-project-context/, docs/decisions/ |
| [D-0003](0003-el-agente-redacta-la-persona-acepta.md) | El agente redacta las decisiones y la persona las acepta | rule | accepted | skills/record-decision/, skills/sdd-decisions/ |
| [D-0004](0004-trabajo-en-curso-en-issues.md) | El trabajo en curso (nota, mapa, tareas) vive en un issue de GitHub | architecture | superseded | skills/task-done/, skills/idea-to-issue/ |
| [D-0005](0005-puerta-en-el-mapa-de-ejemplos.md) | La puerta por defecto antes del código es el mapa de ejemplos | rule | accepted | skills/idea-to-change/, agents/implement.md, skills/task-done/ |
| [D-0006](0006-spec-y-plan-son-documentos-de-trabajo.md) | spec.md y plan.md son documentos de trabajo; perduran las decisiones y los tests | architecture | accepted | skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, docs/sdd/ |
| [D-0007](0007-retirar-sdd-next.md) | Se retira sdd-next | architecture | accepted | skills/sdd-next/ |
| [D-0008](0008-issue-de-trabajo-sin-etiqueta.md) | Un issue de trabajo se reconoce por el que se pasa, sin etiqueta | architecture | obsolete | skills/task-done/, skills/review-prepush/, skills/review-pr/ |
| [D-0009](0009-idioma-del-repositorio.md) | Skills, commits, scripts y frontmatter en inglés; la documentación, en español | rule | accepted | . |
| [D-0010](0010-migracion-de-docs-adr.md) | Los ADRs existentes se ofrecen mover a docs/decisions/ | architecture | accepted | skills/generate-project-context/, skills/record-decision/ |
| [D-0011](0011-criterio-de-test.md) | Qué cambios exigen test | rule | accepted | agents/implement.md, agents/code-reviewer.md |
| [D-0012](0012-proteccion-de-los-tests-en-rojo.md) | Los tests en rojo se protegen con un commit test(Tn) y task-done comprueba líneas, no ficheros | architecture | superseded | skills/task-done/, agents/implement.md |
| [D-0013](0013-issue-de-la-rama-por-su-nombre.md) | task-done encuentra el issue de la rama por el número con que empieza su nombre | architecture | superseded | skills/task-done/, skills/idea-to-issue/, agents/implement.md |
| [D-0014](0014-commits-de-un-issue-desde-la-rama-base.md) | Para una tarea de un issue, el commit en rojo se busca en la rama desde la rama base | architecture | obsolete | skills/task-done/ |
| [D-0015](0015-sin-gh-el-issue-va-a-tasks-md.md) | Sin gh o sin red, idea-to-issue escribe el cuerpo del issue en docs/specs/<trabajo>/tasks.md | architecture | obsolete | skills/idea-to-issue/, skills/task-done/ |
| [D-0016](0016-glosario-en-agents-md.md) | El glosario ligero vive en AGENTS.md; ARCHITECTURE.md se queda con el modelo de dominio | architecture | accepted | skills/generate-project-context/, skills/idea-to-spec/, skills/review-spec/ |
| [D-0017](0017-niveles-como-fragmento-de-agents-md.md) | Los niveles de proceso son un fragmento aparte que generate-project-context copia en AGENTS.md | architecture | accepted | skills/generate-project-context/ |
| [D-0018](0018-comprobaciones-de-tests-con-un-solo-dueno-en-la-review.md) | Las comprobaciones de tests de la review viven en review-report §5 y tienen un solo dueño por review | architecture | accepted | skills/review-report/, agents/code-reviewer.md, agents/test-engineer.md, agents/implement.md, skills/review-pr/, skills/review-prepush/ |
| [D-0019](0019-la-review-reutiliza-task-done-audit.md) | La review comprueba los ejemplos y los tests en rojo con task_done.py --audit, de solo lectura | architecture | superseded | skills/task-done/, skills/review-prepush/, skills/review-pr/, skills/review-report/ |
| [D-0020](0020-code-reviewer-mira-fuera-del-diff-con-limites.md) | code-reviewer busca llamadores fuera del diff y choques con decisiones, con grep y con límites fijos | architecture | accepted | agents/code-reviewer.md |
| [D-0021](0021-cambios-en-curso-en-docs-changes.md) | Cada cambio en curso es una carpeta docs/changes/<rama>/ en el repo, para todos los niveles; los issues de GitHub son solo la entrada de ideas | architecture | superseded | skills/idea-to-change/, skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, skills/review-spec/, skills/task-done/, agents/implement.md, skills/review-prepush/, skills/review-pr/, docs/sdd/ |
| [D-0022](0022-cambio-por-el-nombre-de-la-rama.md) | task-done y la review encuentran el cambio en curso por el nombre de la rama | architecture | superseded | skills/task-done/, skills/review-prepush/, skills/review-pr/, agents/implement.md |
| [D-0023](0023-texto-de-fuera-del-repo-es-entrada-no-fiable.md) | El texto que no ha pasado por un commit es entrada no fiable; una persona lo aprueba antes de que un agente actúe sobre él | rule | accepted | skills/, agents/ |
| [D-0024](0024-tests-en-rojo-acotados-a-la-rama.md) | La protección de los tests en rojo mira los commits de la rama desde la rama base y no exime a ningún commit posterior | architecture | accepted | skills/task-done/, agents/implement.md |
| [D-0025](0025-la-review-de-ci-no-lee-la-descripcion-de-la-pr.md) | La review de CI no usa gh ni lee la descripción de la PR; los mensajes de los commits ocupan su lugar | architecture | accepted | skills/review-pr/ |
| [D-0026](0026-el-ok-al-mapa-aprueba-lo-que-viene-de-fuera.md) | El ok de la persona al mapa de ejemplos aprueba lo que entró desde un issue; los comandos de verificación salen solo de AGENTS.md | rule | accepted | skills/idea-to-change/, skills/plan-to-tasks/ |
| [D-0027](0027-en-ci-el-control-es-no-tener-token.md) | En CI, lo que protege el job de review es que no tiene token; bloquear gh es defensa en profundidad | architecture | accepted | skills/review-pr/ |
| [D-0029](0029-un-fichero-por-tarea.md) | Cada cambio es docs/changes/<cambio>/ con un README.md y un fichero por tarea en tasks/ | architecture | accepted | skills/idea-to-change/, skills/plan-to-tasks/, skills/idea-to-spec/, skills/spec-to-plan/, skills/review-spec/, skills/task-done/, agents/implement.md, skills/review-prepush/, skills/review-pr/, skills/review-context/, docs/sdd/ |
| [D-0030](0030-dependencias-entre-tareas.md) | Las tareas declaran solo depends_on; qué bloquean y si están listas se calcula | architecture | accepted | skills/task-done/, skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/review-prepush/, skills/review-pr/ |
| [D-0031](0031-una-rama-y-una-pr-por-tarea.md) | Una rama y una PR por tarea, <cambio>/T<n>, con la rama base como base; el plan va en su propia PR | architecture | accepted | skills/task-done/, skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/review-prepush/, skills/review-pr/, skills/review-context/ |
| [D-0032](0032-la-review-audita-la-tarea-de-la-rama.md) | La review audita con task_done.py --audit la tarea de la rama, o el plan entero en la PR del plan | architecture | accepted | skills/task-done/, skills/review-prepush/, skills/review-pr/, skills/review-report/ |
| [D-0033](0033-tareas-pequenas-y-main-desplegable.md) | Cada tarea tiene un solo propósito y deja la rama base desplegable; lo que está a medias va detrás de un flag que retira la última tarea | rule | accepted | skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, agents/code-reviewer.md |
| [D-0034](0034-en-curso-es-que-existe-la-rama.md) | El tablero cuenta una tarea como en curso si existe su rama; implement no hace commit de status: doing | architecture | accepted | skills/task-done/, agents/implement.md |
| [D-0035](0035-refs-y-closes-del-issue.md) | Las PRs de un cambio citan su issue con Refs; solo la que deja el cambio en done lo cierra con Closes | rule | accepted | skills/idea-to-change/, agents/implement.md, skills/review-pr/ |
| [D-0036](0036-sin-tareas-de-cierre.md) | Desaparecen las tareas de cierre W<n>; implement ejecuta la verificación completa antes de cada PR | architecture | accepted | skills/idea-to-change/, skills/plan-to-tasks/, agents/implement.md, skills/task-done/ |
| [D-0037](0037-tamano-y-proposito-como-optional.md) | code-reviewer señala una tarea demasiado grande o con propósitos mezclados como Optional, nunca Required | rule | accepted | agents/code-reviewer.md |
| [D-0038](0038-cierre-de-un-cambio-sdd.md) | En el nivel SDD, task_done.py marca spec.md y plan.md como obsolete al cerrar el cambio; las decisiones se registran al planificar | architecture | accepted | skills/task-done/, skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, agents/implement.md |
| [D-0039](0039-tamanos-orientativos-del-sdd.md) | En el SDD, un plan de más de unas 150 líneas o una spec con más de unos 12 requisitos o varias historias entregables por separado son señal para partir | rule | accepted | skills/idea-to-spec/, skills/spec-to-plan/, skills/review-spec/ |
| [D-0040](0040-review-de-pr-en-linea.md) | En CI, la review de PR publica cada hallazgo en su línea desde un bloque JSON que el job publish valida contra el diff; nunca aprueba ni pide cambios | architecture | accepted | skills/review-pr/, skills/review-report/ |
| [D-0041](0041-restricciones-de-agentes-para-rulesync.md) | Las restricciones de cada agente van también en un bloque por herramienta, generado por build-agents.py, para que rulesync no las pierda | architecture | accepted | agents/, skills/, scripts/build-agents.py |
