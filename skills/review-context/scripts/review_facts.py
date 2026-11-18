#!/usr/bin/env python3
"""Facts of a branch for the review, gathered without a model (D-0057).

    python3 review_facts.py [<base>]     # from the repo root

Prints the base (the argument; else the "Base branch" of the Code review section of AGENTS.md; else
origin/HEAD, main or master; `origin/<base>` when it exists), the branch, `git log <base>..HEAD`,
`git diff --stat <base>...HEAD` and a warning about uncommitted changes. With no commits ahead of the
base it prints "sin cambios frente a <base>" and exits 0. Then the task of the branch (`<change>/T<n>` or
`<change>/plan`, as gate.py reads it): "tarea: <file> (<status>)" and the output and exit code of
`task_done.py --audit` (../../task-done/scripts, next to this skill); "tarea: ninguna" with no change folder,
and "auditoría: no comprobada (<reason>)" if the audit cannot run. Then:

Section "TODO sin ticket": the TODO, FIXME, XXX and HACK comments that `git diff <base>...HEAD`
adds, with no ticket on the same line, one `file:line` per line. A ticket is `#<n>`,
`<PROJECT>-<n>` or a URL. Only the comment shape counts: the word in capitals, then `:`
(optionally `(...)` between). Lockfiles (those of diff_size.py) and deleted files are skipped.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock",
             "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}
MARK = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b(?:\([^)]*\))?:")
TICKET = re.compile(r"#\d+|\b[A-Z][A-Z0-9]*-\d+\b|https?://")
HUNK = re.compile(r"^@@ -\S+ \+(\d+)")
BASE_LINE = re.compile(r"^\s*[-*]?\s*Base branch:\s*`?([^\s`<]+)", re.I)
# Neutralise the user's git config (prefixes, colour, signatures, pagers, pretty formats).
GIT = ["git", "-c", "core.quotepath=off", "-c", "color.ui=never", "-c", "diff.noprefix=false",
       "-c", "diff.mnemonicPrefix=false", "-c", "log.showSignature=false", "-c", "log.decorate=no",
       "-c", "status.short=false", "-c", "core.pager=cat"]


def git(*args):
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_PAGER": "cat"}
    return subprocess.run([*GIT, *args], capture_output=True, text=True, env=env)


def ref_exists(ref):
    return git("rev-parse", "--verify", "-q", f"{ref}^{{commit}}").returncode == 0


def agents_base():
    try:
        text = open("AGENTS.md", encoding="utf-8").read()
    except OSError:
        return None
    inside = False
    for text_line in text.splitlines():
        if m := re.match(r"^(#+)\s", text_line):
            inside = bool(re.search(r"code review", text_line, re.I))
        elif inside and (m := BASE_LINE.match(text_line)):
            return m.group(1)
    return None


def resolve_base(arg):
    base = arg or agents_base()
    if not base:
        head = git("symbolic-ref", "-q", "refs/remotes/origin/HEAD").stdout.strip()
        base = head.removeprefix("refs/remotes/origin/") if head else None
    if not base:
        base = next((b for b in ("main", "master") if ref_exists(b) or ref_exists(f"origin/{b}")), None)
    if not base:
        sys.exit("review_facts: no base branch found; pass it as an argument")
    remote = f"origin/{base}"
    return remote if not base.startswith("origin/") and ref_exists(remote) else base


def todos_without_ticket(base):
    run = git("diff", "-U0", "--no-ext-diff", "--no-textconv", "--no-color",
              "--src-prefix=a/", "--dst-prefix=b/", "-M", f"{base}...HEAD", "--")
    if run.returncode:
        sys.exit(f"review_facts: git diff failed: {run.stderr.strip()}")
    found, path, line = [], None, 0
    for text in run.stdout.splitlines():
        if text.startswith("+++ "):
            path = text[6:] if text.startswith("+++ b/") else None
            if path and path.rsplit("/", 1)[-1] in LOCKFILES:
                path = None
        elif m := HUNK.match(text):
            line = int(m.group(1))
        elif path and text.startswith("+"):
            if MARK.search(text) and not TICKET.search(text):
                found.append(f"{path}:{line}")
            line += 1
    return found


def task_facts():
    """The task or plan of the branch and the read-only audit of task-done (R3, D-0032)."""
    scripts = Path(__file__).resolve().parents[2] / "task-done" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        from board import TASK_ID  # the id shape gate.py uses
    except ImportError:
        TASK_ID = re.compile(r"T\d+")
    names = git("branch", "--show-current").stdout.strip().split("/")
    folder = Path("docs/changes") / names[-2] if len(names) > 1 else None
    task = names[-1]
    if not folder or not folder.is_dir() or not (task == "plan" or TASK_ID.fullmatch(task)):
        return print("tarea: ninguna")
    found = next((folder / "tasks").glob(f"{task}-*.md"), None) if task != "plan" else folder / "README.md"
    if not found or not found.is_file():
        return print(f"tarea: {task} sin fichero en {folder}/")
    status = re.search(r"^status:\s*(\S+)", found.read_text(encoding="utf-8"), re.M)
    print(f"tarea: {found.as_posix()} ({status[1] if status else 'sin estado'})")
    script = scripts / "task_done.py"
    if not script.is_file():
        return print(f"auditoría: no comprobada (no encuentro {script})")
    try:
        audit = subprocess.run([sys.executable, str(script), "--audit", str(folder), *([] if task == "plan" else [task])],
                               capture_output=True, text=True)
    except OSError as error:
        return print(f"auditoría: no comprobada ({error})")
    if audit.returncode not in (0, 3):
        return print(f"auditoría: no comprobada (sale {audit.returncode}: {(audit.stderr or audit.stdout).strip()})")
    print(f"auditoría: código {audit.returncode}\n{audit.stdout.rstrip()}")


def main():
    if len(sys.argv) > 2:
        sys.exit("usage: review_facts.py [<base>]")
    base = resolve_base(sys.argv[1] if len(sys.argv) == 2 else None)
    if not ref_exists(base):
        sys.exit(f"review_facts: base '{base}' not found")
    branch = git("branch", "--show-current").stdout.strip() or "(HEAD suelto)"
    print(f"base: {base}\nrama: {branch}")
    dirty = git("status", "--porcelain", "--untracked-files=normal").stdout.strip()
    if dirty:
        print("hay cambios sin commit: los cambios sin commit no se revisan ni se suben")
    log = git("log", "--no-show-signature", "--no-decorate", "--format=%h %s%n%b", f"{base}..HEAD", "--")
    if log.returncode:
        sys.exit(f"review_facts: git log failed: {log.stderr.strip()}")
    if not log.stdout.strip():
        print(f"sin cambios frente a {base}")
        return 0
    print("log base..HEAD:\n" + log.stdout.rstrip())
    stat = git("diff", "--stat=1000", "--no-ext-diff", "--no-color", f"{base}...HEAD", "--")
    if stat.returncode:
        sys.exit(f"review_facts: git diff failed: {stat.stderr.strip()}")
    print("diff --stat:\n" + stat.stdout.rstrip())
    task_facts()
    print("TODO sin ticket:")
    print("\n".join(todos_without_ticket(base)) or "ninguno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
