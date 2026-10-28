---
name: record-decision
description: Records the decisions taken in a conversation as short files in docs/decisions/ (architecture, business rules and discarded approaches), keeps the index up to date and handles superseding an earlier decision. Drafts them as proposed; only the person accepts them. Use it after planning a change with the person, when a debugging session rules out an approach worth remembering, when asked to record, log or document a decision, or to migrate docs/adr/ to docs/decisions/.
kind: skill
uses:
  - skill:sdd-decisions
---

# Record a decision

In two months nobody will remember why something is the way it is. A decision record keeps the why, so that a later change does not contradict it without noticing. **You draft; the person decides.** You write records as `proposed` and never mark them `accepted` yourself.

The code and the tests say what the system does. A record says why, and what was ruled out. It is never edited once accepted: if the decision changes, a new record supersedes it.

## What is recorded

Record a decision when **both** hold:

1. It was a real choice: there were reasonable alternatives (the criterion of `sdd-decisions`).
2. It outlives the current work: a later change could contradict it, or someone could propose the discarded option again.

Three types:

- **architecture:** structure, dependencies, persistence, contracts, tooling. What ADRs used to cover.
- **rule:** a business rule and its edge ("full refund when cancelling more than 1 h ahead; exactly 1 h counts as late").
- **discarded:** "we tried X and it did not work, because Y". The type that saves the most work later.

Not recorded: assumptions with a clear default (they stay in the change's `README.md`, the spec or the plan), naming and layout details, anything the code or a test already makes obvious, and decisions that only matter until the current work item is closed. Most trivial tasks and bug fixes leave no record. If in doubt, propose it and let the person drop it.

## Process

1. **Read the index.** Open `docs/decisions/README.md`. If it does not exist, create the directory from `assets/en/README.md` or `assets/es/README.md` (the language the project is documented in), after telling the person. If the project still has `docs/adr/`, see "Migrating from docs/adr/".
2. **Look for clashes.** Find the rows whose *Affects* overlaps with what the new decision touches and read those records. If the new decision contradicts an accepted one, say so and ask: does it supersede it, or is the new decision wrong? Never contradict a record silently.
3. **Draft the records.** For each decision, get the next id with `python3 <this skill>/scripts/check_decisions.py docs/decisions --next` and copy `assets/<lang>/decision.md` as `docs/decisions/NNNN-title-in-kebab-case.md`. Remove the template's opening comment: the file must start with the frontmatter.
   - Frontmatter keys and values stay in English; the text goes in the project language.
   - `status: proposed`, today's `date`, `issue` if there is one.
   - `affects`: the modules or paths it constrains, as precise as possible. Agents filter on it; `[.]` makes the record show up for every change.
   - Keep the four sections short: a few lines each. Context and the discarded alternatives come from the conversation; do not invent reasons nobody gave. If a reason is missing, ask.
   - **How it is enforced:** name the test, lint rule or check that protects it. A test that protects a decision cites its id in a comment (`# D-0021`). If nothing enforces it, write "not automated".
4. **Add the rows** to the index: `| [D-NNNN](NNNN-title.md) | title | type | status | affects |`.
5. **Check:** run `check_decisions.py docs/decisions` and fix what it reports.
6. **Ask for acceptance.** Show the person one line per record (id, title, type, the decision in one sentence) with the paths. "ok" accepts all of them; they can drop or correct any. Only then change `status` to `accepted`, in the file and in the index, and run the check again.

When called by another skill (`idea-to-change`, the SDD skills, `debug-root-cause`), the acceptance in step 6 is the same stop as that skill's review with the person: do not ask twice.

## Superseding a decision

1. Write the new record with `supersedes: D-OLD`.
2. In the old record, change only `status: superseded` and `superseded_by: D-NEW`. This is the only edit allowed on an accepted record, besides typos and broken links.
3. Update both rows in the index and run the check.

A decision that simply stops applying (the module was deleted) becomes `obsolete`, with one line under **Context** saying why and when.

## Migrating from docs/adr/

Offer it; do not do it without the person's ok. If they say no, the two directories coexist: add one row per ADR to the index, labelled with the ADR's number and linking to it (`| [D-0003](../adr/0003-title.md) | title | architecture | accepted | affects |`), and leave them as they are. `check_decisions.py` only checks that the ADR exists, and `--next` skips the ADR numbers.

If they say yes:

1. `git mv docs/adr/NNNN-title.md docs/decisions/NNNN-title.md`, keeping the numbers. The ADR template (`0000-*.md`) is deleted, not moved.
2. Convert the frontmatter: `id: D-NNNN`, `type: architecture`, translated keys (`titulo` → `title`, `estado` → `status`…). Status: `proposed` and `accepted` stay, `deprecated` becomes `obsolete`, `superseded` stays. A `rejected` ADR becomes `type: discarded` with `status: accepted`.
3. `affects`: propose it from the ADR's tags and content and let the person confirm. Do not leave it empty.
4. Keep the body as it is. Extra sections (Consequences, AI context) are allowed.
5. Replace `docs/adr/` links across the repo (`grep -rn "docs/adr\|adr/" --include=*.md`), rebuild the index, and run the check.

## Never

- Mark a record `accepted` without the person's ok.
- Edit the decision of an accepted record. Write a new one that supersedes it.
- Reuse a number, even if a record was deleted before being accepted.
- Write a record for an assumption or a detail, just to have one.
