## Summary and verdict

The change adds order pagination and invoice downloads, but pagination skips the first page, invoice paths allow directory traversal, and the new ordering breaks an existing caller. The branch is not ready to push.

**Verdict:** BLOCK

## Critical

#### C1 Invoice endpoint permits path traversal

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The disk path is constructed directly from the request’s `file` parameter.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns a readable file outside the invoice directory. The verifier reproduced the disclosure.
- **Fix:** Restrict invoice filenames and ensure the resolved path remains inside the invoice directory, including protection against symlink escapes. Add traversal tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` omits the ten newest orders; `size=50` returns no orders although 25 exist.
- **Fix:** Calculate `(page - 1) * pageSize` and test exact IDs on the first and subsequent pages, including the size cap.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Changed ordering breaks the first-order caller

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` selects the first result even though `listOrders()` now returns newest first.
- **Why it fails / scenario:** It returns order 25 instead of the oldest order, order 1, contrary to its documented “customer since” use.
- **Fix:** Select the oldest order under the new contract and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug log runs on every pagination request.
- **Why it fails / scenario:** Every `/orders` request writes pagination details to standard output and adds log volume.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Invoice route has no behavioral tests

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice route has no tests for its success or error paths.
- **Why it fails / scenario:** The suite would still pass if valid downloads stopped working or missing files stopped returning 404.
- **Fix:** Test a valid invoice, missing or absent filenames, and rejected traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed cache TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new TODO has no tracking reference.
- **Why it fails / scenario:** The proposed caching work has no associated context or owner.
- **Fix:** Remove it or link it to a tracked issue.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:20](repo/src/orders.js:20) validates positive integer pagination inputs and falls back for invalid values.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, zero failures.
- Semgrep: failed because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- Callers: 2 changed symbols, 3 call sites outside the diff read; external HTTP consumers could not be checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=2 uncertain=0