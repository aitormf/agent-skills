<!--
  Optional AGENTS.md section for the review skills (review-prepush, review-pr).
  Copy what you need and delete these comments.

  NOTE: AGENTS.md is loaded in EVERY agent session, not only in reviews.
  Keep this section short (10–20 lines).

  Verification commands do NOT go here: the review reads them from the `## Commands` section
  of AGENTS.md, the same one implement and plan-to-tasks use. If there is an aggregate command
  (`./scripts/check.sh`, `make check`), it runs only that one. It only runs commands that check:
  never deploy, migrations, install, --fix or --write.
-->

## Code review
<!-- All optional. Anything you leave out uses the default shown. -->
- Base branch: `main`                     <!-- default: the remote's default branch -->
- Output language: Spanish                <!-- default: English. Headings and labels are always in English -->
- High-risk paths: `src/auth/**`, `src/billing/**`, `migrations/**`
  <!-- force tier 2 in review-pr and deeper security review.
       default: paths containing auth, session, token, payment, billing, migration, secret, webhook, admin… -->
- Always flag: hand-built SQL queries; HTTP calls without a timeout
- Ignore: `src/generated/**`, `*.snap`, formatting changes in `docs/`
- Conventions the linter does not cover: domain errors are raised as `DomainError`, never `Error`
- Known non-issues:                       <!-- findings that keep coming back and are not problems here, each with its reason.
                                               The finding-verifier refutes them while the reason still holds -->
  - `subprocess` with `shell=True` in `scripts/dev/**`: developer-only scripts, never fed user input
  - Missing auth check in `src/health.py`: the health endpoint is public by design (D-0012)
- Max Optional: 3                          <!-- how many Optional findings are shown (highest impact, lowest cost). 0 = none -->
- Max Nits: 3                              <!-- same for Nits -->
- Semgrep: no                              <!-- "no" if your verification command already runs it (setup-guardrails-python does it in CI) -->
