# Tasks: <feature name>

<!-- Small tasks, in dependency order. [P] = can be done in parallel with the previous one.
Each task starts with its ID (T<n>., W<n>. in wrap-up) and states which files it touches and how it is verified.
The implement agent marks [x] with the task-done skill, only when the verification passes. -->

## Phase 1: <name>

- [ ] T1. <task> — files: `<path>` — verification: <test or command>
- [ ] T2. [P] <task> — files: `<path>` — verification: <test or command>

## Phase 2: <name>

- [ ] T3. <task> — files: `<path>` — verification: <test or command>

## Wrap-up

- [ ] W1. Every acceptance criterion of the spec has a passing test — verification: <command that runs those tests>
- [ ] W2. The verification command from AGENTS.md is green — verification: <verification command>
