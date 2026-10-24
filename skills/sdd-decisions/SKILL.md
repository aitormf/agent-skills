---
name: sdd-decisions
description: Shared criterion of the SDD skills (idea-to-spec, spec-to-plan, plan-to-tasks, review-spec, apply-review) and of record-decision — what is a decision for the person, to be asked, and what is a fix or an assumption with a clear default, to be proposed and written down; and which decisions are recorded in docs/decisions/. Also the question format with a recommended option. Load it whenever one of those skills asks the person something or classifies a review finding.
user-invocable: false
---

# Decisions for the person

The person's time goes into reading and answering. Ask only what is theirs to decide; propose the rest, in writing, where they can see it and change it.

## The criterion

Something is a **decision for the person** if there are reasonable alternatives **and** choosing depends on at least one of:

- **Product:** what the user sees or gets, the behaviour, the wording that reaches them.
- **Scope:** what goes in and what stays out, what is done now and what later.
- **Security or risk:** permissions, data exposure, untrusted input, what an agent or user is allowed to do, cost or data loss if it goes wrong.
- **Hard to reverse:** public contracts, data formats or migrations, external dependencies, anything that other work will be built on.

Everything else has a **clear default**: a reversible detail where one option is obviously reasonable (naming, an internal limit, the layout of a section, a detail the glossary, the principles or an existing pattern already settle). It is not asked. It is:

- in a spec or plan: proposed and written in the `Assumptions` section;
- in a review: reported as a **fix**, with the concrete change.

If in doubt, it is a decision. If a decision is already taken in an approved artifact (the spec for the plan; the spec and plan for the tasks), it is not asked again.

**This is not assuming silently.** An assumption is written in the artifact, in sight; the person or a review can change it. What is never allowed is an assumption nobody can see.

## What is recorded

Once the person has answered, a decision that **outlives the current work** is recorded in `docs/decisions/` with `record-decision`: a later change could contradict it, or someone could propose the discarded option again. It is an architecture choice, a business rule with its edge, or an approach that was tried and discarded.

Assumptions are never recorded there: they stay in the artifact where they were written. Neither are decisions that only matter until the work item is closed (the wording of one message, the order of two tasks).

Draft the records as `proposed` once the planning is done (the spec and plan are drafted, or the example map is settled), and show them together with that artifact: accepting them is part of the same review, not an extra stop.

## How to ask

- Group the questions of a round in one message, numbered. Each one with its options and **the recommended one marked**:

  > **1. Do we notify on every line or only on the ones the user follows?** (product)
  > - **A) Only the ones they follow** ← recommended: it is what the problem describes
  > - B) Every line
  > - C) Leave it as an open question

- After the questions, list the assumptions you are taking for that round, numbered, one line each.
- **"ok"** accepts every recommendation and every assumption. The person only answers what they want to change ("2b", "assumption 3: 30 s, not 10").
- A question with no recommendation is allowed, but say why (both options are equally reasonable, or you lack the information).
