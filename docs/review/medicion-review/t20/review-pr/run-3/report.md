<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an arbitrary file disclosure, an incorrect page offset, and a broken caller of `listOrders`.

**Tier:** 2 — sensitive paths `src/invoices.js` and `src/server.js`. Sensitive area: requires human review by an owner.  
**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 1 · Nits 0

## Critical

#### C1 Invoice filenames allow arbitrary file disclosure

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** The invoice path is built from an unchecked request parameter.
- **Why it fails / scenario:** `GET /invoices?file=../../package.json` reads a file outside the invoice directory. A caller can similarly retrieve other files readable by the service.
- **Fix:** Accept an allowlisted invoice identifier and enforce containment within the invoice directory, including symlink handling. Add a traversal rejection test.
- **Confidence:** high
- **Source:** security-auditor

#### C2 Pagination skips the first page

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats one-indexed pages as zero-indexed.
- **Why it fails / scenario:** The default request skips the ten newest orders; `page=1&size=50` returns an empty page.
- **Fix:** Use `(page - 1) * pageSize` and test the exact order IDs and totals for the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversing orders breaks the oldest-order caller

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder()` selects the first result, but `listOrders()` now returns newest first.
- **Why it fails / scenario:** The customer-since calculation returns order 25 instead of the oldest order, order 1.
- **Fix:** Update the caller to select the oldest order while preserving the new `listOrders()` contract.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Total calculation duplicates an existing helper

- **Location:** [src/orders.js](repo/src/orders.js:25)
- **Problem:** `pageTotal()` duplicates `sumTotals()` in `src/stats.js`.
- **Why it fails / scenario:** Changes to total calculation would need to be kept consistent in both places.
- **Fix:** Extract a shared helper without introducing a dependency cycle.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Debug output remains on every orders request

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** A debug `console.log` remains in the request path.
- **Why it fails / scenario:** Every pagination request writes debug output to the service logs.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Invoice endpoint has no functional tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new invoice route is untested.
- **Why it fails / scenario:** An endpoint that always returns 404 or returns incorrect invoice content would still pass the suite.
- **Fix:** Test a valid invoice and a missing invoice, asserting status, content type and response bytes.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

#### O1 Document the reason and verification

- **Location:** Branch commit description
- **Problem:** The commit description lists the behavior changes but does not explain their motivation or how they were verified.
- **Why it fails / scenario:** A reviewer cannot assess the intended purpose or the author's verification from the description.
- **Fix:** Add the motivation and verification performed to the eventual PR description.
- **Confidence:** high
- **Source:** pr-description
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [src/orders.js](repo/src/orders.js:31) caps the page size at 50.
- [src/server.js](repo/src/server.js:22) returns a generic response for invoice read errors.

## Verification

- Command found in `AGENTS.md`: `npm test`.
- Run: `npm test` → passed; Node reported one test file, with no failures.
- Semgrep: attempted, but could not start because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- Callers: reviewed two changed contracts and three `listOrders` calls outside the diff; external API callers could not be checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0