---
name: apply-review
description: Walks through the findings of a spec or plan review with the person — asks the decisions one by one, applies the fixes in a block the person can see and trim — and applies nothing they have not seen. Then looks for other draft specs affected by the decisions. Use it when there is a review-spec.md or review-plan.md and they want to apply or discard its findings.
kind: skill
uses:
  - skill:sdd-decisions
---

# Apply a review

Help the person decide on the findings and apply only what they have seen and not rejected.

**Core rule:** never apply a change the person has not seen. Ask only what is theirs to decide (the decisions); show the rest (the fixes) and apply it unless they exclude it. If a finding is ambiguous, ask for clarification before offering options.

## Artifacts and status

- Each change lives in `docs/changes/<change>/`; its spec, plan and tasks go on the plan branch `<change>/plan` (the change is the second-to-last segment of the branch name: `feat/42-cancel-trip/plan` → `docs/changes/42-cancel-trip/`), next to its `README.md` and `tasks/`.
- `spec.md` and `plan.md` carry `status: draft | approved | obsolete` in their frontmatter. Only a person sets `approved`.
- If you change an artifact that was `approved`, set it back to `draft` and say so.

## Step 1: present the findings

1. Identify the work item and the review (`review-spec.md` or `review-plan.md`). Ask if it is not clear.
2. Split the findings by their type in the review. If a finding has no type (an older review), classify it with the criterion of the `sdd-decisions` skill; if in doubt, it is a decision.
3. **Decisions**, one at a time, blocking ones first. For each one show:
   - **Finding [N]:** what the review points out.
   - **Options**, from the review, with the recommended one marked, plus:
     - discard, with the reason;
     - defer.

   Wait for the answer before showing the next one. "ok" accepts the recommendation.
4. **Fixes**, all together in one list, numbered as in the review, one line each: the finding and the change that will be made. Then say:
   > I will apply all these fixes. Tell me which ones to exclude or change ("all but 4", "6: <other text>"), or "ok".

   A fix the person excludes is discarded or deferred; ask which only if they do not say.

If there are no decisions, go straight to the fixes; if there are no fixes, skip that step.

## Step 2: confirm, only if needed

Every answer above is explicit, so there is no extra confirmation. Show the summary and ask for confirmation only if:

- you interpreted an answer (a modified option, a free-text reply), or
- a blocking finding ends up discarded or deferred.

```
Decision summary
────────────────
[N] <title> → apply / modified / discarded / deferred
```

## Step 3: apply

1. Apply the accepted decisions and fixes, and only to the reviewed artifacts. Touch nothing else.
2. In the review file, below each finding, note the decision taken:
   - for discarded ones, the reason;
   - for deferred ones, what is still pending.
3. Tell the person where things stand:
   - If no blocking findings remain open, the artifact is ready for them to mark it `approved`, or for another `review-spec` pass.
   - If deferred blocking findings remain, or discarded ones that carry risk, point it out.

## Step 4: other affected specs

Check whether any decision from step 1 affects other specs in progress:

1. Look in `docs/changes/*/spec.md` for those with `status: draft`.
2. For each one, reason whether any decision introduces a conflict, changes a dependency or invalidates an assumption.
3. For each spec that *may* be affected:
   - show which spec, which section and what would need to change;
   - ask: "Does this decision affect it? Shall I propose a change?". **Wait for a yes or a no.**
4. If the answer is yes, draft only the minimal change (the exact section and lines), show the diff and **apply it only after approval**.

Do not improve, extend or reformat anything else in those specs. If at any point it is unclear what to do, stop and ask.
