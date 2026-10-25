---
name: spec-to-plan
description: Turns an approved spec into a minimal technical plan (architecture, components, data model, contracts, tests and risks) and checks it against the non-negotiable principles in ARCHITECTURE.md. Use it when there is a spec and someone asks to plan, design the solution or decide how to implement it.
---

# From spec to plan

Turn a spec into a technical plan that can be split into tasks. The minimum the spec requires, nothing more.

- Each change lives in `docs/changes/<branch>/`, named after the last segment of the branch name (`feat/42-cancel-trip` → `docs/changes/42-cancel-trip/`), next to its `tasks.md`.

## Before you start

1. Identify the work item and read `spec.md`.
2. **Gate:** if the spec does not have `status: approved`, stop and ask:
   > The spec is `<status>`. Planning on an unapproved spec may force the plan to be redone. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer. If the person says to continue, note it under "Open decisions" in the plan.
3. Read, if they exist:
   - `docs/ARCHITECTURE.md`: layers, dependency rules, non-negotiable principles and code map;
   - the index `docs/decisions/README.md` and the accepted decisions whose `affects` covers the areas touched (or the related ADRs in `docs/adr/`, in projects that still use it);
   - the code in the areas that will be touched.

## Behaviour

- First, list the questions and assumptions, with the criterion and the question format of the `sdd-decisions` skill:
  - **ask** only the technical decisions for the person (security, hard to reverse, or a scope consequence), each one with options and your recommendation; the blocking ones before drafting;
  - **propose and write down** the reversible details with a clear default in the plan's `Assumptions` section;
  - **do not ask again** what the spec already decides, nor what `ARCHITECTURE.md`, an accepted decision or an existing pattern in the code already settles.
- Keep product intent (belongs to the spec) apart from technical decisions (belong to the plan). If the plan forces a change to the spec, say so; do not change it.
- Fit the solution into the existing layers and code map. If you propose something new (layer, dependency, pattern), justify it.
- For each acceptance criterion and each negative test in the Security section, state which test will cover it.
- **Principles check:** go one by one through the non-negotiable principles in `ARCHITECTURE.md` ("Non-negotiable principles", or "Principios innegociables" in Spanish-language projects) and fill in their table in the plan. If the plan breaks one, or contradicts an accepted decision, do not hide it: justify it and propose a decision that supersedes it (`record-decision`). If `ARCHITECTURE.md` does not exist, say so in the plan and suggest `generate-project-context`.

Format of each reply: `What I understand` · `Questions` · `Assumptions` · `Draft plan` · `Next step`.

## Result

1. Draft `plan.md` from `assets/plan-template.md`, with `status: draft`.
2. Show the draft and write it only once the person approves.
3. Suggested next step:
   - for a large change, review it with `review-spec`;
   - otherwise, have the person mark it `approved` and move on to `plan-to-tasks`.
