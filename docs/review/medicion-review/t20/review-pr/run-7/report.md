<!-- review-kit:review-pr -->

## Summary and verdict

The branch adds order pagination and invoice downloads. It has three critical defects: arbitrary file disclosure, incorrect page boundaries, and a broken caller of the changed ordering contract. **Tier 2:** the change touches the high-risk invoice and server paths. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 0 · Nits 0

## Critical

#### C1 Invoice requests can read files outside the invoice directory

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The path passed to the disk read is built directly from the request’s `file` parameter, without confinement to the invoice directory.
- **Why it fails / scenario:** Any client can request `/invoices?file=../../package.json` and receive that file’s contents.
- **Fix:** Restrict invoice identifiers and enforce resolved-path containment, including symlinks. Add a traversal regression test.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset multiplies a one-indexed page number directly by the page size.
- **Why it fails / scenario:** The default `/orders` request returns IDs 15 through 6 instead of 25 through 16; the newest ten orders are skipped for every valid page.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and assert exact IDs and totals for the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversing orders breaks the oldest-order caller

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still assumes that the first item returned by `listOrders()` is the oldest.
- **Why it fails / scenario:** After the reversal it returns order 25 instead of order 1, contrary to its documented oldest-order contract.
- **Fix:** Update `firstOrder()` to select the oldest order independently of the new ordering and test its result.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove request-time debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug statement remains in the pagination function.
- **Why it fails / scenario:** Every `/orders` request writes debugging data to the service output.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test invoice downloads and errors

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice endpoint has no tests.
- **Why it fails / scenario:** Returning 404 for an existing invoice or incorrect content would leave the current suite passing.
- **Fix:** Test an existing invoice and a missing invoice, in addition to the traversal regression test in C1.
- **Confidence:** high
- **Source:** test-engineer

#### R3 Test the new ordering contract

- **Location:** [test/orders.test.js:7](repo/test/orders.test.js:7)
- **Problem:** The `listOrders` test checks only the number of results.
- **Why it fails / scenario:** Returning the original ascending order would still pass despite the new newest-first contract.
- **Fix:** Assert the returned order, including the first and last IDs.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:16](repo/src/orders.js:16) reverses a copy, preserving the original `ORDERS` array.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; the runner reported one test file and no failures.
- Semgrep: skipped after its script failed because the read-only environment had no usable temporary directory; no Semgrep MCP tool was available.
- Findings refuted by the verifier: 0. The pagination test finding was folded into C2.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Callers: three changed symbols checked; three outside-diff call sites read.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0