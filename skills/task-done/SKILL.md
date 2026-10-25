---
name: task-done
description: Runs a task's verification command and ticks the task in tasks.md only if the command passes, so no task gets marked [x] without evidence; when the task lists its examples, it first checks in git that their tests were committed red on the branch and left untouched. Use it whenever a task in docs/changes/<branch>/tasks.md (from idea-to-change or plan-to-tasks) is to be marked as done; the implement agent uses it after each task.
---

# Mark a task as done

A task is marked `[x]` by a script, not by hand: the script runs the task's verification and only edits the checkbox if it exits with 0. A failing verification leaves the checklist untouched.

The checklist is the `- [ ] T1.` lines of `docs/changes/<branch>/tasks.md`, the folder named after the last segment of the current branch (`feat/42-cancel-trip` → `docs/changes/42-cancel-trip/tasks.md`). That is the default; another path can be passed. The script reads only files and git: no `gh`, no network. When it ticks the last task, it sets `status: done` in the frontmatter of `tasks.md`.

If the task lists its examples (`- [ ] T3. <task> — tests: E1, E2 — verification: …`) or already has a red commit, the script first checks the test protection in git, among the commits of the current branch that are not in the base branch (`origin/HEAD`, else `origin/main`, `origin/master`, `main` or `master`). One branch, one change: task and example IDs repeat across changes, so older commits do not count. It checks that:

- there is a red commit whose subject starts with `test(T3):`, made before the implementation;
- the red commit adds a line naming each example (`test_E1_…`, `it("E1 …")`), so every example has its test;
- `tasks.md` still declares the examples the task declared at its red commit: dropping one is a change of behaviour for the person, and does not turn the protection off;
- no later commit (the red commits of other tasks and merge commits included) and no uncommitted change removes or changes a non-blank line the red commits added. Lines are followed by identity (`git blame`), not by text: changing the other lines of those files, even one with the same text, adding new tests, and renaming the whole file are allowed; moving the lines elsewhere is not.

`review-prepush` runs the same check over the whole checklist, read-only: `task_done.py --audit [docs/changes/<branch>/tasks.md]`. It runs no verification and ticks nothing; it checks every task that is ticked or has a red commit (committed history only) and that every example of the map (`E1: …` lines) is in some task's `tests:`, and reports unticked tasks without a red commit as pending. Exit 0 if nothing is wrong, 3 if something is (`PROBLEM` lines), 2 if it cannot read the checklist.

## How

1. Take the task ID (`T3`, `W2`…) and its verification from the task line: `- [ ] T3. <task> — files: … — verification: <test or command>` (`verificación:` in Spanish-language projects).
2. Turn the verification into a command. If it names a test, use the single-test command from the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects). Wrap-up tasks declare their own command (`W2`: the full verification command).
3. Run, from the project root, with this skill's directory as `<skill-dir>`:

   ```bash
   python3 <skill-dir>/scripts/task_done.py T3 -- uv run pytest tests/unit/test_foo.py -q   # docs/changes/<branch>/tasks.md
   python3 <skill-dir>/scripts/task_done.py docs/changes/<change>/tasks.md T3 -- …               # another path
   ```

   The command runs without a shell. For pipes or `&&`, pass `bash -c "<command>"`.
4. Read the output and the exit status. The script prints the tail of the output and `--- command: <command> → exit <n>`; no log file is kept.
   - `task_done: warning: … declares verification …` (stderr): the command does not contain the verification declared in the task. It is not a failure, but run the declared one, or say in your report why you did not.
   - `✘ T3 NOT marked: the tests of its red commit are not protected` (exit 3): the lines above it say what is missing. The verification was not run. If the red commit is missing, set the implementation aside (`git stash`), commit the tests, check that they fail, and bring it back. If you changed a red test, the message names the file and the line numbers in the red commit's version (`git show <red commit>:<file>`). If it says `uncommitted changes`, put back exactly those lines as they are in `HEAD` (`git diff -- <file>` shows what you changed) and keep the other changes to the file. If it names a commit, that commit stays in the branch's history: do not try to undo it with another commit or by rewriting history; stop and report the commit, the file and the lines to the person. If the test looks wrong, stop and report it instead.
   - `✔ T3 marked [x]`: done. Report it with the `--- command: … → exit 0` line as evidence.
   - `✘ T3 NOT marked`: the task is not done. Fix the code, not the test, and run it again.
   - `task_done: PROBLEM: cannot read the git history of the branch: no base branch found` (exit 3): there is no `origin/HEAD`, `origin/main`, `origin/master`, `main` or `master` to tell the branch's commits apart. Report it; do not tick by hand.
   - Exit 2: the call was wrong (no such task, duplicated ID, bad arguments), or there is no `tasks.md` where it looked: the message names the path it searched (`docs/changes/<branch>/tasks.md`). Pass the right path, or check that you are on the change's branch; do not edit the checkbox by hand. Also exit 2 if that `tasks.md` is a finished change already in the base branch (`status: done` there): the branch reuses the folder of an earlier one with the same last segment. Report it and propose renaming the branch.
   - `✔ every task is ticked: status: done`: the change is finished; commit `tasks.md` with the last task.

## Rules

- Never tick a checkbox by hand, and never untick one to re-run it: the script accepts tasks that are already `[x]`.
- The verification must exercise the task. A command that always succeeds (`true`, `echo ok`, a test path that collects nothing) is not a verification. If the task has no real one, stop and say so.
- Never rewrite history (`rebase`, `commit --amend`) or move tests to another file to get past the protection check: a red test that looks wrong is reported to the person, not changed.
- Tasks without an ID (old `tasks.md` files) cannot be marked by the script. Add the ID (`T<n>.`, `W<n>.` for wrap-up) to the line, keeping the text, and say you did.
- If `python3` is not available, run the verification yourself and tick the box only if it passed, quoting the output in your report. For a task with examples, also show `git log --oneline` with its red commit and `git diff <red commit> -- <its test files>`.
