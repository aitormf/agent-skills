# Herramientas del arnés (harness) para un proyecto Python con agentes de IA

**Complemento de `informe-proyecto-python-con-ia-2026.md` · octubre de 2026**

> El **arnés** es todo lo que rodea al agente para que trabaje con poca supervisión y sin repetir errores: el contexto que lee y, sobre todo, **las comprobaciones automáticas que le dicen si lo ha hecho bien** (Hashimoto, OpenAI, Böckeler). Este documento recoge las herramientas comentadas, para qué sirve cada una, dónde encaja y cómo configurarla.
>
> Principio rector: **lo que se puede comprobar con una herramienta no se deja en Markdown.** `AGENTS.md` y `ARCHITECTURE.md` explican el porqué; las herramientas hacen cumplir la regla.

---

## 1. Las capas del arnés

Cada comprobación debería ejecutarse lo antes posible, en el punto más barato:

```text
 Segundos ───────────────────────────────────────────────────────────────► Días
 ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
 │ Hooks del    │  │ check.sh     │  │ pre-commit   │  │ CI en la │  │ Periódico    │
 │ agente       │→ │ (el agente   │→ │ (prek)       │→ │ PR       │→ │ Dependabot,  │
 │ tras editar  │  │ se verifica) │  │ al commitear │  │          │  │ revisión docs│
 └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘  └──────────────┘
  Solo Claude Code   Cualquiera        Cualquiera        La última     Mantenimiento
                                                         palabra
```

- **Universal** (vale para cualquier agente y para personas): `scripts/check.sh`, pre-commit y CI. Es la base; impleméntala primero.
- **Específico del agente** (hooks y permisos de `.claude/settings.json`): acelera el bucle de Claude Code, pero **no sustituye** a lo universal. Codex, Cursor u otra persona no lo ejecutan.
- **CI es la autoridad final:** los hooks locales se pueden saltar; CI no.

---

## 2. Resumen de herramientas

| Herramienta | Para qué | Capa | ¿Imprescindible? |
|---|---|---|---|
| **uv** | Python, entornos, dependencias y lockfile | Base de todo | Sí |
| **ruff** | Lint + formato (+ reglas de seguridad `S`, que reimplementan **bandit**) | Hook, pre-commit, check, CI | Sí |
| **bandit** (directo) | Informes de seguridad con severidad y confianza | CI | Solo si lo exige una auditoría (ver §3.2.1) |
| **mypy** / **pyright** / **ty** | Comprobación de tipos | Pre-commit, check, CI | Sí (una de ellas) |
| **pytest** + **pytest-cov** | Tests y cobertura | check, CI | Sí |
| **import-linter** | Reglas de arquitectura (qué capa importa qué) | Pre-commit, check, CI | Si hay capas o módulos |
| **prek** / **pre-commit** | Ejecutar comprobaciones al hacer commit | Pre-commit | Sí |
| **gitleaks** | Detectar secretos | Pre-commit, CI | Sí |
| **GitHub Actions** (u otro CI) | Ejecutar todo en cada PR | CI | Sí |
| **Dependabot** / **Renovate** | Actualizar dependencias y avisar de vulnerabilidades | Periódico | Muy recomendable |
| **Hooks de Claude Code** | Formatear tras editar, verificar antes de terminar, bloquear acciones | Agente | Recomendable |
| **Permisos y sandbox** de Claude Code | Limitar qué puede hacer el agente | Agente | Recomendable |
| **Skills** y **subagentes** | Flujos repetibles y revisión con contexto limpio | Agente | Opcional |
| **MCP** (`.mcp.json`) | Conectar el agente a sistemas externos | Agente | Opcional (con cuidado) |
| **GitHub Spec Kit** | Flujo formal spec → plan → tareas | Proceso | Opcional |
| **Conventional Commits** + **commitizen** (validación) + **git-cliff** (generación) | Changelog y versión automáticos a partir de los commits | Pre-commit (`commit-msg`), CI, release | Muy recomendable |
| **Semgrep**, **pip-audit**/**osv-scanner**, **zizmor**, cooldown de uv, detector de Unicode oculto, hook anti-paquetes alucinados | Seguridad del código generado y de la cadena de suministro | Pre-commit, agente, CI | Sí (ver `plan-seguridad-codigo-ia.md`) |

---

## 3. Herramientas una a una

### 3.1 uv: gestor de proyecto

Gestiona versiones de Python, el entorno virtual, las dependencias y el lockfile (`uv.lock`). Sustituye a pip, pip-tools, pyenv, virtualenv y poetry.

**Por qué importa en el arnés:** con `uv run <herramienta>` cualquiera (persona, agente o CI) ejecuta exactamente las mismas versiones sin activar entornos. Un agente no se equivoca de intérprete.

```bash
uv sync --locked      # en CI: falla si uv.lock no corresponde con pyproject.toml
uv run pytest
uv add --dev ruff     # nunca pip install
```

### 3.2 ruff: lint y formato

Linter y formateador muy rápido (Astral). Sustituye a flake8, isort, black, pyupgrade y, con las reglas `S`, a bandit.

> **Código:** [`snippets/pyproject.toml`](../../skills/setup-guardrails-python/assets/snippets/pyproject.toml), sección `[tool.ruff]`. Es la fuente única: la skill `setup-guardrails-python` lo instala.


```bash
uv run ruff format .          # formatear
uv run ruff check --fix .     # lint con autocorrección
uv run ruff format --check .  # en CI: solo comprobar
```

Truco de arnés: si el agente repite un mal patrón que ruff puede detectar (p. ej. `print` en lugar de logging → regla `T20`), actívala en lugar de escribirlo en `AGENTS.md`.

#### 3.2.1 ¿Y bandit?

Ya está en el arnés, dentro de ruff: las reglas `S` (flake8-bandit) reimplementan la mayoría de los checks de bandit con el mismo número (`S608` ↔ `B608`). Se ejecutan en el hook de formato del agente, en pre-commit, en `check.sh` y en CI, en milisegundos y sin instalar nada más.

| Regla de ruff | bandit | Detecta |
|---|---|---|
| `S101` | B101 | `assert` en código de producción |
| `S105`–`S107` | B105–B107 | Contraseñas escritas en el código |
| `S301` | B301 | `pickle` con datos externos |
| `S311` | B311 | `random` usado para seguridad |
| `S324` | B324 | Hashes débiles (MD5, SHA1) |
| `S501` | B501 | `verify=False` en peticiones |
| `S602`, `S605` | B602, B605 | `shell=True`, `os.system` |
| `S608` | B608 | SQL construido con strings |

**Recomendación: no ejecutar bandit por separado.** Duplicaría los avisos de ruff `S` y de Semgrep, y es más lento. Lo que se escapa al análisis patrón a patrón lo cubren Semgrep y CodeQL (ver `plan-seguridad-codigo-ia.md`, §4.5).

Solo tiene sentido ejecutarlo directamente si:
- Una auditoría o norma de cumplimiento exige un informe de bandit o sus niveles de severidad y confianza.
- Necesitáis una regla que ruff todavía no implementa (comparad la lista de plugins de bandit con las reglas `S` de ruff).
- Preferís su línea base en JSON (`-b baseline.json`) al trinquete de `ruff check --add-noqa`.

En ese caso, solo en CI (en el job `sast` de `security.yml`), para no duplicar en local:

```toml
# pyproject.toml
[tool.bandit]
exclude_dirs = ["tests"]
```

```yaml
- name: Bandit
  run: uvx bandit -c pyproject.toml -r src -ll -ii   # severidad y confianza media o superior
```

### 3.3 Comprobación de tipos: mypy, pyright o ty

Los tipos son documentación que el agente puede **verificar**. Elegid uno:

| Herramienta | Pros | Contras |
|---|---|---|
| **mypy** | El estándar de facto, modo `--strict` maduro, plugins (Pydantic, Django) | Más lento |
| **pyright** | Rápido, muy preciso, es el motor de Pylance en VS Code | Requiere Node (o el paquete `pyright` de PyPI, que lo descarga) |
| **ty** (Astral) | 10-100× más rápido, mismo ecosistema que uv y ruff | **Beta** (0.0.x) en octubre de 2026; el formato de sus diagnósticos puede cambiar |

Recomendación: **mypy --strict** si queréis estabilidad; ty si aceptáis una herramienta en beta y priorizáis velocidad.

> **Código:** [`snippets/pyproject.toml`](../../skills/setup-guardrails-python/assets/snippets/pyproject.toml), sección `[tool.mypy]`. Es la fuente única: la skill `setup-guardrails-python` lo instala.

### 3.4 pytest + pytest-cov: tests y cobertura

Los tests son **el oráculo del agente**: la comprobación que le dice si ha terminado. Es la práctica que más rendimiento aporta, según la documentación de Anthropic.

> **Código:** [`snippets/pyproject.toml`](../../skills/setup-guardrails-python/assets/snippets/pyproject.toml), secciones `[tool.pytest.ini_options]` y `[tool.coverage.*]`. Es la fuente única: la skill `setup-guardrails-python` lo instala.

```bash
uv run pytest --cov            # todo
uv run pytest tests/unit -x    # rápido, se para al primer fallo
```

Consejos:
- Separad `tests/unit/` (rápidos, sin E/S) de `tests/integration/`. El agente debe poder lanzar los rápidos en cada iteración.
- Kent Beck avisa: el agente puede **borrar o debilitar tests** para que pasen. Revisad los diffs de `tests/` en las PRs; podéis exigir CODEOWNERS en esa carpeta.

### 3.5 import-linter: reglas de arquitectura

Comprueba que los imports internos del proyecto respetan las capas definidas. Convierte "domain no importa de infra" (de `ARCHITECTURE.md`) en una regla que CI hace cumplir. Detecta también imports **indirectos**.

> **Código:** [`snippets/pyproject.toml`](../../skills/setup-guardrails-python/assets/snippets/pyproject.toml), bloque comentado `[tool.importlinter]` con un contrato `layers` y uno `forbidden`. Es la fuente única: la skill `setup-guardrails-python` lo instala.

```bash
uv add --dev import-linter
uv run lint-imports
```

Tipos de contrato: `layers` (capas ordenadas), `forbidden` (prohibiciones, también de librerías externas) e `independence` (módulos que no se importan entre sí).

No compensa en scripts pequeños o librerías con dos módulos.

### 3.6 prek / pre-commit: comprobaciones al hacer commit

**pre-commit** es el estándar para ejecutar hooks de git definidos en `.pre-commit-config.yaml`. **prek** es una reimplementación en Rust, **compatible con el mismo fichero**, más rápida, sin depender de Python y que usa uv para los entornos. Elegid uno; la configuración es la misma.

```bash
uv tool install prek     # o: uv tool install pre-commit
prek install             # instala el hook en .git/hooks
prek run --all-files     # ejecutar sobre todo el repo
prek autoupdate          # actualizar los rev de los hooks
```

Qué poner en pre-commit: comprobaciones **rápidas** (formato, lint, tipos, imports, secretos, higiene de ficheros). Los tests completos van en `check.sh` y CI (o en la etapa `pre-push` si son rápidos).

Configuración completa en la sección 4.2.

### 3.7 gitleaks: detección de secretos

Escanea cambios e historial buscando claves API, tokens y credenciales. Imprescindible cuando un agente puede leer `.env` o copiar un token en un test.

- En **pre-commit**: bloquea el commit antes de que el secreto llegue al historial.
- En **CI**: escanea el historial completo de la PR (los hooks locales se pueden saltar).
- Falsos positivos: `# gitleaks:allow` al final de la línea, o una lista de permitidos en `.gitleaks.toml` **con un comentario que explique por qué**.
- Usad `--redact` para no imprimir el secreto en los logs.

Instrucción para el agente (en `AGENTS.md`): *"Si gitleaks bloquea un commit, elimina el secreto y sustitúyelo por una variable de entorno. Nunca uses `--no-verify`."*

Alternativa más exhaustiva (y más lenta): **TruffleHog**, que además detecta por entropía y puede verificar si el secreto está activo.

### 3.8 CI: GitHub Actions

La **autoridad final**: ejecuta en cada PR lo mismo que `check.sh` y el escaneo de secretos. Con protección de rama, nada entra en `main` sin CI en verde. Configuración en la sección 4.3.

### 3.9 Dependabot / Renovate: dependencias

Abren PRs para actualizar dependencias y avisan de vulnerabilidades conocidas. Ambos soportan `uv.lock`. Como las PRs pasan por CI, el arnés valida automáticamente cada actualización.

> **Código:** [`files/.github/dependabot.yml`](../../skills/setup-guardrails-python/assets/files/.github/dependabot.yml) (con `cooldown` de 7 días). Es la fuente única: la skill `setup-guardrails-python` lo instala.

Renovate es más configurable (agrupaciones, automerge de parches); Dependabot viene integrado en GitHub sin instalar nada.

### 3.10 Hooks de Claude Code

Scripts que Claude Code ejecuta en momentos concretos de su ciclo, configurados en `.claude/settings.json` (versionado). A diferencia de `CLAUDE.md`, que es una sugerencia, **los hooks siempre se ejecutan**. Los más útiles:

| Evento | Uso |
|---|---|
| `PostToolUse` (tras `Edit`/`Write`) | Formatear con ruff el fichero que acaba de editar |
| `PreToolUse` | Bloquear acciones: escribir en `.env`, tocar migraciones aplicadas, `git push --force` |
| `Stop` | Ejecutar `check.sh` y **no dejar que termine** hasta que esté en verde |

Configuración en la sección 4.4. Recordad: solo los ejecuta Claude Code. Lo esencial tiene que estar también en pre-commit y CI.

### 3.11 Permisos y sandbox de Claude Code

- **Permisos** (`permissions.allow` / `deny` en `.claude/settings.json`): permitid lo seguro y repetitivo (`uv run`, `git status`, `git diff`) y denegad lo peligroso (leer `.env`, `git commit --no-verify`). Boris Cherny comparte los permisos con su equipo en este fichero en lugar de usar `--dangerously-skip-permissions`.
- **Sandbox** (`/sandbox`): aislamiento del sistema de ficheros y de la red a nivel de sistema operativo, para que el agente trabaje con libertad dentro de unos límites.
- Diseñad los permisos pensando en la **lethal trifecta** de Simon Willison: no combinéis acceso a datos privados, contenido no fiable y salida al exterior.

### 3.12 Skills y subagentes

- **Skills** (`.claude/skills/<nombre>/SKILL.md`, estándar abierto Agent Skills): flujos repetibles que se cargan solo cuando hacen falta. Ejemplos de arnés: `release` (cómo publicar una versión), `new-adr` (crear un ADR con la plantilla), `add-endpoint`.
- **Subagentes** (`.claude/agents/<nombre>.md`): asistentes con contexto propio. El más útil para el arnés es un **revisor** que analiza el diff con contexto limpio contra la spec y `ARCHITECTURE.md` (patrón escritor/revisor).

```markdown
<!-- .claude/agents/reviewer.md -->
---
name: reviewer
description: Revisa el diff actual contra la spec y los principios de docs/ARCHITECTURE.md
tools: Read, Grep, Glob, Bash
---
Revisa el diff (`git diff main...HEAD`). Comprueba: cada requisito de la spec está
implementado y testeado, no se incumple ningún principio innegociable, ningún test
se ha borrado o debilitado. Informa solo de fallos de corrección o de requisitos,
no de preferencias de estilo.
```

### 3.13 MCP (`.mcp.json`)

Conecta el agente con sistemas externos (issue tracker, base de datos, documentación). Se versiona `.mcp.json` para que el equipo comparta los mismos servidores, pero **las credenciales van en variables de entorno**, nunca en el fichero. Cada servidor amplía lo que el agente puede leer y hacer: añadid solo los necesarios y revisad la lethal trifecta.

### 3.14 GitHub Spec Kit (opcional)

Flujo formal de desarrollo guiado por especificaciones: `/speckit.specify` → `plan` → `tasks` → `implement`, con `/speckit.analyze` para comprobar coherencia. Útil para funcionalidades grandes o equipos que quieran un proceso estricto. Si no lo usáis, `docs/specs/`, `docs/plans/` y la sección de principios de `ARCHITECTURE.md` cubren lo esencial (ver la sección 3.1 del informe).

### 3.15 Changelog automático: Conventional Commits + git-cliff

El changelog se **genera** a partir del historial de git; nadie (ni persona ni agente) edita `CHANGELOG.md` a mano. Para que funcione, los mensajes de commit tienen que seguir un formato que una máquina pueda leer: **Conventional Commits**.

```text
feat(api): añadir paginación a /pedidos        → "Añadido"     · sube MINOR
fix: no duplicar pedidos al reintentar         → "Corregido"   · sube PATCH
feat!: eliminar el endpoint /v1/legacy         → cambio incompatible · sube MAJOR
chore(deps): bump httpx de 0.27 a 0.28         → no aparece en el changelog
```

**Por qué importa en el arnés:** los agentes escriben muchos commits. Sin una regla que se compruebe, el formato degenera ("update files", "fix stuff") y el changelog queda inservible. Con la regla en un hook, el commit se rechaza y el agente lo corrige solo, igual que con ruff. Además, el tipo de commit determina la siguiente versión (SemVer), así que la release deja de ser una decisión manual.

Son dos piezas:

| Pieza | Herramienta | Dónde |
|---|---|---|
| **Validar** el mensaje de cada commit | **commitizen** (hook `commit-msg`) | pre-commit; en CI, el título de la PR si hacéis *squash merge* |
| **Generar** changelog, notas de release y siguiente versión | **git-cliff** | Skill `release` o a mano; CI al publicar el tag |

**1. Validar en `commit-msg`.** Se añade al `.pre-commit-config.yaml` (sección 4.2). Ojo: el hook se instala en otra etapa de git, por eso hace falta `default_install_hook_types`:

> **Código:** [`files/.pre-commit-config.yaml`](../../skills/setup-guardrails-python/assets/files/.pre-commit-config.yaml), hook `commitizen` y `default_install_hook_types`. Es la fuente única: la skill `setup-guardrails-python` lo instala.

```bash
prek install    # vuelve a ejecutarlo para instalar también el hook commit-msg
```

Si hacéis **squash merge**, el commit que llega a `main` es el **título de la PR**, no los commits locales. Validadlo en CI (p. ej. con `amannn/action-semantic-pull-request`) y configurad Dependabot para que use el formato:

> **Código:** [`files/.github/dependabot.yml`](../../skills/setup-guardrails-python/assets/files/.github/dependabot.yml), `commit-message` en cada entrada. Es la fuente única: la skill `setup-guardrails-python` lo instala.

**2. Generar con git-cliff.** Se distribuye también en PyPI, así que funciona con `uvx` sin instalar nada más. `git cliff --init` crea un `cliff.toml` con una plantilla por defecto; adaptad la sección `[git]`:

> **Código:** [`files/cliff.toml`](../../skills/setup-guardrails-python/assets/files/cliff.toml). Es la fuente única: la skill `setup-guardrails-python` lo instala.

```bash
uvx git-cliff --unreleased                 # ver qué entraría en la próxima versión
uvx git-cliff --bumped-version             # siguiente versión según los commits
uvx git-cliff --bump -o CHANGELOG.md       # regenerar el changelog con esa versión
```

Flujo de release (buen candidato para la skill `release` de la sección 3.12):

```bash
VERSION=$(uvx git-cliff --bumped-version)          # p. ej. v1.4.0
uv version "${VERSION#v}"                          # actualiza pyproject.toml
uvx git-cliff --bump -o CHANGELOG.md
git commit -am "chore(release): $VERSION"
git tag "$VERSION"                                 # el push lo hace una persona
```

Y en CI, al publicar el tag, las notas de la release salen del mismo sitio:

> **Código:** [`files/.github/workflows/release.yml`](../../skills/setup-guardrails-python/assets/files/.github/workflows/release.yml). Es la fuente única: la skill `setup-guardrails-python` lo instala.

Las notas pasan por fichero y no por `${{ steps.*.outputs }}` dentro de `run:`, para evitar inyección de código desde los mensajes de commit (es lo que señalaría zizmor).

Instrucción para el agente (en `AGENTS.md`): *"Escribe los commits en formato Conventional Commits (`feat:`, `fix:`, `refactor:`…; `!` para cambios incompatibles). No edites `CHANGELOG.md`: lo genera git-cliff."*

Alternativas:

| Herramienta | Cuándo elegirla |
|---|---|
| **commitizen** solo (`cz bump --changelog`) | Queréis una sola herramienta en Python que valide, suba la versión y genere el changelog; plantillas menos flexibles que git-cliff |
| **release-please** (Google) / **python-semantic-release** | Release totalmente automática: abren una PR de release o publican la versión desde CI al hacer merge en `main` |
| **towncrier** | Los commits no son fiables o queréis textos escritos para usuarios: cada PR añade un fragmento en `changes/` (comprobable en CI); lo usan pip y pytest |

Recomendación: **commitizen (solo validación) + git-cliff**. Si más adelante queréis que las releases salgan solas, release-please reutiliza los mismos Conventional Commits sin cambiar nada más.

---

## 4. Cómo se integra todo

### 4.1 `scripts/check.sh`: el único comando de verificación

Es el corazón del arnés: lo ejecutan el agente, las personas, el hook `Stop` y CI. **Una sola definición de "está bien".**

> **Código:** [`files/scripts/check.sh`](../../skills/setup-guardrails-python/assets/files/scripts/check.sh). Es la fuente única: la skill `setup-guardrails-python` lo instala.

```bash
chmod +x scripts/check.sh
```

Si preferís, lo mismo como tarea de un `Makefile` o `justfile`; lo importante es que sea **un comando** y que esté en `AGENTS.md` y `CONTRIBUTING.md`.

### 4.2 `.pre-commit-config.yaml` (sirve para prek y pre-commit)

> **Código:** [`files/.pre-commit-config.yaml`](../../skills/setup-guardrails-python/assets/files/.pre-commit-config.yaml) (incluye también los hooks de seguridad de `plan-seguridad-codigo-ia.md` §4.3). Es la fuente única: la skill `setup-guardrails-python` lo instala.

mypy e import-linter van como hooks `local` con `uv run` para usar exactamente las versiones de `uv.lock` (y, en el caso de mypy, ver las dependencias del proyecto).

### 4.3 `.github/workflows/ci.yml`

> **Código:** [`files/.github/workflows/ci.yml`](../../skills/setup-guardrails-python/assets/files/.github/workflows/ci.yml). Es la fuente única: la skill `setup-guardrails-python` lo instala.

Notas:
- `uv sync --locked` falla si alguien cambió `pyproject.toml` sin actualizar `uv.lock`.
- La acción oficial `gitleaks/gitleaks-action` requiere licencia (gratuita) para repositorios de organizaciones; ejecutar la imagen Docker evita ese paso. Fijad una versión concreta en lugar de `latest` en producción.
- Activad la **protección de rama** de `main`: PR obligatoria, CI en verde y al menos una aprobación.

### 4.4 `.claude/settings.json`

> **Código:** [`files/.claude/settings.json`](../../skills/setup-guardrails-python/assets/files/.claude/settings.json) (ya fusionado con los permisos y el hook de paquetes de `plan-seguridad-codigo-ia.md` §4.4). Es la fuente única: la skill `setup-guardrails-python` lo instala.

> **Código:** [`files/.claude/hooks/check-on-stop.sh`](../../skills/setup-guardrails-python/assets/files/.claude/hooks/check-on-stop.sh). Es la fuente única: la skill `setup-guardrails-python` lo instala.

Notas:
- El hook `PostToolUse` necesita `jq` instalado.
- El hook `Stop` puede ser lento si los tests tardan; en ese caso ejecutad solo los rápidos (`ruff`, `mypy`, `pytest tests/unit`).
- La sintaxis exacta de reglas y eventos puede cambiar entre versiones; comprobadla con `/hooks` y `/permissions` o en la documentación oficial.
- Los permisos personales (más amplios) van en `.claude/settings.local.json`, fuera de git.

---

## 5. Orden de adopción recomendado

1. **Día 1:** uv + ruff + pytest + `scripts/check.sh` + CI. Sin esto no hay arnés.
2. **Día 1:** pre-commit/prek con ruff y gitleaks; `.gitignore` y `.env.example`.
3. **Primera semana:** tipos (mypy --strict desde el principio es mucho más fácil que añadirlo después) y umbral de cobertura.
4. **Cuando aparezcan las capas:** import-linter.
5. **Cuando el equipo use Claude Code a diario:** permisos compartidos, hook de formato, hook `Stop`, subagente revisor.
6. **Desde la primera dependencia:** Dependabot o Renovate.
7. **Antes de la primera versión publicada:** Conventional Commits validados con commitizen y changelog con git-cliff. Cuanto antes, más historial aprovechable.
8. **Continuo, harness engineering:** cada error repetido del agente → ¿lo puede detectar una de estas herramientas? Si sí, añadid la regla. Si no, una línea en `AGENTS.md`.

---

## 6. Llevar el arnés a otros lenguajes

La mayor parte del arnés no depende del lenguaje. Lo específico de Python es la **capa de lenguaje** (paquetes, lint, tipos, tests, arquitectura, reglas de seguridad y auditoría de dependencias), y cada ecosistema tiene su equivalente.

### 6.1 Herramientas que sirven para cualquier proyecto

| Herramienta | Función | Alcance |
|---|---|---|
| prek / pre-commit | Hooks al hacer commit | Cualquier lenguaje |
| gitleaks | Secretos | Cualquier fichero + historial git |
| GitHub Actions / CI | Comprobaciones en cada PR | — |
| Dependabot / Renovate | Actualizar dependencias | npm, Go, Cargo, Maven, Docker, Actions… |
| Semgrep | SAST por patrones | 30+ lenguajes |
| CodeQL | SAST de flujo de datos | JS/TS, Go, Java/Kotlin, C#, C/C++, Ruby, Swift, Rust… |
| osv-scanner | Dependencias vulnerables (CVE) | Lockfiles de npm, Go, Cargo, Maven… |
| zizmor | Seguridad de workflows de CI | GitHub Actions |
| `claude-code-security-review` | Revisión de seguridad con IA (no bloquea) | Cualquier lenguaje |
| Hooks de Claude Code | Formatear, verificar, bloquear acciones | Del agente |
| Permisos y sandbox | Limitar al agente | Del agente |
| Skills y subagentes | Flujos bajo demanda, revisión limpia | Del agente |
| MCP (`.mcp.json`) | Conectar sistemas externos | Del agente |
| `AGENTS.md` | Instrucciones para agentes | Documentación |
| `ARCHITECTURE.md` + ADRs | Estructura, principios y decisiones | Documentación |
| `CONTRIBUTING.md`, plantilla de PR, `SECURITY.md` | Proceso y política de seguridad | Documentación |
| `CODEOWNERS` | Aprobación obligatoria por rutas | GitHub/GitLab |
| GitHub Spec Kit | Spec → plan → tareas | Proceso |
| Conventional Commits + commitizen + git-cliff | Validar commits y generar changelog y versión | Cualquier repo git |
| `check_hidden_unicode.py` | Unicode oculto en ficheros de agentes | Cualquier fichero (script en Python) |

### 6.2 Equivalencias de la capa de lenguaje

| Función | Python | JS/TS | Go | Rust | Java/Kotlin |
|---|---|---|---|---|---|
| Paquetes y lockfile | uv | pnpm / npm | go modules | cargo | Gradle / Maven |
| Lint y formato | ruff | Biome, o ESLint + Prettier | golangci-lint + gofmt | clippy + rustfmt | Checkstyle / Spotless / ktlint |
| Tipos | mypy / pyright / ty | `tsc --noEmit` | El compilador | El compilador | El compilador |
| Tests y cobertura | pytest + coverage | Vitest / Jest | `go test -cover` | `cargo test` + cargo-llvm-cov | JUnit + JaCoCo |
| Reglas de arquitectura | import-linter | dependency-cruiser | depguard (en golangci-lint) | Visibilidad del lenguaje, crates separados, cargo-deny | ArchUnit |
| Reglas de seguridad | ruff `S` / bandit | Plugins de seguridad de ESLint | gosec | clippy + cargo-geiger | SpotBugs + FindSecBugs |
| Dependencias vulnerables | pip-audit | `npm audit` / `pnpm audit` | govulncheck | cargo-audit / cargo-deny | OWASP Dependency-Check |
| Escribir la versión en el manifiesto (release, §3.15) | `uv version` | `npm version` / `pnpm version` (con `--no-git-tag-version`) | — (la versión es el tag de git) | `cargo set-version` (cargo-edit) o cargo-release | `version` en `build.gradle(.kts)` / `mvn versions:set` |
| Espera antes de instalar versiones nuevas | `exclude-newer` de uv | `minimumReleaseAge` de pnpm; `--before` de npm | — (versiones fijadas en `go.sum`) | — | — |

> Equivalencias orientativas: comprobad la sintaxis y la versión mínima de cada herramienta en su documentación antes de usarla (en particular `minimumReleaseAge` de pnpm).

### 6.3 Casos intermedios

- **`check_new_package.py`** consulta PyPI. Se adapta a otros registros cambiando la URL: `registry.npmjs.org/<pkg>`, `crates.io/api/v1/crates/<pkg>` o `proxy.golang.org`.
- **El `cooldown` de Dependabot** sirve en todos sus ecosistemas, aunque el gestor de paquetes no tenga una opción equivalente.
- **El changelog (§3.15)** no depende del lenguaje: Conventional Commits, el hook de commitizen y git-cliff funcionan en cualquier repositorio git. git-cliff es un binario de Rust; fuera de Python se instala con `cargo`, `npm` (`git-cliff`) o su imagen Docker en lugar de `uvx`. Lo único que cambia es la línea que escribe la versión en el manifiesto (ver la tabla anterior). En proyectos JS/TS es habitual validar los commits con **commitlint** + husky en lugar de commitizen; si ya usáis prek, el hook de commitizen sirve igual.
- **`scripts/check.sh`** es universal como idea: un comando que dice verde o rojo. Solo cambian los comandos que contiene. Ejemplo para TypeScript:

```bash
#!/usr/bin/env bash
set -euo pipefail
pnpm biome ci .              # formato + lint
pnpm tsc --noEmit            # tipos
pnpm depcruise src           # arquitectura
pnpm vitest run --coverage   # tests
```

**En resumen:** para llevar el arnés a otro lenguaje se sustituyen 6 o 7 piezas (paquetes, lint, tipos, tests, arquitectura, reglas de seguridad y auditoría de dependencias). El resto (secretos, CI, Semgrep y CodeQL, changelog, documentación, configuración del agente y proceso) se mantiene igual.

---

## 7. Fuentes

- uv (Astral): https://docs.astral.sh/uv/
- ruff (Astral): https://docs.astral.sh/ruff/
- ruff, reglas flake8-bandit (`S`): https://docs.astral.sh/ruff/rules/#flake8-bandit-s
- bandit (PyCQA): https://bandit.readthedocs.io/
- ty (Astral), estado de la beta: https://github.com/astral-sh/ty
- mypy: https://mypy.readthedocs.io/
- pyright: https://github.com/microsoft/pyright
- pytest: https://docs.pytest.org/
- coverage.py: https://coverage.readthedocs.io/
- import-linter: https://import-linter.readthedocs.io/
- pre-commit: https://pre-commit.com/
- prek: https://github.com/j178/prek · https://pydevtools.com/handbook/reference/prek/
- uv-pre-commit: https://github.com/astral-sh/uv-pre-commit
- ruff-pre-commit: https://github.com/astral-sh/ruff-pre-commit
- gitleaks: https://github.com/gitleaks/gitleaks
- Gitleaks + pre-commit + CI (2026): https://www.kunalganglani.com/blog/gitleaks-pre-commit-ci-setup
- setup-uv (GitHub Action): https://github.com/astral-sh/setup-uv
- Dependabot, ecosistemas soportados: https://docs.github.com/en/code-security/dependabot
- Renovate: https://docs.renovatebot.com/
- Claude Code, hooks: https://code.claude.com/docs/en/hooks
- Claude Code, permisos: https://code.claude.com/docs/en/permissions
- Claude Code, best practices: https://code.claude.com/docs/en/best-practices
- Agent Skills (estándar abierto): https://agentskills.io/specification
- GitHub Spec Kit: https://github.com/github/spec-kit
- Conventional Commits: https://www.conventionalcommits.org/es/v1.0.0/
- Keep a Changelog: https://keepachangelog.com/es-ES/1.1.0/
- commitizen: https://commitizen-tools.github.io/commitizen/
- git-cliff: https://git-cliff.org/docs/
- action-semantic-pull-request: https://github.com/amannn/action-semantic-pull-request
- release-please: https://github.com/googleapis/release-please
- python-semantic-release: https://python-semantic-release.readthedocs.io/
- towncrier: https://towncrier.readthedocs.io/
- Mitchell Hashimoto, *My AI Adoption Journey* (harness engineering): https://mitchellh.com/writing/my-ai-adoption-journey
- OpenAI, *Harness engineering*: https://openai.com/index/harness-engineering/
- Birgitta Böckeler / Martin Fowler, *Exploring Generative AI* (harness engineering): https://martinfowler.com/articles/exploring-gen-ai.html
- Simon Willison, *The lethal trifecta*: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
