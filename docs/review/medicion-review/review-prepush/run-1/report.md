## Summary and verdict

The branch adds order pagination and an invoice download endpoint, but four confirmed defects prevent it from fulfilling the intended behavior safely. The invoice endpoint exposes files outside its directory, and the pagination skips the first page.

**Verdict:** BLOCK

## Critical

#### C1 Invoice path traversal exposes readable files

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The request-controlled filename is joined to the invoice directory without confinement.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns the package file; additional `..` segments can expose other files readable by the service.
- **Fix:** Restrict invoice names and enforce confinement to the invoice directory, including symlink handling. Add traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 First page skips the newest orders

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats the page number as zero-indexed despite the one-indexed contract.
- **Why it fails / scenario:** `/orders?page=1&size=10` omits the ten newest orders; size 50 returns an empty first page.
- **Fix:** Use `(page - 1) * pageSize` and test exact IDs and page boundaries.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Changed ordering breaks the oldest-order caller

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` selects index zero after `listOrders()` changed to newest-first.
- **Why it fails / scenario:** The documented customer-since caller receives order 25 instead of the oldest order, 1.
- **Fix:** Select the oldest order and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 Supplied invoice is not a valid PDF

- **Location:** [data/invoices/2026-001.pdf](repo/data/invoices/2026-001.pdf:1)
- **Problem:** The supplied invoice contains only a PDF header and placeholder text, without a valid document structure.
- **Why it fails / scenario:** Downloading `2026-001.pdf` returns bytes that cannot be opened as a PDF invoice.
- **Fix:** Supply a valid PDF fixture or invoice and verify the returned document.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debug output from pagination

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** Every pagination call emits a debug log.
- **Why it fails / scenario:** Every `/orders` request produces `DEBUG pageOrders` output.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test actual pagination results

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The pagination test does not check page contents or the calculated page total.
- **Why it fails / scenario:** The existing off-by-one implementation passes, as would an empty result with an incorrect page total.
- **Fix:** Assert exact IDs and totals for first, subsequent and boundary pages, including the maximum size.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Test invoice endpoint behavior and security

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new disk-reading endpoint has no tests.
- **Why it fails / scenario:** Valid, missing and traversal requests are untested; the current traversal vulnerability passes the suite.
- **Fix:** Add endpoint tests for valid and missing files and traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed invoice caching TODO

- **Location:** [src/invoices.js](repo/src/invoices.js:8)
- **Problem:** The new TODO does not identify a tracked issue.
- **Why it fails / scenario:** The caching work has no tracking context.
- **Fix:** Remove it or link a ticket.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js](repo/src/orders.js:16) copies the order array before reversing it, avoiding mutation of the shared data.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, one test file, zero failures.
- Semgrep: skipped; the local script exited 2 because no writable temporary directory was available, and no Semgrep MCP tool was available.
- Callers: two changed symbols checked; three `listOrders` call sites outside the diff read. No repository callers of `/orders` found.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Working tree was clean; no files were changed.

REVIEW_RESULT: BLOCK critical=4 required=3 uncertain=0