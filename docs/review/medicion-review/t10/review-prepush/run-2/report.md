## Summary and verdict

The change adds order pagination and invoice downloads, but the invoice endpoint permits arbitrary file reads, pagination skips the first page, and the changed ordering breaks `firstOrder()`.

**Verdict:** BLOCK

## Critical

#### C1 Request-controlled path permits arbitrary file reads

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The requested filename is joined directly to the invoice directory.
- **Why it fails / scenario:** A request with `file=../../package.json` returns a file outside that directory. Other files readable by the service can also be exposed.
- **Fix:** Accept only valid invoice basenames and enforce containment in the invoice directory, including symlink handling.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats the one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `page=1&size=10` starts at index 10, omitting the ten newest orders.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 `firstOrder()` now returns the newest order

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former ordering of `listOrders()`.
- **Why it fails / scenario:** With the current data it returns order 25 instead of order 1. Dashboard use is documented in a comment, but no dashboard caller was found.
- **Fix:** Update `firstOrder()` to select the oldest order while preserving the new `listOrders()` contract.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debugging output

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** Pagination emits a `DEBUG` log on each request.
- **Why it fails / scenario:** Normal requests produce leftover debugging output.
- **Fix:** Remove the `console.log`.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Pagination test does not verify page contents

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The test accepts an empty or incorrectly offset page.
- **Why it fails / scenario:** The current off-by-one implementation passes because the test checks only the array type, maximum length and total.
- **Fix:** Assert exact order IDs for the first and subsequent pages, including boundaries and the size cap.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Invoice endpoint has no behavioral tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new file-reading endpoint and its error path have no tests.
- **Why it fails / scenario:** A broken PDF response or the traversal in C1 passes the current suite.
- **Fix:** Test a successful PDF response, a missing invoice and rejection of traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Order reversal has no effective ordering test

- **Location:** [src/orders.js](repo/src/orders.js:15)
- **Problem:** The existing test checks only the order count.
- **Why it fails / scenario:** It passes for either ordering and does not catch the changed behavior of `firstOrder()`.
- **Fix:** Assert newest-first ordering and test that `firstOrder()` returns the oldest order.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js](repo/src/orders.js:31) caps the requested page size at 50 before slicing.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, zero failures.
- Semgrep: failed to start because no usable temporary directory was available; no Semgrep MCP tool was available.
- Callers: the reviewer inspected three `listOrders` call sites outside the diff; no outside route callers were found.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- The working tree remained unchanged.

REVIEW_RESULT: BLOCK critical=3 required=4 uncertain=0