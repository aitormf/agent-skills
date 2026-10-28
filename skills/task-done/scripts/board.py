#!/usr/bin/env python3
"""Board of a change: which tasks are ready, blocked (and by which), doing and done.

Usage:
  board.py [CHANGE_DIR]

  Without CHANGE_DIR, it is docs/changes/<change>/ from the current branch, <...>/<change>/T<n>
  or <...>/<change>/plan (the change is the second-to-last segment), from the repo root.

Each task is a file CHANGE_DIR/tasks/T<n>-<slug>.md with a frontmatter of id, title,
status (todo | doing | done), depends_on ([T1, T3] or []), examples ([E1, E2] or [])
and verification. Done means merged: `status: done` in the base branch (origin/HEAD,
else origin/main, origin/master, main or master). A task is
  done     if it is done in the base branch;
  doing    if not, but its file here says doing or done, or a branch <...>/<change>/T<n>
           exists (local or remote): someone is on it, or its PR waits for review;
  ready    if it is todo and every task in depends_on is done in the base branch;
  blocked  otherwise, by the dependencies not done in the base branch yet.

Read-only. Exit 0; exit 2 if the call is wrong, the folder or the base branch is not
found, or the tasks are wrong: a malformed frontmatter, a dependency that does not
exist or a cycle.
"""

import re
import subprocess
import sys
from pathlib import Path

TASK_ID = re.compile(r"T\d+")
TASK_FILE = re.compile(r"(T\d+)(?:-[^/]+)?\.md")
EXAMPLE_ID = re.compile(r"E\d+")
MAP_EXAMPLE = re.compile(r"^\s*(?:[-*]\s+)?(E\d+)\s*:")
FRONTMATTER = re.compile(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
FIELDS = ("id", "title", "status", "depends_on", "examples", "verification")
STATUSES = ("todo", "doing", "done")


def fail(msg: str) -> None:
    print(f"board: {msg}", file=sys.stderr)
    sys.exit(2)


def git(root: Path, *args: str) -> str:
    # core.quotePath=false: paths with non-ASCII characters (test_canción.py) come out as they are.
    # log.showSignature=false: signature checks must not mix into the output that is parsed.
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-c", "log.showSignature=false", "-C", str(root), *args],
        capture_output=True,
        encoding="utf-8",
        errors="surrogateescape",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


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


def branch_change() -> tuple[Path, str, str]:
    """(docs/changes/<change>, last segment, branch) from a branch <...>/<change>/T<n> or <...>/<change>/plan.

    Raises ValueError saying what is wrong.
    """
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"cannot read the current branch: {error}") from error
    if branch == "HEAD":
        raise ValueError("HEAD is detached (no branch name)")
    segments = branch.split("/")
    if len(segments) < 2 or not (TASK_ID.fullmatch(segments[-1]) or segments[-1] == "plan"):
        raise ValueError(f"branch '{branch}' is not <change>/T<n> nor <change>/plan")
    return root / "docs" / "changes" / segments[-2], segments[-1], branch


def parse_frontmatter(text: str) -> dict[str, str | list[str]] | None:
    """The `key: value` lines of the frontmatter; `[a, b]` values as lists. None without a frontmatter.

    Raises ValueError on a line that is not `key: value`. Unquoted values end at ` #` (a comment).
    """
    match = FRONTMATTER.match(text)
    if not match:
        return None
    fields: dict[str, str | list[str]] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        pair = re.fullmatch(r"([A-Za-z_]+):(.*)", line)
        if not pair:
            raise ValueError(f"'{line.strip()}' is not 'key: value' (lists go in one line: [T1, T2])")
        value = pair.group(2).strip()
        quoted = re.fullmatch(r"""(["'])(.*)\1(?:\s+#.*)?""", value)
        value = quoted.group(2) if quoted else re.sub(r"(^|\s+)#.*$", "", value)
        if value.startswith("[") and value.endswith("]"):
            fields[pair.group(1)] = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
        else:
            fields[pair.group(1)] = value
    return fields


def parse_task(text: str, name: str) -> tuple[dict, list[str]]:
    """(fields, problems) of a task file; name is its file name."""
    try:
        fields = parse_frontmatter(text)
    except ValueError as error:
        return {}, [f"{name}: {error}"]
    if fields is None:
        return {}, [f"{name}: no frontmatter (--- id, title, status, depends_on, examples, verification ---)"]
    problems = [f"{name}: missing {key}" for key in FIELDS if key not in fields]
    lists = {"depends_on": (TASK_ID, "T"), "examples": (EXAMPLE_ID, "E")}
    for key, value in fields.items():
        if key in lists:
            pattern, letter = lists[key]
            if not isinstance(value, list):
                problems.append(f"{name}: {key} must be a list in one line, [{letter}1, {letter}2] or []")
            elif bad := [v for v in value if not pattern.fullmatch(v)]:
                problems.append(f"{name}: {key} has {', '.join(bad)}, not {letter}<n>")
        elif key in FIELDS and not isinstance(value, str):
            problems.append(f"{name}: {key} must not be a list")
    file_id = m.group(1) if (m := TASK_FILE.fullmatch(name)) else None
    if not file_id:
        problems.append(f"{name}: the name must be T<n>-<slug>.md")
    if "id" in fields and fields["id"] != file_id:
        problems.append(f"{name}: id is {fields['id']}, the file name says {file_id}")
    if fields.get("status", "todo") not in STATUSES:
        problems.append(f"{name}: status '{fields['status']}' is not todo, doing or done")
    for key in ("title", "verification"):
        if key in fields and not fields[key]:
            problems.append(f"{name}: {key} is empty")
    return fields, problems


def load_tasks(folder: Path) -> tuple[dict[str, dict], list[str]]:
    """({id: fields + 'path'}, problems) of the tasks in folder/tasks/, from the working tree."""
    tasks: dict[str, dict] = {}
    problems: list[str] = []
    if not (folder / "tasks").is_dir():
        return tasks, [f"no tasks/ folder in {folder}"]
    for path in sorted((folder / "tasks").glob("*.md")):
        try:
            fields, found = parse_task(path.read_text(encoding="utf-8"), path.name)
        except (OSError, ValueError) as error:
            fields, found = {}, [f"{path.name}: cannot read it: {error}"]
        problems += found
        if isinstance(fields.get("id"), str) and TASK_ID.fullmatch(fields["id"]):
            if fields["id"] in tasks:
                problems.append(f"{path.name}: id {fields['id']} is already used by {tasks[fields['id']]['path'].name}")
            else:
                tasks[fields["id"]] = {**fields, "path": path}
    if not tasks and not problems:
        problems.append(f"no task files (T<n>-<slug>.md) in {folder / 'tasks'}")
    return tasks, problems


def graph_problems(tasks: dict[str, dict]) -> list[str]:
    """Dependencies that do not exist and cycles, one line each."""
    problems = []
    deps = {tid: [d for d in t.get("depends_on", []) if isinstance(d, str)] for tid, t in tasks.items()}
    for tid in sorted(deps, key=number):
        for dep in deps[tid]:
            if dep not in deps:
                problems.append(f"{tid} depends on {dep}, which does not exist")
    state: dict[str, int] = {}  # 1: on the current path, 2: finished
    cycles: set[frozenset[str]] = set()

    def visit(tid: str, path: list[str]) -> None:
        state[tid] = 1
        for dep in deps[tid]:
            if dep not in deps:
                continue
            if state.get(dep) == 1:
                cycle = path[path.index(dep) :] + [dep]
                if frozenset(cycle) not in cycles:
                    cycles.add(frozenset(cycle))
                    problems.append(f"cycle: {' -> '.join(cycle)}")
            elif dep not in state:
                visit(dep, path + [dep])
        state[tid] = 2

    for tid in sorted(deps, key=number):
        if tid not in state:
            visit(tid, [tid])
    return problems


def statuses_at(rev: str, folder: Path) -> dict[str, str]:
    """{id: status} of the task files in folder/tasks/ at rev; {} if the folder is not there.

    Raises RuntimeError if git cannot be read.
    """
    root = Path(git(folder, "rev-parse", "--show-toplevel").strip())
    rel = folder.resolve().relative_to(root.resolve()).as_posix()
    found = {}
    for path in git(root, "ls-tree", "-z", "--name-only", rev, "--", f"{rel}/tasks/").split("\0"):
        if not TASK_FILE.fullmatch(path.rsplit("/", 1)[-1]):
            continue
        try:
            fields = parse_frontmatter(git(root, "show", f"{rev}:{path}")) or {}
        except ValueError:
            continue
        if isinstance(fields.get("id"), str) and isinstance(fields.get("status"), str):
            found[fields["id"]] = fields["status"]
    return found


def set_status(text: str, value: str) -> str:
    """text with the status of its frontmatter set to value, keeping any comment; unchanged without one."""
    match = FRONTMATTER.match(text)
    if not match:
        return text
    frontmatter = re.sub(r"^(status:[ \t]*)[^\s#]*", rf"\g<1>{value}", match.group(1), count=1, flags=re.MULTILINE)
    return text[: match.start(1)] + frontmatter + text[match.end(1) :]


def map_examples(folder: Path) -> list[str] | None:
    """The examples of the example map in folder/README.md (`E1: ...` lines); None without a README."""
    try:
        lines = (folder / "README.md").read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError):
        return None
    return list(dict.fromkeys(m.group(1) for line in lines if (m := MAP_EXAMPLE.match(line))))


def number(task_id: str) -> int:
    return int(task_id[1:])


def task_branches(folder: Path) -> dict[str, str]:
    """{task id: branch} for the local and remote branches <...>/<change>/T<n> of this change."""
    found: dict[str, str] = {}
    try:
        refs = git(folder, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes").split()
    except RuntimeError:
        return found
    for ref in refs:
        segments = ref.split("/")
        if len(segments) >= 2 and segments[-2] == folder.name and TASK_ID.fullmatch(segments[-1]):
            found.setdefault(segments[-1], ref)
    return found


def main(argv: list[str]) -> int:
    if len(argv) > 1 or argv[:1] in (["-h"], ["--help"]):
        fail("usage: board.py [CHANGE_DIR]")
    if argv:
        folder = Path(argv[0])
    else:
        try:
            folder, _, _ = branch_change()
        except ValueError as error:
            fail(f"no CHANGE_DIR given and {error}: pass the change folder, docs/changes/<change>")
    if not folder.is_dir():
        fail(f"{folder} does not exist")
    tasks, problems = load_tasks(folder)
    problems += graph_problems(tasks)
    if problems:
        for problem in problems:
            print(f"board: {problem}", file=sys.stderr)
        fail(f"{len(problems)} problem(s) in {folder / 'tasks'}: fix them before picking a task")
    try:
        base = base_branch(folder)
        merged = statuses_at(base, folder)
    except (OSError, RuntimeError, ValueError) as error:
        fail(f"cannot read the base branch: {error}")
    branches = task_branches(folder)

    counts = dict.fromkeys(("ready", "blocked", "doing", "done"), 0)
    for tid in sorted(tasks, key=number):
        task = tasks[tid]
        waiting = [d for d in task["depends_on"] if merged.get(d) != "done"]
        if merged.get(tid) == "done":
            kind, note = "done", ""
        elif task["status"] != "todo" or tid in branches:
            kind, note = "doing", f" (branch {branches[tid]})" if tid in branches else ""
        elif waiting:
            kind, note = "blocked", f" by {', '.join(waiting)}"
        else:
            kind, note = "ready", ""
        counts[kind] += 1
        print(f"{tid} {kind}{note}: {task['title']}")
    summary = ", ".join(f"{n} {kind}" for kind, n in counts.items())
    print(f"--- board of {folder} (done: merged into {base}): {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
