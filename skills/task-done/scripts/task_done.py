#!/usr/bin/env python3
"""Run a task's verification and tick it in tasks.md only if it passes.

Usage:
  task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]

  TASK_ID is the label at the start of the task line (T3, W2...).
  COMMAND runs without a shell; for pipes or &&, pass `bash -c "..."`.

Warns on stderr if COMMAND does not contain the verification declared in the
task. Prints the tail of the output, then the command and its exit status; no
log file is kept. Exit status: the command's. A failing command leaves
tasks.md untouched.

Test protection: if the task declares its examples (`tests: E1, E2`), before
running COMMAND it checks in git that
  - there is a red commit `test(T3): ...` since tasks.md was added,
  - the red commits add a line naming each example (E1, E2...),
  - no later commit (except red commits of other tasks) nor the uncommitted
    changes remove or change a line of the files the red commits touched.
If any of these fails, COMMAND is not run, tasks.md is untouched and the exit
status is 3.
"""

import re
import shlex
import subprocess
import sys
from pathlib import Path

TAIL = 40
PROTECTION_FAILED = 3


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
    sys.exit(2)


def task_block(lines: list[str], index: int) -> str:
    """The task line and its indented continuation lines, joined."""
    block = [lines[index]]
    for line in lines[index + 1 :]:
        if not line[:1].isspace() or not line.strip() or re.match(r"\s*- \[", line):
            break
        block.append(line)
    return " ".join(" ".join(block).split())


def declared_verification(block: str) -> str:
    """Text after 'verification:' in the task block, without backticks if quoted."""
    match = re.search(r"verification:\s*(.+)", block)
    if not match:
        return ""
    text = match.group(1).strip()
    quoted = re.search(r"`([^`]+)`", text)
    return " ".join((quoted.group(1) if quoted else text).split())


def declared_examples(block: str) -> list[str]:
    """Example IDs after 'tests:' (E1, E2...), up to the next '—' field."""
    match = re.search(r"tests:\s*([^—]+)", block)
    if not match:
        return []
    return re.findall(r"(?<![A-Za-z0-9_])([A-Z]+\d+)(?![A-Za-z0-9])", match.group(1).replace("`", " "))


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def hunk_lines(diff: str, sign: str) -> dict[str, list[str]]:
    """Lines starting with sign ('+' added, '-' removed) per file in a git diff."""
    found: dict[str, list[str]] = {}
    current, in_hunk = "", False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            current, in_hunk = line.split(" b/", 1)[-1], False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith(sign):
            found.setdefault(current, []).append(line[1:])
    return found


def check_protection(tasks: Path, task_id: str, examples: list[str]) -> list[str]:
    """Problems with the red commit of task_id; an empty list if its tests are protected."""
    try:
        root = Path(git(tasks.parent, "rev-parse", "--show-toplevel").strip())
        rel = tasks.resolve().relative_to(root.resolve()).as_posix()
        # Only commits since tasks.md was added belong to this work item: T<n> IDs repeat across work items.
        added = git(root, "log", "--diff-filter=A", "--format=%H", "--", rel).split()
        log = git(root, "log", "--reverse", "--format=%H %s", "HEAD").splitlines()
        commits = [(sha, subject) for sha, _, subject in (line.partition(" ") for line in log)]
        shas = [sha for sha, _ in commits]
        if added and added[-1] in shas:
            commits = commits[shas.index(added[-1]) :]
        return protection_problems(root, commits, task_id, examples)
    except (OSError, RuntimeError, ValueError) as error:
        return [f"cannot read the git history: {error}"]


def protection_problems(root: Path, commits: list[tuple[str, str]], task_id: str, examples: list[str]) -> list[str]:
    """commits: (sha, subject), oldest first."""
    red_subject = re.compile(r"^test\(([A-Z]+\d+)\):")
    red = [i for i, (_, subject) in enumerate(commits) if (m := red_subject.match(subject)) and m.group(1) == task_id]
    if not red:
        return [f"no red commit 'test({task_id}): ...' found: commit the failing tests before the implementation"]

    problems: list[str] = []
    protected: set[str] = set()
    added_lines: list[str] = []
    for i in red:
        sha = commits[i][0]
        protected.update(git(root, "show", "--format=", "--name-only", sha).splitlines())
        for lines in hunk_lines(git(root, "show", "--format=", "-U0", sha), "+").values():
            added_lines += lines
    for example in examples:
        if not any(re.search(rf"(?<![A-Za-z0-9]){example}(?![0-9])", line) for line in added_lines):
            problems.append(f"{example} has no test in the red commit (no added line names {example})")

    paths = sorted(protected)
    if not paths:
        return problems
    for sha, subject in commits[red[0] + 1 :]:
        m = red_subject.match(subject)
        if m and m.group(1) != task_id:
            continue  # red commit of another task: it may add tests to the same files
        for path, removed in hunk_lines(git(root, "show", "--format=", "-U0", sha, "--", *paths), "-").items():
            problems.append(
                f"commit {sha[:8]} '{subject}' removes or changes {len(removed)} line(s) of {path}, a test file of the red commit"
            )
    for path, removed in hunk_lines(git(root, "diff", "-U0", "HEAD", "--", *paths), "-").items():
        problems.append(
            f"uncommitted changes remove or change {len(removed)} line(s) of {path}, a test file of the red commit"
        )
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[2] != "--":
        usage("wrong arguments")
    tasks, task_id, command = Path(argv[0]), argv[1], argv[3:]
    if not re.fullmatch(r"[A-Z]+\d+", task_id):
        usage(f"TASK_ID must look like T3 or W2, got '{task_id}'")
    if not tasks.is_file():
        usage(f"{tasks} does not exist")

    lines = tasks.read_text(encoding="utf-8").splitlines(keepends=True)
    pattern = re.compile(rf"^(\s*- )\[([ xX])\]( {re.escape(task_id)}\.)")
    matches = [i for i, line in enumerate(lines) if pattern.match(line)]
    if len(matches) != 1:
        usage(f"expected one '- [ ] {task_id}.' line in {tasks}, found {len(matches)}")
    index = matches[0]
    already_done = pattern.match(lines[index]).group(2) != " "

    block = task_block(lines, index)
    examples = declared_examples(block)
    if examples:
        problems = check_protection(tasks, task_id, examples)
        for problem in problems:
            print(f"task_done: {problem}")
        if problems:
            print(f"✘ {task_id} NOT marked: the tests of its red commit are not protected.")
            return PROTECTION_FAILED
        print(f"--- red commit of {task_id} found; {', '.join(examples)} have tests and they are untouched")

    shown = shlex.join(command)
    declared = declared_verification(block)
    if not declared or declared not in " ".join(" ".join(command).split()):
        print(
            f"task_done: warning: {task_id} declares verification '{declared or '(none)'}', "
            f"but the command run is '{shown}'",
            file=sys.stderr,
        )

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError:
        print(f"task_done: command not found: {command[0]}", file=sys.stderr)
        return 127

    output = result.stdout.splitlines()
    if len(output) > TAIL:
        print(f"--- ({len(output) - TAIL} earlier lines omitted)")
    if output:
        print("\n".join(output[-TAIL:]))
    print(f"--- command: {shown} → exit {result.returncode}")

    if result.returncode != 0:
        print(f"✘ {task_id} NOT marked: the verification failed.")
        return result.returncode
    if already_done:
        print(f"✔ {task_id} was already marked [x]; verification still green.")
        return 0
    lines[index] = pattern.sub(r"\1[x]\3", lines[index], count=1)
    tasks.write_text("".join(lines), encoding="utf-8")
    print(f"✔ {task_id} marked [x] in {tasks}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
