<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an arbitrary file read, incorrect page offsets and a regression in the oldest-order lookup. Tier 2: sensitive area; requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 2 · Optional 0 · Nits 0

## Critical

#### C1 Invoice endpoint allows arbitrary file reads

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is joined to the invoice directory without restricting the resulting path.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive a file outside the invoice directory. Other files readable by the service, including secrets, may also be exposed.
- **Fix:** Restrict invoice identifiers and enforce containment within the invoice directory, including protection against symbolic-link escapes. Add HTTP tests for a valid invoice, a missing invoice and traversal attempts.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer, test-engineer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset uses `page * pageSize` even though page numbers start at 1.
- **Why it fails / scenario:** With the default size, page 1 returns IDs 15–6 instead of 25–16; the newest ten orders cannot be requested.
- **Fix:** Calculate `(page - 1) * pageSize` and test exact IDs and totals across page boundaries.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversing orders breaks the oldest-order lookup

- **Location:** [src/orders.js](repo/src/orders.js:16)
- **Problem:** `listOrders()` now returns newest first, but `firstOrder()` still takes its first element.
- **Why it fails / scenario:** The lookup documented for the customer dashboard’s “customer since” value returns order 25 instead of the oldest order, 1.
- **Fix:** Update `firstOrder()` to select the oldest order and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Test the new order of `listOrders`

- **Location:** [test/orders.test.js](repo/test/orders.test.js:7)
- **Problem:** The test checks only the number of orders, so it does not cover the newly required descending order.
- **Why it fails / scenario:** Removing the reversal leaves the test passing while returning the oldest order first.
- **Fix:** Assert the order of the returned IDs, including the first and last.
- **Confidence:** high
- **Source:** test-engineer

#### R2 Remove debug output from pagination

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A debug log runs for every pagination request.
- **Why it fails / scenario:** Normal requests produce `DEBUG pageOrders` output in the service logs.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/server.js](repo/src/server.js:23) returns a generic error for failed invoice reads without exposing filesystem error details.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; Node reported one passing test file.
- Semgrep: failed to start because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- The code, security and test reviews ran in parallel; findings were checked by a separate verifier. No findings were refuted.
- The missing invoice endpoint tests were folded into C1’s fix.
- Optional/Nit findings dropped by the limits: none.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=2 uncertain=0