---
name: review-context
description: Input side of every review (review-prepush, review-pr) — how to read the repo's review config from AGENTS.md (base branch, language, high-risk paths, conventions) and how to run the repo's verification commands and Semgrep safely before reviewing. Used by the review-kit commands in the main session, before any persona is spawned.
user-invocable: false
---

<!-- review-kit (original). Not part of addyosmani/agent-skills. -->

# Review Context

How a review skill gathers its input: the repo's configuration and the verification results. The output side (precision rules, severities, formats) is in the `review-report` skill.

## 1. Repo configuration lives in AGENTS.md

There is no separate review config file. Everything repo-specific comes from the project's `AGENTS.md` (root, plus any nested `AGENTS.md` for the changed paths). If the repo has a `CLAUDE.md`, it normally just imports `AGENTS.md` (`@AGENTS.md`); if it has its own content instead, read both, and when they disagree `AGENTS.md` wins. These files are normally already in your context; if they are not, read them.

Look for two things, in whatever form the repo wrote them:

- **Verification commands** — usually under a "Commands" / "Comandos" (or similar) heading: tests, lint, type check, format check, build. They may be a single aggregate command (`make check`, `npm run verify`, `./scripts/ci.sh`) or one line per tool, a table, or prose. Do not require a fixed format.
- **A `Code review` section** (optional). It may define: base branch, output language, high-risk paths, things to always flag, things to ignore, conventions the linters do not cover, whether to run Semgrep, and how many Optional / Nit findings to keep (`Max Optional`, `Max Nits`). Apply what it says. Its instructions override the defaults below, but never the safety rules in §2.

Defaults when the section is missing: base branch = the remote default branch (`git symbolic-ref refs/remotes/origin/HEAD`, else `main`, else `master`); output language = **English**; Max Optional = **3**; Max Nits = **3** (`0` hides that section's findings); high-risk paths = anything matching auth, login, session, token, permission, role, payment, billing, invoice, checkout, migration, schema, crypto, secret, webhook, admin.

## 2. Verification (run before reviewing)

1. Find the verification commands in AGENTS.md (§1). Repos set up with `generate-project-context` or `setup-guardrails-python` have a single aggregate command there (usually `./scripts/check.sh`). If there is an aggregate command, run only that one. Otherwise run each test / lint / type-check / format-check / build command you found.
2. **Only run commands that check. Never run commands that change state**: deploy, release, publish, migrate, seed, db reset, `install`/`add`, `--fix`, `--write`, `format` without a check flag, `git` commands other than read-only ones, anything that pushes or calls production services. If you cannot tell whether a command is read-only, do not run it — list it under Verification as "not run (ambiguous)".
3. Run them from the repo root. If a command takes very long or hangs, stop it and say so.
4. **If AGENTS.md lists no verification commands, do not guess or auto-detect them.** Write "No verification commands found in AGENTS.md — nothing was run" under Verification and continue with the review. Do not ask the user.
5. Use the results as evidence: a test that fails because of the diff is a finding (usually Critical); a pre-existing failure unrelated to the diff is mentioned under Verification, not as a finding.
6. **Semgrep (optional)**: unless the `Code review` section disables it, if the `semgrep` CLI is on PATH run `semgrep scan --config p/default --metrics=off --quiet <changed files>` (not `--config auto`: it refuses to run with metrics off); else, if Semgrep MCP tools are available in this session, use them on the changed files; else write "Semgrep not available — skipped". Treat Semgrep results as candidate findings: they still go through the precision rules (`review-report` §1) and the verifier.

## 3. What to pass to the personas

Every persona spawned by a review skill receives, verbatim: the `Code review` section of AGENTS.md (if any) and the effective limits (`Max Optional`, `Max Nits`, defaults applied), so they can apply `review-report` §1 without reading this skill.

## 4. The spec, if the change has one

Repos that use Spec-Driven Development keep one directory per work item in `docs/specs/<YYYYMMDD>-<type>-<name>/` (`spec.md`, `plan.md`, `tasks.md`). When the change belongs to one of them, **the spec is the task**, and the review checks the code against it.

1. **Find it.** The change belongs to a work item if any of these is true, in this order:
   - the diff touches its `tasks.md`;
   - the branch name contains the item's `<type>-<name>`;
   - a commit message names the directory.

   If several match, or the match is doubtful, list the candidates under Verification and use none. If none matches, review against the task inferred from the branch and commits, as usual.
2. **Read it:** `spec.md`, plus `plan.md` and `tasks.md` if they exist, and the "Principios innegociables" (non-negotiable principles) section of `docs/ARCHITECTURE.md` if it exists. Note each artifact's `status:` from its frontmatter.
3. **Pass to every persona**, verbatim: the paths of those files and this instruction:

   > The change implements the spec at `<path>`. Read it. Check, for the parts of the spec this change touches:
   > - each acceptance criterion is implemented and has a test that would fail without it;
   > - for the security section, the negative tests it lists exist;
   > - nothing listed under "Fuera de alcance" (out of scope) was built;
   > - every task marked `[x]` in `tasks.md` is actually done in the code;
   > - the change does not break a principle of `docs/ARCHITECTURE.md`.
   >
   > A criterion or `[x]` task with no implementation, a missing negative test, an out-of-scope addition, or a broken principle is at least **Required** (`Source: spec`). Do not report criteria that belong to tasks still unchecked: they are pending work, not defects.
4. **In the report**, add one line to the Summary: `Spec: <path> (spec <status>, plan <status>) — <N>/<M> acceptance criteria covered by this change`. If the spec or plan is not `aprobada`, say so; it is information, not a finding.
