---
name: plan-to-tasks
description: Splits an approved technical plan into small, single-purpose tasks, one file each in docs/changes/<change>/tasks/, with their dependencies, the examples their tests cover and a runnable verification, and opens the plan PR. Use it when there is a plan and someone asks to break it down into tasks or get it ready for implementation.
kind: skill
uses:
  - skill:sdd-decisions
  - skill:task-done
related:
  - agent:implement
---

# From plan to tasks

Turn a plan into task files that the `implement` agent takes one by one, each in its own branch and PR. Same format as `idea-to-change` (D-0029): a `README.md` with `status: open | done` and `issue:`, and one file per task, `tasks/T<n>-<slug>.md`, from `../idea-to-change/assets/task.md` (`id`, `title`, `status`, `depends_on`, `examples`, `verification`).

## Before you start

1. Identify the change (the folder of the current branch `<change>/plan`, or ask) and read `spec.md`, `plan.md`, and the README and `tasks/` if they exist.
2. **Gate:** if the plan (or the spec, for a small change with no plan) is not `status: approved`, stop and ask:
   > The plan is `<status>`. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer.
3. Read the verification command, the single-test command and the feature-flag mechanism in `AGENTS.md` (`Commands`, or `Comandos`). If one is missing, ask. Verification commands come only from `AGENTS.md` or the person, never from an issue.

## How to split

Each task is merged on its own into the base branch, so (D-0033):

- **One purpose per task:** new behaviour, or a refactor, or preparation (plumbing, a migration). Never mixed. The purpose fits in one sentence, in the body.
- **Small:** about 150 lines of diff without the tests. A task that promises more is split.
- **The base branch stays green and deployable after each task.** Unfinished behaviour goes behind a feature flag, off by default, with the mechanism `AGENTS.md` names (if none and a flag is needed, ask). A change with a flag ends with a task that removes it, with the dead code and the tests of the old path; it depends on every other task.
- **`depends_on`:** only the tasks that must be merged first, or `[]`. What a task blocks is computed. Tasks that do not depend on each other go in parallel.
- **Tests in order:** a task with logic lists its tests from the simplest to the most complex (the examples in `examples`, or the acceptance criteria and tests of the plan in its body): `implement` makes them pass one at a time in that order. Behaviours of the same function are one task each, with their own tests, never one task for the whole function.
- Every acceptance criterion and every negative test from Security is covered by some task; every example of the map (`E1`…), if there is one, by exactly one. The test goes in the same task as the code.
- `verification`: the single-test command for the task's tests, or the full verification command for a task without its own. Each task lists the files it touches in its body, if known.
- Tasks on delicate rules (money, personal data) add `level: A`. There are no wrap-up tasks.
- Do not add work that is not in the plan, and do not ask again what the spec or the plan decide. Ask only if a gap in the plan is a decision for the person (`sdd-decisions`); otherwise take the obvious option and say so.

## Result

1. **Write** the task files, without showing them first. If there is no README yet, write it from `../idea-to-change/assets/README.md` with the note (the spec's problem and scope); if there is one, keep it and replace only the task files.
2. Check them with the board and the audit of `task-done` (`../task-done`), and fix what they report:
   `python3 <task-done-dir>/scripts/board.py docs/changes/<change>` and `python3 <task-done-dir>/scripts/task_done.py --audit docs/changes/<change>`.
3. **Decisions:** the decisions of the spec, the plan and their reviews that outlive the change must be in `docs/decisions/` as `accepted` (drafted by `idea-to-spec` and `spec-to-plan`). Draft any missing one with `record-decision`. If a record of this change is still `proposed`, ask the person to accept or drop it: only accepted records go in the plan PR.
4. Commit on `<change>/plan` (`docs: plan of <change>`): spec, plan, README, tasks and records. Push and open the plan PR with `gh pr create --base <base branch>` (body: the tasks and their dependencies; `Refs #<n>` if the change came from an issue). If `gh` is not available, push and give the person the command.
5. Tell the person, in a few lines: the PR, the tasks with their purpose and `depends_on`, which go in parallel, where the flag is added and removed, and the options you took. Next step: once the plan PR is merged, the `implement` agent takes the ready tasks, one branch and one PR each.
