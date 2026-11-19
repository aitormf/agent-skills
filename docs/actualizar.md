# Actualizar un proyecto que ya usa el kit

Lo que se instala como plugin (o con `npx skills`) llega al actualizar. Lo que `setup-guardrails-python` copió dentro del proyecto no se toca solo: cada versión que cambie esas copias tiene aquí su sección, con los pasos.

La alternativa a seguir los pasos a mano es volver a ejecutar `setup-guardrails-python` en el proyecto: nunca sobrescribe, detecta lo que falta y propone el diff de cada fichero.

## 0.11.0: verificación en el hook y tareas por objetivo

Qué trae:
- **Verificación en el hook.** En el push de un agente, `harness-review` ejecuta los comandos de `[review] verify` y Semgrep antes de lanzar al revisor, y le pasa los resultados. Una verificación en rojo, o que tarda más de 600 s, bloquea el push sin gastar la review. Con Codex en `read-only`, la review ya no se queda sin tests ni Semgrep. Por qué: [97-verificacion-en-el-hook](changes/97-verificacion-en-el-hook/README.md), D-0061 y D-0062.
- **Tareas por objetivo.** `idea-to-change` y `plan-to-tasks` parten por objetivo, sin el límite de 200 líneas, y el gate ya no avisa por tamaño. La review por tramos de commits es opcional. Por qué: [tareas-por-objetivo](changes/tareas-por-objetivo/README.md), D-0058, D-0059 y D-0060.
- **Hechos de la review en una llamada.** `review_facts.py` reúne los hechos de la rama en una sola llamada y los TODO sin ticket van en un solo Nit (#90). Por qué: [95-hechos-de-la-review](changes/95-hechos-de-la-review/README.md) y D-0057.
- **Arreglo:** el gate y la auditoría funcionan en un worktree (#96).

Si el proyecto no tiene aún la 0.10.0, haz antes su sección.

- [ ] **Plugin:** actualiza `harness@aitormf` (Claude Code y Codex) o ejecuta `npx skills update`. En Codex, vuelve a copiar `adapters/codex/agents/*.toml` a `.codex/agents/`, porque cambian `code-reviewer` y `finding-verifier`.
- [ ] En `.pre-commit-config.yaml`, sube la `rev` del kit a `v0.11.0` (`prek autoupdate`). Es un fichero de control, así que va en una PR propia.
- [ ] **Recomendado:** añade `verify` a `[review]` en `.harness-config.toml`, con los comandos que comprueban el proyecto. Por ejemplo, `verify = ["./scripts/check.sh"]`. Va en la misma PR, porque también es un fichero de control y se lee de la rama base. Sin la clave, el revisor ejecuta la verificación como antes, y Codex en `read-only` no puede hacerlo.
- [ ] Instala `semgrep` donde se hace el push si quieres sus hallazgos. Si no está, el fichero de resultados dice «Semgrep: no disponible» y el push sigue. `[review] semgrep = false` lo desactiva.
- [ ] A partir de ahora, un push de agente con la verificación en rojo se bloquea. Es lo que ya exige `implement` antes de cada PR.
- [ ] **No hace falta:** `[review] max_lines_per_reviewer`, que activa la review por tramos. No tiene valor por defecto y la medición no justifica activarla todavía (ver `docs/review/medicion-review.md`).

## 0.10.0: review cruzada

Qué trae: el hook `harness-review` sustituye al `pre-push` copiado. Corre el gate primero y, si el push es de un agente, lo revisa un revisor de otra familia que el autor (por defecto `claude` y `codex`, el primero instalado que no sea el autor); sin ninguno, el push se bloquea. Por qué: [review-cruzada](changes/8-review-cruzada/README.md), D-0054, D-0055 y D-0056.

Si el proyecto no tiene aún la 0.9.0, haz antes su sección: `harness-review` se instala igual que el gate.

- [ ] **Plugin:** actualiza `harness@aitormf` (Claude Code y Codex) o `npx skills update`: trae las personas revisoras con su regla nueva.
- [ ] En `.pre-commit-config.yaml`, sube la `rev` del kit a `v0.10.0` (`prek autoupdate`) y añade `- id: harness-review` junto a `harness-gate` y `harness-context`. Es un fichero de control: va en una PR propia.
- [ ] Instala el CLI de cada revisor que vayas a usar (`claude`, `codex`): si no queda ninguno de otra familia que el agente, el push del agente se bloquea.
- [ ] Borra el `.git/hooks/pre-push` que copiaste del kit. Si es de otra cosa, déjalo. `prek install` lo sobrescribe: ejecútalo tras añadir el hook.
- [ ] Opcional: `[review]` en `.harness-config.toml` (se lee de la rama base): `reviewers = ["claude", "codex"]` en orden de preferencia y `[review.codex]` con `model` y `effort` (por defecto `gpt-6.1-terra` y `medium`).
- [ ] **Claude Code:** copia `.claude/hooks/deny_skip_hooks.py` de la plantilla y añade su entrada `PreToolUse` a `.claude/settings.json`. **Codex y OpenCode:** copia las reglas de la plantilla (`.codex/rules`, `opencode.json`) que niegan `--no-verify` y `SKIP=`. Frenan las vías normales, no un script que haga el push; la garantía real será el sandbox de #77.
- [ ] Un push de una persona ya no se revisa solo. En el push de un agente se ignoran `SKIP_CLAUDE_REVIEW`, `REVIEW_KIT_COMMAND`, `REVIEW_KIT_ALLOWED_TOOLS`, `REVIEW_KIT_MODEL` y `REVIEW_KIT_TIMEOUT`.

## 0.9.0: el gate del flujo

Qué trae: el gate (`harness-gate`) comprueba la rama de cada tarea o del plan en pre-push y en CI (una tarea por rama, commit en rojo, plan aprobado sin cambios, ficheros de control intactos, aviso de tamaño). En Claude Code, la sesión recibe la tarea y las reglas al empezar y no termina el turno con el gate en rojo. Por qué: [control-del-flujo](changes/control-del-flujo/README.md), D-0052, D-0053 y D-0054.

### 1. Las skills y los agentes

- [ ] **Claude Code (plugin):** `/plugin marketplace update aitormf` y actualiza `harness@aitormf` desde `/plugin`.
- [ ] **Codex (plugin):** actualiza el marketplace y el plugin `harness@aitormf`, y vuelve a copiar `adapters/codex/agents/*.toml` a `.codex/agents/`.
- [ ] **OpenCode y `npx skills`:** `npx skills update` y haz commit de lo que cambie.

### 2. Los hooks del gate (primera PR)

- [ ] En `.pre-commit-config.yaml`, añade `pre-push` a `default_install_hook_types` y el repo del kit con la versión fijada:

  ```yaml
  - repo: https://github.com/aitormf/agent-skills
    rev: v0.9.0
    hooks:
      - id: harness-gate
      - id: harness-context
  ```

- [ ] `prek install` (o `pre-commit install`), para que se instale también el hook pre-push.
- [ ] **Claude Code:** copia `.claude/hooks/harness-gate-on-stop.sh` de `skills/setup-guardrails-python/assets/files/` y añade a tu `.claude/settings.json` las entradas `SessionStart` (harness-context) y `Stop` (harness-gate-on-stop.sh) de la plantilla.
- [ ] Opcional: `.harness-config.toml` en la raíz si la lista de ficheros de control no te vale tal cual (`[gate.control]` con `add` y `remove`).

Mergea esta PR antes de seguir: el job de CI del paso 3 lee la configuración de la rama base, y en una PR cuya base todavía no declara `harness-gate` fallaría.

### 3. CI y GitHub (segunda PR)

- [ ] Copia el job `harness-gate` de la plantilla `skills/setup-guardrails-python/assets/files/.github/workflows/ci.yml` a tu workflow.
- [ ] Sin esto el gate es solo un aviso (`--no-verify` se lo salta). En GitHub: protección de la rama base con el check `harness-gate` obligatorio y aplicada también a admins, "Require review from Code Owners", `CODEOWNERS` sobre los ficheros de control (incluido `.harness-config.toml`) y el agente con una identidad propia que no pueda saltarse la protección ni aprobar.

### Ojo

- Las ramas de tareas que ya estuvieran abiertas pasan por el gate en su siguiente push.
- Las versiones siguientes del kit se adoptan subiendo `rev` (`prek autoupdate`) en una PR propia: `.pre-commit-config.yaml` es un fichero de control.
