<!-- review-kit:review-pr -->

## Summary and verdict

The branch adds order pagination and invoice downloads. The review found an exploitable file-read vulnerability, an incorrect pagination offset, and a regression in the first-order statistic. Tier 2: the change touches billing and the repository’s designated high-risk paths.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 3 · Optional 0 · Nits 0

Sensitive area: requires human review by an owner.

## Critical

#### C1 Request-controlled path exposes files

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice filename is joined to the invoice directory without restricting traversal.
- **Why it fails / scenario:** A caller can request `/invoices?file=../../package.json` and receive a file outside the invoice directory. Other files readable by the service can also be exposed.
- **Fix:** Restrict accepted invoice names and enforce containment, including protection against symlinks. Add traversal regression tests.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 First page skips the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` starts at index 10 and omits the ten newest orders.
- **Fix:** Use `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Reversed ordering breaks the first-order statistic

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` selects the first result while `listOrders()` now returns newest first.
- **Why it fails / scenario:** The exported statistic returns order 25 instead of order 1 for its documented “customer since” use.
- **Fix:** Select the oldest order under the new contract and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Pagination writes debug output for every call.
- **Why it fails / scenario:** Ordinary `/orders` traffic continuously generates debug messages.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Assert pagination and ordering results

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** The pagination test does not assert returned items or their order; the ordering test asserts only the count.
- **Why it fails / scenario:** The current incorrect first page passes all assertions.
- **Fix:** Assert exact IDs and totals for the first and later pages, including the last partial page and size cap.
- **Confidence:** high
- **Source:** test-engineer

#### R3 Test invoice route behavior

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice route has no tests.
- **Why it fails / scenario:** Incorrect invoice bytes or missing-file handling can regress without a test failing.
- **Fix:** Test an existing invoice, a missing invoice and rejected traversal.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:16](repo/src/orders.js:16) copies the shared order array before reversing it.
- [src/server.js:22](repo/src/server.js:22) returns a generic invoice error without exposing filesystem error details.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` starts the service and is not a verification command.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- Callers: two changed contracts reviewed; three call sites outside the diff read. External consumers could not be checked.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=3 uncertain=0