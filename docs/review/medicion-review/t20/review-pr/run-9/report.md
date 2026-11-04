<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. It touches sensitive file-access paths, so this is **tier 2**. The review found an exploitable file-read vulnerability and two functional regressions. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 1 · Optional 1 · Nits 0

## Critical

#### C1 Invoice path traversal exposes files

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is used to construct a disk path without restricting traversal.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive that file; other files readable by the service can also be exposed.
- **Fix:** Accept permitted invoice identifiers, enforce containment within the invoice directory including symlink resolution, and test valid downloads and traversal rejection.
- **Confidence:** high
- **Source:** code-reviewer, security-auditor

#### C2 Pagination skips the first page of orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the page number as zero-indexed, although the API uses one-indexed pages.
- **Why it fails / scenario:** `page=1&size=10` starts at index 10, omitting the ten newest orders. Page 3 is empty despite there being 25 orders.
- **Fix:** Calculate `(page - 1) * pageSize` and test exact IDs and totals for successive pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 The oldest-order lookup returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on `listOrders()` returning oldest first, but this change reverses that order.
- **Why it fails / scenario:** The dashboard’s “customer since” lookup returns order 25 instead of order 1.
- **Fix:** Select the oldest order explicitly and add a test for the result.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug statement runs on every pagination request.
- **Why it fails / scenario:** Normal traffic continuously emits `DEBUG pageOrders` entries to the service log.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

#### O1 Explain the motivation and verification

- **Location:** Commit `e76f53b`
- **Problem:** The commit message describes the behavior but omits its motivation and test plan.
- **Why it fails / scenario:** A reviewer cannot tell from the change description why the behavior is needed or how it was verified.
- **Fix:** Add the motivation and verification details to the change description.
- **Confidence:** high
- **Source:** pr-description
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the page size at the stated maximum of 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; Node reported one test file and no failures.
- Semgrep: skipped; it failed because no writable temporary directory was available, and no Semgrep MCP tool was available.
- No applicable change folder or task audit.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Callers: two changed contracts checked; external HTTP callers cannot be inspected from this repository.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=1 uncertain=0