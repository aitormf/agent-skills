#!/usr/bin/env python3
"""Run a task's verification and tick it in tasks.md only if it passes.

Usage:
  task_done.py [TASKS_FILE] TASK_ID -- COMMAND [ARGS...]
  task_done.py --audit [TASKS_FILE]

  TASK_ID is the label at the start of the task line (T3, W2...).
  COMMAND runs without a shell; for pipes or &&, pass `bash -c "..."`.
  Without TASKS_FILE, it is docs/changes/<last segment of the current branch>/tasks.md
  (`feat/42-cancel-trip` -> docs/changes/42-cancel-trip/tasks.md), from the repo root.

Warns on stderr if COMMAND does not contain the verification declared in the
task. Prints the tail of the output, then the command and its exit status; no
log file is kept. Exit status: the command's. A failing command leaves the
checklist untouched. Exit 2: wrong call, or no tasks.md where it was searched.
When the last task is ticked, `status: open` in the frontmatter becomes `status: done`.
Exit 2 also if the base branch already has this tasks.md with `status: done`: the
folder is a finished change of an earlier branch with the same last segment.

Test protection: if the task declares its examples (`tests: E1, E2`), before
running COMMAND it checks in git, among the commits of the current branch that
are not in the base branch (origin/HEAD, else origin/main, origin/master, main
or master), that
  - there is a red commit `test(T3): ...`,
  - the red commits add a line naming each example (E1, E2...),
  - no later commit (red commits of other tasks and merges included) nor the
    uncommitted changes remove or change a non-blank line the red commits added.
    Lines are followed by identity (git blame), not by text: other lines of those
    files may change, even with the same text, and new tests may be added.
    Renaming the whole file keeps the protection; moving lines elsewhere does not.
If any of these fails, or no base branch is found, COMMAND is not run, the
checklist is untouched and the exit status is 3.

--audit (read-only, for the review): runs no command and edits nothing. It
checks the test protection of every task with examples that is ticked or has
a red commit (committed history only), and that every example of the example
map (`E1: ...` lines) is in some task's `tests:`. Unticked tasks without a red
commit are reported as pending. Exit status: 0 if nothing is wrong, 3 if
something is (PROBLEM lines, also when no base branch is found), 2 if the call
is wrong or the checklist cannot be read.
"""

import re
import shlex
import subprocess
import sys
from pathlib import Path

TAIL = 40
RED_SUBJECT = re.compile(r"^test\(([A-Z]+\d+)\):")
TASK_LINE = re.compile(r"^\s*- \[([ xX])\] ([A-Z]+\d+)\.")
MAP_EXAMPLE = re.compile(r"^\s*(?:[-*]\s+)?(E\d+)\s*:")
PROTECTION_FAILED = 3
STATUS_LINE = re.compile(r"^status:[^\n]*", re.MULTILINE)
BLAME_HEADER = re.compile(r"^([0-9a-f]{40,64}) (\d+) \d+(?: \d+)?$")


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py [TASKS_FILE] TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
    print("       task_done.py --audit [TASKS_FILE]", file=sys.stderr)
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
    # core.quotePath=false: paths with non-ASCII characters (test_canción.py) come out as they are.
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(root), *args],
        capture_output=True,
        encoding="utf-8",
        errors="surrogateescape",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def branch_tasks_file() -> Path:
    """docs/changes/<last segment of the current branch>/tasks.md, or exit 2 naming the path searched."""
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    except (OSError, RuntimeError) as error:
        usage(f"no TASKS_FILE given and cannot read the current branch: {error}")
    if branch == "HEAD":
        usage("no TASKS_FILE given and HEAD is detached (no branch name): pass the path of tasks.md")
    path = root / "docs" / "changes" / branch.rsplit("/", 1)[-1] / "tasks.md"
    if not path.is_file():
        usage(f"no TASKS_FILE given and {path} does not exist (from branch '{branch}'): pass the path of tasks.md")
    return path


def base_branch(root: Path) -> str:
    """The remote default branch if known, else origin/main, origin/master, main or master."""
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
    raise RuntimeError("no base branch found (origin/HEAD, origin/main, origin/master, main or master)")


def refuse_finished(path: Path) -> None:
    """Exit 2 if the base branch already has this tasks.md with `status: done` (a finished, merged change)."""
    try:
        folder = path.resolve().parent
        base = base_branch(folder)
        text = git(folder, "show", f"{base}:./{path.name}")
    except (OSError, RuntimeError):
        return  # not in git, no base branch or not in the base branch: not a finished change
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if match and re.search(r"^status:\s*done\b", match.group(1), re.MULTILINE):
        usage(
            f"{path} is a finished change already in {base} (status: done): "
            "this branch reuses its folder; rename the branch (git branch -m <type>/<other-name>)"
        )


def branch_commits(path: Path) -> tuple[Path, str, list[tuple[str, list[str], str]]]:
    """(repo root, base branch, (sha, parents, subject) of the branch's commits not in the base branch).

    Parents come before their children. One branch, one change: T<n> and E<n> IDs repeat across
    changes, so only these commits count.
    """
    root = Path(git(path.resolve().parent, "rev-parse", "--show-toplevel").strip())
    base = base_branch(root)
    lines = git(root, "log", "--reverse", "--topo-order", "--format=%H%x00%P%x00%s", f"{base}..HEAD").split("\n")
    commits = []
    for line in filter(None, lines):
        sha, parents, subject = line.split("\0", 2)
        commits.append((sha, parents.split(), subject))
    return root, base, commits


def check_protection(path: Path, task_id: str, examples: list[str]) -> list[str]:
    """Problems with the red commit of task_id; an empty list if its tests are protected."""
    try:
        root, base, commits = branch_commits(path)
        return protection_problems(root, base, commits, task_id, examples)
    except (OSError, RuntimeError, ValueError) as error:
        return [f"PROBLEM: cannot read the git history of the branch: {error}"]


def blamed(root: Path, rev: str | None, path: str, red: str) -> dict[int, str]:
    """{line number in red's version of the file: text} of the lines of path at rev (None: the worktree) from red.

    git blame follows each line, not its text, through later edits and renames of the whole file.
    """
    # --ignore-revs-file=: a blame.ignoreRevsFile of the repo must not hand a changed line back to the red commit.
    out = git(root, "blame", "--porcelain", "--ignore-revs-file=", *([rev] if rev else []), "--", path)
    found, sha, number = {}, "", 0
    for line in out.split("\n"):
        if line.startswith("\t"):
            if sha == red:
                found[number] = line[1:]
        elif match := BLAME_HEADER.match(line):
            sha, number = match.group(1), int(match.group(2))
    return found


def moved(root: Path, parent: str, sha: str) -> dict[str, str | None]:
    """The paths sha changes from parent: {path in parent: path in sha, None if deleted}."""
    fields = iter(git(root, "diff", "--name-status", "-z", "-M", parent, sha, "--").split("\0"))
    found: dict[str, str | None] = {}
    for status in fields:
        if not status:
            break
        path = next(fields)
        new = next(fields) if status[0] in "RC" else path  # renamed or copied: two paths
        found[path] = None if status == "D" else new if status[0] == "R" else path
    return found


def numbers(lines: set[int]) -> str:
    """'1, 3-5, 9'"""
    ranges: list[list[int]] = []
    for n in sorted(lines):
        if ranges and n == ranges[-1][1] + 1:
            ranges[-1][1] = n
        else:
            ranges.append([n, n])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in ranges)


def lost_lines(who: str, key: tuple[str, str], path: str, lost: set[int]) -> str:
    red, red_path = key
    return (
        f"{who} removes or changes {len(lost)} line(s) of {path} added by the red commit {red[:8]} "
        f"(line(s) {numbers(lost)} of `git show {red[:8]}:{red_path}`)"
    )


def protection_problems(
    root: Path,
    base: str,
    commits: list[tuple[str, list[str], str]],
    task_id: str,
    examples: list[str],
    worktree: bool = True,
) -> list[str]:
    """commits: (sha, parents, subject) of the branch, parents first. worktree: also check the uncommitted changes."""
    red = [sha for sha, _, subject in commits if (m := RED_SUBJECT.match(subject)) and m.group(1) == task_id]
    if not red:
        return [
            (
                f"no red commit 'test({task_id}): ...' among the commits of this branch since {base}: "
                "commit the failing tests before the implementation"
            )
        ]

    problems: list[str] = []
    # The lines each red commit added, per (red commit, file), by their number in the red commit's version.
    added: dict[tuple[str, str], dict[int, str]] = {}
    for sha in red:
        for path in git(root, "show", "--format=", "--name-only", "-z", "-M", "--diff-filter=d", sha).split("\0"):
            if path:
                added[(sha, path)] = blamed(root, sha, path, sha)
    for example in examples:
        if not any(
            re.search(rf"(?<![A-Za-z0-9]){example}(?![0-9])", line)
            for lines in added.values()
            for line in lines.values()
        ):
            problems.append(f"{example} has no test in the red commit (no added line names {example})")

    # Only the non-blank lines the red commits added are protected, followed by identity (git blame), not by text:
    # a line with the same text elsewhere in the file is not one of them. No exemption, not even for the red commit
    # of another task: adding tests or changing the file's other lines is fine, changing these is not.
    protected = {key: {n for n, line in lines.items() if line.strip()} for key, lines in added.items()}
    # Per commit: for each (red commit, its path), the path of that file in the commit and the protected lines left.
    alive: dict[str, dict[tuple[str, str], tuple[str, set[int]]]] = {}
    for sha, parents, subject in commits:
        here: dict[tuple[str, str], tuple[str, set[int]]] = {}
        inherited: dict[tuple[str, str], list[tuple[str, set[int], dict[str, str | None]]]] = {}
        for parent in parents:
            changes = None
            for key, (path, left) in alive.get(parent, {}).items():
                changes = changes if changes is not None else moved(root, parent, sha)
                inherited.setdefault(key, []).append((path, left, changes))
        for key, sources in inherited.items():
            if len(sources) == 1 and sources[0][0] not in sources[0][2]:
                here[key] = sources[0][:2]  # the file is as its only parent left it
                continue
            # A merge (several parents) loses a line only if every parent still had it.
            before = set.intersection(*(left for _, left, _ in sources))
            paths = [new for path, _, changes in sources if (new := changes.get(path, path))]
            if paths:
                left = set(blamed(root, sha, paths[0], key[0])) & protected[key]
                here[key] = (paths[0], left)
                if lost := before - left:
                    problems.append(lost_lines(f"commit {sha[:8]} '{subject}'", key, paths[0], lost))
            elif before:
                problems.append(
                    f"commit {sha[:8]} '{subject}' deletes {sources[0][0]}, with {len(before)} line(s) added by "
                    f"the red commit {key[0][:8]} (moving them to another file counts as deleting them)"
                )
        for key, lines in protected.items():
            if key[0] == sha:
                here[key] = (key[1], lines)
        alive[sha] = here

    if not worktree:
        return problems
    for key, (path, left) in alive.get(git(root, "rev-parse", "HEAD").strip(), {}).items():
        if not left:
            continue
        if not (root / path).is_file():
            problems.append(
                f"uncommitted changes delete {path}, with {len(left)} line(s) added by the red commit {key[0][:8]}"
            )
        elif lost := left - set(blamed(root, None, path, key[0])):
            problems.append(lost_lines("uncommitted changes", key, path, lost))
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


def set_done(text: str) -> str:
    """text with `status: done` in its frontmatter if every task is ticked; unchanged otherwise or without a status."""
    lines = text.splitlines()
    if any(m.group(1) == " " for line in lines if (m := TASK_LINE.match(line))):
        return text
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return text
    frontmatter = STATUS_LINE.sub("status: done", match.group(1), count=1)
    return text[: match.start(1)] + frontmatter + text[match.end(1) :]


def audit(path: Path) -> int:
    """Read-only check of every task of the checklist, for the review. Runs no command, edits nothing."""
    refuse_finished(path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError) as error:
        usage(f"cannot read {path}: {error}")
    tasks = [(i, m) for i, line in enumerate(lines) if (m := TASK_LINE.match(line))]
    if not tasks:
        usage(f"no '- [ ] T1.' checklist in {path}")
    try:
        root, base, commits = branch_commits(path)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"PROBLEM: cannot read the git history of the branch: {error}")
        print(f"--- audit of {path}: not checked; 1 problem(s)")
        return PROTECTION_FAILED
    with_red = {m.group(1) for _, _, subject in commits if (m := RED_SUBJECT.match(subject))}

    problems, assigned, done = 0, set(), 0
    for i, m in tasks:
        task_id, ticked = m.group(2), m.group(1) != " "
        done += ticked
        examples = declared_examples(task_block(lines, i))
        assigned.update(examples)
        mark = "[x]" if ticked else "[ ]"
        if not examples:
            print(f"{task_id} {mark}: no examples declared")
            continue
        if not ticked and task_id not in with_red:
            print(f"{task_id} {mark}: pending, no red commit yet ({', '.join(examples)})")
            continue
        try:
            found = protection_problems(root, base, commits, task_id, examples, worktree=False)
        except (OSError, RuntimeError, ValueError) as error:
            found = [f"cannot read the git history: {error}"]
        for problem in found:
            print(f"{task_id} {mark}: PROBLEM: {problem}")
        if not found:
            print(f"{task_id} {mark}: ok, the red commit tests {', '.join(examples)}, untouched since")
        problems += len(found)

    task_lines = {i for i, _ in tasks}
    mapped = [m.group(1) for i, line in enumerate(lines) if i not in task_lines and (m := MAP_EXAMPLE.match(line))]
    for example in dict.fromkeys(mapped):
        if example not in assigned:
            print(f"{example}: PROBLEM: in the example map but in no task's tests:")
            problems += 1

    print(f"--- audit of {path} (branch since {base}): {len(tasks)} tasks, {done} ticked; {problems} problem(s)")
    return PROTECTION_FAILED if problems else 0


def main(argv: list[str]) -> int:
    rest = list(argv)
    audit_only = rest[:1] == ["--audit"]
    if audit_only:
        rest.pop(0)
        if len(rest) > 1:
            usage("--audit takes only the path of tasks.md")
        return audit(Path(rest[0]) if rest else branch_tasks_file())
    # TASK_ID -- COMMAND, or TASKS_FILE TASK_ID -- COMMAND.
    if len(rest) >= 3 and rest[1] == "--":
        path = branch_tasks_file()
    elif len(rest) >= 4 and rest[2] == "--":
        path = Path(rest.pop(0))
    else:
        usage("wrong arguments")
    if not path.is_file():
        usage(f"{path} does not exist")
    refuse_finished(path)
    task_id, command = rest[0], rest[2:]
    if not re.fullmatch(r"[A-Z]+\d+", task_id):
        usage(f"TASK_ID must look like T3 or W2, got '{task_id}'")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        usage(f"cannot read {path}: {error}")
    lines = text.splitlines(keepends=True)
    index = find_task(lines, task_id, str(path))
    pattern = task_pattern(task_id)
    already_done = pattern.match(lines[index]).group(2) != " "

    block = task_block(lines, index)
    examples = declared_examples(block)
    if examples:
        problems = check_protection(path, task_id, examples)
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

    # Read it again: the person may have edited the file while the verification ran.
    fresh = path.read_text(encoding="utf-8").splitlines(keepends=True)
    i = find_task(fresh, task_id, str(path))
    fresh[i] = pattern.sub(r"\1[x]\3", fresh[i], count=1)
    ticked = "".join(fresh)
    finished = set_done(ticked)
    path.write_text(finished, encoding="utf-8")
    print(f"✔ {task_id} marked [x] in {path}.")
    if finished != ticked:
        print(f"✔ every task is ticked: status: done in {path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
