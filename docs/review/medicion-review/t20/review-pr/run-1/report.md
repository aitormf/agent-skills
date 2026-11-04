<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an exploitable file disclosure and two functional regressions. Tier 2: sensitive area; requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 1 · Optional 0 · Nits 0

## Critical

#### C1 Invoice downloads allow path traversal

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is joined to the invoice directory without restricting traversal.
- **Why it fails / scenario:** Any caller can request `/invoices?file=../../package.json` and receive that file. Additional `../` segments can expose other files readable by the service.
- **Fix:** Restrict invoice identifiers and enforce containment, including symlink handling. Add HTTP tests for a valid invoice, a missing invoice and traversal attempts.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer, test-engineer

#### C2 The first page skips the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** The default `/orders` request returns IDs 15–6 instead of 25–16; page 3 is empty although five orders remain.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test exact contents and totals across pages.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Reversing `listOrders` breaks the oldest-order caller

- **Location:** [src/orders.js:16](repo/src/orders.js:16)
- **Problem:** The changed ordering alters the result of the existing `firstOrder()` caller.
- **Why it fails / scenario:** `firstOrder()` supplies the oldest order for the customer-since dashboard; it now returns ID 25 instead of ID 1.
- **Fix:** Update the caller to select the oldest order and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove debug output from each orders request

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** A debug `console.log` remains in the request path.
- **Why it fails / scenario:** Every `/orders` request emits a `DEBUG pageOrders` record during normal operation.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps page size at the stated maximum of 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed, one test file reported.
- Semgrep: failed because the read-only environment has no usable temporary directory; no Semgrep MCP tool was available.
- Task audit: not applicable; the branch has no matching change folder.
- Independent verification confirmed all four findings. The missing pagination and invoice tests are included in the corresponding fixes.
- Findings refuted: 0. Optional/Nit findings dropped by limits: 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=1 uncertain=0