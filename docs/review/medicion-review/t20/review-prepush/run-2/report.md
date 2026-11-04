## Summary and verdict

The branch adds order pagination and invoice downloads, but the invoice endpoint permits reading files outside the invoice directory. Pagination skips the first page, and the changed order breaks an existing statistics caller.

**Verdict:** BLOCK

## Critical

#### C1 Invoice endpoint permits path traversal
- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The file path incorporates an unvalidated request parameter.
- **Why it fails / scenario:** `GET /invoices?file=../../package.json` returns a file outside `data/invoices`. Other files readable by the process can also be exposed.
- **Fix:** Validate the filename and ensure the resolved real path, including symlinks, remains inside the invoice directory.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 Pagination skips the first page
- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page as zero-indexed.
- **Why it fails / scenario:** `GET /orders?page=1&size=10` returns IDs 15–6 instead of 25–16.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Statistics now report the newest order as the first historical order
- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the previous ordering of `listOrders()`.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, producing an incorrect “customer since” value for the dashboard.
- **Fix:** Adapt `firstOrder()` to the new ordering.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debug output
- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Every pagination request writes a debug message.
- **Why it fails / scenario:** Normal requests produce `DEBUG pageOrders` output.
- **Fix:** Remove the `console.log`.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Add effective tests for the new behavior
- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The pagination test accepts an empty page, and the new order and invoice route have no tests.
- **Why it fails / scenario:** The current assertions pass despite C2; regressions in invoice access and confinement also go undetected.
- **Fix:** Assert page contents and boundaries, order behavior, and invoice HTTP responses, including traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO has no tracking reference
- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** The new caching TODO has no ticket reference.
- **Why it fails / scenario:** There is no identifiable follow-up for the proposed work.
- **Fix:** Remove it or link it to a ticket.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [test/orders.test.js:18](repo/test/orders.test.js:18) checks invalid inputs and fallback values for `parsePositiveInt`.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` is a server start command, not a verification command.
- Run: `npm test` → passed; one test file, zero failures.
- Semgrep: skipped; its script failed because no writable temporary directory was available, and no Semgrep MCP tool was available.
- Callers: two changed contracts and three call sites outside the diff reviewed; none omitted.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=2 uncertain=0