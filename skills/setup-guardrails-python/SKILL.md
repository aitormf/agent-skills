---
name: setup-guardrails-python
description: Installs or completes the deterministic guardrails of a Python repository (uv, ruff, mypy, pytest, scripts/check.sh, pre-commit, gitleaks, CI, security workflow, Dependabot, CODEOWNERS and Claude Code permissions/hooks), in new or existing projects. Use it when asked to prepare the harness, set up the guardrails, configure CI or pre-commit, or harden the security of a Python repo.
kind: skill
---

# Guardrails for a Python repository

Install the controls that always run, with or without an agent. Copy files from `assets/` instead of writing them, and use judgement only to merge with what already exists and to decide what goes in with a ratchet.

- `assets/files/`: copied as is into the repo, keeping their paths.
- `assets/snippets/`: **merged** into files the repo already has (`pyproject.toml`, `.gitignore`, `AGENTS.md`).
- `references/components.md`: what each component protects against and when it is worth it. Read it if the user asks why or is unsure whether to include something.

Out of scope: the content of `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `docs/decisions/`, specs and review. In `AGENTS.md` you only touch the sections from `assets/snippets/AGENTS-guardrails.md`.

## Rules

- **Never overwrite** an existing file. If it clashes, merge and show the diff before writing.
- **Copy the assets literally.** Do not "improve" them or rewrite them from memory. If something does not fit, adapt it after copying and say what you changed.
- **The cooldown (`[tool.uv] exclude-newer`) goes before any `uv add`.** If it is added afterwards, the lower bounds uv writes may be newer than the cooldown and resolution fails.
- Do not push, do not change GitHub settings and do not rotate secrets: a person does that. At the end, give them the list.
- One phase at a time: apply, verify and ask before moving to the next.

## Process

### 1. Diagnosis (read-only)

Find out and summarize in a table:

- **Type:** greenfield (no code or almost none) or brownfield.
- **Dependencies:** uv, Poetry, Pipenv, `requirements*.txt`… and the uv version (`uv --version`; the relative cooldown needs ≥ 0.9.17).
- **Tests:** do they exist?, do they pass?, how long do they take?, current coverage?
- **What already exists** of each component: `scripts/check.sh` (or `make check`, `just check`), `.pre-commit-config.yaml`, `.github/workflows/`, `dependabot.yml`, `CODEOWNERS`, `.claude/settings.json`, ruff and mypy config.
- **Package:** name of the package in `src/` (for CODEOWNERS and import-linter).
- **Tools:** `jq` and `prek` (or `pre-commit`) installed.
- **Agents:** which coding agents the team uses (Claude Code, Codex, OpenCode). Each one has its own config in `assets/files/`.

Brownfield: run `gitleaks git . --redact` if available. If it finds secrets, **stop** and warn: they must be rotated before going on. Removing them from history is not enough.

### 2. Plan

Propose which phases to apply and ask. Default: phases 1 and 2. Phase 3 only for what the user asks for. Also ask:

- Type checker: mypy (default), pyright or ty.
- If there are already layers: enable import-linter?
- Conventional Commits? If not, comment out the `commitizen` hook.

### 3. Phase 1: base

1. **uv.** If there is no project: `uv init --package <name>` and `uv python pin 3.13`. If it comes from `requirements.txt`: `uv init --bare` and `uv add -r requirements.txt`. If it comes from Poetry or Pipenv: `uvx migrate-to-uv`. Check that the tests pass just as before.
2. **`pyproject.toml`.** Merge `assets/snippets/pyproject.toml`, including `[tool.uv]`, **before** step 3. Brownfield:
   - `fail_under` = the current coverage.
   - mypy `strict` only on new modules, with `[[tool.mypy.overrides]] ignore_errors = true` for the legacy ones.
3. **Dev dependencies:** `uv add --dev pytest pytest-cov ruff mypy` (plus `import-linter` if enabled).
4. **Copy the files** without overwriting:
   ```bash
   rsync -a --ignore-existing <skill>/assets/files/ <repo>/
   ```
   For each file that already existed, merge by hand and show the diff.
5. **`scripts/check.sh`.** Keep only the lines for what the repo uses. Brownfield: if there are broken tests, mark them with `@pytest.mark.skip(reason="…")`, propose an issue for each one, and never leave the suite red.
6. **Brownfield, lint with a ratchet:**
   - `uv run ruff check --add-noqa`, and explain that new code has to comply.
   - If `ruff format` changes many files, propose an **isolated formatting-only PR** and add the commit to `.git-blame-ignore-revs`.
7. **`.gitignore`.** Merge `assets/snippets/gitignore`. Create `.env.example` with the names of the variables the code uses, without values.
8. **Pre-commit:** `prek autoupdate` (fills in the `rev`s), `prek install` and `prek run --all-files`. Comment out the hooks for whatever is not used.
9. **`AGENTS.md`.** Add the `## Commands` section from `assets/snippets/AGENTS-guardrails.md`, or merge it if it already exists (if `AGENTS.md` is in Spanish, translate the section and title it `## Comandos`). It is the contract with the other skills: the verification command has to appear there.

**Verification:** `uv sync && ./scripts/check.sh` is green. Show the user the output.

### 4. Phase 2: agent and supply chain

1. The agent config already comes in `assets/files/`. Keep only the files for the agents the team uses and delete the rest:
   - **Claude Code:** `.claude/settings.json` (permissions and hooks) and `.claude/hooks/`. If the repo had its own `settings.json`, merge `permissions` and `hooks` without losing what was there.
   - **Codex:** `.codex/rules/guardrails.rules` (asks before a forced push). It only loads once the person trusts the project's `.codex/` layer.
   - **OpenCode:** `opencode.json` (asks before a forced push). If the repo already had one, merge `permission.bash`.
   - Make the hooks and scripts executable: `chmod +x scripts/*.sh .claude/hooks/*`.
   - Brownfield: ask whether there are critical areas where broad write permissions should not be granted.
2. Add the `## Security` section from `assets/snippets/AGENTS-guardrails.md` to `AGENTS.md` (`## Seguridad`, translated, if `AGENTS.md` is in Spanish).
3. `CODEOWNERS`: replace the `@org/...` teams and the sensitive paths. Ask for the teams; do not make them up.
4. Check the hooks:
   ```bash
   echo '{"tool_input":{"command":"uv add package-that-does-not-exist-xyz"}}' | uv run python .claude/hooks/check_new_package.py   # must exit with 2
   uv run python scripts/check_hidden_unicode.py AGENTS.md CLAUDE.md                                                            # must exit with 0
   echo '{"tool_input":{"command":"git push --force"}}' | uv run python .claude/hooks/ask_on_force_push.py                       # must print "permissionDecision": "ask"
   codex execpolicy check --rules .codex/rules/guardrails.rules -- git push --force                                             # Codex: must print "decision": "prompt"
   ```

### 5. Phase 3: when needed (only what is asked for)

- **import-linter:** uncomment the snippet's block. The contracts come from the non-negotiable principles of `ARCHITECTURE.md`; if it does not exist, ask for the layers. Enable its line in `check.sh` and its hook. Brownfield: list the current violations in `ignore_imports`.
- **Changelog:** `cliff.toml` and `release.yml` are already copied. If there is *squash merge*, validate the PR title in CI.
- **CodeQL:** uncomment the job in `security.yml`. Only in public repos or with GitHub Advanced Security.

### 6. Wrap-up

Summarize what was installed, what was left out and why. Then give the user **the list of what they have to do by hand**:

- [ ] Protect `main`: PR required, ≥ 1 approval, *Require review from Code Owners*, no bypass for administrators.
- [ ] Required checks: `check`, `secrets`, `dependencies`, `sast`, `workflows`, `guardrails`.
- [ ] *Settings → Actions*: *Require approval for all external contributors*.
- [ ] Pin the gitleaks image in `ci.yml` and the actions to a SHA.
- [ ] Rotate any secret found during the diagnosis.
- [ ] Check `/permissions` and `/hooks` in Claude Code; trust the project's `.codex/` layer in Codex.
- [ ] **Acid test:** in a clean clone, ask the agent to *"run the tests"*. It has to work on the first try.
