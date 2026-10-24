---
name: idea-to-issue
description: Turns an idea for a feature or change into a GitHub issue ready to implement — a short note (problem, appetite, out of scope), an example map (rules, concrete examples, questions) and a checklist of vertical-slice tasks that name their tests — with the decisions drafted as proposed in docs/decisions/. The default entry point for normal work, with a single human stop at the example map. Use it when someone has an idea, feature, improvement or change to build, wants to open or prepare an issue for it, or asks for an example map. For a full spec.md, use idea-to-spec.
---

# From idea to issue

The default way to go from an idea to code (level B). Everything about the work in progress lives in one GitHub issue: the note, the example map and the tasks. What outlives it goes elsewhere: the why in `docs/decisions/`, the what in the tests.

**One stop for the person:** they review the example map and the decisions, once. Before that you write; after it, the tasks follow without asking again. **Drafts are written, not pasted in the chat:** you write the issue and the records, and give the person a short summary with the link. They read and correct them there.

## Before you start

1. **Level.** If the change is trivial, a bug with a clear cause or a throwaway prototype, say so and propose skipping this skill (a direct prompt, a failing test and the fix, or `debug-root-cause`). If there is real design to decide (several components, contracts, migrations), propose `idea-to-spec` instead. The person decides.
2. **Where it is written.** Check `gh auth status` and that the repo has a GitHub remote. If an issue number is given, work on that issue (`gh issue view <n>`) instead of creating one. Without `gh` or network, see "Without gh".
3. **Read** `AGENTS.md` (the verification and single-test commands, the glossary) and the index `docs/decisions/README.md`. Open the decisions whose *Affects* covers the area the idea touches. If the idea clashes with an accepted one, say so before going on.

## 1. The note

Ask only for what is missing, in one message:

- **Problem:** what happens today and who cares.
- **Appetite:** how much it is worth investing (an afternoon, two days…). If the idea does not fit, propose splitting it into several issues; the person picks the first one.
- **Out of scope:** what you must not do even if it looks useful.

Create the issue with the body from `assets/issue-body.md`, in the project language, with the note filled in and the other sections still empty: `gh issue create --title "<title>" --body-file <file>`. No label. Keep the body file outside the repo.

## 2. The example map

Propose the map and write it into the issue (`gh issue edit <n> --body-file <file>`):

- **Rules** (`R1`, `R2`…): one business rule each, in the glossary's words. Each one is a candidate task.
- **Examples** (`E1`, `E2`…), numbered across the whole map: concrete input and expected result, under their rule. Each one becomes a test. Cover the edges (the exact limit, empty, not allowed), not only the happy path.
- **Questions:** what you cannot answer from the idea or the code. Classify each one with the `sdd-decisions` criterion:
  - **A decision that outlives this work** (a rule's edge, an architecture choice, a discarded approach): draft it with `record-decision` as `proposed`, with your recommended option as the decision and the others under the discarded alternatives. In the map, the question points to it: `Question: and exactly 1 h? → D-0021`.
  - **A decision that only matters for this work:** leave it in the map with options and your recommendation.
  - **An assumption** with a clear default: write it under **Assumptions** in the issue.

For work that is not a rule (infrastructure, refactor, migration), replace the map with **steps**: each one leaves the project green and says the command that proves it.

## 3. The stop

Tell the person, in a few lines: the issue link, how many rules and examples, one line per decision record (id, title, the recommended choice) and per open question, and how many assumptions. Do not paste the map. "ok" accepts the map, the recommendations and the assumptions; they can answer only what they want to change, here or by editing the issue.

Apply their corrections to the issue. Set the records they accepted to `accepted` (file and index) and run `check_decisions.py docs/decisions`. Never accept a record without their ok.

## 4. The tasks

Add the checklist to the issue, in the format `task-done` reads:

```
- [ ] T1. Thinnest end-to-end slice: cancel without refund — tests: E2 — verification: <single-test command>
- [ ] T2. R1 full refund — tests: E1 — verification: <single-test command>
- [ ] T3. R2 trip started — tests: E3 — verification: <single-test command>
- [ ] W1. Full verification — verification: <verification command from AGENTS.md>
```

- **Vertical slices:** each task goes through every layer it needs and leaves something that works. **T1 is always the thinnest slice that works end to end.**
- Every example goes in exactly one task's `tests:`. Steps without examples have only `verification:`.
- The verification is a runnable command: the single-test command from `AGENTS.md` for the task's tests; the full verification command for `W1`. If `AGENTS.md` has none, ask for it.
- A task is well bounded if you can name its test before starting, it fits in one commit with a readable diff, and it leaves the project green. If not, split it, or go back to the map.
- Tasks on delicate rules (money, personal data) end with `— level: A`: `implement` stops at their red tests and waits for the person's ok.
- Field names follow the project language (`verificación:` in Spanish); `tests:` is the same in both.

This is not a second stop: write the tasks and tell the person they are there. If writing them shows a gap in the map (an example with no task, a task with no test), say so instead of filling it silently.

**Next step:** a branch linked to the issue, `gh issue develop <n> --checkout` (its name starts with the issue number, which is how `task-done` finds the issue), and the `implement` agent with the issue number.

## Without gh

If `gh` is missing, not logged in, or there is no network, say so and write the same body to `docs/specs/<YYYYMMDD>-<type>-<name>/tasks.md` (type as in Conventional Commits, name in kebab-case). The rest of the flow is the same: `task-done` and `implement` work on that file. If the person creates the issue later (`gh issue create --body-file <that file>`), the issue becomes the source and the file is deleted.

## Never

- Paste the map or the tasks in the chat to get them approved: they are in the issue.
- Accept a decision record yourself, or record an assumption as a decision.
- Add a label to the issue, or start implementing: this skill ends at the tasks.
