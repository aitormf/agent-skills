## Summary and verdict

The change adds order pagination and invoice downloads, but the invoice endpoint permits access to files outside the invoice directory. Pagination also skips the newest orders, and the changed ordering breaks an existing caller.

**Verdict:** BLOCK

## Critical

#### C1 Invoice path traversal exposes server files

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The disk path is built directly from the request’s `file` parameter without restricting it to the invoice directory.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns `package.json`. A caller can similarly read other files accessible to the process.
- **Fix:** Validate invoice names and ensure the resolved path remains within the authorized directory, including when symbolic links are present. Add valid-download and traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 The first page skips the newest orders

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset uses `page * pageSize` even though pages are one-indexed.
- **Why it fails / scenario:** Page 1 with size 10 returns orders 15 through 6 instead of 25 through 16; the newest ten orders do not appear on any valid page.
- **Fix:** Use `(page - 1) * pageSize` and test exact page contents and boundaries.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 The ordering change breaks the oldest-order caller

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still takes the first element of `listOrders()`, which now returns newest orders first.
- **Why it fails / scenario:** The caller receives order 25 instead of the oldest order, 1.
- **Fix:** Adapt `firstOrder()` to the new ordering and test that it returns the oldest order.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 The pagination test accepts the wrong page

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The test checks only the maximum number of results, not their identities.
- **Why it fails / scenario:** The incorrect offset described in C2 passes the test, as would an empty page.
- **Fix:** Assert exact order IDs and totals for successive pages and the size limit.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 The invoice endpoint has no tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new disk-reading endpoint and its invalid inputs are untested.
- **Why it fails / scenario:** The suite passes while the traversal described in C1 remains possible.
- **Fix:** Test a valid download, a missing file, and rejection of paths outside the invoice directory.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Debug output remains in the order path

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** `pageOrders` prints a `DEBUG` message on every invocation.
- **Why it fails / scenario:** Every request to `/orders` produces debug output in the server process.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 The total calculation duplicates an existing helper

- **Location:** [src/orders.js](repo/src/orders.js:25)
- **Problem:** `pageTotal` duplicates the existing `sumTotals` implementation.
- **Why it fails / scenario:** Changes to the total calculation can leave the two implementations with different results.
- **Fix:** Share one total calculation without introducing a circular dependency.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO has no tracking reference

- **Location:** [src/invoices.js](repo/src/invoices.js:8)
- **Problem:** The new TODO has no tracking reference.
- **Why it fails / scenario:** The proposed change has no associated follow-up.
- **Fix:** Remove it or link it to a tracked task.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js](repo/src/orders.js:16) reverses a copy of the orders array, leaving the shared array unchanged.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, 1 test and 0 failures.
- Semgrep: skipped; the script exited 2 because the read-only environment had no usable temporary directory. No Semgrep MCP tool was available.
- Callers: 1 changed symbol, 3 call sites outside the diff read; external consumers could not be inspected.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=4 uncertain=0