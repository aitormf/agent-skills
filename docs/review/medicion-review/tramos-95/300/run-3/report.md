## Summary and verdict

The branch consolidates pre-push review facts into one script and records a measurement of the resulting workflow. Two error paths can leave a review without required verification or task audit information.

**Verdict:** BLOCK

## Critical

#### C1 Facts failure skips verification and leaves the reviewer without a base

- **Location:** [skills/review-prepush/SKILL.md:37](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** If the facts script fails, the instructions jump directly to the review step, bypassing configured checks and Semgrep.
- **Why it fails / scenario:** If Python is unavailable or the script fails, a review can proceed without verification and without the base and task facts required for its brief.
- **Fix:** Resolve the base and task through a read-only fallback, then run verification before spawning the reviewer. Report checks that cannot run.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 A missing task file silently suppresses the audit

- **Location:** [skills/review-context/scripts/review_facts.py:107](repo/skills/review-context/scripts/review_facts.py:107)
- **Problem:** A recognized task branch with no matching task file returns without an audit status.
- **Why it fails / scenario:** On `<change>/T2` with a deleted or misnamed task file, the script prints `tarea: T2 sin fichero...`; the review instructions handle neither that value nor the absent audit, so the report can omit the task and test-protection status.
- **Fix:** Emit `auditoría: no comprobada (<reason>)` and explicitly handle the missing task in the review instructions, or run the audit and surface its failure.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 1 TODO/FIXME without a ticket

- **Location:** [scripts/check.sh:1419](repo/scripts/check.sh:1419)
- **Problem:** The facts script lists this location as a TODO without a ticket.
- **Why it fails / scenario:** The review workflow requires listed locations to be reported as one Nit.
- **Fix:** Add a ticket reference if appropriate.
- **Confidence:** high
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- [scripts/check.sh:1375](repo/scripts/check.sh:1375) tests facts collection against user Git configuration overrides and checks that the TODO section remains available.

## Seams

No findings across the two tramos.

## Verification

- Commands found in AGENTS.md: none; no root AGENTS.md was present, so no project verification commands were run.
- `python3 .agents/skills/review-context/scripts/review_facts.py main` → passed; identified two tramos and no associated task.
- Semgrep: failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- Callers, tramo 1: one changed CLI contract; no outside call sites read. Tramo 2: no changed symbol contracts. Seams: no changed symbols crossing into unchanged code checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=1 required=1 uncertain=0