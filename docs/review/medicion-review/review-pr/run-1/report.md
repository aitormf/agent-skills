<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. It is **tier 2** because it changes the invoice and server paths, including a disk read built from request data. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 0 · Nits 0

## Critical

#### C1 Path traversal exposes files readable by the service

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice filename comes directly from the request and is joined to the invoice directory without containment checks.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` to read that file. Additional `../` segments can reach other files readable by the service.
- **Fix:** Restrict invoice names to an allowed format and ensure the resolved file, including any symlink target, stays within the invoice directory. Add traversal regression tests.
- **Confidence:** high
- **Source:** security-auditor

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** Page 1 with size 10 returns orders 15 through 6 instead of 25 through 16. Page 1 with size 50 returns no orders.
- **Fix:** Use `(page - 1) * pageSize` and assert exact IDs at page boundaries.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 New ordering changes the oldest-order result

- **Location:** [src/orders.js:16](repo/src/orders.js:16)
- **Problem:** Reversing `listOrders()` changes the behavior of its existing caller, `firstOrder()`.
- **Why it fails / scenario:** `firstOrder()` promises the oldest order but now returns order 25 instead of order 1.
- **Fix:** Update `firstOrder()` to select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Reuse the existing total calculation

- **Location:** [src/orders.js:25](repo/src/orders.js:25)
- **Problem:** The new `pageTotal` helper duplicates the existing `sumTotals` helper.
- **Why it fails / scenario:** Page totals and revenue now have separate implementations that can diverge when the calculation changes.
- **Fix:** Put the shared calculation in a dependency-neutral module and use it from both callers.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test the invoice endpoint

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new endpoint has no tests for successful or failed invoice reads.
- **Why it fails / scenario:** The suite would still pass if an existing invoice returned 404 or a missing invoice returned an incorrect response.
- **Fix:** Add handler tests for an existing invoice and a missing invoice, alongside the traversal tests in C1.
- **Confidence:** high
- **Source:** test-engineer

#### R3 Verify the page total

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The pagination test does not check the new `pageTotal` calculation.
- **Why it fails / scenario:** The test would pass if every page reported a total of zero.
- **Fix:** Assert the expected `pageTotal` for a page with known orders.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:16](repo/src/orders.js:16) copies the order array before reversing it, preserving the shared array.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: unavailable for this run; it failed because the read-only environment has no usable temporary directory. No Semgrep tool was available as a fallback.
- Findings refuted by the verifier: 0.
- Pagination content assertions and traversal tests are included in the fixes for C2 and C1, respectively.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0