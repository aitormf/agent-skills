---
name: apply-review
description: Walks through the findings of a spec or plan review with the person and applies only the changes they explicitly approve, one by one. Then looks for other draft specs affected by the decisions. Use it when there is a review-spec.md or review-plan.md and they want to apply or discard its findings.
---

# Apply a review

Help the person decide on each finding and apply only what they approve.

**Core rule:** never assume, infer or apply a change without an explicit decision. If a finding is ambiguous, ask for clarification before offering options. Each finding is decided separately; never group them.

## Artifacts and status

- Each work item lives in `docs/specs/<YYYYMMDD>-<type>-<name>/`.
- `spec.md` and `plan.md` carry `status: draft | approved | obsolete` in their frontmatter. Only a person sets `approved`.
- If you change an artifact that was `approved`, set it back to `draft` and say so.

## Step 1: present the findings

1. Identify the work item and the review (`review-spec.md` or `review-plan.md`). Ask if it is not clear.
2. List all findings, numbered, blocking ones first. For each one show:
   - **Finding [N]:** what the review points out.
   - **Suggested fix**, if any.
   - **Options:**
     - A) Apply the fix as is.
     - B) Apply a modified fix (the person describes it).
     - C) Discard, with the reason.
     - D) Defer.

Wait for the person to answer **all** of them before going on.

## Step 2: confirm

```
Decision summary
────────────────
[N] <title> → apply / modified / discarded / deferred
```

Ask: "Do you confirm these decisions before I apply them?" Do not go on without confirmation.

## Step 3: apply

1. Apply only the confirmed changes (A and B), and only to the reviewed artifacts. Touch nothing else.
2. In the review file, below each finding, note the decision taken:
   - for discarded ones, the reason;
   - for deferred ones, what is still pending.
3. Tell the person where things stand:
   - If no blocking findings remain open, the artifact is ready for them to mark it `approved`, or for another `review-spec` pass.
   - If deferred blocking findings remain, or discarded ones that carry risk, point it out.

## Step 4: other affected specs

Check whether any decision from step 2 affects other specs in progress:

1. Look in `docs/specs/*/spec.md` for those with `status: draft`.
2. For each one, reason whether any decision introduces a conflict, changes a dependency or invalidates an assumption.
3. For each spec that *may* be affected:
   - show which spec, which section and what would need to change;
   - ask: "Does this decision affect it? Shall I propose a change?". **Wait for a yes or a no.**
4. If the answer is yes, draft only the minimal change (the exact section and lines), show the diff and **apply it only after approval**.

Do not improve, extend or reformat anything else in those specs. If at any point it is unclear what to do, stop and ask.
