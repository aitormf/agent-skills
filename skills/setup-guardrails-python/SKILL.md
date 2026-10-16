---
name: setup-guardrails-python
description: Instala o completa los guardrails deterministas de un repositorio Python (uv, ruff, mypy, pytest, scripts/check.sh, pre-commit, gitleaks, CI, workflow de seguridad, Dependabot, CODEOWNERS y permisos/hooks de Claude Code), en proyectos nuevos o existentes. Úsala cuando pidan preparar el arnés, montar los guardrails, configurar CI o pre-commit, o endurecer la seguridad de un repo Python.
---

# Guardrails para un repositorio Python

Instala los controles que se ejecutan siempre, con o sin agente. Copia ficheros de `assets/` en lugar de escribirlos, y solo usa criterio para fusionar con lo que ya existe y para decidir qué entra con trinquete.

- `assets/files/`: se copian tal cual al repo, respetando las rutas.
- `assets/snippets/`: se **fusionan** con ficheros que el repo ya tiene (`pyproject.toml`, `.gitignore`, `AGENTS.md`).
- `references/piezas.md`: qué protege cada pieza y cuándo compensa. Léelo si el usuario pregunta por qué o duda si incluir algo.

Fuera de alcance: el contenido de `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, ADRs, specs y review. De `AGENTS.md` solo tocas las secciones de `assets/snippets/AGENTS-guardrails.md`.

## Reglas

- **Nunca sobrescribas** un fichero existente. Si choca, fusiona y enseña el diff antes de escribir.
- **Copia los assets literalmente.** No los "mejores" ni los reescribas de memoria. Si algo no encaja, adáptalo después de copiarlo y di qué has cambiado.
- **El cooldown (`[tool.uv] exclude-newer`) va antes de cualquier `uv add`.** Si se añade después, las cotas mínimas que escribe uv pueden ser más recientes que el cooldown y la resolución falla.
- No hagas push, no cambies la configuración de GitHub y no rotes secretos: eso lo hace una persona. Al final, dale la lista.
- Una fase cada vez: aplica, verifica y pregunta antes de pasar a la siguiente.

## Proceso

### 1. Diagnóstico (solo lectura)

Averigua y resume en una tabla:

- **Tipo:** greenfield (sin código o casi) o brownfield.
- **Dependencias:** uv, Poetry, Pipenv, `requirements*.txt`… y versión de uv (`uv --version`; el cooldown relativo necesita ≥ 0.9.17).
- **Tests:** ¿existen?, ¿pasan?, ¿cuánto tardan?, ¿cobertura actual?
- **Lo que ya existe** de cada pieza: `scripts/check.sh` (o `make check`, `just check`), `.pre-commit-config.yaml`, `.github/workflows/`, `dependabot.yml`, `CODEOWNERS`, `.claude/settings.json`, config de ruff y mypy.
- **Paquete:** nombre del paquete en `src/` (para CODEOWNERS e import-linter).
- **Herramientas:** `jq` y `prek` (o `pre-commit`) instalados.

Brownfield: ejecuta `gitleaks git . --redact` si está disponible. Si encuentra secretos, **para** y avisa: hay que rotarlos antes de seguir. Borrarlos del historial no basta.

### 2. Plan

Propón qué fases aplicar y pregunta. Por defecto: fases 1 y 2. La 3 solo para lo que el usuario pida. Pregunta también:

- Type checker: mypy (por defecto), pyright o ty.
- Si ya hay capas: ¿activar import-linter?
- ¿Conventional Commits? Si no, comenta el hook `commitizen`.

### 3. Fase 1: base

1. **uv.** Si no hay proyecto: `uv init --package <nombre>` y `uv python pin 3.13`. Si viene de `requirements.txt`: `uv init --bare` y `uv add -r requirements.txt`. Si viene de Poetry o Pipenv: `uvx migrate-to-uv`. Comprueba que los tests pasan igual que antes.
2. **`pyproject.toml`.** Fusiona `assets/snippets/pyproject.toml`, incluido `[tool.uv]`, **antes** del paso 3. Brownfield:
   - `fail_under` = la cobertura actual.
   - mypy `strict` solo en módulos nuevos, con `[[tool.mypy.overrides]] ignore_errors = true` para los heredados.
3. **Dependencias de desarrollo:** `uv add --dev pytest pytest-cov ruff mypy` (más `import-linter` si se activa).
4. **Copia los ficheros** sin pisar:
   ```bash
   rsync -a --ignore-existing <skill>/assets/files/ <repo>/
   ```
   Para cada fichero que ya existía, fusiona a mano y enseña el diff.
5. **`scripts/check.sh`.** Deja solo las líneas de lo que el repo usa. Brownfield: si hay tests rotos, márcalos con `@pytest.mark.skip(reason="…")`, propón un issue por cada uno, y nunca dejes la suite en rojo.
6. **Brownfield, lint con trinquete:**
   - `uv run ruff check --add-noqa`, y explica que lo nuevo tiene que cumplir.
   - Si `ruff format` cambia muchos ficheros, propón una **PR aislada solo de formato** y añadir el commit a `.git-blame-ignore-revs`.
7. **`.gitignore`.** Fusiona `assets/snippets/gitignore`. Crea `.env.example` con los nombres de las variables que use el código, sin valores.
8. **Pre-commit:** `prek autoupdate` (rellena los `rev`), `prek install` y `prek run --all-files`. Comenta los hooks de lo que no se use.
9. **`AGENTS.md`.** Añade la sección `## Comandos` de `assets/snippets/AGENTS-guardrails.md`, o fusiónala si ya existe. Es el contrato con el resto de skills: el comando de verificación tiene que aparecer ahí.

**Verificación:** `uv sync && ./scripts/check.sh` sale en verde. Enséñale al usuario la salida.

### 4. Fase 2: agente y cadena de suministro

1. `.claude/settings.json` y `.claude/hooks/` ya vienen en `assets/files/`.
   - Si el repo tenía su propio `settings.json`, fusiona `permissions` y `hooks` sin perder lo que ya había.
   - Haz ejecutables los hooks y los scripts: `chmod +x scripts/*.sh .claude/hooks/*`.
   - Brownfield: pregunta si hay zonas críticas en las que no se deban dar permisos de escritura amplios.
2. Añade la sección `## Seguridad` de `assets/snippets/AGENTS-guardrails.md` a `AGENTS.md`.
3. `CODEOWNERS`: sustituye los `@org/...` y las rutas sensibles. Pregunta los equipos; no te los inventes.
4. Comprueba los hooks:
   ```bash
   echo '{"tool_input":{"command":"uv add paquete-que-no-existe-xyz"}}' | uv run python .claude/hooks/check_new_package.py   # debe salir con 2
   uv run python scripts/check_hidden_unicode.py AGENTS.md CLAUDE.md                                                       # debe salir con 0
   ```

### 5. Fase 3: cuando haga falta (solo lo que se pida)

- **import-linter:** descomenta el bloque del snippet. Los contratos salen de "Principios innegociables" de `ARCHITECTURE.md`; si no existe, pregunta las capas. Activa su línea en `check.sh` y su hook. Brownfield: lista las violaciones actuales en `ignore_imports`.
- **Changelog:** `cliff.toml` y `release.yml` ya están copiados. Si hay *squash merge*, valida el título de la PR en CI.
- **CodeQL:** descomenta el job de `security.yml`. Solo en repos públicos o con GitHub Advanced Security.

### 6. Cierre

Resume lo instalado, lo omitido y por qué. Después, dale al usuario **la lista de lo que tiene que hacer a mano**:

- [ ] Protección de `main`: PR obligatoria, ≥ 1 aprobación, *Require review from Code Owners*, sin bypass para administradores.
- [ ] Checks obligatorios: `check`, `secrets`, `dependencies`, `sast`, `workflows`, `guardrails`.
- [ ] *Settings → Actions*: *Require approval for all external contributors*.
- [ ] Fijar la imagen de gitleaks de `ci.yml` y las actions a un SHA.
- [ ] Rotar cualquier secreto encontrado en el diagnóstico.
- [ ] Comprobar `/permissions` y `/hooks` en Claude Code.
- [ ] **Prueba de fuego:** en un clon limpio, pedir al agente *"ejecuta los tests"*. Tiene que funcionar a la primera.
