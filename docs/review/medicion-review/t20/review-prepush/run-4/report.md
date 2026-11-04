## Summary and verdict

The branch adds order pagination and invoice downloads. It also permits directory traversal, returns the wrong page of orders, and changes the result of an existing statistics function.

**Verdict:** BLOCK

## Critical

#### C1 Invoice endpoint permits reading files outside the invoice directory

- **Location:** [src/invoices.js](repo/src/invoices.js:10)
- **Problem:** A request parameter is joined directly to the invoice directory and read from disk without confinement.
- **Why it fails / scenario:** `/invoices?file=../../package.json` returns the project’s `package.json`; other files readable by the process can also be exposed.
- **Fix:** Restrict invoice names and verify that the resolved real path remains inside the authorized directory, including for symbolic links.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 The first page starts at the second block

- **Location:** [src/orders.js](repo/src/orders.js:32)
- **Problem:** The offset treats pages as zero-indexed although the interface uses one-indexed pages.
- **Why it fails / scenario:** Page 1 with size 10 returns IDs 15–6, omitting the ten newest orders. With size 50, it returns an empty page.
- **Fix:** Calculate the offset as `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 Changing the order breaks the first-order statistic

- **Location:** [src/stats.js](repo/src/stats.js:7)
- **Problem:** `firstOrder` relies on the former ordering of `listOrders`.
- **Why it fails / scenario:** The “customer since” statistic now uses order 25 instead of order 1, the oldest order.
- **Fix:** Select the oldest order under the new contract and add a regression test.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 The pagination test does not verify the returned orders

- **Location:** [test/orders.test.js](repo/test/orders.test.js:11)
- **Problem:** The test accepts any array of at most ten items, including an empty or shifted page.
- **Why it fails / scenario:** The current implementation skips the first page while passing all its assertions.
- **Fix:** Assert the exact IDs and page totals for the first and second pages, and test a requested size above 50.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 The invoice route has no tests

- **Location:** [src/server.js](repo/src/server.js:17)
- **Problem:** The new file-reading route and its security boundary are untested.
- **Why it fails / scenario:** Neither a failure to return an existing invoice nor the current directory traversal is detected by the tests.
- **Fix:** Add HTTP tests for an existing invoice, a missing file and directory traversal attempts.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 The new order is not tested

- **Location:** [test/orders.test.js](repo/test/orders.test.js:7)
- **Problem:** The `listOrders` test checks only the number of orders.
- **Why it fails / scenario:** The previous oldest-first implementation also passes the test.
- **Fix:** Assert that the returned IDs are ordered from newest to oldest.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Debug output runs on every orders request

- **Location:** [src/orders.js](repo/src/orders.js:33)
- **Problem:** Pagination contains a `console.log` marked `DEBUG`.
- **Why it fails / scenario:** Every `/orders` request writes debug data to the service output.
- **Fix:** Remove the debug call.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

#### O1 TODO has no tracking reference

- **Location:** [src/invoices.js](repo/src/invoices.js:8)
- **Problem:** The caching TODO has no tracking reference.
- **Why it fails / scenario:** The proposed work remains in the code without a linked task or context.
- **Fix:** Remove it or link it to a tracked task.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## Nits

None.

## What's done well

- [test/orders.test.js](repo/test/orders.test.js:18) checks invalid, negative, absent and valid inputs for `parsePositiveInt`.

## Verification

- Commands found in AGENTS.md: `npm test`; `npm start` starts the service and is not a verification command.
- Run: `npm test` → passed; Node reported 1 test, 1 pass.
- Semgrep: unavailable; its script exited 2 because no writable temporary directory was available. No Semgrep MCP tool was available.
- Callers: 2 changed contracts checked, with 3 call sites outside the diff read; none omitted.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- The working tree had no uncommitted changes.

REVIEW_RESULT: BLOCK critical=3 required=4 uncertain=0