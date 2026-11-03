<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an arbitrary file read, an incorrect pagination offset, and a broken caller of `listOrders`. Tier 2: the change touches both paths designated as sensitive by the project. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 2 · Optional 0 · Nits 0

## Critical

#### C1 Invoice path traversal exposes files
- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The invoice filename comes directly from the request and is joined to the invoice directory without validation.
- **Why it fails / scenario:** `GET /invoices?file=../../package.json` returns a file outside the invoice directory. A requester can similarly read other files accessible to the service process.
- **Fix:** Restrict accepted invoice names and ensure the resolved real path stays inside the invoice directory, including symlink handling. Add traversal regression tests.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 The first page skips the newest orders
- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `GET /orders?page=1&size=10` returns IDs 15–6 instead of 25–16; with `size=50`, the first page is empty.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`. Test exact IDs, ordering and page totals for the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversed ordering breaks the oldest-order caller
- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` assumes `listOrders()` returns the oldest order first, but the change reverses that order.
- **Why it fails / scenario:** The function returns order 25 instead of order 1, giving the wrong value for the customer-since calculation.
- **Fix:** Update the caller to select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output
- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** Every pagination request writes a debug message to standard output.
- **Why it fails / scenario:** Normal traffic produces debug entries even though this is not an intentional application log.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test the invoice endpoint
- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new invoice endpoint and its error branch have no tests.
- **Why it fails / scenario:** No test checks that a valid invoice returns its PDF content or that a missing invoice returns 404.
- **Fix:** Add endpoint tests for a valid invoice and a missing invoice; include the traversal regression described in C1.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js](repo/src/orders.js:16) copies the orders array before reversing it, preserving the original array.
- [test/orders.test.js](repo/test/orders.test.js:18) covers invalid, missing and valid integer inputs.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, one test file reported.
- Semgrep: attempted, but could not create a temporary directory in the read-only environment; no Semgrep MCP tool was available.
- No change folder matched the branch or diff; the task audit did not apply.
- Callers: reviewed the changed `listOrders` contract and its callers outside the diff.
- Findings refuted by the verifier: 0. The pagination test gap was folded into C2.
- Optional/Nit findings dropped by the limit: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=2 uncertain=0