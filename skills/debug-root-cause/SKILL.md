---
name: debug-root-cause
description: Finds the root cause of a failing test, bug or unexpected behaviour before changing any code, then fixes it with a regression test that is proven to fail without the fix. Use it when debugging a failure whose cause is not yet known, or after a fix did not work. Not for applying review findings, implementing tasks or changes whose cause is already clear.
---

# Debug to the root cause

**Core rule:** no fix without a root cause. A change that makes the symptom disappear without explaining it is a guess, and guesses pile up.

Follow the phases in order. Do not move on until the current one is done.

## 1. Reproduce

1. Read the whole error: message, stack trace, file and line, exit code. It often names the cause.
2. Reproduce it with a command you can run again: a test, a script, a request. Write down the exact command and the output.
3. If it does not reproduce reliably, do not fix anything yet: gather more data (logs, inputs, environment, timing) until it does, or until you can say under which conditions it happens.

## 2. Find where it comes from

1. **What changed?** `git log` and `git diff` of the area, new dependencies, configuration, environment. If it used to work, `git bisect` with the reproduction command finds the commit.
2. **Trace back.** Start where the wrong value shows up and follow it upstream, caller by caller, to where it first becomes wrong. That is the root cause; everything after it is symptom.
3. **Compare with what works.** Find similar code in the repo that behaves correctly and list every difference, however small.
4. **In systems with several components** (API → service → database, CI → build → deploy), log what enters and leaves each boundary once, then look at where the data goes wrong. Remove those logs before finishing.

## 3. One hypothesis at a time

1. State it in one sentence: "X fails because Y, as shown by Z".
2. Test it with the smallest possible change or experiment. Change one variable at a time.
3. If it is not confirmed, discard it and go back to phase 2 with what you learned. Do not stack a second change on top of the first one.
4. If you do not understand something, say so. Do not pretend.

## 4. Fix

1. **Regression test first.** Write a test that reproduces the bug, at the lowest level that can show it, and check that it **fails** for the right reason.
2. **One fix, on the root cause.** No "while I'm here" refactors or unrelated improvements.
3. **Prove the test.** With the fix, the test passes. Revert the fix: the test must fail again. Restore the fix.
4. Run the verification command from the `Commands` section of `AGENTS.md` (`Comandos` in Spanish-language projects) and report its output.

## When to stop and ask

- **Three failed fixes:** stop. Each fix revealing a new problem somewhere else usually means a design problem, not a bug. Explain what you tried and what you learned, and ask the person before trying a fourth.
- **The bug comes from the spec:** if the behaviour follows the spec in `docs/specs/` but the spec is wrong or incomplete, the spec gets fixed first. Say so; do not change behaviour against an approved spec on your own.
- **The fix is large:** if the root cause needs a change beyond a few files, propose following the "complex bug" path of SDD (`spec.md` + `tasks.md`) instead of fixing it on the spot.
- **The cause is outside the repository** (a dependency, the platform, an external service): document what you found, propose a workaround if there is one, and leave the decision to the person.

## Never

- Delete, skip or weaken a test to make the failure go away.
- Add a `sleep` or a retry to hide a timing problem. Wait for the actual condition.
- Catch and silence the error that is the symptom.
- Claim it is fixed without having run the reproduction and the verification in this session.

## Report

- **Symptom** and how to reproduce it.
- **Root cause**, with `file:line`.
- **Fix**, and why it addresses the cause and not the symptom.
- **Regression test**, and proof that it fails without the fix.
- **Verification**: command and result.
- **Discarded approaches**, if any is one someone would plausibly try again ("a retry hides it", "upgrading X does not fix it"): propose recording it as `discarded` with `record-decision`. Most bugs leave no record.
