<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. It is **tier 2** because it changes the server and invoice file access; the review found an arbitrary file read and two order-related regressions. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 0 · Nits 0

## Critical

#### C1 Invoice download permits arbitrary file reads
- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The file path is built directly from the request parameter without restricting it to the invoice directory.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive a file outside `data/invoices`. Other files readable by the service may also be exposed.
- **Fix:** Accept only authorized invoice identifiers, enforce containment within the invoice directory, including against symlink escapes, and add traversal regression tests.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 Pagination skips the first page of orders
- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset uses `page * pageSize` even though pages start at 1.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns IDs 15–6 instead of 25–16; with size 50, the first page is empty despite there being 25 orders.
- **Fix:** Calculate `(page - 1) * pageSize` and assert exact contents and totals for the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversed ordering breaks the existing first-order consumer
- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on `listOrders()` returning the oldest order first, but the change reverses that order.
- **Why it fails / scenario:** `firstOrder()` now returns order 25 instead of order 1, changing the value used for “customer since.”
- **Fix:** Update the consumer to select the oldest order, or preserve a compatible ordering contract, and test the result.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Duplicate total calculation
- **Location:** [src/orders.js:25](repo/src/orders.js:25)
- **Problem:** The new `pageTotal` duplicates the existing `sumTotals` reduction.
- **Why it fails / scenario:** Two implementations of the same calculation can diverge when the total calculation changes.
- **Fix:** Reuse a shared calculation in a module that avoids a circular dependency.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Invoice download has no success-path test
- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice endpoint and its disk-read path have no test.
- **Why it fails / scenario:** Returning incorrect bytes or failing to serve a valid invoice would leave the current suite green.
- **Fix:** Test that a known invoice returns the expected PDF bytes and status. Include the security cases described in C1.
- **Confidence:** high
- **Source:** test-engineer

#### R3 New order contract is not tested
- **Location:** [src/orders.js:15](repo/src/orders.js:15)
- **Problem:** The existing `listOrders` test checks only the number of results.
- **Why it fails / scenario:** Removing `reverse()` would pass the test even though the new contract requires the newest orders first.
- **Fix:** Assert the returned order, including IDs 25 and 1 at the respective ends.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50.
- [src/server.js:22](repo/src/server.js:22) returns a generic response when an invoice read fails.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; Node reported one test file.
- Semgrep: skipped after the script failed because no temporary directory was writable; no Semgrep MCP tool was available.
- Callers: two changed contracts checked; the existing `listOrders` consumer revealed C3.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0