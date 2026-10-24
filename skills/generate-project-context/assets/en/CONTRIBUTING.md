<!--
TEMPLATE for CONTRIBUTING.md (at the repository root)
How to use it:
- Fill in the <placeholders>, delete these comments and adapt the examples.
- This document is for the WHOLE team, whether they use AI or not: it describes the PROCESS (how a change is proposed, reviewed and merged).
- Don't repeat what already lives elsewhere: architecture and principles → docs/ARCHITECTURE.md; agent instructions → AGENTS.md; tool configuration → pyproject.toml.
- If a rule can be automated (formatting, lint, types, secrets), automate it and only mention it here.
-->

# Contributing to <project-name>

Thanks for contributing. This document explains how to set up your environment, how to propose changes and what is expected of a PR. It applies equally whether you code by hand, with AI assistants or with autonomous agents.

**Read first:**
- [`README.md`](README.md): what the project is.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): structure, layers and **non-negotiable principles**.
- [`docs/decisions/`](docs/decisions/README.md): decisions that have been made and why.
- [`AGENTS.md`](AGENTS.md): instructions for AI agents (also useful for humans: it summarizes commands and boundaries).

## 1. Setting up your environment

Requirements: [uv](https://docs.astral.sh/uv/) and git. uv installs the Python version set in `.python-version`.

```bash
git clone <repo-url>
cd <repo>
uv sync                     # creates .venv and installs dependencies from uv.lock
uv tool install prek        # or pre-commit
prek install                # enables the pre-commit hooks
cp .env.example .env        # and fill in the values (never committed)
./scripts/check.sh          # must finish green
```

If `./scripts/check.sh` does not pass on a clean clone, that's a bug: open an issue.

## 2. Common commands

| Action | Command |
|---|---|
| Full verification (same as CI) | `./scripts/check.sh` |
| Tests | `uv run pytest` |
| A single test | `uv run pytest tests/unit/test_x.py::test_y` |
| Format | `uv run ruff format .` |
| Lint with autofix | `uv run ruff check --fix .` |
| Types | `uv run mypy` |
| Add a dependency | `uv add <package>` (dev: `uv add --dev <package>`) |

Don't use `pip install` and don't edit `uv.lock` by hand.

## 3. Before you start

- **Small changes** (obvious bug, typo, local refactor): go ahead, straight to a PR.
- **Medium or large changes** (new feature, several modules, public API): open or assign yourself an issue first and write a short spec in `docs/specs/<feature>.md` (goal, requirements, out of scope and how it is verified end to end).
- **Architecture changes** (new layer, change of persistence, new structural dependency, breaking a principle): need a **decision record** in `docs/decisions/`, accepted before implementation (the `record-decision` skill drafts it).

Before implementing, check your plan against the non-negotiable principles in `docs/ARCHITECTURE.md`.

## 4. Git workflow

- Branch off `main`, named `<type>/<short-description>`: `feat/export-csv`, `fix/booking-timezone`, `docs/cache-decision`.
- Nobody pushes directly to `main`; everything goes through a PR.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Small commits that make sense on their own. You can reorder or squash yours before opening the PR.
- Keep your branch up to date with `main` using <rebase | merge> (team policy: <pick one>).
- Don't skip the hooks (`--no-verify`). If a hook fails for no reason, fix it or open an issue.

## 5. Code quality

Tools check this; here is just a summary:

- **Formatting and lint:** ruff, configured in `pyproject.toml`.
- **Types:** `mypy --strict` on `src/`. Public functions are typed.
- **Tests:** every behavior change comes with tests. For bugs, first a test that reproduces the failure (red), then the fix (green).
- **Coverage:** CI requires at least <N>%. Don't lower coverage without justifying it.
- **Architecture:** dependency rules between layers are checked with import-linter.
- **Secrets:** gitleaks blocks the commit if it finds one. Remove the secret; don't silence the check.

Things tools don't check and that reviewers look at:
- Clear names, consistent with the glossary in `AGENTS.md`.
- No dead code, no "just in case" abstractions and no unnecessary dependencies.
- Useful error messages; no swallowed generic exceptions.

## 6. Using AI

You may use AI assistants and agents (Claude Code, Codex, Copilot, Cursor…). The same rules apply as for hand-written code, plus these:

1. **You are accountable for everything you submit.** Whoever opens the PR must understand and be able to explain every line, no matter who or what wrote it. "The AI generated it" is not an answer in a review.
2. **Review the diffs before asking for review**, especially in `tests/`: agents sometimes weaken or delete tests to make them pass. No PR may remove or relax a test without explaining why.
3. **Small PRs.** AI generating code quickly does not justify PRs with thousands of lines. Guideline: < <400> changed lines (excluding generated files); if it's more, split it.
4. **Verify, don't trust.** Green CI is necessary but not sufficient: test the change manually when it affects visible behavior.
5. **Dependencies suggested by AI:** check them (that they exist, are maintained and are needed) before adding them. Watch out for packages with names similar to real ones.
6. **Data and secrets:** don't paste secrets, personal data or customer data into external AI tools. Use only approved tools: <list or link to policy>.
7. **If an agent makes a recurring mistake**, improve the system in the same PR or a separate one: ideally a lint rule, test or hook; if that's not possible, a line in `AGENTS.md`.
8. **Agent configuration files:**
   - Versioned and reviewed like code: `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/`, `.claude/agents/`, `.mcp.json`.
   - Personal and **not** versioned: `CLAUDE.local.md`, `.claude/settings.local.json`.
9. **Transparency:** state in the PR description if a significant part was generated by an agent (the PR template has a checkbox). Automatic co-author trailers in commits (`Co-Authored-By`) are <allowed | not allowed>.

## 7. Pull requests

**Before opening it:**
- [ ] `./scripts/check.sh` green locally.
- [ ] New or updated tests for the change.
- [ ] Documentation updated in the same PR if applicable: `README.md`, `docs/ARCHITECTURE.md`, `docs/decisions/`, `AGENTS.md`, `.env.example`.
- [ ] No unrelated changes (mass reformatting, drive-by renames).

**Description** (requested by `.github/pull_request_template.md`):
- What changes and why; link to the issue, spec or decision.
- How it was verified (tests, manual testing, screenshots).
- Risks, migrations or deployment steps.
- Relevant AI use.

**Review:**
- At least <1> approval from someone other than the author. Changes in <sensitive areas: auth, payments, migrations, CI> require approval from <@team/CODEOWNERS>.
- An automated AI review is welcome as support, but it **does not replace** human review.
- The author resolves or replies to every comment; the commenter marks the conversation as resolved.
- Merge using <squash | merge commit | rebase> once CI is green and the PR is approved.

## 8. Documentation

| What changes | What to update |
|---|---|
| Structure, layers, integrations, principles | `docs/ARCHITECTURE.md` (principles require a decision record) |
| An architecture choice, a business rule or a discarded approach | New record in `docs/decisions/` (accepted records are not edited: a new one supersedes them) |
| Commands, tools or known pitfalls | `AGENTS.md` |
| Installation or usage | `README.md` |
| Environment variables | `.env.example` and `config.py` |

Anything decided in meetings, chats or issues that affects the code is brought into the repository. What isn't in the repo doesn't exist for agents, nor for whoever joins six months from now.

## 9. Bugs and proposals

- **Bugs:** an issue with steps to reproduce, expected vs. actual behavior, version or commit and relevant logs (no secrets).
- **Proposals:** an issue describing the problem before the solution.
- **Security vulnerabilities:** don't open a public issue; write to <contact> (see `SECURITY.md`).

## 10. Questions

Ask in <Slack/Discord channel / issue labeled `question`>. If the answer should be documented, add it to the relevant document in a PR.
