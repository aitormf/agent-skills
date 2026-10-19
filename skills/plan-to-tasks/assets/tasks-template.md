# Tasks: <feature name>

<!-- Small tasks, in dependency order. [P] = can be done in parallel with the previous one.
Each task states which files it touches and how it is verified. The implement agent marks [x] when it finishes them. -->

## Phase 1: <name>

- [ ] T1. <task> — files: `<path>` — verification: <test or command>
- [ ] T2. [P] <task> — files: `<path>` — verification: <test or command>

## Phase 2: <name>

- [ ] T3. <task> — files: `<path>` — verification: <test or command>

## Wrap-up

- [ ] Every acceptance criterion of the spec has a passing test.
- [ ] The verification command from AGENTS.md is green.
