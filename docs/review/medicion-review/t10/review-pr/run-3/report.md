<!-- review-kit:review-pr -->
## Summary and verdict

The change adds order pagination and invoice downloads. The review found an arbitrary file read, an incorrect first page, and a regression in the existing oldest-order calculation.

Tier 2 — sensitive: the change touches both high-risk paths. Size: 119 lines, small (at most 200). Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 1 · Optional 1 · Nits 0

## Critical

#### C1 Invoice requests can read files outside the invoice directory

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The request’s `file` parameter is joined to the invoice directory without restricting the resulting path.
- **Why it fails / scenario:** A client can request `/invoices?file=../../package.json` and receive a file outside `data/invoices`. Other files readable by the service are also exposed.
- **Fix:** Restrict invoice names to an allowed format and ensure the resolved file, including symlink resolution, remains inside the authorized directory. Add traversal regression tests.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 The first page skips the newest orders

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats the one-indexed page number as zero-indexed.
- **Why it fails / scenario:** The default `page=1&size=10` returns orders 15 through 6, omitting orders 25 through 16.
- **Fix:** Calculate the offset as `(page - 1) * pageSize` and test the exact items on the first and subsequent pages.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Changing the order of `listOrders()` breaks the oldest-order calculation

- **Location:** [src/orders.js:16](repo/src/orders.js:16)
- **Problem:** `listOrders()` now reverses its existing order, while `firstOrder()` depends on the oldest order appearing first.
- **Why it fails / scenario:** [src/stats.js:7](repo/src/stats.js:7) now returns order 25 instead of order 1 for the dashboard’s “customer since” value.
- **Fix:** Preserve the existing `listOrders()` ordering and apply `latestFirst()` when preparing the paginated endpoint response.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 The invoice endpoint has no tests

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** The new file-serving route has no positive or negative endpoint tests.
- **Why it fails / scenario:** The suite passes without checking that an existing invoice downloads, a missing invoice returns 404, or traversal attempts are rejected.
- **Fix:** Add endpoint tests for those cases, including the traversal regression described in C1.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

#### O1 Remove per-request debug output

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Every pagination call writes a debug message to the service logs.
- **Why it fails / scenario:** Normal traffic to `/orders` produces a log line for every request.
- **Fix:** Remove the debug statement.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50.

## Verification

- Command found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file, no failures.
- Semgrep: scan failed because the read-only environment had no usable temporary directory; no Semgrep MCP tool was available.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=1 uncertain=0