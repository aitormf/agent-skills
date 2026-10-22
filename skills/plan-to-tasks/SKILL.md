---
name: plan-to-tasks
description: Splits an approved technical plan into small tasks, ordered by dependencies, with affected files, per-task verification and parallel groups. Use it when there is a plan and someone asks to break it down into tasks or get it ready for implementation.
---

# From plan to tasks

Turn a plan into an executable task list that the `implement` agent can follow and tick off.

- Each work item lives in `docs/specs/<YYYYMMDD>-<type>-<name>/`.
- `tasks.md` has no status: its progress is the `[x]` checkboxes.

## Before you start

1. Identify the work item and read `plan.md` and `spec.md`.
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

1. Draft `tasks.md` from `assets/tasks-template.md`.
2. Show the draft with:
   - the tasks;
   - the parallel groups;
   - the verification points;
   - any remaining questions.
3. Write it only once the person approves.
4. Suggested next step: implement it with the `implement` agent.
