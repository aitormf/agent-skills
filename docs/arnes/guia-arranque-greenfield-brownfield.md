# Guía de arranque: proyecto nuevo (greenfield) y proyecto existente (brownfield)

**Complemento de `informe-proyecto-python-con-ia-2026.md` y `herramientas-arnes.md` · octubre de 2026**

> - **Greenfield:** proyecto desde cero, sin código heredado. Podéis poner el arnés completo **antes** de la primera línea de funcionalidad.
> - **Brownfield:** proyecto que ya existe, con código, deuda y costumbres. El arnés se introduce **de forma gradual**, sin romper el día a día y sin un "big bang".
>
> Las dos rutas comparten el destino: la estructura, los ficheros y las herramientas del informe. Lo que cambia es el orden y la estrategia.

---

## Parte A: Greenfield (desde cero)

**Idea clave:** en un proyecto nuevo todo es barato. Tipado estricto, cobertura mínima, capas y CI cuestan casi nada el primer día y muchísimo después. Montad el arnés **antes** de dejar que el agente escriba funcionalidad, porque el agente copiará los patrones que encuentre desde el primer commit.

### Fase 0: decisiones previas (personas, 1-2 h)

Antes de abrir ningún agente, decidid y apuntad:

- [ ] Qué es el proyecto y qué queda fuera (2-3 frases). Va a `README.md` y a `docs/ARCHITECTURE.md`.
- [ ] Tipo: aplicación, servicio, librería o CLI. Afecta al layout y a si se publica el paquete.
- [ ] Versión mínima de Python (3.13 o 3.14).
- [ ] Framework principal, si lo hay (FastAPI, Django, Typer…).
- [ ] Arquitectura de partida: capas o módulos y reglas de dependencia (aunque sean dos).
- [ ] Type checker: mypy, pyright o ty.
- [ ] Proceso del equipo: merge o squash, aprobaciones necesarias, tamaño de PR, herramientas de IA aprobadas.

Cada decisión estructural se convierte en un ADR corto en la fase 2.

### Fase 1: esqueleto y arnés (día 1)

```bash
# 1. Proyecto con layout src/
uv init --package mi-proyecto && cd mi-proyecto
uv python pin 3.13
git init

# 2. Cooldown de dependencias ANTES del primer uv add (plan-seguridad-codigo-ia.md §4.2)
printf '\n[tool.uv]\nexclude-newer = "7 days"\n' >> pyproject.toml

# 3. Herramientas de desarrollo
uv add --dev pytest pytest-cov ruff mypy import-linter
uv tool install prek

# 4. Estructura de carpetas
mkdir -p tests/unit tests/integration scripts docs/adr docs/specs docs/plans \
         .claude/skills .claude/agents .claude/hooks .github/workflows
touch src/mi_proyecto/py.typed
```

Después, instalad los guardrails con la skill [`setup-guardrails-python`](../../skills/setup-guardrails-python/SKILL.md) o copiadlos a mano desde sus [`assets/`](../../skills/setup-guardrails-python/assets/):

- [ ] Configuración de ruff, mypy, pytest, coverage e import-linter en `pyproject.toml`
- [ ] `scripts/check.sh`
- [ ] `.pre-commit-config.yaml` + `prek install`
- [ ] `.github/workflows/ci.yml` + protección de la rama `main`
- [ ] `.github/dependabot.yml`
- [ ] `.gitignore` (sección 5 del informe) y `.env.example`

**Criterio de salida:** un test trivial (`test_import.py`) pasa, `./scripts/check.sh` sale en verde y CI también. **Todavía no hay funcionalidad.**

### Fase 2: documentación mínima (día 1)

Usad las plantillas y dejadlas **cortas**; crecerán con el proyecto:

- [ ] `docs/ARCHITECTURE.md` (de [`assets/es/ARCHITECTURE.md`](../../skills/generate-project-context/assets/es/ARCHITECTURE.md)): propósito, mapa del código, capas y **principios innegociables**. Las secciones que aún no aplican, borradlas.
- [ ] `CONTRIBUTING.md` (de [`assets/es/CONTRIBUTING.md`](../../skills/generate-project-context/assets/es/CONTRIBUTING.md)) con los `<...>` decididos en la fase 0.
- [ ] `docs/adr/0000-plantilla.md` + ADRs de las decisiones de la fase 0 (p. ej. `0001-uv-ruff-mypy.md`, `0002-arquitectura-por-capas.md`).
- [ ] `AGENTS.md` (de [`assets/es/AGENTS.md`](../../skills/generate-project-context/assets/es/AGENTS.md)), **escrito a mano**, de menos de 100 líneas: comandos, límites y enlaces. La sección "Trampas conocidas" empieza vacía.
- [ ] `CLAUDE.md` con `@AGENTS.md`.
- [ ] `README.md`: qué es y cómo se arranca.

> No generéis `AGENTS.md` con `/init` en un repo vacío: no hay nada que descubrir y saldrá genérico. Según el estudio de ETH Zúrich, los ficheros genéricos o generados no ayudan.

### Fase 3: configuración del agente (día 1-2)

- [ ] `.claude/settings.json`: permisos compartidos, hook de formato y hook `Stop` con `check.sh` (sección 4.4 de `herramientas-arnes.md`).
- [ ] Subagente revisor en `.claude/agents/reviewer.md`.
- [ ] `.mcp.json` solo si ya necesitáis un servidor MCP concreto (p. ej. el issue tracker), y sin credenciales.

**Prueba de fuego:** en un clon limpio, abrid el agente y pedidle *"ejecuta los tests"*. Tiene que funcionar a la primera, sin preguntar nada.

### Fase 4: primera funcionalidad (primer *vertical slice*)

La primera funcionalidad fija los patrones que el agente imitará después. Hacedla con especial cuidado:

1. **Spec:** pedid al agente que os entreviste y escriba `docs/specs/<feature>.md` (objetivo, requisitos, fuera de alcance y verificación de punta a punta). Revisadla.
2. **Plan** en modo plan, revisado contra los principios de `ARCHITECTURE.md`.
3. **Sesión nueva** con contexto limpio para implementar, con TDD rojo/verde y atravesando todas las capas (api → application → domain → infra).
4. **Revisión** con el subagente revisor y después revisión humana **línea a línea**. Este código será la plantilla de todo lo demás.
5. Actualizad `ARCHITECTURE.md` (mapa del código, glosario) en la misma PR.

### Fase 5: ritmo de crucero

- Un issue y una spec por funcionalidad mediana; PRs pequeñas.
- **Harness engineering:** cada error repetido del agente → regla de ruff, contrato de import-linter, test o hook. Si no se puede, una línea en "Trampas conocidas" de `AGENTS.md`.
- Revisión mensual de `AGENTS.md`: podad lo que ya no hace falta, sobre todo al cambiar de modelo.
- Revisión trimestral de `ARCHITECTURE.md` contra el código (se le puede pedir a un agente que señale las discrepancias).

### Errores típicos en greenfield

| Error | Consecuencia | Mejor |
|---|---|---|
| Dejar que el agente genere "todo el proyecto" de un prompt | Arquitectura improvisada que se copiará para siempre | Arnés primero; un vertical slice revisado a mano |
| Posponer tipos, cobertura o CI "para cuando crezca" | Añadirlos después cuesta semanas | Activarlos el día 1, con el código aún vacío |
| `AGENTS.md` enorme el primer día | Más coste por sesión y reglas que se ignoran | Corto; crece solo con errores reales |
| Diseñar 15 capas y 30 principios | Sobreingeniería que el agente reproduce | Mínimo viable; crecer con ADRs |

---

## Parte B: Brownfield (proyecto existente)

**Idea clave:** el agente imita lo que ya hay, incluida la deuda. Antes de pedirle funcionalidades grandes, dadle **una red de seguridad** (tests y CI) y **un mapa** (`AGENTS.md`, `ARCHITECTURE.md`). Introducid las reglas con **trinquete** (*ratchet*): lo nuevo cumple, lo viejo se tolera y la deuda solo puede bajar.

### Fase 0: diagnóstico (1-2 días)

Usad el agente en **modo solo lectura** para explorar; es de lo que mejor hace en un brownfield y no tiene riesgo.

- [ ] Inventario con el agente (modo plan): *"Analiza el repositorio y dime: cómo se instala y ejecuta, cómo se lanzan los tests, estructura de módulos, dependencias principales, puntos de entrada y zonas que te parezcan frágiles. No modifiques nada."*
- [ ] ¿Se puede arrancar desde un clon limpio siguiendo el README? Anotad cada paso que falte.
- [ ] Estado de los tests: ¿existen?, ¿pasan?, ¿cuánto tardan?, ¿qué cobertura tienen?
- [ ] Gestión de dependencias actual: `requirements.txt`, Poetry, pip-tools, Pipenv…
- [ ] **Secretos en el historial:** `gitleaks git . --redact` sobre todo el historial. Si aparece alguno, **rotadlo** (eliminarlo del historial no basta: ya se ha filtrado).
- [ ] Conocimiento fuera del repo: wikis, Notion, Slack, personas clave. Haced una lista de lo que habría que traer al repositorio.
- [ ] Mapa de zonas: **críticas** (pagos, auth, datos), **frágiles** (sin tests, muy acopladas) y **seguras** (bien testeadas). Determina dónde dejar trabajar al agente primero.

**Entregable:** un documento `docs/plans/AAAA-MM-DD-adopcion-ia.md` con el diagnóstico y el plan de las fases siguientes.

### Fase 1: red de seguridad mínima (primera semana)

Objetivo: que cualquier cambio, humano o del agente, se pueda verificar automáticamente.

1. **Un comando que funcione:** `scripts/check.sh` con lo que haya hoy (aunque solo sea `pytest`). Que pase en verde. Si hay tests rotos, marcadlos con `@pytest.mark.skip(reason="…")` y un issue, en lugar de dejar la suite en rojo: un rojo permanente enseña a todos (también al agente) a ignorar el rojo.
2. **CI** que ejecute `check.sh` en cada PR, y protección de rama.
3. **gitleaks** en pre-commit y en CI. Para hallazgos antiguos ya rotados, usad una *baseline* (`--baseline-path`) para que solo bloquee los nuevos.
4. **Formato:** `ruff format` en **una única PR aislada**, solo de formato, y añadid su commit a `.git-blame-ignore-revs` para no ensuciar `git blame`.

```bash
uv run ruff format .
git commit -am "style: aplicar ruff format a todo el repositorio"
git rev-parse HEAD >> .git-blame-ignore-revs
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

### Fase 2: contexto para el agente (primera semana)

- [ ] **`AGENTS.md`**: aquí **sí** podéis partir de `/init` (en brownfield hay mucho que descubrir), pero **podadlo a mano**. Quitad descripciones de ficheros, resúmenes del repo y todo lo que el agente pueda deducir leyendo el código. Dejad comandos, peculiaridades del entorno, trampas y límites. Objetivo: menos de 150 líneas.
- [ ] Añadid una sección **"Zonas"** en `AGENTS.md`: qué carpetas son críticas o frágiles y qué hacer en ellas (p. ej. *"`billing/`: no modificar sin test de caracterización previo y aprobación de @equipo-pagos"*).
- [ ] **`docs/ARCHITECTURE.md` descriptivo:** cómo **es**, no cómo debería ser. Mapa del código, flujos principales y glosario. Pedid un borrador al agente y corregidlo con quien conoce el sistema.
- [ ] **ADRs retroactivos** solo de las decisiones que más se cuestionan (*"¿por qué no usamos el ORM aquí?"*). Con 3-5 basta. Lo importante es recoger las alternativas descartadas, para que el agente no vuelva a proponerlas.
- [ ] Traed al repositorio el conocimiento externo de la fase 0 que afecte al código.
- [ ] `CLAUDE.md` con `@AGENTS.md`; `.claude/settings.json` con permisos prudentes. Al principio, **sin** permisos de escritura amplios en las zonas críticas.

### Fase 3: modernizar herramientas con trinquete (semanas 2-4)

Introducid cada herramienta de forma que **no bloquee el código existente, pero sí el nuevo**:

| Herramienta | Cómo introducirla sin "big bang" |
|---|---|
| **uv** | Desde `requirements.txt`: `uv init --bare` y `uv add -r requirements.txt` (y `-r requirements-dev.txt --dev`). Desde Poetry o Pipenv: `uvx migrate-to-uv`. Comprobad que los tests pasan igual antes de retirar lo anterior. Añadid el cooldown (`exclude-newer`) **antes** de importar las dependencias; si alguna cota mínima es más reciente que el cooldown, la resolución falla (ver `plan-seguridad-codigo-ia.md` §4.2) |
| **ruff (lint)** | Activad las reglas que queráis y ejecutad `ruff check --add-noqa` una vez: marca las infracciones actuales con `# noqa` y todo lo nuevo debe cumplir. Id quitando los `noqa` poco a poco |
| **mypy** | Empezad sin `strict` global: `strict = true` solo en los módulos nuevos o limpios mediante `[[tool.mypy.overrides]]`, y `ignore_errors = true` en los heredados. Cada módulo que se limpia sale de la lista de ignorados |
| **Cobertura** | Umbral `fail_under` = cobertura actual (aunque sea un 23 %). Se sube cada vez que aumenta; nunca baja |
| **import-linter** | Definid los contratos de la arquitectura deseada y listad las violaciones actuales en `ignore_imports`. Esa lista solo puede encoger |
| **pre-commit/prek** | Los hooks solo analizan los ficheros modificados, así que el código viejo se va limpiando cuando se toca (regla del boy scout) |

```toml
# Ejemplo: mypy con trinquete
[tool.mypy]
strict = true
files = ["src"]

[[tool.mypy.overrides]]
module = ["mi_proyecto.legacy.*", "mi_proyecto.reports.*"]
ignore_errors = true   # deuda conocida: issue #123. Esta lista solo puede encoger.
```

```toml
# Ejemplo: import-linter con violaciones conocidas
[[tool.importlinter.contracts]]
name = "Arquitectura por capas"
type = "layers"
layers = ["mi_proyecto.api", "mi_proyecto.services", "mi_proyecto.models"]
ignore_imports = [
    "mi_proyecto.models.order -> mi_proyecto.services.pricing",  # deuda: issue #456
]
```

### Fase 4: primeras tareas con el agente (de menos a más riesgo)

Ganad confianza en el arnés y en el agente subiendo el riesgo de forma gradual:

1. **Solo lectura:** preguntas sobre el código, explicaciones, documentación. Sin riesgo y útil para onboarding.
2. **Tests de caracterización** (Michael Feathers, *Working Effectively with Legacy Code*): pedid al agente tests que **fijen el comportamiento actual** de las zonas frágiles, aunque sea "raro". Es el mejor primer uso del agente en un brownfield, porque crea la red de seguridad para todo lo demás. Revisad que comprueban comportamiento real y no detalles triviales.
3. **Tareas acotadas en zonas seguras:** bugs con test que los reproduzca, pequeños refactors, eliminar `noqa` y `ignore_errors` del trinquete, actualizar dependencias.
4. **Funcionalidades nuevas** con el flujo completo: spec → plan → TDD → revisión.
5. **Zonas críticas**, al final, con tests de caracterización ya en su sitio, plan revisado y aprobación de los responsables.

Mitchell Hashimoto propone un ejercicio útil al principio: **hacer el trabajo dos veces**, una a mano y otra con el agente, para aprender qué contexto le falta. Cada carencia descubierta es una mejora del arnés.

### Fase 5: mejora continua

- **Harness engineering:** cada error del agente → regla, test, hook o, como último recurso, línea en `AGENTS.md`.
- **Medid el trinquete:** número de `noqa`, módulos en `ignore_errors`, entradas en `ignore_imports` y cobertura. Revisadlo mensualmente; la deuda solo puede bajar.
- Cuando una zona tenga tests y tipos, pasadla de "frágil" a "segura" en `AGENTS.md` y relajad sus restricciones.
- Revisad `AGENTS.md` y `ARCHITECTURE.md` con la misma cadencia que en greenfield.

### Errores típicos en brownfield

| Error | Consecuencia | Mejor |
|---|---|---|
| Pedir al agente un refactor grande sin tests | Cambios de comportamiento invisibles | Tests de caracterización primero |
| Activar `mypy --strict` o reglas nuevas de ruff en todo el repo de golpe | Miles de errores, el equipo desactiva la herramienta | Trinquete: lo nuevo cumple, lo viejo se tolera |
| Formatear el repo mezclado con cambios funcionales | PRs imposibles de revisar; `git blame` inútil | PR aislada de formato + `.git-blame-ignore-revs` |
| `AGENTS.md` generado con `/init` sin podar | Contexto caro y genérico (estudio de ETH) | Generar, podar a lo no deducible y mantener |
| `ARCHITECTURE.md` que describe el ideal, no la realidad | El agente asume reglas que el código no cumple | Describir lo que hay; el ideal va en ADRs y en el trinquete de import-linter |
| Dejar la suite en rojo "porque ya estaba así" | Nadie, ni el agente, confía en el rojo | Verde siempre; lo roto, `skip` con issue |
| Soltar al agente en las zonas críticas desde el día 1 | Riesgo alto, confianza baja | Escalar el riesgo de forma gradual (fase 4) |

---

## Parte C: Comparativa rápida

| Aspecto | Greenfield | Brownfield |
|---|---|---|
| Estrategia | Arnés completo antes del código | Red de seguridad primero; reglas con trinquete |
| Primer uso del agente | Primer vertical slice, revisado a mano | Exploración en solo lectura y tests de caracterización |
| `AGENTS.md` | Escrito a mano, corto | Partir de `/init`, podar a fondo, añadir "Zonas" |
| `ARCHITECTURE.md` | Prescriptivo: cómo será | Descriptivo: cómo es (el ideal, en ADRs) |
| ADRs | Las decisiones de la fase 0 | 3-5 retroactivos de lo más cuestionado |
| Tipos y lint | Estrictos desde el día 1 | Estrictos para lo nuevo; lo viejo con trinquete |
| Cobertura | Umbral fijo razonable (p. ej. 80 %) | Umbral = la actual, y solo sube |
| Mayor riesgo | Que el agente fije malos patrones al principio | Que el agente cambie comportamiento sin que nadie lo note |
| Spec Kit | `specify init` | `specify init --here` |

---

## Fuentes

- Anthropic, *Claude Code best practices* (explorar → planificar → implementar, verificación, `/init`): https://code.claude.com/docs/en/best-practices
- OpenAI, *Harness engineering* (el repo como fuente de verdad, imponer la arquitectura mecánicamente): https://openai.com/index/harness-engineering/
- Mitchell Hashimoto, *My AI Adoption Journey* (reproducir el propio trabajo, harness engineering): https://mitchellh.com/writing/my-ai-adoption-journey
- Gloaguen et al. (ETH Zúrich), *Evaluating AGENTS.md*: https://arxiv.org/abs/2602.11988
- Kent Beck, *Augmented Coding: Beyond the Vibes*: https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes
- Simon Willison, *Agentic Engineering Patterns*: https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/
- Addy Osmani, *How to write a good spec for AI agents*: https://addyosmani.com/blog/good-spec/
- Michael Feathers, *Working Effectively with Legacy Code* (tests de caracterización), Prentice Hall, 2004
- Martin Fowler, *Architecture Decision Record*: https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html
- GitHub Spec Kit (greenfield y brownfield): https://github.com/github/spec-kit
- uv, migrar proyectos existentes: https://docs.astral.sh/uv/
- migrate-to-uv: https://github.com/mkniewallner/migrate-to-uv
- ruff, `--add-noqa`: https://docs.astral.sh/ruff/linter/
- mypy, configuración por módulo: https://mypy.readthedocs.io/en/stable/config_file.html
- import-linter, `ignore_imports`: https://import-linter.readthedocs.io/
- gitleaks, baselines: https://github.com/gitleaks/gitleaks
- GitHub, ignorar commits en blame (`.git-blame-ignore-revs`): https://docs.github.com/en/repositories/working-with-files/using-files/viewing-and-understanding-files
