#!/usr/bin/env bash
# scripts/check.sh: verificación del repositorio. Rápida y sin red.
# El smoke test de guardrails (necesita red) va aparte: scripts/test-guardrails-python.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "▶ agentes generados al día"
scripts/build-agents.py --check

echo "▶ frontmatter de skills y agentes"
python3 - <<'EOF'
import re, sys
from pathlib import Path
bad = []
for f in sorted(Path("skills").glob("*/SKILL.md")) + sorted(Path("agents").glob("*.md")):
    m = re.match(r"---\n(.*?)\n---\n", f.read_text(encoding="utf-8"), re.S)
    fm = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l and not l.startswith(" ")) if m else {}
    name = fm.get("name", "").strip()
    if not name or not fm.get("description", "").strip():
        bad.append(f"{f}: falta name o description")
    elif f.name == "SKILL.md" and name != f.parent.name:
        bad.append(f"{f}: name '{name}' no coincide con el directorio")
for b in bad:
    print(b, file=sys.stderr)
sys.exit(1 if bad else 0)
EOF

echo "▶ manifiestos"
python3 - <<'EOF'
import json, sys
claude = json.load(open(".claude-plugin/plugin.json"))
codex = json.load(open(".codex-plugin/plugin.json"))
markets = [json.load(open(p)) for p in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")]
errors = []
if claude["name"] != codex["name"]:
    errors.append("el nombre del plugin no coincide entre Claude y Codex")
if claude["version"] != codex["version"]:
    errors.append(f"versión distinta: Claude {claude['version']}, Codex {codex['version']}")
for m in markets:
    if claude["name"] not in {p["name"] for p in m["plugins"]}:
        errors.append(f"el catálogo '{m['name']}' no incluye el plugin '{claude['name']}'")
for e in errors:
    print(e, file=sys.stderr)
sys.exit(1 if errors else 0)
EOF
if command -v claude >/dev/null; then
  claude plugin validate --strict .claude-plugin/plugin.json >/dev/null
  claude plugin validate --strict .claude-plugin/marketplace.json >/dev/null
else
  echo "  (claude no está instalado: se omite claude plugin validate)"
fi

echo "✔ todo en verde"
