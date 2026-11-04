## Summary and verdict

The branch adds order pagination and invoice downloads, but neither feature is ready to push: invoice paths allow arbitrary file disclosure, pagination skips the first page, and the supplied invoice is not a valid PDF. Reversing order results also breaks an existing caller.

**Verdict:** BLOCK

## Critical

#### C1 Invoice download permits path traversal

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is joined directly to the invoice directory and read from disk.
- **Why it fails / scenario:** An unauthenticated request to `/invoices?file=../../package.json` returns the server’s `package.json`; deeper traversal can expose other readable files.
- **Fix:** Restrict invoice names and enforce containment within the invoice directory, including symlink handling. Add traversal regression tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The starting offset uses `page * pageSize` even though pages are one-indexed.
- **Why it fails / scenario:** The default request returns IDs 15–6 instead of 25–16; page 3 is empty.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact consecutive pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Reversed ordering breaks the oldest-order caller

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still takes the first element after `listOrders()` changed to newest-first.
- **Why it fails / scenario:** It now returns order 25 instead of the oldest order, 1.
- **Fix:** Select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 Supplied invoice is not a valid PDF

- **Location:** [data/invoices/2026-001.pdf](repo/data/invoices/2026-001.pdf:1)
- **Problem:** The supplied file contains only a PDF header and placeholder text, with no PDF objects or trailer.
- **Why it fails / scenario:** Downloading the provided invoice returns bytes that a PDF reader cannot render as an invoice.
- **Fix:** Supply a valid PDF and verify the downloaded file can be parsed.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Pagination and ordering tests do not verify results

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The pagination test checks only the array type, maximum length and total count; the ordering test checks only the number of orders.
- **Why it fails / scenario:** An empty or incorrectly ordered page passes the assertions, as does the current offset error.
- **Fix:** Assert exact page contents and ordering, the size cap and page totals.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Invoice route has no tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new file-reading endpoint and its error branches have no tests.
- **Why it fails / scenario:** Regressions in valid downloads, missing files or malicious paths can pass the suite.
- **Fix:** Add HTTP tests for successful downloads, missing input and files, and traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Debug output runs on every order request

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A `DEBUG` console statement remains in `pageOrders`.
- **Why it fails / scenario:** Every order request writes debugging data to the process output.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

#### O1 Remove the unused ordering helper

- **Location:** [src/orders.js](repo/src/orders.js:43)
- **Problem:** `latestFirst` has no remaining callers in the repository.
- **Why it fails / scenario:** The unused helper and export remain to be maintained; external consumers, if any, are unknown.
- **Fix:** Remove it if the exported API has no external consumers.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [test/orders.test.js](repo/test/orders.test.js:18) covers invalid, absent and valid inputs to the positive-integer parser.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; 1 test file, 0 failures.
- Semgrep: skipped; the scan failed because no usable temporary directory was available, and no Semgrep MCP tool was available.
- Diff size: 119 lines; reviewed by one independent reviewer.
- Callers: the reviewer checked the three `listOrders` call sites outside the diff.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=4 required=3 uncertain=0