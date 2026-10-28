#!/usr/bin/env python3
"""Genera los agentes de Codex y OpenCode a partir de agents/*.md (formato Claude Code).

La fuente única es agents/*.md. Este script escribe:
  adapters/codex/agents/<name>.toml     -> se copian a .codex/agents/ del proyecto
  adapters/opencode/agents/<name>.md    -> se copian a .opencode/agents/ del proyecto
  los bloques claudecode: y opencode: al final del frontmatter de agents/*.md, para rulesync (atril sync):
  rulesync quita tools, skills y model si no van en el bloque de cada herramienta.

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
BLOCKS = "# Bloques para rulesync: los genera scripts/build-agents.py desde tools, skills, model y mode. No editar a mano."


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: falta el frontmatter")
    fm_text, body = text[4:].split("\n---\n", 1)
    fm: dict[str, str] = {"_own": fm_text.split(f"\n{BLOCKS}\n", 1)[0]}
    key = ""
    for line in fm["_own"].splitlines():
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


def opencode_permission(fm: dict[str, str], indent: str) -> str:
    """El mode y el mapa permission de OpenCode (formato v1, que OpenCode 2 también lee). Nunca junto a un campo de v2."""
    t = tools(fm)
    edit = "allow" if t & {"Write", "Edit"} else "deny"
    bash = "ask" if "Bash" in t else "deny"
    # Sin `Agent` en tools, ningún subagente: si no, delegaría en `general`, que puede escribir (probado en OpenCode 2.2.0).
    task = "allow" if "Agent" in t else "deny"
    lines = [f"mode: {fm.get('mode') or 'subagent'}", "permission:", f"  edit: {edit}", f"  bash: {bash}",
             "  webfetch: deny", "  skill: allow", f"  task: {task}"]
    return "".join(f"{indent}{line}\n" for line in lines)


def blocks(fm: dict[str, str]) -> str:
    """Las restricciones de cada herramienta, dentro de su bloque, para que rulesync no las pierda."""
    claude = [f"  tools: {fm['tools']}"]
    if fm.get("skills"):
        claude += ["  skills:"] + [f"    - {s.strip()}" for s in fm["skills"].split(",")]
    if fm.get("model"):
        claude.append(f"  model: {fm['model']}")
    return f"{BLOCKS}\nclaudecode:\n" + "\n".join(claude) + "\nopencode:\n" + opencode_permission(fm, "  ")


def source(fm: dict[str, str], body: str) -> str:
    return f"---\n{fm['_own']}\n{blocks(fm)}---\n\n{body}"


def opencode(fm: dict[str, str], body: str, src: str) -> str:
    # El nombre del agente sale del nombre del fichero. Sin model, el subagente usa el de quien lo llama.
    return (
        "---\n"
        f"description: {json.dumps(fm['description'], ensure_ascii=False)}\n"
        + opencode_permission(fm, "")
        + "---\n"
        f"<!-- {HEADER.format(src=src)} -->\n\n"
        f"{body}"
    )


def build() -> dict[Path, str]:
    files = {}
    for path in sorted(SRC.glob("*.md")):
        fm, body = parse(path)
        files[OUT / "codex" / "agents" / f"{fm['name']}.toml"] = codex(fm, body, path.name)
        files[OUT / "opencode" / "agents" / f"{fm['name']}.md"] = opencode(fm, body, path.name)
        files[path] = source(fm, body)
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
