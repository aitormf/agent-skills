---
name: plan-to-tasks
description: Splits an approved technical plan into small tasks, ordered by dependencies, with affected files, per-task verification and parallel groups. Use it when there is a plan and someone asks to break it down into tasks or get it ready for implementation.
---

# From plan to tasks

Turn a plan into an executable task list that the `implement` agent can follow and tick off.

- Each change lives in `docs/changes/<branch>/`, named after the last segment of the branch name (`feat/42-cancel-trip` → `docs/changes/42-cancel-trip/`), next to its `spec.md` and `plan.md`.
- `tasks.md` has the same format at every level (the one `idea-to-change` writes): frontmatter with `status: open | done` and `issue:` (the number or `null`), then the note and the tasks. Its progress is the `[x]` checkboxes; `task-done` sets `status: done` when it ticks the last one.

## Before you start

1. Identify the change (the folder of the current branch, or ask) and read `plan.md` and `spec.md`, and `tasks.md` if it already exists.
2. **Gate:** if the plan does not have `status: approved`, stop and ask:
   > The plan is `<status>`. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer. For a small change with no plan, the gate applies to the spec.
3. Read the **verification command** in the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects). If there is none, ask what it is or leave the wrap-up task with a warning.

## How to split

- Small tasks: each one is a reviewable change that leaves the project green.
- Ordered by dependencies. Mark with `[P]` those that can be done in parallel with the previous one.
- Each task starts with an **ID** (`T1.`, `T2.`…; `W1.`, `W2.` in the wrap-up) and lists the **files** it touches, if known, and **how it is verified**: which test, or which command. The verification has to be runnable: the `task-done` skill runs it to tick the task.
- If the project works with TDD (`CONTRIBUTING.md` or `AGENTS.md` will say so), the test goes before the code or in the same task, never at the end.
- Every acceptance criterion of the spec and every negative test from Security must be covered by at least one task. If one is not, say so.
- The **Wrap-up** phase is mandatory: acceptance criteria with tests and the verification command green, each with its own runnable command.
- Do not add work that is not in the plan. If something is missing from the plan, raise it as a question.
- Do not ask again what the spec or the plan already decide, including their `Assumptions`. Ask only if a gap in the plan is a decision for the person (criterion of the `sdd-decisions` skill); otherwise, take the obvious option and say so when you show the draft.

## Result

1. Draft `tasks.md` from `assets/tasks-template.md`. If the change already has a `tasks.md` (it started at level B with `idea-to-change`), keep its frontmatter, note, example map and assumptions, and replace only its task checklist. When a task covers examples of the map (`E1`…), list them in `tests:`.
2. Show the draft with:
   - the tasks;
   - the parallel groups;
   - the verification points;
   - any remaining questions.
3. Write it only once the person approves.
4. Suggested next step: implement it with the `implement` agent.
