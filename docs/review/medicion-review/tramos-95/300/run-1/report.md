## Summary and verdict

The branch consolidates pre-push review facts, task auditing and TODO reporting, and records measurements of the revised workflow. Two defects need attention: the audit can use a different base from the review, and a failure of the facts script leaves required review inputs unavailable.

**Verdict:** FIX BEFORE PR

## Critical

None.

## Required

#### R1 The audit can use a different base from the review

- **Location:** [review_facts.py:115](repo/skills/review-context/scripts/review_facts.py:115)
- **Problem:** The facts script does not pass its resolved base to the task auditor, which selects its own base.
- **Why it fails / scenario:** A review against `develop` with `origin/HEAD` pointing to `main` checks the diff against `develop` but audits commits and dependencies against `main`. The audit can therefore report false problems or miss missing test protection or dependencies.
- **Fix:** Pass the resolved base to the auditor and use it for its checks; add a test with divergent bases.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 A facts-script failure leaves the review without required inputs

- **Location:** [SKILL.md:37](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** The skill says to continue if `review_facts.py` fails but prohibits collecting facts by other commands, while the reviewer brief requires the base and diff.
- **Why it fails / scenario:** If Python is unavailable or base resolution fails before the facts are printed, the review lacks those inputs; the task audit and TODO detection also go unchecked.
- **Fix:** Define a read-only fallback for the base and diff, and either perform the audit and TODO checks or explicitly report each as unchecked.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 One TODO without a ticket

- **Location:** [scripts/check.sh:1419](repo/scripts/check.sh:1419)
- **Problem:** The facts script lists one TODO without a ticket. It appears inside a test fixture.
- **Why it fails / scenario:** The report lists this fixture as an unticketed TODO.
- **Confidence:** high
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- [medicion-review.md:16](repo/docs/review/medicion-review.md:16) states the sample size, the Codex version change and that the task audit was not exercised, making the measurement’s limits clear.

## Seams

No findings at the boundary between the implementation and measurement tramos.

## Verification

- Commands found in `AGENTS.md`: none; no root `AGENTS.md` exists.
- `python3 .agents/skills/review-context/scripts/review_facts.py main` → passed; two tramos, no task identified.
- Semgrep: skipped after its script failed because no writable temporary directory was available. No Semgrep MCP tool was available.
- Callers: implementation tramo reported one changed contract and no external calls read; the documentation tramo and seams pass identified no changed contracts.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: PASS critical=0 required=2 uncertain=0