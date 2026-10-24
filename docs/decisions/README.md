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
| [D-0004](0004-trabajo-en-curso-en-issues.md) | El trabajo en curso (nota, mapa, tareas) vive en un issue de GitHub | architecture | accepted | skills/task-done/, skills/idea-to-issue/ |
| [D-0005](0005-puerta-en-el-mapa-de-ejemplos.md) | La puerta por defecto antes del código es el mapa de ejemplos | rule | accepted | skills/idea-to-issue/, agents/implement.md, skills/task-done/ |
| [D-0006](0006-spec-y-plan-son-documentos-de-trabajo.md) | spec.md y plan.md son documentos de trabajo; perduran las decisiones y los tests | architecture | accepted | skills/idea-to-spec/, skills/spec-to-plan/, skills/plan-to-tasks/, docs/sdd/ |
| [D-0007](0007-retirar-sdd-next.md) | Se retira sdd-next | architecture | accepted | skills/sdd-next/ |
| [D-0008](0008-issue-de-trabajo-sin-etiqueta.md) | Un issue de trabajo se reconoce por el que se pasa, sin etiqueta | architecture | accepted | skills/task-done/, skills/review-prepush/, skills/review-pr/ |
| [D-0009](0009-idioma-del-repositorio.md) | Skills, commits, scripts y frontmatter en inglés; la documentación, en español | rule | accepted | . |
| [D-0010](0010-migracion-de-docs-adr.md) | Los ADRs existentes se ofrecen mover a docs/decisions/ | architecture | accepted | skills/generate-project-context/, skills/record-decision/ |
