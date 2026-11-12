# Actualizar un proyecto que ya usa el kit

Lo que se instala como plugin (o con `npx skills`) llega al actualizar. Lo que `setup-guardrails-python` copió dentro del proyecto no se toca solo: cada versión que cambie esas copias tiene aquí su sección, con los pasos.

La alternativa a seguir los pasos a mano es volver a ejecutar `setup-guardrails-python` en el proyecto: nunca sobrescribe, detecta lo que falta y propone el diff de cada fichero.

## 0.9.0: el gate del flujo

Qué trae: el gate (`kit-gate`) comprueba la rama de cada tarea o del plan en pre-push y en CI (una tarea por rama, commit en rojo, plan aprobado sin cambios, ficheros de control intactos, aviso de tamaño). En Claude Code, la sesión recibe la tarea y las reglas al empezar y no termina el turno con el gate en rojo. Por qué: [control-del-flujo](changes/control-del-flujo/README.md), D-0052, D-0053 y D-0054.

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
      - id: kit-gate
      - id: kit-context
  ```

- [ ] `prek install` (o `pre-commit install`), para que se instale también el hook pre-push.
- [ ] **Claude Code:** copia `.claude/hooks/kit-gate-on-stop.sh` de `skills/setup-guardrails-python/assets/files/` y añade a tu `.claude/settings.json` las entradas `SessionStart` (kit-context) y `Stop` (kit-gate-on-stop.sh) de la plantilla.
- [ ] Opcional: `.harness-config.toml` en la raíz si la lista de ficheros de control no te vale tal cual (`[gate.control]` con `add` y `remove`).

Mergea esta PR antes de seguir: el job de CI del paso 3 lee la configuración de la rama base, y en una PR cuya base todavía no declara `kit-gate` fallaría.

### 3. CI y GitHub (segunda PR)

- [ ] Copia el job `kit-gate` de la plantilla `skills/setup-guardrails-python/assets/files/.github/workflows/ci.yml` a tu workflow.
- [ ] Sin esto el gate es solo un aviso (`--no-verify` se lo salta). En GitHub: protección de la rama base con el check `kit-gate` obligatorio y aplicada también a admins, "Require review from Code Owners", `CODEOWNERS` sobre los ficheros de control (incluido `.harness-config.toml`) y el agente con una identidad propia que no pueda saltarse la protección ni aprobar.

### Ojo

- Las ramas de tareas que ya estuvieran abiertas pasan por el gate en su siguiente push.
- Las versiones siguientes del kit se adoptan subiendo `rev` (`prek autoupdate`) en una PR propia: `.pre-commit-config.yaml` es un fichero de control.
