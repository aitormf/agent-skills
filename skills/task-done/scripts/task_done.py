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
"""

import re
import shlex
import subprocess
import sys
from pathlib import Path

TAIL = 40


def usage(msg: str) -> None:
    print(f"task_done: {msg}", file=sys.stderr)
    print("usage: task_done.py TASKS_FILE TASK_ID -- COMMAND [ARGS...]", file=sys.stderr)
    sys.exit(2)


def declared_verification(lines: list[str], index: int) -> str:
    """Text after 'verification:' in the task line or its indented continuation lines."""
    block = [lines[index]]
    for line in lines[index + 1 :]:
        if not line[:1].isspace() or not line.strip() or re.match(r"\s*- \[", line):
            break
        block.append(line)
    match = re.search(r"verification:\s*(.+)", " ".join(block))
    if not match:
        return ""
    text = match.group(1).strip()
    quoted = re.search(r"`([^`]+)`", text)
    return " ".join((quoted.group(1) if quoted else text).split())


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

    shown = shlex.join(command)
    declared = declared_verification(lines, index)
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
