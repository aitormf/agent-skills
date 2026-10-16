<!--
TEMPLATE for SECURITY.md (at the root or in .github/)
GitHub shows it in the "Security" tab and when issues are opened.
Fill in the <placeholders> and delete these comments.
If the repository is private and internal, simplify it: internal reporting channel and secrets/AI policy.
-->

# Security policy

## Supported versions

| Version | Security support |
|---|---|
| <main branch / latest version x.y> | ✅ |
| < x.y | ❌ |

## Reporting a vulnerability

**Do not open a public issue, PR or discussion.**

Use one of these channels:

- **GitHub Private Vulnerability Reporting:** *Security* tab → *Report a vulnerability* (preferred).
- **Email:** <security@your-domain.com> <!-- optional: PGP key for encryption -->

If you can, include:

- A description of the problem and its impact.
- Steps to reproduce or a proof of concept.
- The affected version or commit.
- Whether it is already public or known to third parties.

### What to expect

| Step | Target time |
|---|---|
| Acknowledgement | <2> business days |
| Initial assessment and severity | <5> business days |
| Fix or mitigation plan | By severity: critical < <7> days, high < <30> days |
| Coordinated disclosure | After the fix is released, agreed with the reporter |

We will credit you in the security advisory unless you prefer to remain anonymous.

## Scope

**In scope:** the code in this repository and its dependencies as used here.
**Out of scope:** <third-party services, social engineering, volumetric DoS, automated scanner reports without a demonstrated exploit>.

## Project security practices

For contributors (humans and AI agents):

- **Secrets:** never in the repository. They go in `.env` (ignored by git) or in the <name> secrets manager. `.env.example` documents the variables without values. **gitleaks** runs in pre-commit and CI; it is not skipped (`--no-verify`).
- **If a secret leaks:** rotate it **immediately** and notify <contact/channel>. Removing it from history is not enough.
- **Dependencies:** Dependabot/Renovate flag vulnerabilities; new dependencies are justified in the PR. Check that the package exists and is the one you think it is (watch out for similar names, *typosquatting*).
- **Static analysis:** ruff security rules (`S`, equivalent to bandit) in `scripts/check.sh` and CI.
- **Review:** changes to <auth, payments, permissions, cryptography, migrations> require approval from <@security-team / CODEOWNERS>.

### AI agents

- Secrets, personal data and customer data are not pasted into unapproved AI tools. Approved tools: <list or link to policy>.
- Agents work with scoped permissions (`.claude/settings.json`) and without access to `.env`; broader personal permissions go in `.claude/settings.local.json` (outside git).
- We avoid giving a single agent all three capabilities of the *lethal trifecta* (Simon Willison): access to private data, exposure to untrusted content and the ability to communicate externally. Check this when adding MCP servers (`.mcp.json`, always without credentials).
- AI-generated code goes through exactly the same checks and reviews as hand-written code.
