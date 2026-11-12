#!/usr/bin/env python3
"""The flow gate: decides what to check from the branch (R1 of control-del-flujo).
Usage: gate.py [--require-task]
The branch is GITHUB_HEAD_REF if set (CI checks out a detached HEAD), else the current one.
  - <...>/<change>/T<n>: the file docs/changes/<change>/tasks/T<n>-*.md must exist.
  - <...>/<change>/plan: the plan PR carries no code.
  - any other branch: nothing is checked, unless --require-task: then a change of code
    (anything outside docs/ and the *.md of the root) fails.
Exit status: 0 passes, 1 a rule is broken, 2 cannot check (no base branch, no branch name).
"""
import os
import re
import sys
from pathlib import Path

from board import TASK_ID, base_branch, git


def changed_code(root: Path, base: str) -> list[str]:
    files = git(root, "diff", "--name-only", "-z", f"{base}...HEAD").split("\0")
    return [f for f in files if f and not f.startswith("docs/") and not ("/" not in f and f.endswith(".md"))]


def main(argv: list[str]) -> int:
    if any(a != "--require-task" for a in argv):
        print("usage: gate.py [--require-task]", file=sys.stderr)
        return 2
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        branch = os.environ.get("GITHUB_HEAD_REF") or git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
        if branch == "HEAD":
            raise RuntimeError("HEAD is detached and GITHUB_HEAD_REF is empty")
        base = base_branch(root)
        code = changed_code(root, base)
    except (OSError, RuntimeError) as error:
        message = "no encuentro la rama base" if "no base branch" in str(error) else str(error)
        print(f"gate: no puedo comprobar: {message}", file=sys.stderr)
        return 2
    segments = branch.split("/")
    last = segments[-1]
    if len(segments) >= 2 and last == "plan":
        if code:
            print(f"gate: la PR del plan no lleva código: {', '.join(code[:5])}", file=sys.stderr)
            return 1
        return 0
    if len(segments) >= 2 and TASK_ID.fullmatch(last):
        change = f"docs/changes/{segments[-2]}"
        if not list((root / change / "tasks").glob(f"{last}-*.md")):
            print(f"gate: la tarea {last} no existe en {change}/", file=sys.stderr)
            return 1
        return 0
    if "--require-task" in argv and code:
        print(f"gate: la rama no nombra una tarea y cambia código: {', '.join(code[:5])}", file=sys.stderr)
        return 1
    if "--require-task" not in argv:
        print("gate: la rama no nombra una tarea: no se comprueba nada")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
