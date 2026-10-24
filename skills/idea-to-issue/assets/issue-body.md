<!--
TEMPLATE for the body of the issue (idea-to-issue). Write it in the project language, headings included
(Spanish: Problema, Plazo máximo, Fuera de alcance, Mapa de ejemplos, Supuestos, Tareas). Delete this comment.
The note is about 10 lines. Sections still empty are left with "—" until their step.
-->
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
