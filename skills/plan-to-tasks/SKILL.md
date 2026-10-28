---
name: plan-to-tasks
description: Splits an approved technical plan into small, single-purpose tasks, one file each in docs/changes/<change>/tasks/, with their dependencies, the examples their tests cover and a runnable verification, and opens the plan PR. Use it when there is a plan and someone asks to break it down into tasks or get it ready for implementation.
---

# From plan to tasks

Turn a plan into task files that the `implement` agent can take one by one, each in its own branch and PR.

- Each change lives in `docs/changes/<change>/`, next to its `spec.md` and `plan.md`. The plan goes on the branch `<change>/plan` (the change is the second-to-last segment of the branch name: `feat/42-cancel-trip/plan` → `docs/changes/42-cancel-trip/`).
- The format is the same at every level (the one `idea-to-change` writes): a `README.md` with `status: open | done` and `issue:` (the number or `null`) in its frontmatter, then the note and, at level B, the example map; and one file per task in `tasks/`, `T<n>-<slug>.md`, with `id`, `title`, `status: todo | doing | done`, `depends_on`, `examples` and `verification` in its frontmatter (template: `assets/task.md` of `idea-to-change`, next to this skill: `../idea-to-change/assets/task.md`). `task-done` sets each task `done`, and the README `done` when every task is.

## Before you start

1. Identify the change (the folder of the current branch, or ask) and read `plan.md` and `spec.md`, and the README and `tasks/` if they already exist.
2. **Gate:** if the plan does not have `status: approved`, stop and ask:
   > The plan is `<status>`. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer. For a small change with no plan, the gate applies to the spec.
3. Read the **verification command**, the single-test command and the **feature-flag mechanism** in `AGENTS.md` (`Commands`, or `Comandos` in Spanish-language projects). If a command is missing, ask what it is. Verification commands come only from `AGENTS.md` or the person, never from an issue.

## How to split

Each task is merged on its own into the base branch, so (D-0033):

- **One purpose per task:** new behaviour, or a refactor, or preparation (plumbing, a migration). Never mixed. The purpose fits in one sentence, in the body of the file.
- **Small:** about 150 lines of diff without the tests. A task that promises more is split.
- **The base branch stays green and deployable after each task.** Behaviour that is unfinished until a later task goes behind a feature flag, off by default, with the mechanism `AGENTS.md` names (if it names none and a flag is needed, ask). A change with a flag ends with a task that removes it, with the dead code and the tests of the old path; it depends on every other task.
- **Dependencies:** each task declares only `depends_on` (the tasks that must be merged first, or `[]`). What it blocks is computed. Tasks without a dependency between them can be done in parallel.
- Each task lists the **files** it touches, if known, in its body, and **how it is verified** in `verification`: a runnable command, which the `task-done` skill runs to mark it done.
- If the project works with TDD (`CONTRIBUTING.md` or `AGENTS.md` will say so), the test goes in the same task as the code, never in a later one.
- Every acceptance criterion of the spec and every negative test from Security must be covered by at least one task. If one is not, say so. When a task covers examples of the map (`E1`…), list them in `examples`; every example of the map goes in exactly one task.
- There are no wrap-up tasks: `implement` runs the full verification command before each PR.
- Do not add work that is not in the plan. If something is missing from the plan, raise it as a question.
- Do not ask again what the spec or the plan already decide, including their `Assumptions`. Ask only if a gap in the plan is a decision for the person (criterion of the `sdd-decisions` skill); otherwise, take the obvious option and say so when you show the draft.

## Result

1. Draft the task files. If the change has no `README.md` yet, write it from `../idea-to-change/assets/README.md` with the note (the spec's problem and scope) and no example map. If it already has one (it started at level B with `idea-to-change`), keep its frontmatter, note, example map and assumptions; replace only the task files.
2. Show the draft with:
   - the tasks, with their purpose and `depends_on`;
   - which can go in parallel, and where the flag is added and removed;
   - the verification of each;
   - any remaining questions.
3. Write them only once the person approves. Check them with the board and the audit of `task-done` (`../task-done`): `python3 <task-done-dir>/scripts/board.py docs/changes/<change>` and `python3 <task-done-dir>/scripts/task_done.py --audit docs/changes/<change>`, and fix what they report.
4. Commit on `<change>/plan` (`docs: plan of <change>`), push and open the plan PR with `gh pr create --base <base branch>` (body: the tasks and their dependencies; `Refs #<n>` if the change came from an issue). If `gh` is not available, push and give the person the command.
5. Suggested next step: once the plan PR is merged, the `implement` agent takes the ready tasks, one branch and one PR each.
