<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an arbitrary file-read vulnerability, an incorrect pagination offset, and a regression in the oldest-order calculation.

Tier 2: sensitive paths `src/invoices.js` and `src/server.js` are changed. Diff size: **119 lines, small**. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 1 · Optional 0 · Nits 0

## Critical

#### C1 Invoice download permits reading files outside the invoice directory

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is joined to the invoice directory and read without checking where it resolves.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive a file outside `data/invoices`. Other files readable by the service process can also be exposed.
- **Fix:** Restrict accepted invoice names and ensure the resolved file remains inside the authorized directory, including when symbolic links are present. Add traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page of orders

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset uses `page * pageSize`, although page numbers start at 1.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns IDs 15 through 6 instead of 25 through 16. With `size=50`, the first page is empty despite 25 existing orders.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact page contents and boundaries.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 The oldest-order calculation now returns the newest order

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still takes the first element after `listOrders()` was changed to return newest orders first.
- **Why it fails / scenario:** The documented “customer since” calculation receives order 25 instead of order 1.
- **Fix:** Update `firstOrder()` for the new ordering and add a regression test for the oldest order.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Debug output is emitted for every pagination request

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A `DEBUG` log remains in `pageOrders`.
- **Why it fails / scenario:** Every request to `/orders` emits debugging output into the service logs.
- **Fix:** Remove the debug log.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js](repo/src/orders.js:31) caps page size at 50, limiting the number of items returned per page.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, 1 test file.
- Semgrep: skipped; it could not start because no writable temporary directory was available. No Semgrep MCP tool was available.
- The separate missing-test finding was folded into the fixes for C1–C3.
- Findings refuted by the verifier: 1 — the separate test-coverage finding duplicated C1–C3.
- Optional/Nit findings dropped by the limit: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=1 uncertain=0