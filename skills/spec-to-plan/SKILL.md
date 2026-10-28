---
name: spec-to-plan
description: Turns an approved spec into a short, design-level technical plan (components and the existing ones it reuses, contracts, data model, technical decisions, which test covers each criterion, risks), checked against the non-negotiable principles in ARCHITECTURE.md, and writes it straight to the file as a draft. Use it when there is a spec and someone asks to plan, design the solution or decide how to implement it.
---

# From spec to plan

Turn a spec into a design the tasks can be split from. The minimum the spec requires, nothing more.

- The plan goes in `docs/changes/<change>/plan.md`, on the plan branch `<change>/plan` (the change is the second-to-last segment: `feat/42-cancel-trip/plan` → `docs/changes/42-cancel-trip/`).

## Before you start

1. Read `spec.md`. **Gate:** if it is not `status: approved`, stop and ask:
   > The spec is `<status>`. Planning on an unapproved spec may force the plan to be redone. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer; if it is "continue", note it under "Open decisions".
2. Read, if they exist: `docs/ARCHITECTURE.md` (layers, non-negotiable principles, code map), the index `docs/decisions/README.md` and the accepted decisions whose `affects` covers the areas touched (or `docs/adr/`), and the code in those areas.

## What goes in the plan

**Design, not an implementation script.** In: components and responsibilities, **the existing components it reuses** (modules, functions, libraries already installed) before anything new, contracts between layers, the data model, technical decisions with their alternatives, which test covers each acceptance criterion and each negative test from Security, and risks. Out: exact commands, call arguments, code, test names, line-level steps. Those belong to `implement` (test-first) and to the code review, unless the detail is itself a decision with consequences ("no shell", "no git hooks"). A plan over about 150 lines is going too low, or the change is too big: say so and propose splitting it.

- Ask only the technical decisions for the person (security, hard to reverse, a scope consequence), with the `sdd-decisions` criterion and format. Do not ask again what the spec, `ARCHITECTURE.md`, an accepted decision or an existing pattern already settles; the rest goes to `Assumptions`.
- Keep product intent (the spec) apart from technical decisions (the plan). If the plan forces a change to the spec, say so; do not change it.
- Fit the solution into the existing layers. Justify anything new (layer, dependency, pattern).
- **Principles check:** fill in the table with each non-negotiable principle of `ARCHITECTURE.md` ("Principios innegociables" in Spanish-language projects). A plan that breaks one, or contradicts an accepted decision, justifies it and proposes a decision that supersedes it (`record-decision`). If `ARCHITECTURE.md` does not exist, say so and suggest `generate-project-context`.

## Result

1. Write `plan.md` from `assets/plan-template.md`, with `status: draft`. **Do not paste it in the chat:** the person reviews the file.
2. Draft, with `record-decision`, the technical decisions that outlive the change, as `proposed`.
3. Tell the person, in a few lines: the path, the decisions taken, the numbered assumptions, the open decisions and one line per record. "ok" accepts the assumptions and the records (set them `accepted`).
4. Next step: `review-spec` for a large change; otherwise the person sets `status: approved` and moves on to `plan-to-tasks`.
