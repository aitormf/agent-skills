## Summary and verdict

The branch adds order pagination and invoice downloads, but the invoice endpoint exposes files outside its intended directory. Pagination also skips the first page, an existing oldest-order helper returns the wrong order, and the supplied invoice is not a valid PDF.

**Verdict:** BLOCK

## Critical

#### C1 Path traversal exposes local files

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The invoice path is built directly from a request parameter without restricting it to the invoice directory.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns a file outside `data/invoices`. Other files readable by the service can also be exposed.
- **Fix:** Restrict accepted invoice names and enforce directory containment, including symlink handling. Add traversal regression tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 First page skips the newest orders

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset uses `page * pageSize` although pages are one-indexed.
- **Why it fails / scenario:** Page 1 with size 10 starts at index 10; page 1 with size 50 returns no orders.
- **Fix:** Use `(page - 1) * pageSize` and test exact page contents.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Oldest-order helper returns the newest order

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former ascending order of `listOrders()`.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, violating its documented oldest-order contract.
- **Fix:** Update the helper for the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 Supplied invoice is not a valid PDF

- **Location:** [data/invoices/2026-001.pdf](repo/data/invoices/2026-001.pdf:1)
- **Problem:** The file contains only a fake PDF header and text, without a PDF document structure.
- **Why it fails / scenario:** The endpoint returns the supplied invoice unchanged, but a PDF reader cannot open it.
- **Fix:** Supply a valid PDF fixture or invoice.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Pagination test cannot detect the wrong page

- **Location:** [test/orders.test.js](repo/test/orders.test.js:12)
- **Problem:** The test accepts any array of at most ten items.
- **Why it fails / scenario:** It passes with the current offset bug, and would also accept an empty page.
- **Fix:** Assert exact IDs, lengths, totals and boundaries for the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Invoice endpoint has no coverage

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new request parsing, disk access and error branches have no tests.
- **Why it fails / scenario:** A broken download or a traversal vulnerability can pass the existing suite.
- **Fix:** Add endpoint tests for a valid invoice, a missing invoice and malicious filenames.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Debug output remains in the request path

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A debug statement runs on every pagination request.
- **Why it fails / scenario:** Each `/orders` request writes internal pagination details to the process log.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js](repo/src/orders.js:31) caps the requested page size at 50 before slicing.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` is a server start command, not a verification command.
- Run: `npm test` → passed; one test file reported, zero failures.
- Semgrep: failed because no usable temporary directory was available; no Semgrep MCP tool was available.
- Callers: the reviewer checked three call sites outside the diff; dynamic external HTTP consumers could not be checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=4 required=3 uncertain=0