<!-- review-kit:review-pr -->

## Summary and verdict

The branch adds order pagination and invoice downloads. It has three confirmed critical defects affecting file access, pagination, and an existing caller. Tier 2: the change touches the invoice and server paths; sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 2 · Optional 1 · Nits 0

## Critical

#### C1 Path traversal exposes readable files

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice path is constructed directly from a request parameter without restricting it to the invoice directory.
- **Why it fails / scenario:** An unauthenticated request to `/invoices?file=../../package.json` returns the application’s `package.json`. Further traversal can expose other files readable by the service.
- **Fix:** Restrict invoice identifiers and enforce containment after resolving symlinks. Add a test that rejects traversal.
- **Confidence:** high
- **Source:** security-auditor

#### C2 Pagination skips the first page

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats one-indexed page numbers as zero-indexed.
- **Why it fails / scenario:** Page 1 with size 10 returns IDs 15–6 instead of the newest IDs 25–16; page 3 is empty even though five orders remain.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact page contents and totals.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 The first-order caller now returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` still takes the first result from `listOrders()`, whose ordering was reversed.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, giving the customer-since dashboard the wrong order.
- **Fix:** Select the oldest order while preserving the new `listOrders()` ordering, and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug log remains in the request path.
- **Why it fails / scenario:** Every `/orders` request emits pagination diagnostics to standard output.
- **Fix:** Remove the debug log.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test invoice download and error handling

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** No test exercises the new invoice endpoint.
- **Why it fails / scenario:** The suite remains green if valid invoice downloads or missing-file responses break.
- **Fix:** Add endpoint tests for a valid invoice’s bytes and content type, and for a missing invoice. Add the traversal test described in C1.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

#### O1 Document the reason and verification

- **Location:** Branch commit description
- **Problem:** The commit describes the changes but does not explain their motivation or how they were verified.
- **Why it fails / scenario:** A reviewer cannot establish the intended reason or verification plan from the branch description.
- **Fix:** Add the motivation and verification results to the PR description.
- **Confidence:** high
- **Source:** pr-description
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50.
- [src/server.js:22](repo/src/server.js:22) returns a generic response when an invoice read fails.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: attempted but could not run because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- No change folder matched the branch or diff; task audit did not apply.
- Callers: two changed symbols checked; three call sites outside the diff read. External consumers were not available for inspection.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=2 uncertain=0