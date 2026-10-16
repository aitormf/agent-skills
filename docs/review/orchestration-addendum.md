<!-- review-kit (original). Extends upstream's orchestration-patterns.md; does not replace it. -->

# Orchestration addendum: fan-out → verify → synthesize

review-kit uses upstream's patterns 2 (single-persona command) and 3 (parallel fan-out with merge) and adds one step to both: a **verification pass** run by the command after the reviewers report. This file documents it in the format upstream asks for new patterns.

```
/review-pr
  ├── (parallel) code-reviewer    ─┐
  ├── (parallel) security-auditor ─┤→ merge + dedupe (main) → finding-verifier → synthesis (main)
  └── (parallel) test-engineer    ─┘

/review-prepush
  code-reviewer → finding-verifier → report (main)
```

The verifier does two things with the findings it receives, all of them including Optional and Nits:

1. **Filter** — every finding is `CONFIRMED`, `REFUTED` or `UNCERTAIN` against the code.
2. **Rank** — surviving Optional and Nit findings get an **impact** (`high`/`medium`/`low`) and a **cost to fix** (`S`/`M`/`L`) and are ordered separately: higher impact first, then lower cost, then the more concrete scenario.

The command then applies the repo's limits mechanically: it keeps the first `Max Optional` and `Max Nits` (set in AGENTS.md's `Code review` section, default 3 each; `0` hides them) and lists the rest — ID, title, impact/cost — under Verification. Critical and Required findings are never capped.

## Why it is not an anti-pattern

| Upstream rule | How this pattern complies |
|---|---|
| Personas do not invoke personas | The **command** spawns `finding-verifier`; no persona knows the verifier exists. |
| Orchestration depth ≤ 1 | Every subagent is spawned directly by the command in the main session. |
| No paraphrasing hops (anti-pattern C) | The command passes findings to the verifier **verbatim**; the verifier reads the code itself rather than trusting a summary. |
| No router persona (anti-pattern A) | The verifier has domain value (refuting false positives against code, ranking suggestions by impact vs. cost), not routing value. |

## Why a separate step and not a rule inside each reviewer

Reviewers are asked to find problems; telling the same agent to also argue against its own findings weakens both jobs. A fresh context whose *only* goal is to refute (default stance: false positive) filters more aggressively and is cheaper: one verifier call over all merged findings, instead of one per reviewer.

## Why rank in the verifier and cut in the command

- **Rank after verifying, not before.** Cutting first would spend the limit on suggestions that may be false; ranking only confirmed findings means the slots go to real, worthwhile ones.
- **Impact vs. cost, not impact alone.** A medium-impact, few-line fix is more useful to the author than a high-impact redesign buried in a pre-push review; the cost axis surfaces the cheap wins.
- **The cut is mechanical.** The verifier never drops a finding for being low-value — it only orders. The command applies a number the repo chose, so the limit can change (per repo, or later for everyone) without touching any persona prompt.
- **Cost stays bounded.** Personas already apply the same limits before reporting, so the verifier receives at most `limit × number of personas` Optional/Nit findings.

## When to use it

- The findings will be shown to a human who pays the cost of each false positive (PR comments, a blocking hook).
- The merge step yields more than a couple of findings.

Skip the step when there are no findings (both commands do).

## Anti-pattern shadow

- **Verifier that also reviews**: if the verifier starts adding new findings, it becomes a fourth reviewer with no merge step. It must only confirm, refute, mark uncertain and rank — never add findings.
- **Verifier that cuts**: if the verifier starts deciding how many suggestions to keep, the limit stops being configurable and its judgment of "low value" silently hides findings. It ranks; the command cuts.
- **Verifier per persona**: three verifiers in parallel lose cross-report deduplication and triple the cost. Verify once, after the merge.
- **Discarding on assumption**: a verifier that refutes security findings with "probably validated elsewhere" turns a safety net into a hole. Security/auth findings can only be refuted with checked evidence; otherwise they stay as `UNCERTAIN`.
