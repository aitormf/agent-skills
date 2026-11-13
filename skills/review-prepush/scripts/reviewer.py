#!/usr/bin/env python3
"""Who reviews the push (D-0056): the first of `[review] reviewers` of the BASE branch's
.harness-config.toml that is not of an author family and is installed.

Usage: reviewer.py <base> <author families…>. Prints the reviewer; for codex, then one per line its
options: model and effort of `[review.codex]` of the base (never of the branch), and the review personas
of the kit itself, at the rev the project pinned (never the .codex/agents/ of the branch under review, which
the pushing agent could have edited). Codex does not load personas from a project it does not trust, so
they are registered. Exit 1: none left (message on
stderr, the push is blocked whatever the fail-open policy); exit 2: the config cannot be read."""
import shutil
import subprocess
import sys
import tomllib

import json
from pathlib import Path
DEFAULT = ["claude", "codex"]
PERSONAS = Path(__file__).resolve().parents[3] / "adapters" / "codex" / "agents"
REVIEW_PERSONAS = ("code-reviewer", "security-auditor", "test-engineer", "finding-verifier")
SUPPORTED = ("claude", "codex")  # opencode is only an author in this change

base, authors = sys.argv[1], sys.argv[2:]
shown = subprocess.run(["git", "show", f"{base}:.harness-config.toml"], capture_output=True, text=True) if base else None
try:
    review = tomllib.loads(shown.stdout if shown and shown.returncode == 0 else "").get("review", {})
    reviewers = review.get("reviewers", DEFAULT)
    if not isinstance(reviewers, list) or not all(isinstance(r, str) for r in reviewers):
        raise ValueError("reviewers es una lista de nombres")
    codex = {"model": "gpt-6.1-terra", "effort": "medium", **review.get("codex", {})}
    if not all(isinstance(codex[k], str) and codex[k] for k in ("model", "effort")):
        raise ValueError("[review.codex] model y effort son texto")
except (tomllib.TOMLDecodeError, AttributeError, ValueError) as error:
    print(f"review-kit: .harness-config.toml de la rama base no es válido: {error}", file=sys.stderr)
    sys.exit(2)

problems = []
for name in (r for r in reviewers if r not in authors):
    if name not in SUPPORTED:
        problems.append(f"{name} no está soportado como revisor")
    elif not shutil.which(name):
        problems.append(f"{name} no está instalado")
    else:
        print(name)
        if name == "codex":
            print("-m", codex["model"], "-c", f"model_reasoning_effort={json.dumps(codex['effort'])}", sep="\n")
            for f in (PERSONAS / f"{p}.toml" for p in REVIEW_PERSONAS):
                try:
                    t = tomllib.loads(f.read_text(encoding="utf-8"))
                    print("-c", f"agents.{t['name']}.description={json.dumps(t['description'])}",
                          "-c", f"agents.{t['name']}.config_file={json.dumps(str(f.resolve()))}", sep="\n")
                except (tomllib.TOMLDecodeError, KeyError, OSError):
                    pass  # a persona that cannot be read is not registered
        sys.exit(0)
print("review-kit: " + ("; ".join(problems) if problems else
      f"no hay revisor de otra familia: el agente es {' y '.join(authors)} y reviewers solo tiene {', '.join(reviewers) or 'nada'}"), file=sys.stderr)
sys.exit(1)
