## Summary and verdict

The branch adds order pagination and invoice downloads, but the invoice endpoint exposes files outside the invoice directory. Pagination also skips the first page, and the changed ordering breaks an existing caller.

**Verdict:** BLOCK

## Critical

#### C1 Invoice endpoint permits path traversal

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice path incorporates an unchecked request parameter.
- **Why it fails / scenario:** A request for `/invoices?file=../../package.json` returns a readable file outside the invoice directory.
- **Fix:** Restrict permitted invoice filenames and ensure the resolved target stays inside the invoice directory, including through symlinks.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` starts at index 10 and omits the ten newest orders.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 The oldest-order caller now returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder` relies on the former ordering of `listOrders`.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, despite being intended to return the oldest order.
- **Fix:** Select the oldest order under the new ordering and test that behavior.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debugging output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Every pagination request writes a debug message to standard output.
- **Why it fails / scenario:** Normal `/orders` traffic produces debug logs for every request.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test the actual pagination results

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The pagination test checks only the result type and upper bound.
- **Why it fails / scenario:** It passes with the current incorrect offset, or even with an empty page.
- **Fix:** Assert exact order IDs for the first and subsequent pages, including the size limit and last page.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Cover invoice retrieval and input validation

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new disk-reading endpoint has no tests.
- **Why it fails / scenario:** Neither successful retrieval nor rejection of traversal inputs is checked.
- **Fix:** Add endpoint tests for a valid invoice, a missing invoice, and traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Cover the changed ordering

- **Location:** [src/orders.js:15](repo/src/orders.js:15)
- **Problem:** The existing test checks only the number of orders.
- **Why it fails / scenario:** `listOrders` could return oldest first and the test would still pass.
- **Fix:** Assert the returned ID order, including the newest and oldest entries.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new caching TODO has no tracking reference.
- **Why it fails / scenario:** The proposed follow-up has no traceable scope.
- **Fix:** Remove it or link it to a tracked task.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- The parser tests in [test/orders.test.js:18](repo/test/orders.test.js:18) cover valid input and several invalid or missing values.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` starts the service and is not a verification command.
- Run: `npm test` → passed, 1 test file, 0 failures.
- Semgrep: failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- Callers: 2 changed contracts, 3 call sites outside the diff read; external HTTP clients could not be inspected.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=4 uncertain=0