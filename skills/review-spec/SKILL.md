---
name: review-spec
description: Reviews a spec or a plan before implementation, looking for ambiguities, gaps, contradictions, over-engineering and clashes with the principles in ARCHITECTURE.md and the ADRs. Writes a recommendation, never approves. Use it when asked to review or audit a spec, a plan or a task list.
---

# Review a spec or plan

Review the artifacts of a work item and leave a recommendation. **You do not approve or modify anything**: approval belongs to a person, and changes are applied by `apply-review`.

To review with a clean context, delegate to the `spec-reviewer` subagent, which applies this same skill.

## Artifacts and status

- Each work item lives in `docs/specs/<YYYYMMDD>-<type>-<name>/`.
- `spec.md` and `plan.md` carry `status: draft | approved | obsolete` in their frontmatter. **Only a person sets `approved`. You never change `status`.**

## What to review

Identify the work item (ask if it is not clear) and what is to be reviewed:

- **Spec** (`spec.md`).
- **Plan** (`spec.md` + `plan.md`, and `tasks.md` if it exists).

Also read, if they exist:

- `docs/ARCHITECTURE.md`, especially the non-negotiable principles ("Non-negotiable principles", or "Principios innegociables" in Spanish-language projects) and the glossary;
- the related ADRs in `docs/adr/`.

Look for:

- **Ambiguity:** requirements that can be read two ways; terms that are not in the glossary or are used with another meaning.
- **Gaps:**
  - uncovered edge cases;
  - acceptance criteria that cannot be verified;
  - requirements with no acceptance criterion;
  - the Security section, if it is missing and the feature touches data, auth or external input;
  - in a plan, acceptance criteria with no test proving them.
- **Contradictions:** between sections, between spec and plan, or with other current specs in `docs/specs/`.
- **Principles and ADRs:** every clash with a non-negotiable principle or with an accepted ADR is **blocking**, unless the plan justifies it and proposes an ADR.
- **Over-engineering and scope:** complexity the spec does not ask for, or a plan that does more than the spec says.
- Undeclared **assumptions**.

## Result

1. Write `review-spec.md` or `review-plan.md` in the work item's directory, from `assets/review-template.md`.
   - Findings numbered and by priority: blocking, important and minor. Each one with the affected section, what is wrong and the suggested fix.
   - If a previous review already existed, replace it; the history stays in git.
2. Recommendation:
   - **"Ready to approve"** if there are no blocking findings;
   - **"Send back"** if there are, with the reason.
3. Tell the person the next step:
   - apply the changes with `apply-review`;
   - or, if it is ready, set `status: approved` themselves.

Be concrete and cite the section. Do not rewrite the artifact or propose improvements that do not come from a finding.
