---
status: open      # open | done. task-done sets done when it ticks the last task.
issue: null       # the GitHub issue this change started from (a number), or null. The PR closes it: Closes #<n>.
---
<!--
TEMPLATE for docs/changes/<branch>/tasks.md (idea-to-change; plan-to-tasks uses the same format).
Write it in the project language, headings included (Spanish: Problema, Plazo máximo, Fuera de alcance,
Mapa de ejemplos, Supuestos, Tareas). Delete this comment. The note is about 10 lines.
Sections still empty are left with "—" until their step.
-->
# <change title>

**Problem:** <what happens today and who cares>

**Appetite:** <how much it is worth investing; if it does not fit, split the idea>

**Out of scope:** <what must not be done even if it looks useful>

## Example map

```
Rule R1: <business rule>
  E1: <concrete input> → <expected result>
  E2: <concrete input> → <expected result>
Rule R2: <business rule>
  E3: <concrete input> → <expected result>
Question: <what is not decided yet> → D-NNNN | options, recommended one marked
```

<!-- Work that is not a rule (infrastructure, refactor, migration): steps instead of rules.
  S1: <step that leaves the project green> → verify with <command> -->

## Assumptions

- <reversible detail with a clear default>

## Tasks

- [ ] T1. <thinnest end-to-end slice> — tests: E1 — verification: <single-test command>
- [ ] W1. Full verification — verification: <verification command from AGENTS.md>
