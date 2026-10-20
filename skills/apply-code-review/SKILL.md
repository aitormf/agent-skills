---
name: apply-code-review
description: Acts on code review feedback (a review-prepush or review-pr report, PR comments, or a person's review) by checking each finding against the real code before changing anything, pushing back with evidence when a finding is wrong, and fixing the accepted ones one by one with verification. Use it when there is code review feedback to address; for spec or plan reviews, use apply-review.
---

# Apply a code review

Feedback is a set of claims about the code. Check each one before acting on it. Correctness wins over politeness: agreeing with a wrong finding breaks the code just as much as ignoring a right one.

## Step 1: read and understand everything first

1. Collect the feedback: a `review-prepush` or `review-pr` report, the PR comments (`gh pr view --comments`, `gh api repos/{owner}/{repo}/pulls/<n>/comments`), or what the person said.
2. Read **all** of it before changing anything. Findings are often related.
3. Restate each finding in one line of your own. If any finding is unclear, ask about it **before implementing any** of them. Example: "I understand C1, R1 and R3. In R2, do you mean X or Y?"

## Step 2: check each finding against the code

For each finding, open the code it points to and answer:

- Is the problem real in this codebase, at this version? Reproduce it if you can.
- Does the suggested fix break something else, or other platforms or versions?
- Is there a reason for the current code (a comment, an ADR, the spec, `git log -L`)?
- Does it ask for something nobody uses? Search for real callers. If there are none, propose removing the code (YAGNI) instead of "doing it properly".
- Does it conflict with `docs/ARCHITECTURE.md`, an ADR or the approved spec? Then the person decides, not the review.

Weigh the source:

- **The person you work with:** trusted. Implement once it is understood; ask only if the scope is unclear.
- **Our review reports:** findings marked `CONFIRMED` by `finding-verifier` already carry evidence, but check that the code has not changed since. `UNCERTAIN` findings need your own check.
- **External reviewers and bots:** be sceptical, but check carefully. They may lack context.

## Step 3: present the triage

```
Triage
──────
C1 <title> → accept: <one line of evidence>
R2 <title> → push back: <technical reason, with file:line>
O1 <title> → accept / skip: <why>
R3 <title> → can't verify: <what is needed to check it>
```

Wait for the person to confirm before changing code. If they ask you to address the feedback directly, act on the triage, but still stop on any push-back that contradicts a reviewer they trust, and on any finding that conflicts with the spec, `ARCHITECTURE.md` or an ADR.

## Step 4: fix one at a time

1. Order: Critical and blocking findings, then simple ones (typos, imports), then complex ones (logic, refactors).
2. One finding at a time. For each one, make the change, run its test (add one if the finding is a bug with no test) and check for regressions.
3. Do not widen the scope: fix what the finding says. If you see something else, note it; do not fix it in passing.
4. At the end, run the verification command from the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects).

## How to talk about it

- No performative agreement ("You're absolutely right!", "Great catch!"). State the fix, or just make it: the diff shows you heard.
- When pushing back, give the evidence: `file:line`, a test, a command output. "I don't think so" is not a reason.
- If you pushed back and turn out to be wrong, say so plainly and fix it.
- Reply to PR comments, resolve threads or push only when the person asks. If you reply, answer in the comment's thread (`gh api repos/{owner}/{repo}/pulls/<n>/comments/<id>/replies`), not as a top-level comment.

## Report

```
Code review applied
───────────────────
C1 <title> → fixed (<file:line>, test <name>)
R2 <title> → pushed back: <reason>
O1 <title> → skipped: <reason>
Verification: `<command>` → <result>
```

List what is still open: pushed-back findings awaiting an answer, unverifiable ones and anything deferred.
