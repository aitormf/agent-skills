---
name: sdd-next
description: Tells where a work item in docs/specs/ stands and what the next step is, by looking at which artifacts exist and their status; with no arguments, summarizes all work items. Read-only, never changes status. Use it when asked "what now?", "where is X at?", "which specs are open?" or for the status of the specs.
---

# SDD next step

Infer the state of each work item from its artifacts. There is no central backlog or state machine: the source of truth is the files and their frontmatter. **You only read**: you never change `status` or write artifacts, and you do not launch other skills unless the person asks.

Work management (priority, owner, whether it is done) lives in the tracker. If an artifact has `issue:`, show it, but do not look it up.

## How to infer the next step

For `docs/specs/<work-item>/`, apply the first row that matches:

| Situation | Next step |
|---|---|
| No `spec.md` (and no `tasks.md`) | Write the spec: `idea-to-spec` |
| `spec.md` in `draft`, with a review that has undecided findings | Decide them: `apply-review` |
| `spec.md` in `draft` | Review it (`review-spec`) or have the person approve it |
| `spec.md` approved, no `plan.md` | Plan: `spec-to-plan` (or straight to tasks, for a small change) |
| `plan.md` in `draft`, with a review that has undecided findings | Decide them: `apply-review` |
| `plan.md` in `draft` | Review it (`review-spec`) or have the person approve it |
| Plan approved (or spec approved for a small change), no `tasks.md` | Split into tasks: `plan-to-tasks` |
| `tasks.md` with unchecked boxes | Implement: `implement` agent (say how many are left) |
| All boxes checked | Review the code against the spec (`review-prepush`) and open the PR (`review-pr`) |
| `status: obsolete` | Nothing. Say what replaces it, if stated |

A review has "undecided findings" if any of them has no `apply-review` decision noted below it.

## Warnings

Besides the next step, warn if:

- **The plan may be stale:** `spec.md` was modified after `plan.md`. Compare with `git log -1 --format=%cI -- <file>`. Same between `plan.md` and `tasks.md`.
- **A gate was skipped:** there is a `plan.md` with the spec in `draft`, or a `tasks.md` with the plan in `draft`. It may be a deliberate decision; just say it.
- **It has been idle for a while:** more than 30 days without commits in the directory and not finished. Ask whether it is still alive or should be marked `obsolete`.

## Format

**One work item:** directory, artifacts with their status, task progress (`5/8`), next step and warnings.

**All** (no argument): a table sorted by date, most recent first. Columns: work item, spec, plan, tasks, next step and warning. Finished and obsolete items go at the end, one line each. This view is generated every time: do not save it to a file.
