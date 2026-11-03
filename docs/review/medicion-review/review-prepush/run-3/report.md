## Summary and verdict

The branch adds order pagination and invoice downloads. It has three confirmed Critical defects: arbitrary file disclosure, incorrect page offsets, and a broken existing caller of `listOrders()`.

**Verdict:** BLOCK

## Critical

#### C1 Invoice download permits path traversal

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice path is built directly from a request parameter without restricting traversal.
- **Why it fails / scenario:** A request for `/invoices?file=../../package.json` returns a file outside the invoice directory. Other files readable by the service can also be exposed.
- **Fix:** Restrict names to allowed invoice basenames and ensure the resolved file remains inside the invoice directory, including when symlinks are present.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the 1-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` starts at index 10 and omits the ten newest orders; page 3 is empty despite there being 25 orders.
- **Fix:** Use `(page - 1) * pageSize` and test the exact IDs returned on the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Existing caller returns the newest order as the first order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former ordering of `listOrders()`.
- **Why it fails / scenario:** Reversing `listOrders()` causes `firstOrder()` to return order 25 instead of order 1.
- **Fix:** Update the caller to select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Pagination test does not verify page contents

- **Location:** [test/orders.test.js:14](repo/test/orders.test.js:14)
- **Problem:** The test accepts any array of at most ten items, including an empty or incorrectly offset page.
- **Why it fails / scenario:** The current off-by-one implementation passes the test.
- **Fix:** Assert exact order IDs and totals for the first page and a later page, and check the size limit.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Remove debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Every pagination request writes a debug message to standard output.
- **Why it fails / scenario:** Normal traffic generates unsolicited debug logs.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Invoice endpoint has no behavioral test

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new disk-reading endpoint has no test covering its response or path restrictions.
- **Why it fails / scenario:** A broken PDF response or path traversal can pass the current suite.
- **Fix:** Add endpoint tests for a valid invoice, a missing invoice, and traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new caching TODO has no tracking reference.
- **Why it fails / scenario:** The follow-up has no traceable context.
- **Fix:** Remove it or link it to a tracked task.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [test/orders.test.js:18](repo/test/orders.test.js:18) checks invalid, missing, and valid inputs to `parsePositiveInt`.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` starts the service and is not a verification command.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: skipped; the scan failed because the read-only environment has no writable temporary directory.
- Callers: two changed symbols checked, with three call sites outside the diff read; dynamic callers cannot be enumerated.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- No files were changed.

REVIEW_RESULT: BLOCK critical=3 required=3 uncertain=0