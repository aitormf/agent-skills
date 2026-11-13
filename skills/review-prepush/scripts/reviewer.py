#!/usr/bin/env python3
"""Who reviews the push (D-0056): the first of `[review] reviewers` of the BASE branch's
.harness-config.toml that is not of an author family and is installed.

Usage: reviewer.py <base> <author families…>. Prints the reviewer. Exit 1: none left (message on
stderr, the push is blocked whatever the fail-open policy); exit 2: the config cannot be read."""
import shutil
import subprocess
import sys
import tomllib

DEFAULT = ["claude", "codex"]
SUPPORTED = ("claude", "codex")  # opencode is only an author in this change

base, authors = sys.argv[1], sys.argv[2:]
shown = subprocess.run(["git", "show", f"{base}:.harness-config.toml"], capture_output=True, text=True) if base else None
try:
    reviewers = tomllib.loads(shown.stdout if shown and shown.returncode == 0 else "").get("review", {}).get("reviewers", DEFAULT)
    if not isinstance(reviewers, list) or not all(isinstance(r, str) for r in reviewers):
        raise ValueError("reviewers es una lista de nombres")
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
        sys.exit(0)
print("review-kit: " + ("; ".join(problems) if problems else
      f"no hay revisor de otra familia: el agente es {' y '.join(authors)} y reviewers solo tiene {', '.join(reviewers) or 'nada'}"), file=sys.stderr)
sys.exit(1)
