#!/usr/bin/env python3
"""The flow gate: decides what to check from the branch (R1 of control-del-flujo).
Usage: gate.py [--require-task | --context]
The branch is GITHUB_HEAD_REF if set (CI checks out a detached HEAD), else the current one.
  - <...>/<change>/T<n>: the file docs/changes/<change>/tasks/T<n>-*.md must exist; above 200
    lines of diff it warns (D-0053), it does not fail.
    It fails if the branch touches a control file (the list of the base branch, R7).
  - <...>/<change>/plan: the plan PR carries no code.
  - any other branch: nothing is checked, unless --require-task: then a change of code
    (anything outside docs/ and the *.md of the root) fails.
--context prints what a Claude Code session needs (R5): the task of the branch, if any, and the rules of
the flow. It never fails: it exits 0 and warns.
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
# R7: control files; the project extends the list in CONTROL_LIST (one pattern per line, "!pattern" drops a
# default one), itself a control file that cannot be dropped.
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
    lines = [p.strip() for p in extra if p.strip() and not p.lstrip().startswith("#")]
    dropped = {p[1:].strip() for p in lines if p.startswith("!")}  # "!pattern" drops a default pattern
    patterns = tuple(p for p in CONTROL if p not in dropped) + tuple(p for p in lines if not p.startswith("!"))
    return [f for f in files if f == CONTROL_LIST or any(fnmatch.fnmatchcase(f, p) for p in patterns)]


def size_warning(root: Path, base: str) -> str | None:
    """R3 (D-0053): the size counted by diff_size.py (D-0047); above 200 lines it warns, it never blocks."""
    script = Path(__file__).resolve().parents[2] / "review-context" / "scripts" / "diff_size.py"
    run = subprocess.run([sys.executable, str(script), f"{base}...HEAD"], cwd=root, capture_output=True, text=True)
    count = re.match(r"(\d+) lines, large", run.stdout)
    return f"{count[1]} líneas > 200 (D-0044): parte la tarea en el plan" if count else None


RULES = """Reglas del flujo (las comprueba el gate, no se saltan):
- Una tarea, una rama (<cambio>/T<n>), una PR; las dependencias, ya integradas.
- Antes del código, el commit test(T<n>) en rojo con los tests de sus ejemplos; después no se tocan.
- El plan aprobado (examples, verification, depends_on) y el fichero de otra tarea no se cambian en la rama.
- Una tarea no cambia el arnés (hooks, CI, ajustes de los agentes): va en su propia PR.
- Hasta 200 líneas con los tests; si no cabe, para y pide partir la tarea.
- El estado se marca con task-done, nunca a mano."""


def context(root: Path, branch: str) -> list[str]:
    """R5: the task of the branch (title, purpose, examples, verification); empty if there is none."""
    segments = branch.split("/")
    if len(segments) < 2 or not TASK_ID.fullmatch(segments[-1]):
        return []
    change = f"docs/changes/{segments[-2]}"
    found = list((root / change / "tasks").glob(f"{segments[-1]}-*.md"))
    if not found:
        print(f"gate: la tarea {segments[-1]} no existe en {change}/", file=sys.stderr)
        return []
    text = found[0].read_text(encoding="utf-8")
    fields = parse_frontmatter(text) or {}
    purpose = next((m[0] for m in re.finditer(r"^\*\*Propósito:.*$", text, re.M)), "")
    readme = (root / change / "README.md").read_text(encoding="utf-8") if (root / change / "README.md").is_file() else ""
    lines = [f"Rama {branch}: tarea {segments[-1]}: {fields.get('title', '')}", purpose, f"Fichero: {found[0].relative_to(root)}"]
    for example in fields.get("examples", []):
        lines += [m[0].strip() for m in re.finditer(rf"^\s*{re.escape(example)}:.*$", readme, re.M)]
    return [*lines, f"Verification: {fields.get('verification', '')}"]


def main_context() -> int:
    """Never fails: whatever goes wrong is a warning, the rules are always printed."""
    lines: list[str] = []
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        branch = os.environ.get("GITHUB_HEAD_REF") or git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
        lines = context(root, branch)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"gate: aviso: no puedo leer la tarea: {error}", file=sys.stderr)
    print("\n".join([*(l for l in lines if l), RULES]))
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--context"]:
        return main_context()
    if any(a != "--require-task" for a in argv):
        print("usage: gate.py [--require-task | --context]", file=sys.stderr)
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
