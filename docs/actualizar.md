# Actualizar un proyecto que ya usa el kit

Lo que se instala como plugin (o con `npx skills`) llega al actualizar. Lo que `setup-guardrails-python` copió dentro del proyecto no se toca solo: cada versión que cambie esas copias tiene aquí su sección, con los pasos.

La alternativa a seguir los pasos a mano es volver a ejecutar `setup-guardrails-python` en el proyecto: nunca sobrescribe, detecta lo que falta y propone el diff de cada fichero.

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
