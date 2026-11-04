# Report format

Only the main session reads this file, when it writes the final report (`review-prepush`, `review-pr`). The personas do not need it.

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
