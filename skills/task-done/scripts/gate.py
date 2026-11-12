#!/usr/bin/env python3
"""The flow gate: decides what to check from the branch (R1 of control-del-flujo).
Usage: gate.py [--require-task]
The branch is GITHUB_HEAD_REF if set (CI checks out a detached HEAD), else the current one.
  - <...>/<change>/T<n>: the file docs/changes/<change>/tasks/T<n>-*.md must exist; above 200
    lines of diff it warns (D-0053), it does not fail.
    It fails if the branch touches a control file (the list of the base branch, R7).
  - <...>/<change>/plan: the plan PR carries no code.
  - any other branch: nothing is checked, unless --require-task: then a change of code
    (anything outside docs/ and the *.md of the root) fails.
Exit status: 0 passes, 1 a rule is broken, 2 cannot check (no base branch, no branch name).
"""
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

from board import TASK_ID, base_branch, git, parse_frontmatter

PLAN_FIELDS = ("examples", "verification", "depends_on")
# R7: control files; the project extends the list in CONTROL_LIST, itself a control file.
CONTROL = (".github/**", ".pre-commit-config.yaml", ".claude/settings*.json", ".claude/hooks/**", ".codex/**",
           "opencode.json", "scripts/check.sh", ".gitattributes", "CODEOWNERS")
CONTROL_LIST = ".kit-control"


def changed_files(root: Path, base: str) -> list[str]:
    return [f for f in git(root, "diff", "--name-only", "-z", f"{base}...HEAD").split("\0") if f]


def changed_code(files: list[str]) -> list[str]:
    return [f for f in files if not f.startswith("docs/") and not ("/" not in f and f.endswith(".md"))]


def task_problems(root: Path, base: str, change: str, task: str, files: list[str]) -> list[str]:
    """R2: the audit of task_done.py, the approved plan of the task file and the files of other tasks."""
    audit = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("task_done.py")), "--audit", change, task],
        cwd=root, capture_output=True, text=True,
    )
    if audit.returncode not in (0, 3):
        raise RuntimeError(audit.stderr.strip() or audit.stdout.strip())
    found = [line for line in audit.stdout.splitlines() if "PROBLEM" in line]
    if files and "pending, no red commit yet" in audit.stdout:
        found.append(f"{task}: PROBLEM: la rama tiene cambios y no el commit test({task}) en rojo de sus ejemplos")
    own = next((root / change / "tasks").glob(f"{task}-*.md")).relative_to(root).as_posix()
    others = [f for f in files if re.fullmatch(r"docs/changes/[^/]+/tasks/T\d+(-[^/]+)?\.md", f) and f != own]
    if others:
        found.append(f"la rama de {task} toca el fichero de otra tarea: {', '.join(others)}")
    try:
        before = parse_frontmatter(git(root, "show", f"{base}:{own}")) or {}
    except (RuntimeError, ValueError):
        return found  # the task is not in the base branch yet: nothing approved to compare with
    now = parse_frontmatter((root / own).read_text(encoding="utf-8")) or {}
    if changed := [k for k in PLAN_FIELDS if before.get(k) != now.get(k)]:
        found.append(f"el plan aprobado no se cambia en la rama de la tarea ({', '.join(changed)} de {own})")
    return found


def control_files(root: Path, base: str, files: list[str]) -> list[str]:
    """R7: files of the diff that match the control list, read from the base branch, never from the branch."""
    try:
        extra = git(root, "show", f"{base}:{CONTROL_LIST}").splitlines()
    except RuntimeError:
        extra = []  # the base has no project list
    patterns = CONTROL + tuple(p.strip() for p in extra if p.strip() and not p.lstrip().startswith("#"))
    return [f for f in files if f == CONTROL_LIST or any(fnmatch.fnmatchcase(f, p) for p in patterns)]


def size_warning(root: Path, base: str) -> str | None:
    """R3 (D-0053): the size counted by diff_size.py (D-0047); above 200 lines it warns, it never blocks."""
    script = Path(__file__).resolve().parents[2] / "review-context" / "scripts" / "diff_size.py"
    run = subprocess.run([sys.executable, str(script), f"{base}...HEAD"], cwd=root, capture_output=True, text=True)
    count = re.match(r"(\d+) lines, large", run.stdout)
    return f"{count[1]} líneas > 200 (D-0044): parte la tarea en el plan" if count else None


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
        files = changed_files(root, base)
        code = changed_code(files)
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
        try:
            problems = task_problems(root, base, change, last, files)
        except (OSError, RuntimeError) as error:
            print(f"gate: no puedo comprobar: {error}", file=sys.stderr)
            return 2
        if touched := control_files(root, base, files):
            problems.append(f"una tarea no cambia el arnés: va en su propia PR, revisada por CODEOWNERS ({', '.join(touched)})")
        for problem in problems:
            print(f"gate: {problem}", file=sys.stderr)
        if warning := size_warning(root, base):
            print(f"gate: aviso: {warning}", file=sys.stderr)
        return 1 if problems else 0
    if "--require-task" in argv and code:
        print(f"gate: la rama no nombra una tarea y cambia código: {', '.join(code[:5])}", file=sys.stderr)
        return 1
    if "--require-task" not in argv:
        print("gate: la rama no nombra una tarea: no se comprueba nada")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
