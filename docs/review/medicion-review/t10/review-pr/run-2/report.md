<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. It is **tier 2** because it changes the high-risk invoice and server paths. The diff is **119 lines, small**. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 2 · Optional 0 · Nits 0

## Critical

#### C1 Invoice requests can read files outside the invoice directory

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The file path is built directly from the request parameter without restricting its destination.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive a file readable by the service process.
- **Fix:** Accept only valid invoice identifiers, confine the resolved file to the invoice directory including through symbolic links, and add traversal regression tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 The first page omits the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats pages as zero-indexed although the API uses one-indexed pages.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns IDs 15–6 instead of 25–16; the newest ten orders do not appear on any valid page.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test the exact contents of the first, subsequent and final pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 `firstOrder()` returns the newest order

- **Location:** [src/orders.js:15](repo/src/orders.js:15)
- **Problem:** Reversing `listOrders()` changes the order expected by its existing `firstOrder()` caller.
- **Why it fails / scenario:** `firstOrder()` now returns order 25 instead of the oldest order, 1.
- **Fix:** Preserve the original `listOrders()` ordering and reverse it for the endpoint, or update the caller explicitly; test the oldest-order contract.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Invoice endpoint branches have no tests

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice route has no tests for successful and unsuccessful reads.
- **Why it fails / scenario:** The suite passes without checking that an existing invoice is returned or that a missing one produces 404.
- **Fix:** Add endpoint tests for a valid invoice and a missing invoice.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Debug output runs on every order request

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug `console.log` remains in the request path.
- **Why it fails / scenario:** Every `/orders` request writes a debug line, producing log noise proportional to traffic.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the page size at 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, no failures.
- Semgrep: could not run because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=2 uncertain=0