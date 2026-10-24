#!/usr/bin/env python3
"""Run a task's verification and tick it in tasks.md or in a GitHub issue only if it passes.

Usage:
  task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]
  task_done.py --issue [NUMBER] TASK_ID -- COMMAND [ARGS...]

  TASK_ID is the label at the start of the task line (T3, W2...).
  COMMAND runs without a shell; for pipes or &&, pass `bash -c "..."`.
  --issue reads and edits the task checklist in the body of the issue with gh.
  Without NUMBER, the issue is the number the current branch name starts with
  (`42-cancel-trip`, `feat/42-cancel-trip`), as `gh issue develop` names it.

Warns on stderr if COMMAND does not contain the verification declared in the
task. Prints the tail of the output, then the command and its exit status; no
log file is kept. Exit status: the command's. A failing command leaves the
checklist untouched. Exit 2: wrong call, or the issue cannot be read (no gh,
no network). Exit 4: the verification passed but the issue could not be edited.

Test protection: if the task declares its examples (`tests: E1, E2`), before
running COMMAND it checks in git that
  - there is a red commit `test(T3): ...` since tasks.md was added (for an
    issue: on the current branch, since the base branch),
  - the red commits add a line naming each example (E1, E2...),
  - no later commit (except red commits of other tasks) nor the uncommitted
    changes remove or change a line of the files the red commits touched.
If any of these fails, COMMAND is not run, the checklist is untouched and the
exit status is 3.
"""

import json
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

TAIL = 40
PROTECTION_FAILED = 3
ISSUE_NOT_EDITED = 4


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
    print("       task_done.py --issue [NUMBER] TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
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
    """Text after 'verification:' (or 'verificación:') in the task block, without backticks if quoted."""
    match = re.search(r"(?:verification|verificación):\s*(.+)", block)
    if not match:
        return ""
    text = match.group(1).strip()
    quoted = re.search(r"`([^`]+)`", text)
    # Unquoted, it ends at the next '—' field (`— level: A`).
    return " ".join((quoted.group(1) if quoted else text.split("—")[0]).split())


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


class TasksFile:
    """A tasks.md file; its work item starts with the commit that added it."""

    def __init__(self, path: Path) -> None:
        self.path, self.label = path, str(path)

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8")

    def tick(self, update: Callable[[str], str]) -> None:
        self.path.write_text(update(self.read()), encoding="utf-8")

    def commits(self) -> tuple[Path, list[tuple[str, str]]]:
        root = Path(git(self.path.parent, "rev-parse", "--show-toplevel").strip())
        rel = self.path.resolve().relative_to(root.resolve()).as_posix()
        # Only commits since tasks.md was added belong to this work item: T<n> IDs repeat across work items.
        added = git(root, "log", "--diff-filter=A", "--format=%H", "--", rel).split()
        commits = log(root, "HEAD")
        shas = [sha for sha, _ in commits]
        if added and added[-1] in shas:
            commits = commits[shas.index(added[-1]) :]
        return root, commits


class Issue:
    """The task checklist in the body of a GitHub issue, read and edited with gh."""

    def __init__(self, number: str) -> None:
        self.number, self.label = number, f"issue #{number}"

    def gh(self, *args: str, stdin: str | None = None) -> str:
        try:
            result = subprocess.run(["gh", "issue", *args], input=stdin, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            raise RuntimeError("gh is not installed") from None
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"gh exited with {result.returncode}")
        return result.stdout

    def read(self) -> str:
        return str(json.loads(self.gh("view", self.number, "--json", "body"))["body"])

    def tick(self, update: Callable[[str], str]) -> None:
        # Read it again: the person may have edited the issue while the verification ran.
        self.gh("edit", self.number, "--body-file", "-", stdin=update(self.read()))

    def commits(self) -> tuple[Path, list[tuple[str, str]]]:
        # The work item is the branch: T<n> IDs repeat across issues, so only commits since the base branch count.
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        return root, log(root, f"{base_branch(root)}..HEAD")


def branch_issue() -> str:
    """Issue number the current branch name starts with (42-x, feat/42-x, issue-42), or exit 2."""
    try:
        branch = git(Path.cwd(), "rev-parse", "--abbrev-ref", "HEAD").strip()
    except (OSError, RuntimeError) as error:
        usage(f"no issue number given and cannot read the current branch: {error}")
    match = re.search(r"(?:^|/)(?:issue-|gh-)?(\d+)(?:-|$)", branch)
    if not match:
        usage(f"no issue number given and branch '{branch}' does not start with one: pass --issue NUMBER")
    return match.group(1)


def base_branch(root: Path) -> str:
    """The remote default branch if known, else main or master."""
    try:
        candidates = [git(root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD").strip()]
    except RuntimeError:
        candidates = []
    for ref in [*candidates, "origin/main", "origin/master", "main", "master"]:
        try:
            git(root, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}")
            return ref
        except RuntimeError:
            continue
    raise RuntimeError("no base branch found (origin/HEAD, main or master)")


def log(root: Path, revisions: str) -> list[tuple[str, str]]:
    """(sha, subject) of the commits in revisions, oldest first."""
    lines = git(root, "log", "--reverse", "--format=%H %s", revisions).splitlines()
    return [(sha, subject) for sha, _, subject in (line.partition(" ") for line in lines)]


def check_protection(source: "TasksFile | Issue", task_id: str, examples: list[str]) -> list[str]:
    """Problems with the red commit of task_id; an empty list if its tests are protected."""
    try:
        root, commits = source.commits()
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


def task_pattern(task_id: str) -> re.Pattern[str]:
    return re.compile(rf"^(\s*- )\[([ xX])\]( {re.escape(task_id)}\.)")


def find_task(lines: list[str], task_id: str, label: str) -> int:
    """Index of the only '- [ ] <task_id>.' line, or exit 2."""
    pattern = task_pattern(task_id)
    matches = [i for i, line in enumerate(lines) if pattern.match(line)]
    if len(matches) != 1:
        usage(f"expected one '- [ ] {task_id}.' line in {label}, found {len(matches)}")
    return matches[0]


def main(argv: list[str]) -> int:
    rest = list(argv)
    source: TasksFile | Issue
    if rest[:1] == ["--issue"]:
        rest.pop(0)
        number = rest.pop(0).lstrip("#") if rest and re.fullmatch(r"#?\d+", rest[0]) else branch_issue()
        source = Issue(number)
    else:
        if not rest:
            usage("wrong arguments")
        source = TasksFile(Path(rest.pop(0)))
        if not source.path.is_file():
            usage(f"{source.path} does not exist")
    if len(rest) < 3 or rest[1] != "--":
        usage("wrong arguments")
    task_id, command = rest[0], rest[2:]
    if not re.fullmatch(r"[A-Z]+\d+", task_id):
        usage(f"TASK_ID must look like T3 or W2, got '{task_id}'")

    try:
        text = source.read()
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        usage(f"cannot read {source.label}: {error}. Without gh or network, use a tasks.md (see SKILL.md)")
    lines = text.splitlines(keepends=True)
    index = find_task(lines, task_id, source.label)
    pattern = task_pattern(task_id)
    already_done = pattern.match(lines[index]).group(2) != " "

    block = task_block(lines, index)
    examples = declared_examples(block)
    if examples:
        problems = check_protection(source, task_id, examples)
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

    def tick(current: str) -> str:
        fresh = current.splitlines(keepends=True)
        i = find_task(fresh, task_id, source.label)
        fresh[i] = pattern.sub(r"\1[x]\3", fresh[i], count=1)
        return "".join(fresh)

    try:
        source.tick(tick)
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"✘ {task_id} NOT marked: the verification passed, but {source.label} could not be edited: {error}")
        return ISSUE_NOT_EDITED
    print(f"✔ {task_id} marked [x] in {source.label}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
