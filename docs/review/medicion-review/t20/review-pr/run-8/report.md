<!-- review-kit:review-pr -->
## Summary and verdict

The branch adds order pagination and invoice downloads. It has four confirmed functional or security defects. **Tier 2:** it changes the invoice and server paths identified as high risk.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 4 · Required 1 · Optional 0 · Nits 0

Sensitive area: requires human review by an owner.

## Critical

#### C1 Invoice endpoint permits path traversal
- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** The disk path is built directly from the request’s `file` parameter without confinement.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns a file outside the invoice directory. A client can similarly read other files accessible to the service.
- **Fix:** Restrict invoice names and enforce confinement to the invoice directory, including symlink handling. Test valid, missing and traversal requests.
- **Confidence:** high
- **Source:** security-auditor, test-engineer

#### C2 Pagination skips the first page
- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** The offset treats a 1-indexed page as zero-indexed.
- **Why it fails / scenario:** The default page starts at index 10, omitting the ten newest orders.
- **Fix:** Use `(page - 1) * pageSize`. Test exact IDs and page totals for multiple pages and the default HTTP request.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 Oldest-order consumer returns the newest order
- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` relies on the former ascending order of `listOrders()`.
- **Why it fails / scenario:** It now returns order 25 instead of order 1, contrary to its documented oldest-order contract.
- **Fix:** Select the oldest order independently of the former list ordering and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 The supplied invoice is not a valid PDF
- **Location:** [data/invoices/2026-001.pdf:1](repo/data/invoices/2026-001.pdf:1)
- **Problem:** The only supplied invoice is a one-line placeholder without PDF structure.
- **Why it fails / scenario:** Downloading `2026-001.pdf` returns content that cannot be opened as a PDF.
- **Fix:** Supply a valid PDF and verify the successful invoice response.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

## Required

#### R1 Test the newest-first ordering contract
- **Location:** [test/orders.test.js:7](repo/test/orders.test.js:7)
- **Problem:** The `listOrders` test checks only the number of returned orders.
- **Why it fails / scenario:** Returning the previous ascending order still passes, despite contradicting the new contract.
- **Fix:** Assert the expected descending IDs, including the first and last entries.
- **Confidence:** high
- **Source:** test-engineer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) caps the requested page size at 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → passed; one test file reported.
- Semgrep: skipped after the script failed because no writable temporary directory was available; no Semgrep MCP tool was available.
- Findings refuted by the verifier: 0. Two test findings overlapped C1, C2 and C4 and were incorporated into their fixes.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Callers: two changed contracts checked; three `listOrders` calls outside the diff inspected. External consumers of `/orders` were not visible.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=4 required=1 uncertain=0