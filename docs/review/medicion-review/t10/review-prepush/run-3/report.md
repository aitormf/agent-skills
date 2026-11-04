## Summary and verdict

The change adds order pagination and invoice downloads, but pagination skips the first page, invoice requests can read files outside the invoice directory, and the changed order sequence breaks an existing caller.

**Verdict:** BLOCK

## Critical

#### C1 Request can read files outside the invoices directory

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The filename supplied by the request is joined to the invoice directory without validation.
- **Why it fails / scenario:** A request to `/invoices?file=../../package.json` returns the repository’s package file. Other files readable by the server process are also exposed.
- **Fix:** Restrict filenames to permitted PDF basenames and enforce containment within the invoice directory, including symlink handling.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns orders 15 through 6 instead of the newest ten. With `size=50`, the first page is empty.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact page contents.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Changing the order breaks the oldest-order caller

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` assumes that `listOrders()` returns the oldest order first.
- **Why it fails / scenario:** After the reversal, `firstOrder()` returns order 25 instead of order 1. The code documents this value as the dashboard’s “customer since” order.
- **Fix:** Update `firstOrder()` to select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A debug log runs on every pagination request.
- **Why it fails / scenario:** Normal `/orders` traffic produces unsolicited debug output.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Pagination test does not check the returned orders

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The test accepts any array of at most ten items, including an empty or incorrect page.
- **Why it fails / scenario:** The off-by-one implementation passes the test.
- **Fix:** Assert exact IDs and totals for first and subsequent pages, the size cap, and a page beyond the end.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Invoice endpoint has no tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new file-reading endpoint and its error and security branches have no tests.
- **Why it fails / scenario:** The suite passes even though a request can read files outside the invoice directory.
- **Fix:** Test a valid PDF, a missing file, an invalid filename, and traversal attempts through the handler.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Newest-first ordering has no effective test

- **Location:** [test/orders.test.js](repo/test/orders.test.js:7)
- **Problem:** The existing test checks only the number of orders.
- **Why it fails / scenario:** Reverting `listOrders()` to oldest-first would leave the suite green.
- **Fix:** Assert the expected sequence of order IDs.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

#### O1 Remove the unused ordering helper

- **Location:** [src/orders.js](repo/src/orders.js:44)
- **Problem:** `latestFirst` has no remaining in-repository callers.
- **Why it fails / scenario:** Its only known caller was removed, leaving an unused exported helper.
- **Fix:** Remove the helper and export if they are not a supported external API.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [test/orders.test.js](repo/test/orders.test.js:18) checks valid and invalid inputs to the positive-integer parser.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` is a server startup command.
- Run: `npm test` → passed, one test file.
- Semgrep: failed because no usable temporary directory was available; no Semgrep MCP tool was available.
- Diff size: 119 lines; one independent reviewer.
- Callers: three call sites outside the diff inspected; external HTTP clients were unavailable.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- No files were changed.

REVIEW_RESULT: BLOCK critical=3 required=4 uncertain=0