# agent-skills

Skills y guías para trabajar con agentes de IA en repositorios de código.

```
skills/     Skills autocontenidas (SKILL.md + assets/ + references/)
docs/arnes/ Guías del arnés: el porqué de cada pieza. El código vive en los assets de las skills
scripts/    Tests de las skills
```

## Skills

| Skill | Qué hace |
|---|---|
| [`setup-guardrails-python`](skills/setup-guardrails-python/SKILL.md) | Instala los guardrails deterministas de un repo Python (check.sh, pre-commit, CI, seguridad, permisos y hooks de Claude Code), en greenfield o brownfield |

## Tests

```bash
scripts/test-guardrails-python.sh   # requiere uv, jq y red
```
