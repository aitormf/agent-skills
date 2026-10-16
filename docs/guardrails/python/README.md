# Guardrails para proyectos Python: checklist

Lista de tareas para montar a mano los guardrails deterministas de un repo Python: los que se ejecutan siempre, con o sin agente. Se hace una vez por repo y luego cada proyecto los ajusta a su manera.

- **Ficheros listos para copiar:** [`files/`](files/) (se copian tal cual) y [`snippets/`](snippets/) (se fusionan con lo que ya tengas).
- **El porqué de cada pieza:** `herramientas-arnes.md`, `plan-seguridad-codigo-ia.md` y `guia-arranque-greenfield-brownfield.md`. Cada paso indica la sección.
- **Fuera de este checklist:** `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, ADRs, specs y review. Eso lo hacen las skills, que no dependen del lenguaje.

Cada paso dice qué cambia en un proyecto **brownfield** (uno que ya existe). Si no dice nada, es igual en los dos casos.

---

## 0. El contrato (lo único obligatorio)

Las skills de implementación y review no saben nada de Python. Solo necesitan esto:

- [ ] **Un único comando de verificación**: `scripts/check.sh`. Sale con 0 si todo está bien y con otro código si no.
- [ ] **`AGENTS.md` lo nombra** en su sección `## Comandos` ([`snippets/AGENTS-guardrails.md`](snippets/AGENTS-guardrails.md)).

Todo lo demás es recomendable, pero si un repo cumple estos dos puntos, el resto del arnés funciona.

---

## 1. Base (día 1 · brownfield: primera semana)

Copia los ficheros sin pisar los que ya existan y fusiona a mano los que choquen:

```bash
rsync -a --ignore-existing docs/guardrails/python/files/ /ruta/al/repo/
```

### Proyecto y herramientas

- [ ] **uv**: `uv init --package <nombre>` y `uv python pin 3.13`. *(herramientas §3.1)*
  - Brownfield: con `requirements.txt` → `uv init --bare && uv add -r requirements.txt`; con Poetry o Pipenv → `uvx migrate-to-uv`. Comprueba que los tests pasan igual antes de retirar lo anterior. *(guía B·F3)*
- [ ] Fusiona [`snippets/pyproject.toml`](snippets/pyproject.toml) con tu `pyproject.toml`: ruff (con `S` y `PLE`), mypy, pytest, coverage y el cooldown de uv. *(herramientas §3.2–3.4, seguridad §4.2)*
  - `exclude-newer = "7 days"` necesita uv ≥ 0.9.17.
  - **Hazlo antes de `uv add`.** Si añades el cooldown después, las cotas que escribió uv (`ruff>=<última>`) pueden apuntar a versiones de hace menos de 7 días y la resolución falla. Brownfield: si te pasa, baja esas cotas mínimas o espera unos días.
- [ ] Dependencias de desarrollo: `uv add --dev pytest pytest-cov ruff mypy`.
  - Brownfield, ruff: ejecuta una vez `uv run ruff check --add-noqa`; lo nuevo cumple y lo viejo queda marcado.
  - Brownfield, mypy: `strict` solo en los módulos nuevos, con `ignore_errors` en los heredados (en el snippet hay un ejemplo comentado).
  - Brownfield, cobertura: `fail_under` = la cobertura que tengas hoy. Solo sube, nunca baja.
- [ ] Fusiona [`snippets/gitignore`](snippets/gitignore) con tu `.gitignore` y crea `.env.example` con los nombres de las variables (sin valores).

### El comando de verificación

- [ ] [`scripts/check.sh`](files/scripts/check.sh): quita las líneas de lo que aún no uses (p. ej. import-linter). *(herramientas §4.1)*
  - Brownfield: empieza solo con lo que haya hoy, aunque sea `pytest`, y que salga en verde. Los tests rotos se marcan con `@pytest.mark.skip(reason="…")` y un issue; no dejes la suite en rojo. *(guía B·F1)*
- [ ] `chmod +x scripts/check.sh && ./scripts/check.sh` sale en verde.
- [ ] Brownfield: aplica `ruff format` en **una PR aislada**, solo de formato, y apunta el commit en `.git-blame-ignore-revs`:
  ```bash
  git rev-parse HEAD >> .git-blame-ignore-revs
  git config blame.ignoreRevsFile .git-blame-ignore-revs
  ```

### Pre-commit

- [ ] [`.pre-commit-config.yaml`](files/.pre-commit-config.yaml) *(herramientas §4.2)*:
  ```bash
  uv tool install prek
  prek autoupdate          # sustituye los rev: <versión> por las actuales
  prek install             # instala los hooks pre-commit y commit-msg
  prek run --all-files
  ```
  - Si aún no usas import-linter o Conventional Commits, comenta esos hooks.
  - Brownfield: los hooks solo miran los ficheros modificados, así que lo viejo se va limpiando cuando se toca.

### Secretos

- [ ] gitleaks ya va en pre-commit y en `ci.yml`. *(herramientas §3.7)*
  - Brownfield: escanea el historial completo con `gitleaks git . --redact`. **Rota** cualquier secreto que aparezca (borrarlo del historial no basta) y genera una *baseline* para que solo bloquee los nuevos.

### CI

- [ ] [`.github/workflows/ci.yml`](files/.github/workflows/ci.yml): `uv sync --locked`, `check.sh` y gitleaks. *(herramientas §4.3)*
- [ ] Fija la imagen de gitleaks a una versión concreta en lugar de `latest`.
- [ ] Protección de `main`: PR obligatoria, ≥ 1 aprobación y el check `check` y `secrets` como obligatorios. *(seguridad §4.5.1)*
- [ ] [`.github/dependabot.yml`](files/.github/dependabot.yml): uv y GitHub Actions, con cooldown de 7 días. *(herramientas §3.9)*

**Criterio de salida:** en un clon limpio, `uv sync && ./scripts/check.sh` sale en verde, y CI también.

---

## 2. Agente y cadena de suministro (primera semana · brownfield: semanas 1–2)

### Configuración de Claude Code

- [ ] [`.claude/settings.json`](files/.claude/settings.json): permisos y hooks. *(herramientas §4.4, seguridad §4.4)*
  - `allow`: `uv run`, `check.sh` y git de solo lectura.
  - `ask`: `uv add` y `uv remove`.
  - `deny`: leer `.env` y credenciales, `pip install`, `git push`, `--no-verify`, y editar `.github/`, pre-commit y el propio `settings.json`.
  - Hooks: formatear con ruff tras editar, comprobar paquetes antes de `uv add` y no terminar sin `check.sh` en verde.
  - Necesitan `jq` instalado.
  - Brownfield: al principio, sin permisos de escritura amplios en las zonas críticas.
- [ ] [`.claude/hooks/check-on-stop.sh`](files/.claude/hooks/check-on-stop.sh) (`chmod +x`). Si `check.sh` tarda mucho, cámbialo por una versión rápida (ruff, mypy y `pytest tests/unit`).
- [ ] [`.claude/hooks/check_new_package.py`](files/.claude/hooks/check_new_package.py): bloquea paquetes que no existen en PyPI o que tienen menos de 90 días. Si usas un índice privado, añade una lista de permitidos. *(seguridad §4.4)*
- [ ] Comprueba la sintaxis con `/permissions` y `/hooks` en Claude Code; puede cambiar entre versiones.
- [ ] Los permisos personales van en `.claude/settings.local.json`, fuera de git.
- [ ] Copia el bloque `## Seguridad` de [`snippets/AGENTS-guardrails.md`](snippets/AGENTS-guardrails.md) a `AGENTS.md`. *(seguridad §4.1)*

**Prueba de fuego:** en un clon limpio, pide al agente *"ejecuta los tests"*. Tiene que funcionar a la primera, sin preguntar nada.

### Seguridad en CI

- [ ] [`scripts/check_hidden_unicode.py`](files/scripts/check_hidden_unicode.py): detecta Unicode invisible en ficheros de agentes (*Rules File Backdoor*). Ya está enganchado en pre-commit y en `security.yml`. *(seguridad §4.3)*
- [ ] [`.github/workflows/security.yml`](files/.github/workflows/security.yml) *(seguridad §4.5)*:
  - `dependencies`: pip-audit sobre el lockfile (también se ejecuta a diario).
  - `sast`: Semgrep; en las PRs solo cuenta lo que introduce la PR, así que vale para brownfield.
  - `workflows`: zizmor.
  - `guardrails`: Unicode oculto y `# noqa: S…` sin `security-reviewed: <motivo>`.
- [ ] Añade `dependencies`, `sast`, `workflows` y `guardrails` como checks obligatorios en la protección de `main`.
- [ ] Actions fijadas por SHA (zizmor te lo marcará) y `permissions: contents: read` por defecto.
- [ ] En *Settings → Actions*: **Require approval for all external contributors**.

### Revisión humana obligatoria

- [ ] [`.github/CODEOWNERS`](files/.github/CODEOWNERS): sustituye los `@org/...` y las rutas sensibles (`auth/`, `payments/`…). *(seguridad §4.8)*
- [ ] Protección de `main`: **Require review from Code Owners**.

---

## 3. Cuando haga falta

- [ ] **import-linter**, cuando haya capas o módulos con reglas de dependencia. Los contratos salen de los "Principios innegociables" de `ARCHITECTURE.md`. Descomenta el bloque del snippet, `uv add --dev import-linter` y activa su línea en `check.sh` y su hook. *(herramientas §3.5)*
  - Brownfield: lista las violaciones actuales en `ignore_imports`. Esa lista solo puede encoger.
- [ ] **Conventional Commits + changelog**, antes de la primera versión publicada *(herramientas §3.15)*:
  - el hook de commitizen ya está en pre-commit;
  - [`cliff.toml`](files/cliff.toml) y [`.github/workflows/release.yml`](files/.github/workflows/release.yml);
  - con *squash merge*, valida el título de la PR en CI (p. ej. `amannn/action-semantic-pull-request`).
- [ ] **CodeQL**: gratis en repos públicos; en privados requiere GitHub Advanced Security. Hay un job comentado en `security.yml`. *(seguridad §4.5)*
- [ ] **Revisión de seguridad con IA** en la PR (`anthropics/claude-code-security-review`): nunca obligatoria, solo con PRs de confianza. *(seguridad §4.5.2)*
- [ ] **Devcontainer con firewall** antes de dejar al agente trabajar de forma desatendida. `--dangerously-skip-permissions` solo dentro de él. *(seguridad §4.7)*
- [ ] **Servidores MCP**: antes de añadir uno a `.mcp.json`, rellena la matriz de la *lethal trifecta*. Las credenciales van en variables de entorno. *(seguridad §4.6)*

---

## 4. Continuo

- [ ] **Harness engineering:** cada error repetido del agente se convierte en una regla de ruff, un contrato de import-linter, un test o un hook. Si no se puede, es una línea en "Trampas conocidas" de `AGENTS.md`.
- [ ] Brownfield, **revisión mensual del trinquete**: número de `noqa`, módulos en `ignore_errors`, entradas en `ignore_imports` y cobertura. Solo pueden mejorar.
- [ ] Revisión trimestral de permisos, servidores MCP, CODEOWNERS y excepciones (`noqa`, allowlists de gitleaks).
