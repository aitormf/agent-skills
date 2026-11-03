# agent-skills

Skills y guías para trabajar con agentes de IA en repositorios de código.

```
skills/     Skills autocontenidas (SKILL.md + assets/ + references/)
agents/     Subagentes en formato Claude Code (fuente única)
adapters/   Agentes generados para Codex y OpenCode (no editar a mano)
docs/arnes/ Guías del arnés: el porqué de cada pieza. El código y las plantillas viven en los assets de las skills
docs/sdd/   Guía de uso de SDD
docs/review/ Guía de code review y material de Addy (UPSTREAM.md)
scripts/    check.sh, generador de agentes y tests
tests/      Sandbox con bugs plantados para probar la review y suite de activación de skills
```

## Instalar

El repositorio es privado: se instala por SSH y solo funciona para quien tenga acceso. En los comandos, `git@github.com:aitormf/agent-skills.git` es la URL SSH. Si en `~/.ssh/config` usas un alias de host (p. ej. `github.com-personal`), pon el alias. Si el repositorio pasa a ser público, en Claude Code, Codex y `npx skills` basta con `aitormf/agent-skills`.

| Herramienta | Skills | Agentes (`implement`, `spec-reviewer`) |
|---|---|---|
| Claude Code | Plugin | Incluidos en el plugin |
| Codex | Plugin o `npx skills` | Copiar `adapters/codex/agents/` |
| OpenCode | `npx skills` | Copiar `adapters/opencode/agents/` |
| pi | Paquete de pi | — (pi no tiene subagentes) |

Sin los agentes, el flujo funciona igual: la revisión y la implementación se hacen en la sesión principal, pero sin contexto limpio.

### Qué se garantiza en cada herramienta

Lo que el kit hace cumplir, sin depender de que el modelo siga sus instrucciones, en tres momentos. Las barreras de la sesión vienen de `setup-guardrails-python`, y las de los agentes, de sus ficheros.

| Momento | Garantía | Claude Code | Codex | OpenCode | pi |
|---|---|---|---|---|---|
| **Sesión del agente** | No leer secretos (`.env`, `~/.ssh`…), no usar `pip`, no editar el arnés ni hacer `commit --no-verify` | ✅ `settings.json` | — | — | — |
| | Preguntar antes de un push forzado | ✅ hook | ✅ `.codex/rules`, si confías en la capa `.codex/` | ✅ `opencode.json` | — |
| | Paquetes inventados o con menos de 90 días | ✅ hook | — | — | — |
| | No terminar con `check.sh` en rojo | ✅ hook `Stop` | — | — | — |
| | Agentes de review de solo lectura | ✅ `tools:` | — heredan el sandbox de la sesión | ✅ `permission:` | — sin subagentes |
| **Commit y push** (cualquier herramienta) | ruff, mypy, gitleaks, Unicode oculto, zizmor, formato de commit | ✅ pre-commit | ✅ | ✅ | ✅ |
| | Review antes del push; bloquea con un Critical confirmado | ✅ hook pre-push, si está el CLI `claude` | ✅ | ✅ | ✅ |
| **CI** (la autoridad final) | `check.sh`, gitleaks, pip-audit, Semgrep, zizmor | ✅ | ✅ | ✅ | ✅ |
| | Review de la PR con comentarios en línea | ✅ Action con Claude Code | ✅ | ✅ | ✅ |

- **Lo que se pierde fuera de Claude Code** son las barreras de la sesión: allí solo quedan las instrucciones. Lo que falle se para en el commit (si el agente no se salta los hooks) y, en última instancia, en CI.
- `pre-commit` y el hook pre-push se saltan con `--no-verify`. Solo Claude Code lo impide en la sesión; por eso CI repite todas las comprobaciones.
- Una garantía es de `setup-guardrails-python` o del hook pre-push solo si están instalados en el repo.

¿El proyecto ya usaba la v1? Sigue [Actualizar un repositorio a la v2](docs/actualizar-a-v2.md).

### Claude Code

```
/plugin marketplace add git@github.com:aitormf/agent-skills.git
/plugin install harness@aitormf
```

- Como plugin, todo va con namespace: las skills son `/harness:idea-to-change`, `/harness:idea-to-spec`… y los agentes, `harness:implement` y `harness:spec-reviewer`.
- Para que el equipo lo tenga en un proyecto, declara el catálogo en el `.claude/settings.json` del proyecto. Claude Code ofrecerá instalarlo al abrir el proyecto:

  ```json
  {
    "extraKnownMarketplaces": {
      "aitormf": { "source": { "source": "git", "url": "git@github.com:aitormf/agent-skills.git" } }
    },
    "enabledPlugins": { "harness@aitormf": true }
  }
  ```

  Comprueba el formato de `source` con la documentación de plugins de tu versión.
- Para probar cambios sin instalar nada: `claude --plugin-dir /ruta/a/agent-skills`.

### Codex

```bash
codex plugin marketplace add git@github.com:aitormf/agent-skills.git
codex plugin add harness@aitormf
```

Los agentes se copian aparte: Codex no los carga desde plugins.

```bash
git clone --depth 1 git@github.com:aitormf/agent-skills.git /tmp/agent-skills
mkdir -p .codex/agents && cp /tmp/agent-skills/adapters/codex/agents/*.toml .codex/agents/
```

Para tenerlos en todos los proyectos, cópialos a `~/.codex/agents/` (o `$CODEX_HOME/agents/`). Si hay un agente con el mismo nombre en el proyecto, gana el del proyecto.

```bash
mkdir -p ~/.codex/agents && cp /tmp/agent-skills/adapters/codex/agents/*.toml ~/.codex/agents/
```

En Codex, el sandbox y las aprobaciones de un subagente salen siempre de la sesión principal. Lo que el agente puede hacer lo limitan sus instrucciones, no su fichero.

### OpenCode

OpenCode no tiene manifiesto de plugins. Las skills se instalan con `npx skills`, que las deja en `.agents/skills/`:

```bash
npx skills add git@github.com:aitormf/agent-skills.git -a opencode     # pregunta qué skills
git clone --depth 1 git@github.com:aitormf/agent-skills.git /tmp/agent-skills
mkdir -p .opencode/agents && cp /tmp/agent-skills/adapters/opencode/agents/*.md .opencode/agents/
```

Para tenerlos en todos los proyectos, cópialos a `~/.config/opencode/agents/` (en versiones antiguas, `~/.config/opencode/agent/`). Si hay un agente con el mismo nombre en el proyecto, gana el del proyecto.

```bash
mkdir -p ~/.config/opencode/agents && cp /tmp/agent-skills/adapters/opencode/agents/*.md ~/.config/opencode/agents/
```

### pi

```bash
pi install git:git@github.com:aitormf/agent-skills.git -l   # -l: solo en este proyecto (.pi/settings.json)
```

pi encuentra las skills por la carpeta `skills/`, sin manifiesto.

### Cualquier otro agente: `npx skills`

```bash
npx skills add git@github.com:aitormf/agent-skills.git --list                    # ver las skills
npx skills add git@github.com:aitormf/agent-skills.git -s <skill> -a <agente>    # claude-code, codex, opencode, gemini-cli, cursor…
```

Copia las skills a `.agents/skills/`, enlaza `.claude/skills/` y registra las versiones en `skills-lock.json`. Haz commit de las tres cosas. `npx skills update` trae la versión nueva.

### Bajo demanda: atril

Con [atril](https://github.com/manufosela/karajan-code/tree/main/packages/atril), las skills viven en un almacén (`.atril/` del proyecto o `~/.atril`) y el agente solo carga las que necesita cada tarea (`atril route`), en vez de todas en cada sesión. Cada skill y cada agente del kit declara `kind` y lo que usa (`uses`) o a quién delega (`delegates`), así que `atril route` devuelve el bloque entero: `review-pr` trae `review-context`, `review-report`, `task-done` y sus cuatro agentes.

Lo que se lee bajo demanda no se registra en la herramienta, y pierde dos cosas:
- **Los agentes, sus restricciones** (`tools:` en Claude Code, `permission:` en OpenCode): leído como fichero, `code-reviewer` ya no es un subagente de solo lectura.
- **`review-pr` y `review-prepush`, su `allowed-tools`:** las órdenes de git y `gh` de solo lectura piden permiso. Es fricción, no un riesgo.

Por eso, **fija** con `atril expose` los agentes y lo que necesitan, y deja el resto **bajo demanda**. `atril expose` no fija lo que usa cada pieza: un agente fijado precarga sus skills (`code-reviewer`, `review-report`), y si no están fijadas, Claude Code no las encuentra. La lista ya incluye todo lo que usan:

```bash
npm install -g @karajan-family/atril rulesync
git clone git@github.com:aitormf/agent-skills.git /tmp/kit
for s in /tmp/kit/skills/*/; do atril install "$s"; done
for a in /tmp/kit/agents/*.md; do atril install "$a"; done
atril expose agent:code-reviewer agent:security-auditor agent:test-engineer agent:finding-verifier \
  agent:implement agent:spec-reviewer skill:review-pr skill:review-prepush skill:review-context \
  skill:review-report skill:code-review-and-quality skill:task-done skill:idea-to-change \
  skill:sdd-decisions skill:record-decision skill:review-spec
rulesync init                     # y añade "commands" a "features" en rulesync.jsonc, para el puente /atril
atril sync && rulesync generate   # o "rulesync": { "generate": true } en .atril/atril.json
```

- **Bajo demanda** quedan el SDD (`idea-to-spec`, `spec-to-plan`, `plan-to-tasks`, `apply-review`), `generate-project-context`, `setup-guardrails-python` y `debug-root-cause`. Se piden con `/atril <tarea>` o por su nombre.
- **Las restricciones llegan:** cada agente y cada skill con campos propios de Claude Code llevan un bloque `claudecode:` (y los agentes, uno `opencode:`) en su frontmatter, que es lo que rulesync conserva. En OpenCode, rulesync los escribe en el formato v2 (`permissions:`), con `subagent` denegado.
- **La búsqueda de atril es por palabras** y las descripciones están en inglés: una tarea en español encaja peor, y «review this pull request» empata con `code-review-and-quality`. Pide la skill por su nombre cuando importe.
- En Codex los agentes heredan el sandbox de la sesión, con atril o sin él.

Probado con atril 1.2.0 y rulesync 43.2.0 en Claude Code 2.1.312; el detalle está en el [plan v3](docs/plan-v3.md) (§3).

## Skills

### Preparar el proyecto

| Skill | Qué hace |
|---|---|
| [`generate-project-context`](skills/generate-project-context/SKILL.md) | Entrevista para crear AGENTS.md, ARCHITECTURE.md (con principios innegociables), CONTRIBUTING.md, el registro de decisiones (`docs/decisions/`) y SECURITY.md. Sustituye a la constitución de Spec Kit; en proyectos con `docs/adr/`, ofrece moverlos |
| [`setup-guardrails-python`](skills/setup-guardrails-python/SKILL.md) | Instala los guardrails deterministas de un repo Python: check.sh, pre-commit, CI, seguridad, y permisos y hooks de Claude Code |

### Cuánto proceso: niveles A, B y C

El proceso se ajusta al tamaño y al riesgo del cambio. El nivel dice dónde se para la persona antes de que haya código; la tabla completa, con las señales para subir o bajar, es la que `generate-project-context` añade al `AGENTS.md` de cada proyecto ([`AGENTS-levels.md`](skills/generate-project-context/assets/es/AGENTS-levels.md)).

| Nivel | Para qué | Parada antes del código |
|---|---|---|
| **C** | Trivial, bug con causa clara (test y arreglo) o de causa desconocida (`debug-root-cause`) | Ninguna: se revisa el diff con `review-prepush` |
| **B** (por defecto) | Feature normal: `idea-to-change` | Una por idea: el mapa de ejemplos y sus decisiones |
| **A** | Reglas delicadas (dinero, datos personales) | Lo de B, y los tests en rojo de cada tarea delicada (`level: A`) |
| **SDD** (último nivel) | Feature grande o con diseño de verdad que decidir: `idea-to-spec` → `spec-to-plan` → `plan-to-tasks` | La spec y el plan, que la persona aprueba en el fichero |

Todos los niveles con tareas terminan igual: una PR del plan y una PR por tarea, y las decisiones que sobreviven al cambio en `docs/decisions/`.

### Flujo por defecto: de la idea al cambio (nivel B)

| Skill / agente | Qué hace |
|---|---|
| [`idea-to-change`](skills/idea-to-change/SKILL.md) | De idea (o de un issue de GitHub) a un cambio listo para implementar, en `docs/changes/<cambio>/` y en la PR del plan (rama `<cambio>/plan`): un `README.md` con la nota (problema, plazo máximo, fuera de alcance) y el mapa de ejemplos (reglas, ejemplos, preguntas), y un fichero por tarea en `tasks/`: tareas pequeñas, de un solo propósito, con sus dependencias y los tests que nombran. Las decisiones van a `docs/decisions/` en `proposed`. Una sola parada: la persona revisa el mapa y las decisiones en el fichero, no en el chat. El texto de un issue se trata como entrada no fiable |
| agente [`implement`](agents/implement.md) | Implementa las tareas listas, una rama (`<cambio>/T<n>`) y una PR por tarea: commit de tests en rojo, un test cada vez, `task-done`, push y PR; sigue con la siguiente lista mientras las PRs esperan revisión |
| [`task-done`](skills/task-done/SKILL.md) | Pone `status: done` en la tarea solo si su verificación pasa y sus tests en rojo siguen intactos en los commits de la rama; con la última, también en el README. Su tablero (`board.py`) dice qué tareas están listas, bloqueadas, en curso o hechas |

```
idea-to-change → docs/changes/<cambio>/ → ★ persona: mapa de ejemplos y decisiones
  → tareas en tasks/ y PR del plan (<cambio>/plan) → merge
  → implement, por cada tarea lista: rama <cambio>/T<n> → review-prepush → PR → review-pr → merge
    (la PR de la última tarea cierra el issue con Closes #<n>, si partió de uno)
```

Si hay diseño de verdad que decidir, el último nivel es el SDD (más abajo).

### Decisiones

| Skill | Qué hace |
|---|---|
| [`record-decision`](skills/record-decision/SKILL.md) | Registra en `docs/decisions/` las decisiones que deben sobrevivir al trabajo en curso: arquitectura, reglas de negocio y enfoques descartados. Las redacta en `proposed`; solo una persona las pasa a `accepted`. Mantiene el índice, gestiona la sustitución y migra `docs/adr/`. `check_decisions.py` valida el directorio |

Los agentes leen solo el índice y abren las decisiones cuyo `affects` cubre lo que van a tocar. Una decisión aceptada no se edita: se escribe otra que la sustituye.

### Spec-Driven Development (último nivel)

Para cuando hay diseño de verdad que decidir. Las skills escriben la spec, el plan y las tareas directamente en el fichero, en `draft`, y en el chat solo preguntan las decisiones de la persona y resumen lo supuesto. La spec y el plan son documentos de trabajo: al terminar la última tarea, `task-done` los marca `obsolete`, y lo que perdura son las decisiones (en `docs/decisions/`) y los tests. Cómo usarlo, paso a paso: **[guía de SDD](docs/sdd/README.md)**.

| Skill / agente | Qué hace |
|---|---|
| [`idea-to-spec`](skills/idea-to-spec/SKILL.md) | De idea a `spec.md`, preguntando solo las decisiones; propone partir un cambio grande |
| [`review-spec`](skills/review-spec/SKILL.md) · agente [`spec-reviewer`](agents/spec-reviewer.md) | Revisa la spec o el plan. Recomienda, nunca aprueba |
| [`apply-review`](skills/apply-review/SKILL.md) | Pregunta las decisiones una a una y aplica los arreglos en bloque, salvo los que la persona excluya |
| [`spec-to-plan`](skills/spec-to-plan/SKILL.md) | De spec aprobada a un `plan.md` de diseño (componentes, los que reutiliza, contratos, qué test cubre cada criterio), con comprobación de principios |
| [`plan-to-tasks`](skills/plan-to-tasks/SKILL.md) | De plan aprobado a un fichero por tarea en `tasks/` (el formato del nivel B), con sus dependencias, sus tests en orden y su verificación, y la PR del plan |
| agente [`implement`](agents/implement.md) | Implementa las tareas listas, una rama y una PR por tarea, cada una con el comando de verificación en verde |
| [`task-done`](skills/task-done/SKILL.md) | Ejecuta la verificación de una tarea y solo si pasa le pone `status: done`; si la tarea lista sus ejemplos, comprueba antes en git que sus tests están en un commit en rojo y no han cambiado. Su tablero dice qué tareas están listas. La usa `implement` |
| [`sdd-decisions`](skills/sdd-decisions/SKILL.md) | Interna: qué es una decisión de la persona (se pregunta) y qué un supuesto o arreglo con respuesta por defecto (se propone por escrito) |

```
idea-to-spec → [review-spec → apply-review] → persona: status: approved
  → spec-to-plan → [review-spec → apply-review] → persona: status: approved
  → plan-to-tasks → PR del plan → implement (una PR por tarea) → review-prepush → review-pr
```

Convenciones de SDD:

- Cada cambio vive en `docs/changes/<cambio>/` (`docs/changes/42-cancelar-viaje/`): `README.md` y `tasks/` (el mismo formato que en el nivel B), `spec.md`, `plan.md` y las revisiones. El plan va en la rama `<cambio>/plan` y cada tarea en `<cambio>/T<n>`, cada una con su PR. Subir del nivel B al SDD es añadir ficheros a la carpeta.
- `spec.md` y `plan.md` llevan `status: draft | approved | obsolete` en el frontmatter. **Solo una persona pone `approved`.** Las skills avisan y preguntan si se intenta avanzar sin aprobación. `task-done` los pone en `obsolete` con la última tarea.
- No hay backlog central: los cambios abiertos son las carpetas con `status: open` (`grep -l "status: open" docs/changes/*/README.md`), y el tablero de cada uno lo da `task-done` (`scripts/board.py`). La prioridad y el responsable viven en el tracker; el README enlaza su issue con `issue:`, y la PR de la última tarea lo cierra.
- El contrato con los guardrails es el comando de verificación de la sección `Commands` (o `Comandos`) de `AGENTS.md`.

### Depuración

| Skill | Qué hace |
|---|---|
| [`debug-root-cause`](skills/debug-root-cause/SKILL.md) | Ante un bug o un test que falla: reproducir, encontrar la causa raíz y arreglarla con un test de regresión que falla sin el arreglo |

`debug-root-cause` y `task-done` se inspiran en [superpowers](https://github.com/obra/superpowers) (MIT): `systematic-debugging` y los scripts `task-start`/`task-done`. Están reescritas para este flujo, no copiadas.

### Code review

Cómo usarlo: **[guía de code review](docs/review/README.md)**. Basado en [agent-skills de Addy Osmani](https://github.com/addyosmani/agent-skills) (MIT, ver [NOTICE.md](NOTICE.md)).

| Skill / agente | Qué hace |
|---|---|
| [`review-prepush`](skills/review-prepush/SKILL.md) | ¿Está la rama lista para push? Verificación, `code-reviewer` y `finding-verifier`. En la rama de una tarea, comprueba además que cada ejemplo de la tarea tiene su test, que los tests en rojo no cambiaron y que sus dependencias están mergeadas; en la del plan, el tablero y que cada ejemplo está en alguna tarea (`task-done --audit`), los choques con decisiones aceptadas y los llamadores fuera del diff. Bloquea solo con Critical confirmados. Incluye el hook `pre-push` |
| [`review-pr`](skills/review-pr/SKILL.md) | Review de una PR según su riesgo: tres personas en paralelo, verificador y revisión de la descripción. Nunca aprueba. Incluye la GitHub Action |
| [`code-review-and-quality`](skills/code-review-and-quality/SKILL.md) | Review de cinco ejes en la sesión actual (Addy) |
| [`review-context`](skills/review-context/SKILL.md) · [`review-report`](skills/review-report/SKILL.md) | Internas: entrada (configuración, verificación, spec) y salida (precisión, severidades, formato) |
| agentes [`code-reviewer`](agents/code-reviewer.md), [`security-auditor`](agents/security-auditor.md), [`test-engineer`](agents/test-engineer.md), [`finding-verifier`](agents/finding-verifier.md) | Las personas que lanzan `review-prepush` y `review-pr` |

Si la rama tiene su carpeta en `docs/changes/`, la review comprueba el código contra su tarea: ejemplos y criterios de aceptación con test, nada fuera de su propósito ni de alcance, la tarea `done` hecha de verdad, y señala las tareas que mezclan propósitos o pasan con claridad de unas 150 líneas. Ni la review ni el hook ni la Action leen issues ni usan `gh` para las tareas.

## Desarrollo

```bash
scripts/check.sh                    # agentes generados al día, frontmatter, manifiestos, task-done y check_decisions (rápido, sin red)
scripts/test-guardrails-python.sh   # smoke test de setup-guardrails-python (requiere uv, jq y red)
tests/evals/triggering/run.py       # suite de activación: ¿cada petición real invoca la skill esperada? (requiere claude y red)
```

- **Al crear, renombrar o cambiar la `description` de una skill**, añade o ajusta sus frases en `tests/evals/triggering/cases.tsv` (una por línea: `<skill>⇥<petición>`, mejor en español) y pasa la suite. Cada caso se ejecuta con `claude -p --plugin-dir .` en un directorio vacío y sin herramientas que escriban; cuenta la primera skill invocada. Opciones: `--only <skill>`, `--runs N` para ver la variación, `--model`, y `--save` para guardar el resultado con fecha en `results/`.

- **Al cambiar `agents/*.md`, o el `allowed-tools` o `argument-hint` de una skill**, ejecuta `scripts/build-agents.py` y haz commit de `adapters/` y de los bloques para rulesync que escribe al final del frontmatter. `check.sh` falla si se te olvida.
- **Cada skill y cada agente declara `kind`, y en `uses`, `delegates` o `related` lo que necesita** (`skill:<nombre>`, `agent:<nombre>`), para atril. Un agente lleva en `uses` las skills que precarga, y no puede haber ciclos en `uses` y `delegates`. `check.sh` lo valida.
- **Al publicar cambios**, sube `version` en `.claude-plugin/plugin.json` y en `.codex-plugin/plugin.json`, que deben coincidir. Claude Code y Codex solo actualizan cuando cambia la versión.
- Los catálogos (`.claude-plugin/marketplace.json` y `.agents/plugins/marketplace.json`) no llevan versión: la toman del plugin.
