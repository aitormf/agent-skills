#!/usr/bin/env python3
"""Run a task's verification and tick it in tasks.md only if it passes.

Usage:
  task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]

  TASK_ID is the label at the start of the task line (T3, W2...).
  COMMAND runs without a shell; for pipes or &&, pass `bash -c "..."`.

The full output goes to a log file; only its tail is printed.
Exit status: the command's. A failing command leaves tasks.md untouched.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

TAIL = 40


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
    sys.exit(2)


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

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError:
        print(f"task_done: command not found: {command[0]}", file=sys.stderr)
        return 127

    with tempfile.NamedTemporaryFile("w", prefix=f"task-{task_id}-", suffix=".log", delete=False) as log:
        log.write(result.stdout)
    tail = result.stdout.splitlines()[-TAIL:]
    print("\n".join(tail))
    print(f"--- full output: {log.name}")
    print(f"--- {' '.join(command)} → exit {result.returncode}")

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
