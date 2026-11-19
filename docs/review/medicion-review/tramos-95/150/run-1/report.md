## Summary and verdict

The branch consolidates review facts into one script, changes how unticketed TODOs are reported, and records a measurement of the review process. The review found gaps in failure handling and audit scope, plus conflicts with an accepted language decision.

**Verdict:** FIX BEFORE PR

## Critical

None.

## Required

#### R1 Preserve verification when fact gathering fails

- **Location:** [skills/review-prepush/SKILL.md](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** A facts-script failure sends the review directly to Step 3, skipping the checks in Step 2.
- **Why it fails / scenario:** If Python is unavailable or the base cannot be resolved, configured checks and Semgrep are omitted, and the reviewer lacks the base and task context.
- **Fix:** Run verification despite the failure and provide a fallback for the review scope, or stop with an explicit incomplete-review report.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Use the selected base for the task audit

- **Location:** [skills/review-context/scripts/review_facts.py](repo/skills/review-context/scripts/review_facts.py:115)
- **Problem:** The audit is invoked without the base selected for the review; it resolves its own base independently.
- **Why it fails / scenario:** A review against `develop` can audit history and dependencies against `main`, producing false problems or missing real ones.
- **Fix:** Pass the selected base through to the audit, or report the audit as unchecked when the bases differ.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Report an unchecked audit when the task file is missing

- **Location:** [skills/review-context/scripts/review_facts.py](repo/skills/review-context/scripts/review_facts.py:106)
- **Problem:** A missing task file or plan README causes an early return without an audit result or an unchecked-audit marker.
- **Why it fails / scenario:** A task branch with a missing task file can silently omit the test-protection limitation from the review.
- **Fix:** Emit an unchecked-audit reason or surface the audit failure, and cover this path with a test.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Align script messages with the language decision

- **Location:** [skills/review-context/scripts/review_facts.py](repo/skills/review-context/scripts/review_facts.py:130)
- **Problem:** New script output uses Spanish despite accepted decision D-0009 requiring English for scripts.
- **Why it fails / scenario:** Consumers receive labels and messages that conflict with the repository’s recorded language convention.
- **Fix:** Use English consistently and update the skill and tests, or record a superseding decision.
- **Confidence:** high
- **Source:** code-reviewer

#### R5 Resolve the language decision for measurement reports

- **Location:** [docs/review/medicion-review/t6-hechos/run-1/report.md](repo/docs/review/medicion-review/t6-hechos/run-1/report.md:3)
- **Problem:** The three new generated reports under `docs/` are in English, while D-0009 requires project-language documentation and generated artifacts.
- **Why it fails / scenario:** The recorded reports conflict with an accepted decision without an exception.
- **Fix:** Bring the artifacts into compliance or record an exception that permits preserving the original measurement evidence.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 One TODO/FIXME without a ticket

- **Location:** [scripts/check.sh](repo/scripts/check.sh:1419)
- **Problem:** The facts script lists one added TODO without a ticket.
- **Why it fails / scenario:** It cannot be traced to a ticket from the comment.
- **Fix:** Add a ticket reference if the comment represents outstanding work.
- **Confidence:** high
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- The tests exercise Git formatting configuration and base-selection precedence, protecting the facts output from common local configuration differences.
- The TODO flow keeps the locations together and specifies a single consolidated Nit.

## Seams

The seams review independently found R1; it is reported once above.

## Verification

- Commands found in `AGENTS.md`: none; no root `AGENTS.md` exists.
- `python3 .agents/skills/review-context/scripts/review_facts.py main` → passed; identified three tramos and no associated task.
- Semgrep → failed to start because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- Callers: reviewers examined the changed facts CLI and its relevant consumer; dynamic invocations cannot be enumerated.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits (`Max Optional=3`, `Max Nits=3`): 0.

REVIEW_RESULT: PASS critical=0 required=5 uncertain=0