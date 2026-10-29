---
name: review-spec
description: Reviews a spec or a plan before implementation, looking for ambiguities, gaps, contradictions, over-engineering and clashes with the principles in ARCHITECTURE.md and the recorded decisions. Writes a recommendation, never approves. Use it when asked to review or audit a spec, a plan or a task list.
kind: skill
uses:
  - skill:sdd-decisions
related:
  - agent:spec-reviewer
  - skill:apply-review
---

# Review a spec or plan

Review the artifacts of a work item and leave a recommendation. **You do not approve or modify anything**: approval belongs to a person, and changes are applied by `apply-review`.

To review with a clean context, delegate to the `spec-reviewer` subagent, which applies this same skill.

## Artifacts and status

- Each change lives in `docs/changes/<change>/`; its spec, plan and tasks go on the plan branch `<change>/plan` (the change is the second-to-last segment of the branch name: `feat/42-cancel-trip/plan` → `docs/changes/42-cancel-trip/`), next to its `README.md` and `tasks/`.
- `spec.md` and `plan.md` carry `status: draft | approved | obsolete` in their frontmatter. **Only a person sets `approved`. You never change `status`.**

## What to review

Identify the work item (ask if it is not clear) and what is to be reviewed:

- **Spec** (`spec.md`).
- **Plan** (`spec.md` + `plan.md`, and the task files in `tasks/` if they exist).

Also read, if they exist:

- `docs/ARCHITECTURE.md`, especially the non-negotiable principles ("Non-negotiable principles", or "Principios innegociables" in Spanish-language projects), and the glossary (in `AGENTS.md`; in older projects, in `docs/ARCHITECTURE.md`);
- the index `docs/decisions/README.md` and the accepted decisions whose `affects` covers the areas touched (or the related ADRs in `docs/adr/`, in projects that still use it).

Look for:

- **Ambiguity:** requirements that can be read two ways; terms that are not in the glossary or are used with another meaning.
- **Gaps:**
  - uncovered edge cases;
  - acceptance criteria that cannot be verified;
  - requirements with no acceptance criterion;
  - the Security section, if it is missing and the feature touches data, auth or external input;
  - in a plan, acceptance criteria with no test proving them.
- **Contradictions:** between sections, between spec and plan, or with the specs of other open changes in `docs/changes/*/`.
- **Principles and decisions:** every clash with a non-negotiable principle or with an accepted decision is **blocking**, unless the plan justifies it and proposes a new decision that supersedes it.
- **Over-engineering and scope:** complexity the spec does not ask for, or a plan that does more than the spec says.
- Undeclared **assumptions**.
- In a plan, a plan that goes **below design level** (exact commands, code, line-level steps): one finding, a fix that removes them.

**A plan is reviewed at design level.** Implementation details (a missing timezone, how a process is killed, a test helper) are not findings: they belong to `implement` and the code review. If one carries a real risk, note it in one line under the review's `Risks`, for `implement`: not a finding, neither a decision nor a fix.

Do not report what the artifact already lists as an open question or an assumption, unless it is wrong or it is really a decision for the person that should not have been assumed (see below).

## Precision

- **A few real findings beat many doubtful ones.** Report only what you would defend in front of the author with the artifact open.
- **Justify before you classify:** first why it is a problem and in which scenario; the priority last.
- **At most 3 minor findings**, the most useful ones. Drop wording and formatting preferences that do not change what gets built.
- If in doubt, say so and state what would confirm it. Never present a guess as a fact.

## Decision or fix

Classify each finding with the criterion of the `sdd-decisions` skill:

- **Decision for the person:** there are reasonable alternatives and choosing depends on product, scope, security or something hard to reverse. Give the options (2 or 3) and your recommendation, with the reason.
- **Fix:** it has one reasonable answer. Give the concrete change (the text to add or replace), not a description of it.

If in doubt, it is a decision. Priority and type are independent: a blocking finding can be a fix, and a minor one can be a decision.

## Result

1. Write `review-spec.md` or `review-plan.md` in the work item's directory, from `assets/review-template.md`.
   - Findings numbered and by priority: blocking, important and minor. Each one with the affected section, what is wrong, its type (decision or fix) and, depending on the type, the options with a recommendation or the concrete fix.
   - If a previous review already existed, replace it; the history stays in git.
2. Recommendation:
   - **"Ready to approve"** if there are no blocking findings;
   - **"Send back"** if there are, with the reason.
3. Tell the person the next step:
   - apply the changes with `apply-review`;
   - or, if it is ready, set `status: approved` themselves.

Be concrete and cite the section. Do not rewrite the artifact or propose improvements that do not come from a finding.
