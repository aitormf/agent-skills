---
name: task-done
description: Runs a task's verification command and sets the task to status done only if the command passes, so no task is done without evidence; when the task lists its examples, it first checks in git that their tests were committed red on the branch and left untouched. Also shows the board of a change (ready, blocked, doing, done tasks). Use it whenever a task in docs/changes/<change>/tasks/ (from idea-to-change or plan-to-tasks) is to be marked as done, or to see where a change stands and which tasks are ready; the implement agent uses it for each task.
---

# Mark a task as done

A task is marked done by a script, not by hand: the script runs the task's verification and only sets `status: done` in the task file if it exits with 0. A failing verification leaves the file untouched.

Each change is a folder `docs/changes/<change>/`: a `README.md` (note, example map; `status: open | done` and `issue:` in its frontmatter) and one file per task in `tasks/`, `T<n>-<slug>.md`:

```yaml
---
id: T2
title: Full refund when cancelled more than 1 h before
status: todo            # todo | doing | done
depends_on: [T1]
examples: [E1, E3]
verification: pytest tests/test_cancel.py -k "E1 or E3"
---
```

Each task has its own branch and PR, `<…>/<change>/T<n>`, from the base branch; the plan has `<change>/plan`. By default the script takes the folder and the task from the current branch (`42-cancel-trip/T2` → `docs/changes/42-cancel-trip/`, task `T2`: the change is the second-to-last segment, the task the last one). The folder, a task file or the task ID can be passed instead. The script reads only files and git: no `gh`, no network. When the verification passes it sets `status: done` in the task file, inside the task's own PR; once every task of the change is done (here, or already merged into the base branch), it also sets `status: done` in the README, and `status: obsolete` in `spec.md` and `plan.md` if the change has them: they are working documents, and their decisions are already in `docs/decisions/` (D-0006).

If the task lists its examples (`examples: [E1, E2]`) or already has a red commit, the script first checks the test protection in git, among the commits of the current branch that are not in the base branch (`origin/HEAD`, else `origin/main`, `origin/master`, `main` or `master`). One branch, one task: task and example IDs repeat across changes, so older commits do not count. It checks that:

- there is a red commit whose subject starts with `test(T3):`, made before the implementation;
- the red commit adds a line naming each example (`test_E1_…`, `it("E1 …")`), so every example has its test;
- the task file still declares the examples it declared at its red commit: dropping one is a change of behaviour for the person, and does not turn the protection off;
- no later commit (the red commits of other tasks and merge commits included) and no uncommitted change removes or changes a non-blank line the red commits added. Lines are followed by identity (`git blame`), not by text: changing the other lines of those files, even one with the same text, adding new tests, and renaming the whole file are allowed; moving the lines elsewhere is not.

## The board

`scripts/board.py [docs/changes/<change>]` (default: the change of the current branch) lists each task as `ready`, `blocked by T1, T3`, `doing` or `done`, read-only. **Done means merged:** `status: done` in the base branch. A task is `doing` if it is not merged but its file here says `doing` or `done`, or a branch `<…>/<change>/T<n>` exists, local or remote (someone is on it, or its PR waits for review). It is `ready` if it is `todo` and all its `depends_on` are merged. Only `depends_on` is written; what a task blocks is computed. Exit 2, with one line per problem, if a frontmatter is malformed, a dependency does not exist or there is a cycle: fix the task files before picking a task.

## The review: `--audit`

`review-prepush` and `review-pr` run `task_done.py --audit`, read-only: it runs no verification and edits nothing. Its scope follows the branch:

- **Task branch** (`<change>/T<n>`, or a task given): that task only. Its test protection if it is done or has a red commit (committed history only), that its `examples` are in the README's example map (`E1: …` lines), and that its `depends_on` are done in the base branch. A task not done without a red commit is reported as `pending`.
- **Plan branch** (`<change>/plan`, or a folder given without a task): the task files (frontmatter, ids, no dependency that does not exist, no cycle) and that every example of the map is in some task's `examples`.

Exit 0 if nothing is wrong, 3 if something is (`PROBLEM` lines), 2 if it cannot find the folder or the task.

## How

1. Take the task's verification from the `verification:` of its file. If it names a test, use the single-test command from the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects).
2. Run, from the project root, with this skill's directory as `<skill-dir>`:

   ```bash
   python3 <skill-dir>/scripts/task_done.py -- uv run pytest tests/unit/test_foo.py -q               # the task of the branch
   python3 <skill-dir>/scripts/task_done.py docs/changes/<change> T3 -- …                              # another task
   ```

   The command runs without a shell. For pipes or `&&`, pass `bash -c "<command>"`.
3. Read the output and the exit status. The script prints the tail of the output and `--- command: <command> → exit <n>`; no log file is kept.
   - `task_done: warning: … declares verification …` (stderr): the command does not contain the verification declared in the task. It is not a failure, but run the declared one, or say in your report why you did not.
   - `✘ T3 NOT marked: the tests of its red commit are not protected` (exit 3): the lines above it say what is missing. The verification was not run. If the red commit is missing, set the implementation aside (`git stash`), commit the tests, check that they fail, and bring it back. If you changed a red test, the message names the file and the line numbers in the red commit's version (`git show <red commit>:<file>`). If it says `uncommitted changes`, put back exactly those lines as they are in `HEAD` (`git diff -- <file>` shows what you changed) and keep the other changes to the file. If it names a commit, that commit stays in the branch's history: do not try to undo it with another commit or by rewriting history; stop and report the commit, the file and the lines to the person. If the test looks wrong, stop and report it instead.
   - `✔ T3 marked status: done`: done. Commit the task file with the implementation, and report the `--- command: … → exit 0` line as evidence.
   - `✘ T3 NOT marked`: the task is not done. Fix the code, not the test, and run it again.
   - `task_done: PROBLEM: cannot read the git history of the branch: no base branch found` (exit 3): there is no `origin/HEAD`, `origin/main`, `origin/master`, `main` or `master` to tell the branch's commits apart. Report it; do not edit the status by hand.
   - Exit 2: the call was wrong, the task file is malformed (the message says which field), or there is no folder or task file where it looked: the message names what it searched (`docs/changes/<change>`, `tasks/T3-*.md`). Pass the right folder and task, or check that you are on the task's branch (`<change>/T<n>`; the plan branch has no task to mark). Also exit 2 if the change is already finished in the base branch (`status: done` in its README there): the branch reuses the name of an earlier change. Report it and propose renaming the branch.
   - `✔ every task of the change is done: status: done in …/README.md`: the change is finished; commit the README with the task, and `spec.md` and `plan.md` if it set them `obsolete`.

## Rules

- Never set `status: done` by hand, and never set it back to re-run: the script accepts tasks that are already done.
- The verification must exercise the task. A command that always succeeds (`true`, `echo ok`, a test path that collects nothing) is not a verification. If the task has no real one, stop and say so.
- Never rewrite history (`rebase`, `commit --amend`) or move tests to another file to get past the protection check: a red test that looks wrong is reported to the person, not changed.
- If `python3` is not available, run the verification yourself and set `status: done` only if it passed, quoting the output in your report. For a task with examples, also show `git log --oneline` with its red commit and `git diff <red commit> -- <its test files>`.
