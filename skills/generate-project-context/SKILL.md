---
name: generate-project-context
description: Creates or updates a project's context files (AGENTS.md, docs/ARCHITECTURE.md with its non-negotiable principles, CONTRIBUTING.md, ADRs, SECURITY.md and PR template) through a guided interview. Use it when starting a project, when adopting agents in an existing project, or when asked for a "constitution", project principles, architecture rules or documentation for agents.
---

# Project context

Help the person decide and write down the project's stable rules, each in the file where it belongs. **The person makes the decisions**: you read, propose concrete options and draft.

It replaces Spec Kit's `constitution.md`. All of its content has a better home:

| Content | File | Read by |
|---|---|---|
| Stack, layers, dependency rules, **non-negotiable principles**, glossary | `docs/ARCHITECTURE.md` | People and agents; `spec-to-plan` and `review-spec` check the principles |
| Quality, branches, commits, PRs, review, AI usage | `CONTRIBUTING.md` | People (and agents, via link) |
| The why of each structural decision and the discarded alternatives | `docs/adr/NNNN-*.md` | Both, on demand |
| Commands, boundaries, non-obvious conventions, documentation map | `AGENTS.md` (+ `CLAUDE.md` with `@AGENTS.md`) | Agents, in **every** session |
| How to report vulnerabilities, agent policy | `SECURITY.md` | People |

Templates in `assets/en/` (English) and `assets/es/` (Spanish). Use the language the project is documented in; ask if it is not clear. Each template explains in its opening comment how to fill it in.

## Rules

- **Do not duplicate.** If something is already in `pyproject.toml`, in CI or in a linter, link to it; do not copy it. If a principle appears in two files, they will end up contradicting each other: principles live only in `ARCHITECTURE.md`.
- **Short `AGENTS.md`:** under 150 lines. It is a map that links; it does not contain. For each line: "if I remove it, would the agent get it wrong?". If not, out.
- **What can be checked with a tool is checked with a tool.** For each principle, ask how it is verified (lint, import-linter, test, CI, review) and note it in its column.
- **Nothing volatile:** no sprint status or TODOs. Those go in the tracker or in `docs/plans/`.
- Show each file in full (or the diff, if it already exists) and write only after the person approves it.

## Process

### 1. Read the project

Before asking anything, read: manifests (`pyproject.toml`, `package.json`, `go.mod`…), `README.md`, any existing context files, `.github/workflows/`, linter config and the folder structure. Use what you find to **propose answers** instead of asking open questions.

Decide the mode and tell the person:

- **Greenfield** (no code or almost none): `ARCHITECTURE.md` is **prescriptive**, how it will be.
- **Brownfield**: `ARCHITECTURE.md` is **descriptive**, how it is today. The ideal goes into ADRs and the tools' ratchets. If context files already exist, only ask about the gaps and propose diffs.
- **Migration from a `constitution.md`**: distribute its content according to the table above and propose deleting it or reducing it to a link.

### 2. Interview by rounds

One category at a time. For each question, offer concrete options (A, B, "leave open", "other"). If the files already answer it, ask for confirmation instead of asking. If a category does not apply (e.g. there is no database), skip it and say so. At the end of each round, summarize what was decided.

| Round | What is decided | Destination |
|---|---|---|
| 1. Purpose | What the project is and what is out; type (app, service, library, CLI) | `ARCHITECTURE.md` §1, `README.md` |
| 2. Stack and architecture | Language, framework, persistence, infrastructure; layers or modules and what may import what | `ARCHITECTURE.md` §2–4, one ADR per structural decision |
| 3. Non-negotiable principles | 5–10 stable, verifiable rules: why, and how each one is checked | `ARCHITECTURE.md` §5 |
| 4. Quality | Test first or after, minimum coverage, typing, what is never mocked | `CONTRIBUTING.md` §5; if non-negotiable, also a principle |
| 5. Security | Authentication, sensitive data, input validation, regulatory compliance | `ARCHITECTURE.md` §10, `SECURITY.md` |
| 6. Process | Branches, Conventional Commits, merge or squash, approvals, PR size, allowed AI tools | `CONTRIBUTING.md` §4, §6–7 |
| 7. Dependencies | Policy for adding them, banned libraries, build or buy | Principle (if non-negotiable) or `CONTRIBUTING.md` |
| 8. For the agent | Commands (the verification one is mandatory), non-obvious conventions, critical or fragile areas (brownfield), boundaries (always / ask / never) | `AGENTS.md` |

In round 8, the **verification command** is the contract with the other skills (`plan-to-tasks`, `implement`, review). If it does not exist, propose `setup-guardrails-python` (or an equivalent for the language) or leave it as an open question in `AGENTS.md`. If the project will use `review-prepush` or `review-pr`, also offer the optional `## Code review` section (template in `review-context/assets/AGENTS-code-review.md`): base branch, high-risk paths, report language…

### 3. Draft and write

Order: `ARCHITECTURE.md` → ADRs → `CONTRIBUTING.md` → `SECURITY.md` → `AGENTS.md`. `AGENTS.md` goes last because it links to all of them.

- Start from the template in `assets/`. Delete the sections that do not apply yet; do not leave them empty.
- ADRs: copy `ADR.md` as `docs/adr/0000-template.md` (`0000-plantilla.md` in Spanish) and `adr-README.md` as `docs/adr/README.md`. Create one ADR per structural decision from rounds 2–3. Brownfield: only 3–5 retroactive ones, for what is most questioned, with the discarded alternatives.
- `AGENTS.md` must include:
  - the "Planning" line: check the plan against the principles in `docs/ARCHITECTURE.md` before implementing;
  - a link to `CONTRIBUTING.md` for the process.
- `CLAUDE.md` contains only `@AGENTS.md`, unless it already has content. In that case, propose moving it into `AGENTS.md`.
- `pull_request_template.md` goes in `.github/`. Offer it, do not impose it.

### 4. Wrap-up

List the files created or changed and the questions left open. Remind the person:

- `AGENTS.md` is reviewed monthly and pruned, especially when changing models.
- `ARCHITECTURE.md` is checked against the code every quarter.
- Every mistake the agent repeats becomes a tool rule or, as a last resort, a line under "Known pitfalls".
