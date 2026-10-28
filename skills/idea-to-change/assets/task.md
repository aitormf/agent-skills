---
id: T1
title: <what this task does, in a few words>
status: todo            # todo | doing | done. task-done sets done; nobody edits it by hand.
depends_on: []          # tasks that must be merged first: [T1, T3]. What this one blocks is computed.
examples: [E1]          # the examples of the map this task's tests cover; [] for a step without examples
verification: <single-test command from AGENTS.md, for this task's tests>
---
<!--
TEMPLATE for docs/changes/<change>/tasks/T<n>-<slug>.md (idea-to-change, plan-to-tasks). One task, one branch
(<change>/T<n>), one PR. Write it in the project language; the frontmatter keys stay in English. Add
`level: A` to the frontmatter for a delicate task (money, personal data): implement stops at its red tests.
Delete this comment.
-->
**Purpose:** <one sentence: new behaviour, or refactor, or preparation; never two of them>

**In:** <what this task changes>

**Not in:** <what is left for other tasks>

**Flag:** <name of the feature flag and its default (off), or "none">
