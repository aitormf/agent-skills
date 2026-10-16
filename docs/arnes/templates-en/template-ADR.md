<!--
ADR TEMPLATE → docs/adr/0000-template.md
Based on the Michael Nygard / MADR format, with extras that help AI agents.

How to use it:
- Copy it as docs/adr/NNNN-title-in-kebab-case.md (sequential numbering, numbers are never reused).
- One ADR = one decision. Short: 1-2 pages at most.
- Write the decision in the active voice ("We use X"), not "we could consider".
- An accepted ADR is NOT edited (except for typos or links): if the decision changes, create a new one
  that supersedes it and mark this one as "Superseded by ADR-NNNN".
- The rejected alternatives section is the most valuable one: it stops humans and agents from proposing them again.
- Add a line to the index in docs/adr/README.md.
-->

---
id: ADR-NNNN
title: <Decision in a few words>
status: proposed             # proposed | accepted | rejected | deprecated | superseded
date: YYYY-MM-DD
owners: ["@person", "@team"]
tags: [persistence, api]     # helps an agent find the relevant ADRs
supersedes: null             # ADR-XXXX if it replaces another one
superseded_by: null          # ADR-YYYY once it becomes obsolete
---

# ADR-NNNN: <Decision in a few words>

## Context

<!-- What problem or need forces a decision. Forces at play: requirements, technical, business
and team constraints, deadlines. Facts, not opinions. -->

## Decision

<!-- The decision in the active voice, concrete. What is done and, if relevant, where it applies. -->

We use <X> for <Y>.

## Alternatives considered

| Alternative | Why it was rejected |
|---|---|
| <Option A> | <concrete reason> |
| <Option B> | <concrete reason> |
| Do nothing | <reason> |

## Consequences

**Positive**
- <benefit>

**Negative / accepted costs**
- <cost, debt or limitation we consciously accept>

**Risks and mitigations**
- <risk> → <mitigation>

## Compliance

<!-- How it is enforced. If it can be automated, better: lint, import-linter contract, test, hook, CI. -->

- Automated check: <e.g. "Pure domain" contract in import-linter / ruff rule / architecture test>
- If it affects a non-negotiable principle: updated in `docs/ARCHITECTURE.md` (section 5).
- Instruction for agents, if needed: <line added to AGENTS.md or "not needed">

## AI context (optional)

<!-- Fill in if an agent proposed or significantly influenced the decision. -->

- Agent / model: <e.g. Claude Code / claude-opus-5-5>
- Prompt or task summary: <…>
- Human review: <who, and what they validated>

## References

- <issues, specs, PRs, documentation, benchmarks>
