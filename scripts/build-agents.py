#!/usr/bin/env python3
"""Genera los agentes de Codex y OpenCode a partir de agents/*.md (formato Claude Code).

La fuente única es agents/*.md. Este script escribe:
  adapters/codex/agents/<name>.toml     -> se copian a .codex/agents/ del proyecto
  adapters/opencode/agents/<name>.md    -> se copian a .opencode/agents/ del proyecto

Uso:
  scripts/build-agents.py          regenera los adaptadores
  scripts/build-agents.py --check  falla si los adaptadores no están al día (para tests y CI)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "agents"
OUT = ROOT / "adapters"
HEADER = "Generado por scripts/build-agents.py desde agents/{src}. No editar a mano."


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: falta el frontmatter")
    fm_text, body = text[4:].split("\n---\n", 1)
    fm: dict[str, str] = {}
    key = ""
    for line in fm_text.splitlines():
        if line.startswith("  - ") and key:  # lista YAML: se guarda como "a, b"
            fm[key] = ", ".join(filter(None, [fm[key], line[4:].strip()]))
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        fm[key] = value.strip()
    for key in ("name", "description", "tools"):
        if not fm.get(key):
            raise SystemExit(f"{path}: falta '{key}' en el frontmatter")
    return fm, body.strip() + "\n"


def tools(fm: dict[str, str]) -> set[str]:
    return {t.strip() for t in fm["tools"].split(",")}


def codex(fm: dict[str, str], body: str, src: str) -> str:
    # sandbox_mode y approval_policy se ignoran en los agentes de Codex: los hereda la sesión principal.
    # Sin model, el agente usa el modelo por defecto de [agents] o el de la sesión principal.
    if "'''" in body:
        raise SystemExit(f"agents/{src}: el cuerpo no puede contener ''' (delimitador TOML)")
    description = fm["description"].replace("\\", "\\\\").replace('"', '\\"')
    return (
        f"# {HEADER.format(src=src)}\n"
        f'name = "{fm["name"]}"\n'
        f'description = "{description}"\n'
        f"developer_instructions = '''\n{body}'''\n"
    )


def opencode(fm: dict[str, str], body: str, src: str) -> str:
    # El nombre del agente sale del nombre del fichero. Sin model, el subagente usa el de quien lo llama.
    t = tools(fm)
    edit = "allow" if t & {"Write", "Edit"} else "deny"
    bash = "ask" if "Bash" in t else "deny"
    # Sin `Agent` en tools, ningún subagente: si no, delegaría en `general`, que puede escribir (probado en OpenCode 2.2.0).
    task = "allow" if "Agent" in t else "deny"
    return (
        "---\n"
        f"description: {json.dumps(fm['description'], ensure_ascii=False)}\n"
        f"mode: {fm.get('mode') or 'subagent'}\n"
        "permission:\n"
        f"  edit: {edit}\n"
        f"  bash: {bash}\n"
        "  webfetch: deny\n"
        "  skill: allow\n"
        f"  task: {task}\n"
        "---\n"
        f"<!-- {HEADER.format(src=src)} -->\n\n"
        f"{body}"
    )


def build() -> dict[Path, str]:
    files = {}
    for path in sorted(SRC.glob("*.md")):
        fm, body = parse(path)
        files[OUT / "codex" / "agents" / f"{fm['name']}.toml"] = codex(fm, body, path.name)
        files[OUT / "opencode" / "agents" / f"{fm['name']}.md"] = opencode(fm, body, path.name)
    return files


def main() -> int:
    files = build()
    existing = {p for p in OUT.glob("*/agents/*") if p.is_file()}
    if "--check" in sys.argv:
        stale = [p for p, c in files.items() if not p.exists() or p.read_text(encoding="utf-8") != c]
        stale += sorted(existing - files.keys())
        for p in stale:
            print(f"desactualizado: {p.relative_to(ROOT)}", file=sys.stderr)
        if stale:
            print("Ejecuta scripts/build-agents.py y haz commit del resultado.", file=sys.stderr)
        return 1 if stale else 0
    for p in existing - files.keys():
        p.unlink()
    for p, content in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
