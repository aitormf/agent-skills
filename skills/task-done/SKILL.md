---
name: task-done
description: Runs a task's verification command and ticks the task in tasks.md only if the command passes, so no task gets marked [x] without evidence; when the task lists its examples, it first checks in git that their tests were committed red and left untouched. Use it whenever a task in docs/specs/<work-item>/tasks.md is to be marked as done; the implement agent uses it after each task.
---

# Mark a task as done

A task in `tasks.md` is marked `[x]` by a script, not by hand: the script runs the task's verification and only edits the checkbox if it exits with 0. A failing verification leaves `tasks.md` untouched.

If the task lists its examples (`- [ ] T3. <task> — tests: E1, E2 — verification: …`), the script first checks the test protection in git, among the commits since `tasks.md` was added:

- there is a red commit whose subject starts with `test(T3):`, made before the implementation;
- the red commit adds a line naming each example (`test_E1_…`, `it("E1 …")`), so every example has its test;
- no later commit (except the red commits of other tasks) and no uncommitted change removes or changes a line of the files the red commit touched. Adding new tests to those files is allowed.

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
   - `✘ T3 NOT marked: the tests of its red commit are not protected` (exit 3): the lines above it say what is missing. The verification was not run. If the red commit is missing, set the implementation aside (`git stash`), commit the tests, check that they fail, and bring it back. If you changed a red test, restore it (`git checkout <red commit> -- <file>`); if it looks wrong, stop and report it instead.
   - `✔ T3 marked [x]`: done. Report it with the `--- command: … → exit 0` line as evidence.
   - `✘ T3 NOT marked`: the task is not done. Fix the code, not the test, and run it again.
   - Exit 2: the call was wrong (no such task, duplicated ID, bad arguments). Fix the call; do not edit the checkbox by hand.

## Rules

- Never tick a checkbox by hand, and never untick one to re-run it: the script accepts tasks that are already `[x]`.
- The verification must exercise the task. A command that always succeeds (`true`, `echo ok`, a test path that collects nothing) is not a verification. If the task has no real one, stop and say so.
- Never rewrite history (`rebase`, `commit --amend`) or move tests to another file to get past the protection check: a red test that looks wrong is reported to the person, not changed.
- Tasks without an ID (old `tasks.md` files) cannot be marked by the script. Add the ID (`T<n>.`, `W<n>.` for wrap-up) to the line, keeping the text, and say you did.
- If `python3` is not available, run the verification yourself and tick the box only if it passed, quoting the output in your report. For a task with examples, also show `git log --oneline` with its red commit and `git diff <red commit> -- <its test files>`.
