<!-- review-kit:review-pr -->
## Summary and verdict

The change adds order pagination and invoice downloads. This is **tier 2** because it changes the request-facing server and filesystem access. The review found an exploitable file-read vulnerability and two correctness regressions.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 2 · Optional 0 · Nits 0

Sensitive area: requires human review by an owner.

## Critical

#### C1 Request-controlled path exposes files

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The invoice filename comes directly from the request and is read without restricting the resulting path.
- **Why it fails / scenario:** Any client can request `/invoices?file=../../package.json` and receive that file. Further traversal can expose other files readable by the service, including secrets.
- **Fix:** Accept approved invoice names or IDs, enforce containment after resolving paths including symlinks, and test traversal rejection.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 Pagination skips the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the one-indexed page number as zero-indexed.
- **Why it fails / scenario:** `/orders?page=1&size=10` returns IDs 15–6 instead of 25–16; the newest ten orders are inaccessible through pagination.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and assert page contents and totals in tests.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 First-order statistic now returns the newest order

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former ordering of `listOrders()`.
- **Why it fails / scenario:** After the reversal, it returns order 25 instead of order 1, making the dashboard’s “customer since” statistic wrong.
- **Fix:** Select the oldest order explicitly and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Remove pagination debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Pagination prints a debug message on every call.
- **Why it fails / scenario:** Every `/orders` request adds diagnostic output to production logs.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Test the invoice endpoint

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new invoice route has no tests.
- **Why it fails / scenario:** Regressions in successful PDF delivery or missing-file handling pass the current suite.
- **Fix:** Add endpoint tests for an existing invoice and missing filename or file. Cover traversal rejection as part of C1.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:16](repo/src/orders.js:16) copies the shared order array before reversing it, avoiding mutation of the original data.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; 1 test file, no failures.
- Semgrep: skipped after the scan failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- No change folder matched this branch, so no task audit was applicable.
- Callers: the changed `listOrders` contract and its three call sites outside the diff were reviewed.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limits (Max Optional=3, Max Nits=3): 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=2 uncertain=0