---
name: task-done
description: Runs a task's verification command and ticks the task in tasks.md only if the command passes, so no task gets marked [x] without evidence. Use it whenever a task in docs/specs/<work-item>/tasks.md is to be marked as done; the implement agent uses it after each task.
---

# Mark a task as done

A task in `tasks.md` is marked `[x]` by a script, not by hand: the script runs the task's verification and only edits the checkbox if it exits with 0. A failing verification leaves `tasks.md` untouched.

## How

1. Take the task ID (`T3`, `W2`…) and its verification from the task line: `- [ ] T3. <task> — files: … — verification: <test or command>`.
2. Turn the verification into a command. If it names a test, use the single-test command from the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects). Wrap-up tasks declare their own command (`W2`: the full verification command).
3. Run, from the project root, with this skill's directory as `<skill-dir>`:

   ```bash
   python3 <skill-dir>/scripts/task_done.py docs/specs/<work-item>/tasks.md T3 -- uv run pytest tests/unit/test_foo.py -q
   ```

   The command runs without a shell. For pipes or `&&`, pass `bash -c "<command>"`.
4. Read the output and the exit status. The script prints the tail of the output and `--- command: <command> → exit <n>`; no log file is kept.
   - `task_done: warning: … declares verification …` (stderr): the command does not contain the verification declared in the task. It is not a failure, but run the declared one, or say in your report why you did not.
   - `✔ T3 marked [x]`: done. Report it with the `--- command: … → exit 0` line as evidence.
   - `✘ T3 NOT marked`: the task is not done. Fix the code, not the test, and run it again.
   - Exit 2: the call was wrong (no such task, duplicated ID, bad arguments). Fix the call; do not edit the checkbox by hand.

## Rules

- Never tick a checkbox by hand, and never untick one to re-run it: the script accepts tasks that are already `[x]`.
- The verification must exercise the task. A command that always succeeds (`true`, `echo ok`, a test path that collects nothing) is not a verification. If the task has no real one, stop and say so.
- Tasks without an ID (old `tasks.md` files) cannot be marked by the script. Add the ID (`T<n>.`, `W<n>.` for wrap-up) to the line, keeping the text, and say you did.
- If `python3` is not available, run the verification yourself and tick the box only if it passed, quoting the output in your report.
