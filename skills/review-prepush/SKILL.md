---
name: review-prepush
description: Fast pre-push review of the current branch against its base — runs the repo's checks from AGENTS.md, a fresh-context code-reviewer (against the branch's docs/changes/ folder, if it has one), and an adversarial finding-verifier. Blocks only on confirmed Critical findings. Use before pushing, or when asked whether a branch is ready.
argument-hint: "[base-branch]"
allowed-tools: Read, Grep, Glob, Agent, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git rev-parse:*), Bash(git merge-base:*), Bash(git symbolic-ref:*), Bash(git branch:*), Bash(git show:*)
kind: skill
uses:
  - skill:review-context
  - skill:review-report
delegates:
  - agent:code-reviewer
  - agent:finding-verifier
related:
  - skill:task-done
# Bloques para rulesync: los genera scripts/build-agents.py desde los campos de arriba. No editar a mano.
claudecode:
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

**Read only what you use.** Do not read the persona definitions (`.codex/agents/`, `agents/`): the tool loads them when it spawns the persona. Do not read `task-done`: `review_facts.py` runs its audit script.

## Step 1 — Scope (main session)

1. **Facts**, in one call, from the repo root: `python3 <review-context-dir>/scripts/review_facts.py [<base>]`, with `<review-context-dir>` the directory of the `review-context` skill (next to this one: `../review-context`) and `<base>` = `$ARGUMENTS` if given (otherwise the script resolves it). It prints the base, branch, log, size, the `tramo <i>: <a>..<b>` lines (D-0060), diff stat, a warning about uncommitted changes, the task with its `task-done` audit, and the TODO without a ticket. Keep the output whole: it goes as is in the brief of Step 3. Gather nothing else. If it cannot run, write "Facts: not checked (<reason>)" under Verification and continue with Step 3 (the reviewer reads the diff itself).
2. If it says `sin cambios frente a <base>`, output the report with verdict OK and "No changes against `<base>`" and stop.
3. If it warns of uncommitted changes, note it under Verification ("uncommitted changes are neither reviewed nor pushed").
4. **Task**, from its `tarea:` line:
   - a change folder (`review-context` §4): on a task branch, `<change>/T<n>`, read that task's file, the README and, if they exist, `spec.md` and `plan.md`: they are the task; on a plan branch, `<change>/plan`, the plan itself (README and task files) is what is reviewed. Never read the GitHub issue its `issue:` names;
   - `tarea: ninguna`: infer what the change is supposed to do from the branch name and commit messages (and a linked ticket ID if any). If it is unclear, say so — do not invent a task.

## Step 2 — Verification (main session)

If `REVIEW_KIT_VERIFICATION` names a readable file, the hook already ran the checks: run nothing; use its results as `review-context` §2 says. Without it: run the verification commands from AGENTS.md as `review-context` §2 says (aggregate command if present, only read-only commands, nothing guessed; if none, say so and continue), and Semgrep per §2.6 if available. Keep the raw results for the report.

**Audit** (the `auditoría:` lines of the facts, only with a change folder): it is the read-only audit of `task-done`, which runs no verification and edits nothing. Its scope follows the branch (D-0032). On a task branch, only that task: that each of its examples has a test named after it in the red commit (`test(T3): …`) and no later commit changed or removed those tests (a task not done without a red commit is `pending`), that its examples are in the README's example map, and that its `depends_on` are done in the base branch. On the plan branch: the task files (frontmatter, no dependency that does not exist, no cycle) and that every example of the map is in some task. Keep it as a verification result (exit 0: nothing wrong; exit 3: `PROBLEM` lines). If it says `auditoría: no comprobada (<reason>)`, or its only `PROBLEM` is that it cannot read the git history of the branch (no base branch found), write "Test protection: not checked (<reason>)" under Verification.

**TODO without a ticket** (D-0057), always: the `TODO sin ticket:` section of the facts lists, one `file:line` per line, the TODO, FIXME, XXX and HACK comments the branch adds without a ticket, or `ninguno`. Keep its list for Step 5.

## Step 3 — Review (one subagent per tramo)

Count the `tramo <i>:` lines of the facts. With a **single tramo** (the usual case, and when facts could not run) the review is today's: spawn **one** subagent `code-reviewer` (use the name exactly as the Agent tool lists it — `harness:code-reviewer` when installed as the Claude Code plugin). Every persona starts without the main session's history, so it reviews independently of what the main session read: in Codex pass `agent_type: "code-reviewer"` (so its definition loads) and `fork_turns: "none"` (default `all`) to `spawn_agent`; Claude Code subagents do not inherit the history and have no such parameter. The brief must stand on its own: do not assume the persona saw anything of this session. Give it, verbatim:

- the base ref and the exact diff command: `git diff <base>...HEAD` (it must read the diff and the surrounding code itself);
- the task (the paths of the change folder and the `review-context` §4 instruction, or the inferred task);
- the verification results from Step 2 (commands, pass/fail, failing test names and messages), and the output of `review_facts.py` as is (Step 1: base, branch, log, diff stat, task, audit, TODO), not summarised;
- the `Code review` section of AGENTS.md, if any, and the effective limits (`Max Optional`, `Max Nits`);
- this brief:

  > Pre-push review. Focus only on: (1) does the change fulfil the task (if there is a change folder, apply the checks you were given for it); (2) correctness bugs on realistic paths; (3) tests in the diff that would not fail if the logic were wrong, and quality lowered to pass (review-report §1); (4) debug leftovers, commented-out or dead code (do not report new TODO/FIXME without a ticket: a script lists them, do not repeat them); (5) obvious security holes in the changed lines; (6) the "Beyond the diff" checks of your instructions: callers outside the diff of symbols whose contract changed, and clashes with accepted decisions in `docs/decisions/`; (7) you are the only persona, so apply the test checks of review-report §5 (the test criterion, and one finding per `PROBLEM` line of the audit output in the facts); (8) on a task branch, the size and purpose check of your instructions (D-0033). Skip architecture, naming and style unless they hide a bug. Apply review-report precision rules (§1). Report findings in review-report §3 format, plus one concrete "what's done well" item and your one-line `Callers:` summary. Do not modify files.

**Several tramos** (D-0060): consecutive commits `<a>..<b>`, first to last. Spawn **one `code-reviewer` per tramo**, in parallel, each without history. Every tramo brief is the brief above with these changes: the diff is its tramo's, `git diff <a>^..<b>`; it carries the task and the whole facts (all the tramos); and it says: *you see only part of the branch; before reporting anything as missing or absent, read `git diff <base>...HEAD`: another tramo may add it. If it is there, do not report it.* A `tramo grande` (one commit over the threshold) is reviewed like the others.

**Seams pass** (2 or more tramos; with a single tramo there is no seams pass): **one more `code-reviewer`**, without history (D-0046), in parallel. It reads `git diff <base>...HEAD` whole and looks only at the seams: what each tramo exposes and who uses it in another, whether the use matches the contract, and whether all the examples of the task have their test and behaviour. It does not repeat what is inside one tramo.

**Without subagents** (a tool that cannot spawn them, e.g. pi): run each persona's role yourself, one after another, using the same brief and keeping its output separate (with several tramos: each tramo, then the seams pass); then verify the findings yourself with the `finding-verifier` procedure. Say so under Verification ("personas run in the main session, not in a fresh context"; with several tramos, "tramos reviewed one after another in the main session").

## Step 4 — Verify findings (one subagent)

If the reviewers reported zero findings, skip this step. Otherwise spawn **one** subagent `finding-verifier` (`harness:finding-verifier` as a plugin) with, in the same way (no inherited history; in Codex `agent_type: "finding-verifier"` and `fork_turns: "none"`): the task, the base ref and diff command, the verification results, the `Known non-issues` of AGENTS.md (`review-context` §3), and **all** findings verbatim (Optional and Nits included — it verifies and ranks them). Do not filter or rephrase them first. With several tramos: first merge the same finding reported by two tramos (or by a tramo and the seams pass) into one, it goes to the verifier and the report once. Tell the verifier that each reviewer saw only part of the branch: it confirms only what is still true in `HEAD` (code a later tramo deletes, or a check another tramo adds, refutes it).

Keep only `CONFIRMED` and `UNCERTAIN` findings, with the verifier's final severity. Label uncertain ones `(unverified)` in their title. Debug leftovers stay Required (`review-report` §1) — tell the verifier so. Record refuted ones (ID + one-line reason) for the Verification section.

The TODO/FIXME without a ticket of Step 2 do not go to the `finding-verifier`: it does not see them.

## Step 5 — Report (main session)

Read `../review-report/references/report-format.md` (the `review-report` skill's directory, next to this one) and produce the report in the full layout (§4.1). Apply the limits after verification: keep the first `Max Optional` Optional and `Max Nits` Nit findings in the verifier's ranking (limits from AGENTS.md, default 3; see `review-context` §1); Optional findings that only extend a Critical/Required one are folded into its Fix. List what was dropped (ID, title, impact/cost) under Verification. **TODO without a ticket** (D-0057): if the script listed locations, add one single Nit, `<N> TODO/FIXME without a ticket`, with all the locations (`file:line`), outside `Max Nits` (it does not count for the limit, and it is not dropped by it) and not verified. If the script listed none, there is no Nit for them. If there is a change folder, add one line to the Summary: `Task: <task file path> (<status>)` on a task branch, or `Plan: <folder> — <N> tasks` on the plan branch, followed by `; audit: <ok | N problems | not checked>`. Under Verification, add the audit exit status from the facts, and the reviewer's `Callers:` line (one per tramo). With several tramos, add a **Seams** section with what the seams pass found (or "no findings"); with one, none. Verdict values:

- **BLOCK** — at least one CONFIRMED Critical, in any tramo or in the seams.
- **FIX BEFORE PR** — no confirmed Critical, but Required findings (or uncertain Critical).
- **OK** — nothing above Optional.

Output only the report (`report-format.md`): no preamble, no closing remarks.

The last line of the output must be exactly (for the `harness-review` git hook, installed from `.pre-commit-config.yaml`, not copied):

```
REVIEW_RESULT: <BLOCK|PASS> critical=<confirmed Critical count> required=<Required count> uncertain=<UNCERTAIN count>
```

`BLOCK` if and only if confirmed Critical > 0.
