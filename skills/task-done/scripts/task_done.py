#!/usr/bin/env python3
"""Run a task's verification and mark it done only if it passes.

Usage:
  task_done.py [CHANGE_DIR | TASK_FILE] [TASK_ID] -- COMMAND [ARGS...]
  task_done.py --audit [CHANGE_DIR | TASK_FILE] [TASK_ID]

  The task is the file CHANGE_DIR/tasks/<TASK_ID>-<slug>.md (TASK_ID: T3); its
  frontmatter has id, title, status (todo | doing | done), depends_on, examples and
  verification. What is not given comes from the current branch, <...>/<change>/T<n>:
  the change folder is docs/changes/<change>/ (the second-to-last segment), from the
  repo root, and the task is T<n> (the last one). <...>/<change>/plan is the plan
  branch: it has no task to mark. COMMAND runs without a shell; for pipes or &&,
  pass `bash -c "..."`.

Warns on stderr if COMMAND does not contain the task's `verification`. Prints the
tail of the output, then the command and its exit status; no log file is kept.
Exit status: the command's. A failing command leaves the task file untouched; a
passing one sets `status: done` in it, and in the change's README.md once every
task is done here or in the base branch; then spec.md and plan.md, if any, get
`status: obsolete` (D-0006). Exit 2: wrong call, malformed task file,
or no change folder or task file where it was searched. Exit 2 also if the base
branch already has the change's README.md with `status: done`: the folder is a
finished change of an earlier branch with the same name.

Test protection: if the task declares its examples (`examples: [E1, E2]`), before
running COMMAND it checks in git, among the commits of the current branch that
are not in the base branch (origin/HEAD, else origin/main, origin/master, main
or master), that
  - there is a red commit `test(T3): ...`,
  - the red commits add a line naming each example (E1, E2...),
  - the task file still declares the examples it declared at the red commits,
  - no later commit (red commits of other tasks and merges included) nor the
    uncommitted changes remove or change a non-blank line the red commits added.
    Lines are followed by identity (git blame), not by text: other lines of those
    files may change, even with the same text, and new tests may be added.
    Renaming the whole file keeps the protection; moving lines elsewhere does not.
If any of these fails, or no base branch is found, COMMAND is not run, the task
file is untouched and the exit status is 3.

--audit (read-only, for the review): runs no command and edits nothing.
  - On a task (a <change>/T<n> branch, or TASK_ID given): the test protection of
    the task if it is done or has a red commit (committed history only), that its
    examples are in the example map of README.md (`E1: ...` lines), and that its
    depends_on are done in the base branch. A task not done without a red commit
    is reported as pending.
  - On the plan (a <change>/plan branch, or CHANGE_DIR without TASK_ID): the task
    files (frontmatter, ids, no dependency that does not exist, no cycle) and that
    every example of the map is in some task's examples.
Exit status: 0 if nothing is wrong, 3 if something is (PROBLEM lines, also when
no base branch is found), 2 if the call is wrong or the folder or task cannot be found.
"""

import re
import shlex
import subprocess
import sys
from pathlib import Path

from board import (
    TASK_FILE,
    TASK_ID,
    base_branch,
    branch_change,
    git,
    graph_problems,
    load_tasks,
    map_examples,
    number,
    parse_frontmatter,
    parse_task,
    set_status,
    statuses_at,
)

TAIL = 40
RED_SUBJECT = re.compile(r"^test\(([A-Z]+\d+)\):")
PROTECTION_FAILED = 3
BLAME_HEADER = re.compile(r"^([0-9a-f]{40,64}) (\d+) \d+(?: \d+)?$")


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py [CHANGE_DIR | TASK_FILE] [TASK_ID] -- COMMAND [ARGS...]", file=sys.stderr)
    print("       task_done.py --audit [CHANGE_DIR | TASK_FILE] [TASK_ID]", file=sys.stderr)
    sys.exit(2)


def locate(args: list[str], need_task: bool) -> tuple[Path, str | None]:
    """(change folder, task id or None for the plan) from the arguments, the rest from the branch; or exit 2."""
    ids = [a for a in args if TASK_ID.fullmatch(a)]
    paths = [Path(a) for a in args if not TASK_ID.fullmatch(a)]
    if len(ids) > 1 or len(paths) > 1:
        usage("pass at most one change folder (or task file) and one TASK_ID")
    folder, task_id = (paths[0] if paths else None), (ids[0] if ids else None)
    if folder is not None and folder.is_file():
        match = TASK_FILE.fullmatch(folder.name)
        if not match or folder.parent.name != "tasks":
            usage(f"{folder} is not a task file (<change>/tasks/T<n>-<slug>.md) nor a change folder")
        folder, task_id = folder.parent.parent, task_id or match.group(1)
    if folder is None or (need_task and task_id is None):
        try:
            branch_folder, last, branch = branch_change()
        except ValueError as error:
            usage(f"no change folder or task given and {error}: pass them")
        if folder is None:
            folder = branch_folder
            if not folder.is_dir():
                usage(f"{folder} does not exist (from branch '{branch}'): pass the change folder")
        if task_id is None and last != "plan":
            task_id = last
        if need_task and task_id is None:
            usage(f"'{branch}' is the plan branch: it has no task to mark; pass TASK_ID")
    if not folder.is_dir():
        usage(f"{folder} does not exist")
    return folder, task_id


def task_file(folder: Path, task_id: str) -> Path:
    """The only folder/tasks/<task_id>-<slug>.md, or exit 2 naming what was searched."""
    found = [p for p in sorted((folder / "tasks").glob(f"{task_id}*.md")) if TASK_FILE.fullmatch(p.name)]
    found = [p for p in found if TASK_FILE.fullmatch(p.name).group(1) == task_id]
    if len(found) != 1:
        usage(f"expected one {folder / 'tasks' / f'{task_id}-*.md'}, found {len(found)}")
    return found[0]


def read_task(path: Path) -> tuple[str, dict]:
    """(text, fields) of a task file, or exit 2 if it is malformed."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        usage(f"cannot read {path}: {error}")
    fields, problems = parse_task(text, path.name)
    if problems:
        usage(f"{path}: malformed task file: {'; '.join(problems)}")
    return text, fields


def refuse_finished(folder: Path) -> None:
    """Exit 2 if the base branch already has this change's README.md with `status: done` (a finished change)."""
    try:
        base = base_branch(folder.resolve())
        text = git(folder.resolve(), "show", f"{base}:./README.md")
    except (OSError, RuntimeError):
        return  # not in git, no base branch or not in the base branch: not a finished change
    try:
        fields = parse_frontmatter(text) or {}
    except ValueError:
        return
    if fields.get("status") == "done":
        usage(
            f"{folder} is a finished change already in {base} (status: done in its README.md): "
            "this branch reuses its folder; rename the branch (git branch -m <other-change>/T<n>)"
        )


def branch_commits(folder: Path) -> tuple[Path, str, list[tuple[str, list[str], str]]]:
    """(repo root, base branch, (sha, parents, subject) of the branch's commits not in the base branch).

    Parents come before their children. One branch, one task: T<n> and E<n> IDs repeat across
    changes, so only these commits count.
    """
    root = Path(git(folder.resolve(), "rev-parse", "--show-toplevel").strip())
    base = base_branch(root)
    lines = git(root, "log", "--reverse", "--topo-order", "--format=%H%x00%P%x00%s", f"{base}..HEAD").split("\n")
    commits = []
    for line in filter(None, lines):
        sha, parents, subject = line.split("\0", 2)
        commits.append((sha, parents.split(), subject))
    return root, base, commits


def has_red(commits: list[tuple[str, list[str], str]], task_id: str) -> bool:
    return any((m := RED_SUBJECT.match(subject)) and m.group(1) == task_id for _, _, subject in commits)


def check_protection(folder: Path, task_id: str, examples: list[str]) -> list[str]:
    """Problems with the red commit of task_id; an empty list if its tests are protected.

    A task with no examples and no red commit has nothing to protect. One with a red commit is
    always checked, even if its examples were removed from its task file afterwards.
    """
    try:
        root, base, commits = branch_commits(folder)
        if not examples and not has_red(commits, task_id):
            return []
        return protection_problems(root, base, commits, task_id, examples, folder=folder)
    except (OSError, RuntimeError, ValueError) as error:
        if not examples:
            return []
        return [f"PROBLEM: cannot read the git history of the branch: {error}"]


def examples_at(root: Path, sha: str, folder: Path, task_id: str) -> list[str]:
    """The examples task_id declared in its task file as it was at commit sha; [] if it was not there."""
    try:
        rel = folder.resolve().relative_to(root.resolve()).as_posix()
        paths = git(root, "ls-tree", "-z", "--name-only", sha, "--", f"{rel}/tasks/").split("\0")
        found = [p for p in paths if (m := TASK_FILE.fullmatch(p.rsplit("/", 1)[-1])) and m.group(1) == task_id]
        if len(found) != 1:
            return []
        examples = (parse_frontmatter(git(root, "show", f"{sha}:{found[0]}")) or {}).get("examples", [])
    except (RuntimeError, ValueError):
        return []
    return examples if isinstance(examples, list) else []


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
    folder: Path | None = None,
) -> list[str]:
    """commits: (sha, parents, subject) of the branch, parents first. worktree: also check the uncommitted changes.

    folder: the change folder; the examples the task file declared at the red commits stay protected
    even if it no longer declares them.
    """
    red = [sha for sha, _, subject in commits if (m := RED_SUBJECT.match(subject)) and m.group(1) == task_id]
    if not red:
        return [
            (
                f"no red commit 'test({task_id}): ...' among the commits of this branch since {base}: "
                "commit the failing tests before the implementation"
            )
        ]

    problems: list[str] = []
    if folder is not None:
        earlier = list(dict.fromkeys(e for sha in red for e in examples_at(root, sha, folder, task_id)))
        dropped = [e for e in earlier if e not in examples]
        if dropped:
            problems.append(
                f"the task file of {task_id} no longer declares {', '.join(dropped)}, but it did at the red commit: "
                "removing an example is a change of behaviour for the person to decide"
            )
        examples = list(dict.fromkeys(examples + earlier))
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


def all_done(folder: Path) -> bool:
    """Every task of the change is done, in the working tree or in the base branch."""
    tasks, problems = load_tasks(folder)
    if problems or not tasks:
        return False
    try:
        merged = statuses_at(base_branch(folder.resolve()), folder)
    except (OSError, RuntimeError, ValueError):
        merged = {}
    return all(t["status"] == "done" or merged.get(tid) == "done" for tid, t in tasks.items())


def audit_task(folder: Path, task_id: str) -> int:
    """Read-only check of one task, for the review of its branch. Runs no command, edits nothing."""
    path = task_file(folder, task_id)
    try:
        fields, problems = parse_task(path.read_text(encoding="utf-8"), path.name)
    except (OSError, ValueError) as error:
        usage(f"cannot read {path}: {error}")
    status = fields.get("status", "?")
    label = f"{task_id} ({status})"
    found = [f"malformed task file: {problem}" for problem in problems]
    examples = fields["examples"] if isinstance(fields.get("examples"), list) else []
    try:
        root, base, commits = branch_commits(folder)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"PROBLEM: cannot read the git history of the branch: {error}")
        print(f"--- audit of {path}: not checked; 1 problem(s)")
        return PROTECTION_FAILED

    mapped = map_examples(folder)
    if mapped is None:
        found.append(f"no README.md in {folder}: the examples cannot be checked against the example map")
    elif missing := [e for e in examples if e not in mapped]:
        found.append(f"{', '.join(missing)} not in the example map of README.md")
    try:
        merged = statuses_at(base, folder)
    except (OSError, RuntimeError, ValueError) as error:
        merged, found = {}, found + [f"cannot read the tasks in {base}: {error}"]
    deps = fields.get("depends_on", []) if isinstance(fields.get("depends_on"), list) else []
    if waiting := [d for d in deps if merged.get(d) != "done"]:
        found.append(f"depends on {', '.join(waiting)}, not done in {base}: merge those first")

    if not examples and not has_red(commits, task_id):
        print(f"{label}: no examples declared")
    elif status != "done" and not has_red(commits, task_id):
        print(f"{label}: pending, no red commit yet ({', '.join(examples)})")
    else:
        try:
            protection = protection_problems(root, base, commits, task_id, examples, worktree=False, folder=folder)
        except (OSError, RuntimeError, ValueError) as error:
            protection = [f"cannot read the git history: {error}"]
        if not protection:
            tested = f"tests {', '.join(examples)}" if examples else "declares no examples"
            print(f"{label}: ok, the red commit {tested}, untouched since")
        found += protection
    for problem in found:
        print(f"{label}: PROBLEM: {problem}")
    print(f"--- audit of {path} (branch since {base}): {len(found)} problem(s)")
    return PROTECTION_FAILED if found else 0


def audit_plan(folder: Path) -> int:
    """Read-only check of the plan of a change, for the review of the plan branch: the task files and the map."""
    tasks, found = load_tasks(folder)
    found += graph_problems(tasks)
    mapped = map_examples(folder)
    if mapped is None:
        found.append(f"no README.md in {folder}")
    assigned = {e for t in tasks.values() if isinstance(t.get("examples"), list) for e in t["examples"]}
    for example in mapped or []:
        if example not in assigned:
            found.append(f"{example} is in the example map but in no task's examples")
    for problem in found:
        print(f"PROBLEM: {problem}")
    ids = ", ".join(sorted(tasks, key=number)) or "none"
    print(f"--- audit of the plan in {folder}: tasks {ids}; {len(found)} problem(s)")
    return PROTECTION_FAILED if found else 0


def main(argv: list[str]) -> int:
    rest = list(argv)
    if rest[:1] == ["--audit"]:
        folder, task_id = locate(rest[1:], need_task=False)
        refuse_finished(folder)
        return audit_task(folder, task_id) if task_id else audit_plan(folder)
    if "--" not in rest or not rest[rest.index("--") + 1 :]:
        usage("wrong arguments")
    split = rest.index("--")
    folder, task_id = locate(rest[:split], need_task=True)
    command = rest[split + 1 :]
    refuse_finished(folder)
    path = task_file(folder, task_id)
    _, fields = read_task(path)
    already_done = fields["status"] == "done"

    examples = fields["examples"]
    problems = check_protection(folder, task_id, examples)
    for problem in problems:
        print(f"task_done: {problem}")
    if problems:
        print(f"✘ {task_id} NOT marked: the tests of its red commit are not protected.")
        return PROTECTION_FAILED
    if examples:
        print(f"--- red commit of {task_id} found; {', '.join(examples)} have tests and they are untouched")

    shown = shlex.join(command)
    declared = " ".join(fields["verification"].strip("`").split())
    if declared not in " ".join(" ".join(command).split()):
        print(
            f"task_done: warning: {task_id} declares verification '{declared}', but the command run is '{shown}'",
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
        print(f"✔ {task_id} was already done; verification still green.")
    else:
        # Read it again: the person may have edited the file while the verification ran.
        text, _ = read_task(path)
        path.write_text(set_status(text, "done"), encoding="utf-8")
        print(f"✔ {task_id} marked status: done in {path}.")
    readme = folder / "README.md"
    if readme.is_file() and all_done(folder):
        text = readme.read_text(encoding="utf-8")
        if (finished := set_status(text, "done")) != text:
            readme.write_text(finished, encoding="utf-8")
            print(f"✔ every task of the change is done: status: done in {readme}.")
            # D-0006: spec and plan are working documents; their decisions are already in docs/decisions/.
            for doc in (folder / "spec.md", folder / "plan.md"):
                text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
                if (closed := set_status(text, "obsolete")) != text:
                    doc.write_text(closed, encoding="utf-8")
                    print(f"✔ status: obsolete in {doc}: a working document of a finished change.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
