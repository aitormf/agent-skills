## Summary and verdict

The change adds order pagination, newest-first ordering and invoice downloads, but all three introduce confirmed defects. The invoice endpoint allows callers to read files outside the invoice directory.

**Verdict:** BLOCK

## Critical

#### C1 Path traversal exposes server files

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is used to construct a disk read without restricting it to the invoice directory.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns a file outside that directory. A caller can traverse further to read other files accessible to the process.
- **Fix:** Allowlist invoice filenames and enforce containment within the invoice directory, including after symlink resolution.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** The default request skips the newest 10 orders; page 1 with `size=50` is empty.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Oldest-order caller returns the newest order

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still selects index zero after `listOrders()` changed to newest-first ordering.
- **Why it fails / scenario:** The customer-since value uses order 25 instead of the oldest order, order 1.
- **Fix:** Update `firstOrder()` to select the oldest order under the new contract.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debug output

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** Pagination emits a debug log during normal requests.
- **Why it fails / scenario:** Service traffic produces unintended debug output.
- **Fix:** Remove the `console.log`.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Pagination test does not verify the selected page

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The test checks only the result’s type, maximum length and total.
- **Why it fails / scenario:** Page 1 returns the second group of orders while the test passes.
- **Fix:** Assert the exact items on the first and subsequent pages, including the maximum-size boundary.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Ordering and invoice behavior lack effective tests

- **Location:** [test/orders.test.js](repo/test/orders.test.js:7)
- **Problem:** The order test checks only the count, and there are no invoice tests.
- **Why it fails / scenario:** Incorrect ordering and invoice path traversal both leave the suite green.
- **Fix:** Assert newest-first ordering and add invoice success, missing-file and traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

#### O1 Remove the unused ordering helper

- **Location:** [src/orders.js](repo/src/orders.js:44)
- **Problem:** `latestFirst` has no remaining repository callers.
- **Why it fails / scenario:** The exported helper remains alongside the new ordering contract without an in-repository use.
- **Fix:** Remove it if there are no supported external consumers.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## Nits

#### N1 Resolve or ticket the TODO

- **Location:** [src/invoices.js](repo/src/invoices.js:8)
- **Problem:** The new caching TODO has no tracking reference.
- **Why it fails / scenario:** The deferred work has no tracked follow-up.
- **Fix:** Remove it or link it to a ticket.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [The positive-integer parser tests](repo/test/orders.test.js:18) cover invalid, missing and valid inputs.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` is a server startup command, not a verification command.
- Run: `npm test` → passed, 1 test file, 0 failures.
- Semgrep: skipped; the scan failed because no usable temporary directory was available, and no Semgrep MCP tool was available.
- Callers: two changed symbols examined; three call sites outside the diff read.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Working tree was clean. No files were modified.

REVIEW_RESULT: BLOCK critical=3 required=3 uncertain=0