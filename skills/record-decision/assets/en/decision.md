<!--
TEMPLATE → docs/decisions/NNNN-title-in-kebab-case.md
Copy it with the next free number (check_decisions.py --next). Numbers are never reused.
Short: these four sections, a few lines each. Delete this comment.
-->
---
id: D-NNNN
title: <the decision in a few words>
type: architecture        # architecture | rule | discarded
status: proposed          # proposed | accepted | superseded | obsolete. Only a person marks it accepted.
date: YYYY-MM-DD
affects: [src/billing/]   # modules or paths this decision constrains; agents filter on it
supersedes: null          # D-XXXX if it replaces another decision
superseded_by: null       # D-YYYY, set when a newer decision replaces this one
issue: null               # "#42" or a URL
---

# D-NNNN: <the decision in a few words>

## Context

<!-- What forced a choice: the problem, the constraints, the facts. Not opinions. -->

## Decision

<!-- Active voice, concrete: "Refunds are full when cancelling more than 1 h ahead". For a discarded
approach: what was tried, what happened, and "we do not use X". -->

## Alternatives discarded

<!-- The most valuable section: it stops people and agents from proposing them again. -->

- <option>: <concrete reason>

## How it is enforced

<!-- Test (and its name), lint rule, architecture test, CI check, or "not automated". -->
