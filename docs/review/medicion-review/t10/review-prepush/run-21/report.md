## Summary and verdict

The branch adds order pagination and invoice downloads, but the pagination skips the newest orders, an existing caller returns the wrong first order, and the invoice endpoint permits arbitrary file disclosure. These defects block the push.

**Verdict:** BLOCK

## Critical

#### C1 Arbitrary file disclosure through invoice path

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The request-supplied filename is joined to the invoice directory without restricting traversal.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and read files accessible to the server process.
- **Fix:** Allow only valid invoice filenames, enforce containment within the invoice directory, including symlinks, and add traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The slice offset treats a one-indexed page as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns orders 15 through 6 instead of 25 through 16; the ten newest orders are unreachable.
- **Fix:** Calculate `(page - 1) * pageSize` and test the exact items on the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 First-order caller now returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former oldest-first ordering of `listOrders()`.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, although its documented purpose is to return the oldest order for “customer since.”
- **Fix:** Select the oldest order under the new ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Debug output on every orders request

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug `console.log` remains in the request path.
- **Why it fails / scenario:** Each call to `pageOrders` writes a DEBUG line with pagination parameters.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Invoice endpoint has no tests

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new file-reading endpoint and its error handling are untested.
- **Why it fails / scenario:** The suite can pass when invoice downloads fail or traversal is accepted.
- **Fix:** Test a successful response, missing files and attempts to escape the invoice directory.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed invoice caching TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new TODO has no tracking reference.
- **Why it fails / scenario:** The follow-up has no issue to track it.
- **Fix:** Remove it or reference a tracking issue.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` is a startup command, not a verification command.
- Run: `npm test` → passed, 1 test file, 0 failures.
- Diff: 119 lines; reviewed by one reviewer and an independent finding verifier.
- Semgrep: skipped after the scan failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- Callers: three call sites outside the diff inspected; external HTTP clients cannot be enumerated from this repository.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=2 uncertain=0