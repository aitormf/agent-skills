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

### Claude Code

```
/plugin marketplace add git@github.com:aitormf/agent-skills.git
/plugin install harness@aitormf
```

- Como plugin, todo va con namespace: las skills son `/harness:idea-to-spec`, `/harness:sdd-next`… y los agentes, `harness:implement` y `harness:spec-reviewer`.
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

## Skills

### Preparar el proyecto

| Skill | Qué hace |
|---|---|
| [`generate-project-context`](skills/generate-project-context/SKILL.md) | Entrevista para crear AGENTS.md, ARCHITECTURE.md (con principios innegociables), CONTRIBUTING.md, el registro de decisiones (`docs/decisions/`) y SECURITY.md. Sustituye a la constitución de Spec Kit; en proyectos con `docs/adr/`, ofrece moverlos |
| [`setup-guardrails-python`](skills/setup-guardrails-python/SKILL.md) | Instala los guardrails deterministas de un repo Python: check.sh, pre-commit, CI, seguridad, y permisos y hooks de Claude Code |

### Decisiones

| Skill | Qué hace |
|---|---|
| [`record-decision`](skills/record-decision/SKILL.md) | Registra en `docs/decisions/` las decisiones que deben sobrevivir al trabajo en curso: arquitectura, reglas de negocio y enfoques descartados. Las redacta en `proposed`; solo una persona las pasa a `accepted`. Mantiene el índice, gestiona la sustitución y migra `docs/adr/`. `check_decisions.py` valida el directorio |

Los agentes leen solo el índice y abren las decisiones cuyo `affects` cubre lo que van a tocar. Una decisión aceptada no se edita: se escribe otra que la sustituye.

### Spec-Driven Development

Cómo usarlo, paso a paso: **[guía de SDD](docs/sdd/README.md)**.

| Skill / agente | Qué hace |
|---|---|
| [`idea-to-spec`](skills/idea-to-spec/SKILL.md) | De idea a `spec.md` mediante entrevista por rondas |
| [`review-spec`](skills/review-spec/SKILL.md) · agente [`spec-reviewer`](agents/spec-reviewer.md) | Revisa la spec o el plan. Recomienda, nunca aprueba |
| [`apply-review`](skills/apply-review/SKILL.md) | Pregunta las decisiones una a una y aplica los arreglos en bloque, salvo los que la persona excluya |
| [`spec-to-plan`](skills/spec-to-plan/SKILL.md) | De spec aprobada a `plan.md`, con comprobación de principios |
| [`plan-to-tasks`](skills/plan-to-tasks/SKILL.md) | De plan aprobado a `tasks.md`, con la verificación de cada tarea |
| agente [`implement`](agents/implement.md) | Implementa las tareas, marca `[x]` y termina con el comando de verificación en verde |
| [`task-done`](skills/task-done/SKILL.md) | Ejecuta la verificación de una tarea y la marca `[x]` en `tasks.md` solo si pasa. La usa `implement` |
| [`sdd-next`](skills/sdd-next/SKILL.md) | ¿En qué punto está cada trabajo y qué toca ahora? Solo lectura |
| [`sdd-decisions`](skills/sdd-decisions/SKILL.md) | Interna: qué es una decisión de la persona (se pregunta) y qué un supuesto o arreglo con respuesta por defecto (se propone por escrito) |

```
idea-to-spec → [review-spec → apply-review] → persona: status: approved
  → spec-to-plan → [review-spec → apply-review] → persona: status: approved
  → plan-to-tasks → implement → review-prepush → PR → review-pr
```

Convenciones de SDD:

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/` (`spec.md`, `plan.md`, `tasks.md` y las revisiones).
- `spec.md` y `plan.md` llevan `status: draft | approved | obsolete` en el frontmatter. **Solo una persona pone `approved`.** Las skills avisan y preguntan si se intenta avanzar sin aprobación.
- No hay backlog central. La gestión del trabajo (prioridad, responsable, hecho) vive en el tracker; la spec puede enlazarlo con `issue:`.
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
| [`review-prepush`](skills/review-prepush/SKILL.md) | ¿Está la rama lista para push? Verificación, `code-reviewer` y `finding-verifier`. Bloquea solo con Critical confirmados. Incluye el hook `pre-push` |
| [`review-pr`](skills/review-pr/SKILL.md) | Review de una PR según su riesgo: tres personas en paralelo, verificador y revisión de la descripción. Nunca aprueba. Incluye la GitHub Action |
| [`code-review-and-quality`](skills/code-review-and-quality/SKILL.md) | Review de cinco ejes en la sesión actual (Addy) |
| [`review-context`](skills/review-context/SKILL.md) · [`review-report`](skills/review-report/SKILL.md) | Internas: entrada (configuración, verificación, spec) y salida (precisión, severidades, formato) |
| agentes [`code-reviewer`](agents/code-reviewer.md), [`security-auditor`](agents/security-auditor.md), [`test-engineer`](agents/test-engineer.md), [`finding-verifier`](agents/finding-verifier.md) | Las personas que lanzan `review-prepush` y `review-pr` |

Si el cambio pertenece a una spec de `docs/specs/`, la review comprueba el código contra ella: criterios de aceptación con test, nada fuera de alcance, tareas `[x]` hechas de verdad.

## Desarrollo

```bash
scripts/check.sh                    # agentes generados al día, frontmatter, manifiestos, task-done y check_decisions (rápido, sin red)
scripts/test-guardrails-python.sh   # smoke test de setup-guardrails-python (requiere uv, jq y red)
tests/evals/triggering/run.py       # suite de activación: ¿cada petición real invoca la skill esperada? (requiere claude y red)
```

- **Al crear, renombrar o cambiar la `description` de una skill**, añade o ajusta sus frases en `tests/evals/triggering/cases.tsv` (una por línea: `<skill>⇥<petición>`, mejor en español) y pasa la suite. Cada caso se ejecuta con `claude -p --plugin-dir .` en un directorio vacío y sin herramientas que escriban; cuenta la primera skill invocada. Opciones: `--only <skill>`, `--runs N` para ver la variación, `--model`, y `--save` para guardar el resultado con fecha en `results/`.

- **Al cambiar `agents/*.md`**, ejecuta `scripts/build-agents.py` y haz commit de `adapters/`. `check.sh` falla si se te olvida.
- **Al publicar cambios**, sube `version` en `.claude-plugin/plugin.json` y en `.codex-plugin/plugin.json`, que deben coincidir. Claude Code y Codex solo actualizan cuando cambia la versión.
- Los catálogos (`.claude-plugin/marketplace.json` y `.agents/plugins/marketplace.json`) no llevan versión: la toman del plugin.
