---
status: open      # open | done. task-done sets done when the last task is done.
issue: null       # the GitHub issue this change started from (a number), or null. The PR of the last task closes it: Closes #<n>.
---
<!--
TEMPLATE for docs/changes/<change>/README.md (idea-to-change; plan-to-tasks uses the same folder).
Write it in the project language, headings included (Spanish: Problema, Plazo máximo, Fuera de alcance,
Mapa de ejemplos, Supuestos, Tareas). Delete this comment. The note is about 10 lines.
Sections still empty are left with "—" until their step. The tasks are files in tasks/ (assets/task.md).
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

One file per task in `tasks/`, each with its branch and PR. Which are ready: the board of `task-done`
(`scripts/board.py`). Do not list them here: the task files are the only source.
