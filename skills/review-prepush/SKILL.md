---
name: review-prepush
description: Fast pre-push review of the current branch against its base — runs the repo's checks from AGENTS.md, a fresh-context code-reviewer (against the SDD spec, if the branch has one), and an adversarial finding-verifier. Blocks only on confirmed Critical findings. Use before pushing, or when asked whether a branch is ready.
argument-hint: "[base-branch]"
allowed-tools: Read, Grep, Glob, Agent, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git rev-parse:*), Bash(git merge-base:*), Bash(git symbolic-ref:*), Bash(git branch:*), Bash(git show:*)
---

<!--
  review-kit (original). Derived from upstream /review (addyosmani/agent-skills):
  same five-axis skill, but run by the code-reviewer persona in a fresh context,
  scoped to "is this branch ready to push", and filtered by finding-verifier.
-->

# /review-prepush

Goal: answer, quickly, **"is this branch ready to push?"** Focus on: does the work do what the task asked, real bugs, tests that do not actually test anything, debug leftovers, TODOs and dead code. Not an architecture review — keep it fast.

Follow the `review-context` skill for config and verification, and the `review-report` skill for precision rules, severities and formats (namespaced `harness:review-context` / `harness:review-report` when installed as the Claude Code plugin). Do not edit any file.

## Step 1 — Scope (main session)

1. Base branch: `$ARGUMENTS` if given; else the base branch in the `Code review` section of AGENTS.md; else the remote default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`), else `main`, else `master`. Use `origin/<base>` if it exists, otherwise the local branch.
2. Collect: `git rev-parse --abbrev-ref HEAD`, `git log --format='%h %s%n%b' <base>..HEAD`, `git diff --stat <base>...HEAD`.
3. If there are no commits ahead of base, output the report with verdict OK and "No changes against `<base>`" and stop.
4. If `git status --porcelain` shows uncommitted changes, note it under Verification ("uncommitted changes are neither reviewed nor pushed").
5. **Task**: if the change belongs to a spec (`review-context` §4), the spec is the task. Otherwise, infer what the change is supposed to do from the branch name and commit messages (and a linked ticket ID if any). If it is unclear, say so — do not invent a task.

## Step 2 — Verification (main session)

Run the verification commands from AGENTS.md exactly as `review-context` §2 says (aggregate command if present, only read-only commands, nothing guessed; if none, say so and continue). Run Semgrep per `review-context` §2.6 if available. Keep the raw results for the report.

## Step 3 — Review (one subagent)

Spawn **one** subagent `code-reviewer` (use the name exactly as the Agent tool lists it — `harness:code-reviewer` when installed as the Claude Code plugin). Give it, verbatim:

- the base ref and the exact diff command: `git diff <base>...HEAD` (it must read the diff and the surrounding code itself);
- the task (the spec paths and the `review-context` §4 instruction, or the inferred task);
- the verification results from Step 2 (commands, pass/fail, failing test names and messages);
- the `Code review` section of AGENTS.md, if any, and the effective limits (`Max Optional`, `Max Nits`);
- this brief:

  > Pre-push review. Focus only on: (1) does the change fulfil the task (if there is a spec, apply the spec checks you were given); (2) correctness bugs on realistic paths; (3) tests in the diff that would not fail if the logic were wrong, and quality lowered to pass (review-report §1); (4) debug leftovers, new TODO/FIXME without a ticket, commented-out or dead code; (5) obvious security holes in the changed lines. Skip architecture, naming and style unless they hide a bug. Apply review-report precision rules (§1). Report findings in review-report §3 format, plus one concrete "what's done well" item. Do not modify files.

**Without subagents** (a tool that cannot spawn them, e.g. pi): run each persona's role yourself, one after another, using the same brief and keeping its output separate; then verify the findings yourself with the `finding-verifier` procedure. Say so under Verification ("personas run in the main session, not in a fresh context").

## Step 4 — Verify findings (one subagent)

If the reviewer reported zero findings, skip this step. Otherwise spawn **one** subagent `finding-verifier` (`harness:finding-verifier` as a plugin) with: the base ref and diff command, the verification results, and **all** findings verbatim (Optional and Nits included — it verifies and ranks them). Do not filter or rephrase them first.

Keep only `CONFIRMED` and `UNCERTAIN` findings, with the verifier's final severity. Label uncertain ones `(unverified)` in their title. Debug leftovers stay Required (`review-report` §1) — tell the verifier so. Record refuted ones (ID + one-line reason) for the Verification section.

## Step 5 — Report (main session)

Produce the `review-report` §4 report. Apply the limits after verification: keep the first `Max Optional` Optional and `Max Nits` Nit findings in the verifier's ranking (limits from AGENTS.md, default 3; see `review-context` §1); Optional findings that only extend a Critical/Required one are folded into its Fix. List what was dropped (ID, title, impact/cost) under Verification. Verdict values:

- **BLOCK** — at least one CONFIRMED Critical.
- **FIX BEFORE PR** — no confirmed Critical, but Required findings (or uncertain Critical).
- **OK** — nothing above Optional.

Output only the report (`review-report` §4): no preamble, no closing remarks.

The last line of the output must be exactly (for the git hook):

```
REVIEW_RESULT: <BLOCK|PASS> critical=<confirmed Critical count> required=<Required count> uncertain=<UNCERTAIN count>
```

`BLOCK` if and only if confirmed Critical > 0.
