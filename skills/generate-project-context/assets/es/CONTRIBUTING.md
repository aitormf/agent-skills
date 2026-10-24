<!--
PLANTILLA de CONTRIBUTING.md (en la raíz del repositorio)
Cómo usarla:
- Rellena los <marcadores>, borra estos comentarios y adapta los ejemplos.
- Este documento es para TODO el equipo, use IA o no: describe el PROCESO (cómo se propone, revisa y mergea un cambio).
- No repitas lo que ya está en otro sitio: arquitectura y principios → docs/ARCHITECTURE.md; instrucciones para agentes → AGENTS.md; configuración de herramientas → pyproject.toml.
- Si una regla se puede automatizar (formato, lint, tipos, secretos), automatízala y aquí solo menciónala.
-->

# Cómo contribuir a <nombre-del-proyecto>

Gracias por contribuir. Este documento explica cómo preparar el entorno, cómo proponer cambios y qué se espera de una PR. Vale igual si programas a mano, con asistentes de IA o con agentes autónomos.

**Lecturas previas:**
- [`README.md`](README.md): qué es el proyecto.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): estructura, capas y **principios innegociables**.
- [`docs/decisions/`](docs/decisions/README.md): decisiones tomadas y por qué.
- [`AGENTS.md`](AGENTS.md): instrucciones para agentes de IA (útil también para personas: resume comandos y límites).

## 1. Preparar el entorno

Requisitos: [uv](https://docs.astral.sh/uv/) y git. uv instala la versión de Python indicada en `.python-version`.

```bash
git clone <url-del-repo>
cd <repo>
uv sync                     # crea .venv e instala dependencias desde uv.lock
uv tool install prek        # o pre-commit
prek install                # activa los hooks de pre-commit
cp .env.example .env        # y rellena los valores (nunca se commitea)
./scripts/check.sh          # debe terminar en verde
```

Si `./scripts/check.sh` no pasa en un clon limpio, es un bug: abre un issue.

## 2. Comandos habituales

| Acción | Comando |
|---|---|
| Verificación completa (lo mismo que CI) | `./scripts/check.sh` |
| Tests | `uv run pytest` |
| Un test concreto | `uv run pytest tests/unit/test_x.py::test_y` |
| Formatear | `uv run ruff format .` |
| Lint con autocorrección | `uv run ruff check --fix .` |
| Tipos | `uv run mypy` |
| Añadir una dependencia | `uv add <paquete>` (de desarrollo: `uv add --dev <paquete>`) |

No uses `pip install` ni edites `uv.lock` a mano.

## 3. Antes de empezar

- **Cambios pequeños** (bug evidente, typo, refactor local): adelante, directamente con una PR.
- **Cambios medianos o grandes** (funcionalidad nueva, varios módulos, API pública): abre o asígnate un issue primero y escribe una especificación breve en `docs/specs/<feature>.md` (objetivo, requisitos, fuera de alcance y cómo se verifica de punta a punta).
- **Cambios de arquitectura** (nueva capa, cambio de persistencia, nueva dependencia estructural, romper un principio): necesitan una **decisión** en `docs/decisions/`, aceptada antes de implementar (la redacta la skill `record-decision`).

Antes de implementar, revisa tu plan contra los principios innegociables de `docs/ARCHITECTURE.md`.

## 4. Flujo de trabajo con git

- Rama desde `main`, con el formato `<tipo>/<descripcion-corta>`: `feat/export-csv`, `fix/timezone-reservas`, `docs/decision-cache`.
- Nadie hace push directo a `main`; todo entra por PR.
- Commits con [Conventional Commits](https://www.conventionalcommits.org/es/): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Commits pequeños y con sentido propio. Antes de abrir la PR puedes reordenar o fusionar los tuyos.
- Mantén la rama al día con `main` mediante <rebase | merge> (política del equipo: <elegir una>).
- No te saltes los hooks (`--no-verify`). Si un hook falla sin motivo, arréglalo o abre un issue.

## 5. Calidad del código

Lo comprueba la herramienta; aquí solo se resume:

- **Formato y lint:** ruff, con la configuración de `pyproject.toml`.
- **Tipos:** `mypy --strict` en `src/`. Las funciones públicas van tipadas.
- **Tests:** todo cambio de comportamiento lleva tests. Para bugs, primero un test que reproduzca el fallo (rojo) y después el arreglo (verde).
- **Cobertura:** CI exige como mínimo <N> %. No bajes la cobertura sin justificarlo.
- **Arquitectura:** las reglas de dependencia entre capas se comprueban con import-linter.
- **Secretos:** gitleaks bloquea el commit si detecta uno. Quita el secreto; no lo silencies.

Criterios que la herramienta no comprueba y que se miran en revisión:
- Nombres claros y coherentes con el glosario de `docs/ARCHITECTURE.md`.
- Sin código muerto, sin abstracciones "por si acaso" y sin dependencias innecesarias.
- Mensajes de error útiles; nada de excepciones genéricas tragadas.

## 6. Uso de IA

Puedes usar asistentes y agentes de IA (Claude Code, Codex, Copilot, Cursor…). Las reglas son las mismas que para el código escrito a mano, más estas:

1. **Respondes de todo lo que envías.** Quien abre la PR debe entender y poder explicar cada línea, la haya escrito quien la haya escrito. "Lo generó la IA" no es una respuesta en una revisión.
2. **Revisa los diffs antes de pedir revisión**, sobre todo en `tests/`: los agentes a veces debilitan o borran tests para que pasen. Ninguna PR puede eliminar ni relajar un test sin explicar por qué.
3. **PRs pequeñas.** Que la IA genere rápido no justifica PRs de miles de líneas. Orientación: < <400> líneas cambiadas (sin contar ficheros generados); si es más, divídela.
4. **Verifica, no confíes.** CI en verde es necesario pero no suficiente: prueba el cambio manualmente cuando afecte a comportamiento visible.
5. **Dependencias propuestas por la IA:** compruébalas (que existan, estén mantenidas y sean necesarias) antes de añadirlas. Cuidado con paquetes con nombres parecidos a los reales.
6. **Datos y secretos:** no pegues en herramientas de IA externas secretos, datos personales ni datos de clientes. Usa solo las herramientas aprobadas: <lista o enlace a la política>.
7. **Si un agente comete un error recurrente**, mejora el sistema en la misma PR o en una aparte: mejor un lint, test o hook; si no se puede, una línea en `AGENTS.md`.
8. **Ficheros de configuración de agentes:**
   - Se versionan y se revisan como código: `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/`, `.claude/agents/`, `.mcp.json`.
   - Son personales y **no** se versionan: `CLAUDE.local.md`, `.claude/settings.local.json`.
9. **Transparencia:** indica en la descripción de la PR si una parte relevante la generó un agente (la plantilla de PR tiene una casilla). Los co-autores automáticos en commits (`Co-Authored-By`) están <permitidos | no permitidos>.

## 7. Pull requests

**Antes de abrirla:**
- [ ] `./scripts/check.sh` en verde en local.
- [ ] Tests nuevos o actualizados para el cambio.
- [ ] Documentación actualizada en la misma PR si aplica: `README.md`, `docs/ARCHITECTURE.md`, `docs/decisions/`, `AGENTS.md`, `.env.example`.
- [ ] Sin cambios no relacionados (formateos masivos, renombrados de paso).

**Descripción** (lo pide `.github/pull_request_template.md`):
- Qué cambia y por qué; enlace al issue, spec o decisión.
- Cómo se ha verificado (tests, prueba manual, capturas).
- Riesgos, migraciones o pasos de despliegue.
- Uso de IA relevante.

**Revisión:**
- Mínimo <1> aprobación de alguien que no sea el autor. Cambios en <zonas sensibles: auth, pagos, migraciones, CI> requieren aprobación de <@equipo/CODEOWNERS>.
- Una revisión automática con IA es bienvenida como apoyo, pero **no sustituye** a la humana.
- El autor resuelve o responde todos los comentarios; quien comenta marca la conversación como resuelta.
- Merge mediante <squash | merge commit | rebase> cuando CI está en verde y hay aprobación.

## 8. Documentación

| Qué cambia | Qué actualizar |
|---|---|
| Estructura, capas, integraciones, principios | `docs/ARCHITECTURE.md` (los principios requieren una decisión) |
| Una decisión de arquitectura, una regla de negocio o un enfoque descartado | Decisión nueva en `docs/decisions/` (las aceptadas no se editan: se sustituyen por otra) |
| Comandos, herramientas o trampas conocidas | `AGENTS.md` |
| Instalación o uso | `README.md` |
| Variables de entorno | `.env.example` y `config.py` |

Lo que se decida en reuniones, chats o issues y afecte al código se lleva al repositorio. Lo que no está en el repo no existe para los agentes, ni para quien llegue dentro de seis meses.

## 9. Bugs y propuestas

- **Bugs:** issue con pasos para reproducir, comportamiento esperado frente al real, versión o commit y logs relevantes (sin secretos).
- **Propuestas:** issue describiendo el problema antes que la solución.
- **Vulnerabilidades de seguridad:** no abras un issue público; escribe a <contacto> (ver `SECURITY.md`).

## 10. Dudas

Pregunta en <canal de Slack/Discord/issue con etiqueta `question`>. Si la respuesta debería estar documentada, añádela al documento correspondiente en una PR.
