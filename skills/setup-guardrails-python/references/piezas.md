# Qué protege cada pieza

Resumen para decidir qué incluir. La explicación completa está en `docs/arnes/` del repositorio de skills.

| Pieza | Fichero | Protege contra | ¿Cuándo? |
|---|---|---|---|
| `scripts/check.sh` | `files/scripts/check.sh` | Que "terminado" signifique cosas distintas para persona, agente y CI | Siempre. Es el contrato con las demás skills |
| ruff (`S`, `PLE`) | `snippets/pyproject.toml` | Código inseguro típico (`shell=True`, SQL con strings, `verify=False`), Unicode bidireccional | Siempre. Sustituye a bandit |
| mypy `--strict` | `snippets/pyproject.toml` | Errores de tipos que el agente no ve | Siempre. Brownfield con trinquete |
| pytest + cobertura | `snippets/pyproject.toml` | Que el agente dé por bueno código sin probar | Siempre. Brownfield: umbral = cobertura actual |
| Cooldown de uv | `snippets/pyproject.toml` (`[tool.uv]`) | Versiones maliciosas recién publicadas | Siempre, antes del primer `uv add` |
| import-linter | `snippets/pyproject.toml` (comentado) | Que el agente rompa las capas | Cuando hay capas o módulos con reglas |
| pre-commit (prek) | `files/.pre-commit-config.yaml` | Que los errores lleguen al historial | Siempre |
| gitleaks | pre-commit + `ci.yml` | Secretos en commits; los agentes filtran el doble | Siempre |
| Unicode oculto | `files/scripts/check_hidden_unicode.py` | Instrucciones invisibles en `AGENTS.md` y reglas (*Rules File Backdoor*) | Siempre |
| zizmor | pre-commit + `security.yml` | Workflows de CI inyectables o con permisos excesivos | Si hay GitHub Actions |
| CI | `files/.github/workflows/ci.yml` | Que se salten los hooks locales; es la autoridad final | Siempre |
| Seguridad en CI | `files/.github/workflows/security.yml` | CVE en dependencias (pip-audit), patrones OWASP (Semgrep), `noqa: S` sin justificar | Siempre. Semgrep solo cuenta lo nuevo, así que sirve en brownfield |
| Dependabot | `files/.github/dependabot.yml` | Dependencias desactualizadas o vulnerables | Desde la primera dependencia |
| CODEOWNERS | `files/.github/CODEOWNERS` | Que alguien (o un agente) relaje el arnés, debilite tests o añada dependencias sin revisión | Si hay más de una persona |
| Permisos de Claude Code | `files/.claude/settings.json` | Que el agente lea secretos, use `pip`, haga push o edite el arnés | Si se usa Claude Code |
| Hook Stop | `files/.claude/hooks/check-on-stop.sh` | Que el agente termine con `check.sh` en rojo | Si se usa Claude Code |
| Hook de paquetes | `files/.claude/hooks/check_new_package.py` | Paquetes alucinados (*slopsquatting*) o con menos de 90 días | Si se usa Claude Code |
| git-cliff + commitizen | `files/cliff.toml`, `release.yml`, pre-commit | Commits ilegibles y changelog manual | Antes de la primera versión publicada |
