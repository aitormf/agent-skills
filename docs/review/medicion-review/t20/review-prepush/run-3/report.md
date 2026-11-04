## Summary and verdict

The change adds order pagination and invoice downloads, but four confirmed defects prevent it from fulfilling its intended behavior. The invoice endpoint exposes files outside its directory, and pagination skips the first page.

**Verdict:** BLOCK

## Critical

#### C1 Path traversal exposes files outside the invoices directory

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** An unvalidated request parameter is used to construct a disk path.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns the service’s `package.json`. Other files readable by the process can also be exposed.
- **Fix:** Restrict invoice names and ensure the resolved file stays within the invoice directory, including protection against symlinks.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the 1-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` skips the ten newest orders; `size=50` returns an empty page despite 25 existing orders.
- **Fix:** Use `(page - 1) * pageSize` and test the contents of the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 The oldest-order consumer returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still selects the first item after `listOrders()` changed to newest-first order.
- **Why it fails / scenario:** It returns order 25 instead of order 1, contrary to its documented purpose of supplying “customer since.”
- **Fix:** Select the oldest order explicitly and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 The supplied invoice is not a valid PDF

- **Location:** [data/invoices/2026-001.pdf:1](repo/data/invoices/2026-001.pdf:1)
- **Problem:** The file contains only a fake PDF header and text, without PDF objects or cross-reference structure.
- **Why it fails / scenario:** The endpoint returns these bytes as `application/pdf`, but a PDF reader cannot render the promised invoice.
- **Fix:** Supply a valid invoice PDF or provide a valid invoice source.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 The pagination test does not verify page contents

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The test checks only the array type, maximum length and total.
- **Why it fails / scenario:** An empty page or the wrong orders pass; the current off-by-one implementation passes.
- **Fix:** Assert exact ordered items and totals for first, later and out-of-range pages, including the maximum size.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 The invoice endpoint has no tests

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new disk-reading endpoint and its security boundary are untested.
- **Why it fails / scenario:** The suite passes even when requests escape the invoice directory or the endpoint fails to return an invoice.
- **Fix:** Test a valid invoice, a missing file and traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Debug output remains on every pagination request

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug `console.log` remains in the request path.
- **Why it fails / scenario:** Every pagination call emits `DEBUG pageOrders` and pagination details.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 Unticketed TODO

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The caching TODO has no associated ticket.
- **Why it fails / scenario:** The deferred work has no tracked context.
- **Fix:** Remove it or link it to a tracked issue.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50 before slicing.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` starts the service and is not a verification command.
- Run: `npm test` → passed; Node reported one test file and no failures.
- Semgrep: `python3 .agents/skills/review-context/scripts/semgrep_added.py main` → exit 2; Semgrep could not find a writable temporary directory. No Semgrep MCP tool was available.
- Callers: 2 changed symbols, 3 call sites outside the diff read; external HTTP clients could not be checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- No uncommitted changes were present.

REVIEW_RESULT: BLOCK critical=4 required=3 uncertain=0