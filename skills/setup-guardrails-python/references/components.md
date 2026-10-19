# What each component protects against

Summary to decide what to include. The full explanation is in `docs/arnes/` of the skills repository.

| Component | File | Protects against | When? |
|---|---|---|---|
| `scripts/check.sh` | `files/scripts/check.sh` | "Done" meaning different things to the person, the agent and CI | Always. It is the contract with the other skills |
| ruff (`S`, `PLE`) | `snippets/pyproject.toml` | Typical insecure code (`shell=True`, SQL built from strings, `verify=False`), bidirectional Unicode | Always. Replaces bandit |
| mypy `--strict` | `snippets/pyproject.toml` | Type errors the agent does not see | Always. Brownfield with a ratchet |
| pytest + coverage | `snippets/pyproject.toml` | The agent accepting untested code | Always. Brownfield: threshold = current coverage |
| uv cooldown | `snippets/pyproject.toml` (`[tool.uv]`) | Freshly published malicious versions | Always, before the first `uv add` |
| import-linter | `snippets/pyproject.toml` (commented out) | The agent breaking the layers | When there are layers or modules with rules |
| pre-commit (prek) | `files/.pre-commit-config.yaml` | Mistakes reaching the history | Always |
| gitleaks | pre-commit + `ci.yml` | Secrets in commits; agents leak twice as many | Always |
| Hidden Unicode | `files/scripts/check_hidden_unicode.py` | Invisible instructions in `AGENTS.md` and rules (*Rules File Backdoor*) | Always |
| zizmor | pre-commit + `security.yml` | Injectable CI workflows or workflows with excessive permissions | If there are GitHub Actions |
| CI | `files/.github/workflows/ci.yml` | Local hooks being skipped; it is the final authority | Always |
| Security in CI | `files/.github/workflows/security.yml` | CVEs in dependencies (pip-audit), OWASP patterns (Semgrep), unjustified `noqa: S` | Always. Semgrep only counts new findings, so it works in brownfield |
| Dependabot | `files/.github/dependabot.yml` | Outdated or vulnerable dependencies | From the first dependency |
| CODEOWNERS | `files/.github/CODEOWNERS` | Someone (or an agent) loosening the harness, weakening tests or adding dependencies without review | If there is more than one person |
| Claude Code permissions | `files/.claude/settings.json` | The agent reading secrets, using `pip`, pushing or editing the harness | If Claude Code is used |
| Stop hook | `files/.claude/hooks/check-on-stop.sh` | The agent finishing with `check.sh` red | If Claude Code is used |
| Package hook | `files/.claude/hooks/check_new_package.py` | Hallucinated packages (*slopsquatting*) or packages less than 90 days old | If Claude Code is used |
| git-cliff + commitizen | `files/cliff.toml`, `release.yml`, pre-commit | Unreadable commits and manual changelog | Before the first published release |
