---
name: review-report
description: Output side of every review (review-prepush, review-pr) — precision rules (what is worth reporting), the severity scale and mapping, the per-finding format and the common report format. Load it whenever a review skill (review-prepush, review-pr) or persona (code-reviewer, security-auditor, test-engineer, finding-verifier) produces, verifies or merges review findings.
user-invocable: false
kind: skill
---

<!-- review-kit (original). Not part of addyosmani/agent-skills. -->

# Review Report

How to turn a review into findings and a report. These rules sit on top of `code-review-and-quality` (the *how* of reviewing); where they conflict, this file wins. The input side (repo config, verification commands) is in the `review-context` skill.

## 1. Precision rules

- **Three real findings beat twenty doubtful ones.** Report only what you would defend in front of the author with the code open.
- **Do not repeat what linters, formatters or type checkers already catch** (or would catch, given the repo's config). If the verification step reported it, reference it once under Verification instead of as a finding.
- **Justify before you classify.** For each finding, first write why it fails and in which scenario; pick the severity last, from that reasoning.
- **If in doubt, say so.** Mark the finding `Confidence: low` and state what would confirm it. Never present a guess as a fact.
- **Limit Optional and Nit findings** to the limits the command gives you (`Max Optional`, `Max Nits`; default 3 each). Pick the most useful ones by impact and drop the rest. The final cut is made after verification, using the verifier's impact/cost ranking (§3). An Optional must be worth the author's time on its own:
  - not a restatement or extension of a Critical/Required finding (fold it into that finding's Fix instead);
  - no "add tests for code that already works" unless it is business logic with no test at all;
  - no generic hardening or best-practice advice without a concrete scenario in this change.
- **Order by impact** within each severity: correctness and security first, then structure, then everything else.
- **Stay on the diff.** Pre-existing problems in untouched code are out of scope unless the change makes them reachable or worse. A caller outside the diff that the change breaks is in scope: the change made it worse.
- **Watch for quality being lowered to make the change pass** — these are at least Required:
  - tests weakened, deleted, skipped (`skip`, `xit`, `@Ignore`, `t.Skip`) or marked flaky without reason;
  - assertions rewritten to match new (possibly wrong) output, or loosened (`toEqual` → `toBeTruthy`, exact → contains);
  - tests that cannot fail: no assertion, asserting on the mock, tautologies, catching the error the test should surface;
  - lint rules disabled, inline suppressions added (`eslint-disable`, `# noqa`, `@ts-ignore`, `//nolint`, `#[allow]`), coverage thresholds or type strictness lowered;
  - a new helper that duplicates an existing one in the repo (search before claiming).
- **Leftovers**: debug output (`console.log`, `print`, `dbg!`, `fmt.Println` used for debugging) and commented-out code are always **Required** in pre-push reviews (that is what the pre-push review is for); the verifier may refute them only if the output is intentional (e.g. a real logger call), never downgrade them. New TODO/FIXME without a ticket and dead code introduced by the change: Nit or Optional.

## 2. Severity scale

| Severity | Meaning | Author action |
|---|---|---|
| **Critical** | Broken functionality on a realistic path, data loss/corruption, exploitable security issue, failing tests caused by the change | Must fix; blocks push/merge |
| **Required** | Real defect or risk that must be fixed before merge: missing/ineffective test for new logic, wrong error handling, quality lowered (§1), non-exploitable-yet-real security weakness | Must fix before merge |
| **Optional** | Worth considering: simpler design, refactor, a missing test for untested business logic. Capped (default 3) | Author decides |
| **Nit** | Cosmetic. Capped (default 3) | Author may ignore |

Mapping of the checks beyond the diff:

- The test checks of §5: a change that needs a test and has none, or a `PROBLEM` from `task_done.py --audit` → **Required**. Never Critical on their own: a process check does not block a push.
- A change that contradicts an accepted decision in `docs/decisions/` with no record superseding it → **Required**; Critical only if it also breaks functionality as defined above.
- A caller outside the diff broken by the change → the scale above, like any bug: Critical when it breaks on a realistic path.

Mapping from `security-auditor`'s scale: Critical → Critical; High → Required; Medium → Required if exploitable in this codebase as deployed, else Optional; Low/Info → drop unless the repo's `Code review` section in AGENTS.md asks for them.

## 3. Finding format

Every finding — in persona reports and in the final report — uses this shape:

```markdown
#### <ID> <short title>
- **Location:** path/to/file.ext:LINE (or LINE-LINE)
- **Problem:** what is wrong, in one or two sentences.
- **Why it fails / scenario:** concrete input or state → wrong result. For security: who can trigger it and what they get.
- **Fix:** concrete change (code snippet when short). Mandatory for Critical and Required.
- **Confidence:** high | medium | low (+ what would confirm it, if not high)
- **Source:** code-reviewer | security-auditor | test-engineer | semgrep | verification | spec | pr-description
- **Impact / cost:** high|medium|low / S|M|L — Optional and Nit only; set by the verifier (value for the codebase vs. effort to fix)
```

IDs, written bare (`#### C1 Path traversal in …`, no brackets): `C1, C2…` for Critical, `R1…` Required, `O1…` Optional, `N1…` Nit.

## 4. Report format

**Output only the report.** No preamble ("Here is the report…"), no closing remarks: the first line is the first heading (or the marker line the command asks for) and the last line is the `REVIEW_RESULT` line when the command requires one.

Headings and field labels are always in English, exactly as below, so tooling can parse them; the free text follows the output language (set in AGENTS.md, see `review-context` §1; English by default). There are two layouts with the same sections; the command says which one to use.

### 4.1 Full layout

Every section, in this order:

```markdown
## Summary and verdict
<2–4 sentences: what the change does, whether it fulfils its task, overall verdict.>
<If the change has a spec (`review-context` §4): `Spec: <path> (spec <status>, plan <status>) — <N>/<M> acceptance criteria covered by this change`.>
**Verdict:** <see command-specific values>

## Critical
<findings, or "None.">

## Required
<findings, or "None.">

## Optional
<up to Max Optional, ordered by the verifier's ranking, or "None.">

## Nits
<up to Max Nits, ordered by the verifier's ranking, or "None.">

## What's done well
- <at least one concrete, specific observation with file:line — not generic praise>

## Verification
- Commands found in AGENTS.md: <list, or "none">
- Run: `<cmd>` → <pass/fail + key numbers, e.g. "12 passed, 1 failed (test_x)">
- Not run: `<cmd>` → <reason>
- Semgrep: <result, or "not available — skipped">
- Findings refuted by the verifier: <N> (<one line each: ID — reason>)
- Optional/Nit findings dropped by the limit (Max Optional=<n>, Max Nits=<n>): <N> (ID, title and impact/cost, one line each)
```

### 4.2 Short layout

The same content, with only what needs action in view: the summary with one count line, then Critical and Required in full (a section with no findings is left out), and everything else folded.

```markdown
## Summary and verdict
<as in the full layout>
**Verdict:** <see command-specific values>
**Findings:** Critical <n> · Required <n> · Optional <n> · Nits <n>

## Critical
<findings>

## Required
<findings>

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional
## Nits
## What's done well
## Verification
<as in the full layout>

</details>
```

### 4.3 Findings block

When the command asks for it (`review-pr --inline`, in the GitHub workflow), write the report's content again as one JSON block, after the report and before the `REVIEW_RESULT` line. The workflow posts each finding as a comment on its line and builds the summary comment from this block alone, without reading the Markdown. It must be valid JSON: newlines in strings as `\n`, quotes escaped.

````markdown
```json review-kit
{"verdict": "CHANGES NEEDED", "tier": 1,
 "summary": "<the summary sentences, with the tier and any line the command adds>",
 "findings": [
   {"id": "R1", "title": "<short title>", "path": "src/a.py", "start_line": 40, "line": 42,
    "body": "- **Problem:** …\n- **Why it fails / scenario:** …\n- **Fix:** …\n- **Confidence:** high\n- **Source:** code-reviewer"}],
 "done_well": ["<one item per line of What's done well>"],
 "verification": ["<one item per line of Verification>"]}
```
````

- `findings`: every finding of the report, with its ID, after the limits; none more.
- `path` is relative to the repository root and `line` is the line in the head version of the file (the last line of a range; `start_line` only for a range). A finding with no single line, such as a missing file or one about the whole change, has `"path": null` and no `line`.
- `body` is the finding in §3 format without its heading and its `Location` line. The severity comes from the ID.
- The workflow checks each `path` and `line` against the PR diff: a finding on a line the diff does not show goes into the summary comment in full, so give its real line anyway. If the block is not valid, the workflow posts the Markdown report as it is.

## 5. Test checks

Who applies them: `test-engineer` when it runs (`review-pr` tiers 1–2); otherwise the `code-reviewer`, when it is the only persona (`review-prepush`, `review-pr` tier 0). The review command says which. One owner, so the same finding is not reported twice.

**When a change needs a test.** It needs one if it adds or changes a branch, a loop, a parser or format conversion, money, security or permissions, a data write, or if it fixes a bug (a regression test that fails without the fix). Docs, comments, configuration values and renames covered by existing tests do not; neither does a refactor whose behaviour existing tests already cover, as long as they stay green unchanged. "It is a small change" is not an exception: small changes break too. If in doubt, it needs a test.

- A change that needs a test and has none that would fail without it is a missing test for new logic: **Required**. Do not report missing tests for changes the criterion exempts.
- **Audit of the task or the plan.** When the command passes the output of `task_done.py --audit` (from the `task-done` skill), turn each `PROBLEM` line into one finding, **Required**, `Source: verification`. On a task branch: the task done without its red commit (`test(T3): …`), an example of the task without a test named after it, a red-commit test changed or removed later (quality lowered, §1), an example of the task not in the README's example map, a dependency not done in the base branch (the PR would merge before what it needs). On the plan branch: a malformed task file, a dependency that does not exist, a cycle, a map example in no task. Locate it at the test file, the task file or the README. Do not redo the check by hand, and do not report a `pending` task: it is work not done yet. If the audit did not run, or could not read the git history of the branch (`PROBLEM: cannot read the git history…`, e.g. no base branch), do not guess and do not turn it into a finding: it is listed under Verification.
