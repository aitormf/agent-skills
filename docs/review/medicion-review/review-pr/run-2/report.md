<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an arbitrary file-read vulnerability, an incorrect page offset, and a regression in an existing order consumer. **Tier 2:** the change touches invoice access and the HTTP server. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 0 · Nits 1

## Critical

#### C1 Request-controlled invoice path exposes files

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice filename comes directly from the request and is joined to the invoice directory without validation.
- **Why it fails / scenario:** `/invoices?file=..%2F..%2Fpackage.json` returns the repository’s `package.json`. Further traversal can expose other files readable by the service.
- **Fix:** Accept only permitted invoice identifiers, enforce containment within the invoice directory, prevent symlink escapes, and add traversal tests.
- **Confidence:** high
- **Source:** code-reviewer, security-auditor

#### C2 The first page skips the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a 1-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns IDs 15–6 instead of 25–16. With `size=50`, the first page is empty despite 25 orders existing.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact page boundaries.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 The oldest-order consumer now returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on `listOrders()` returning the oldest order first; the change reverses that order.
- **Why it fails / scenario:** `firstOrder()` now returns order 25 instead of order 1, contrary to its documented contract.
- **Fix:** Update the consumer to select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove request-time debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Pagination writes a debug message for every request.
- **Why it fails / scenario:** Normal `/orders` traffic produces unnecessary debug log output.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Verify pagination results in tests

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The pagination test checks the result type, maximum length and total count, but not the selected orders or page total.
- **Why it fails / scenario:** The test passes for the incorrect offset in C2 and would also accept an empty page.
- **Fix:** Assert exact IDs and `pageTotal` for the first and subsequent pages, as well as the size cap and newest-first endpoint behavior.
- **Confidence:** high
- **Source:** test-engineer

#### R3 Test the invoice endpoint and its security boundary

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** No test exercises the new invoice route or request-controlled filenames.
- **Why it fails / scenario:** The suite remains green if a valid invoice cannot be downloaded or a traversal request reads a file outside the invoice directory.
- **Fix:** Add handler tests for a valid invoice, a missing invoice and traversal attempts, checking status, content type and response body.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

#### N1 Track or remove the cache TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new cache TODO has no associated ticket.
- **Why it fails / scenario:** The proposed work has no tracked owner or acceptance criteria.
- **Fix:** Remove the TODO or link it to a tracked task.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:16](repo/src/orders.js:16) reverses a copy, preserving the shared `ORDERS` array.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: skipped; the scan failed because the read-only environment has no usable writable temporary directory. No Semgrep MCP tool was available.
- No matching change folder or task audit.
- Callers: two changed contracts and three call sites outside the diff reviewed; external HTTP consumers were unavailable.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0