---
name: spec-to-plan
description: Turns an approved spec into a minimal technical plan (architecture, components, data model, contracts, tests and risks) and checks it against the non-negotiable principles in ARCHITECTURE.md. Use it when there is a spec and someone asks to plan, design the solution or decide how to implement it.
---

# From spec to plan

Turn a spec into a technical plan that can be split into tasks. The minimum the spec requires, nothing more.

- Each work item lives in `docs/specs/<YYYYMMDD>-<type>-<name>/`.

## Before you start

1. Identify the work item and read `spec.md`.
2. **Gate:** if the spec does not have `status: approved`, stop and ask:
   > The spec is `<status>`. Planning on an unapproved spec may force the plan to be redone. Shall I continue anyway, review it first with `review-spec`, or will you approve it now?

   Continue only with an explicit answer. If the person says to continue, note it under "Open decisions" in the plan.
3. Read, if they exist:
   - `docs/ARCHITECTURE.md`: layers, dependency rules, non-negotiable principles and code map;
   - the related ADRs in `docs/adr/`;
   - the code in the areas that will be touched.

## Behaviour

- First, list the open questions and assumptions. If any of them blocks, ask it before drafting, with concrete options.
- Keep product intent (belongs to the spec) apart from technical decisions (belong to the plan). If the plan forces a change to the spec, say so; do not change it.
- Fit the solution into the existing layers and code map. If you propose something new (layer, dependency, pattern), justify it.
- For each acceptance criterion and each negative test in the Security section, state which test will cover it.
- **Principles check:** go one by one through the non-negotiable principles in `ARCHITECTURE.md` ("Non-negotiable principles", or "Principios innegociables" in Spanish-language projects) and fill in their table in the plan. If the plan breaks one, do not hide it: justify it and propose an ADR. If `ARCHITECTURE.md` does not exist, say so in the plan and suggest `generate-project-context`.

Format of each reply: `What I understand` · `Open questions` · `Draft plan` · `Next step`.

## Result

1. Draft `plan.md` from `assets/plan-template.md`, with `status: draft`.
2. Show the draft and write it only once the person approves.
3. Suggested next step:
   - for a large change, review it with `review-spec`;
   - otherwise, have the person mark it `approved` and move on to `plan-to-tasks`.
